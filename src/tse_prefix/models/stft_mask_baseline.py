from __future__ import annotations

import torch
from torch import nn
from torch.nn import functional as F
from torch.nn.utils.rnn import pad_sequence


class STFTMaskBaseline(nn.Module):
    def __init__(
        self,
        n_fft: int = 512,
        hop_length: int = 128,
        win_length: int = 512,
        hidden_dim: int = 256,
        reference_dim: int = 128,
        gru_layers: int = 2,
        conditioning_mode: str = "ref_film",
    ) -> None:
        super().__init__()
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.win_length = win_length
        self.freq_bins = (n_fft // 2) + 1
        self.conditioning_mode = conditioning_mode

        if conditioning_mode == "legacy_bias":
            self.mix_proj = nn.Linear(self.freq_bins, hidden_dim)
            self.ref_encoder = nn.Sequential(
                nn.Linear(self.freq_bins, hidden_dim),
                nn.ReLU(),
                nn.Linear(hidden_dim, reference_dim),
                nn.ReLU(),
            )
            self.condition_proj = nn.Linear(reference_dim, hidden_dim)
            gru_input_dim = hidden_dim
        elif conditioning_mode == "ref_film":
            self.mix_proj = nn.Sequential(
                nn.Linear(self.freq_bins, hidden_dim),
                nn.LayerNorm(hidden_dim),
                nn.ReLU(),
            )
            self.ref_frame_encoder = nn.Sequential(
                nn.Linear(self.freq_bins, hidden_dim),
                nn.ReLU(),
                nn.LayerNorm(hidden_dim),
                nn.Linear(hidden_dim, hidden_dim),
                nn.ReLU(),
            )
            self.ref_attention = nn.Linear(hidden_dim, 1)
            self.ref_encoder = nn.Sequential(
                nn.Linear(hidden_dim, hidden_dim),
                nn.ReLU(),
                nn.Linear(hidden_dim, reference_dim),
                nn.ReLU(),
            )
            self.reference_to_hidden = nn.Linear(reference_dim, hidden_dim)
            self.condition_scale = nn.Linear(reference_dim, hidden_dim)
            self.condition_shift = nn.Linear(reference_dim, hidden_dim)
            gru_input_dim = hidden_dim + 1
        else:
            raise ValueError(f"Unsupported conditioning_mode: {conditioning_mode}")

        self.temporal_model = nn.GRU(
            input_size=gru_input_dim,
            hidden_size=hidden_dim,
            num_layers=gru_layers,
            batch_first=True,
            bidirectional=True,
        )
        self.mask_head = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, self.freq_bins),
            nn.Sigmoid(),
        )

        self.register_buffer("window", torch.hann_window(win_length), persistent=False)

    def stft(self, waveform: torch.Tensor) -> torch.Tensor:
        return torch.stft(
            waveform,
            n_fft=self.n_fft,
            hop_length=self.hop_length,
            win_length=self.win_length,
            window=self.window,
            return_complex=True,
        )

    def istft(self, stft_tensor: torch.Tensor, lengths: torch.Tensor) -> torch.Tensor:
        outputs = []
        for spec, length in zip(stft_tensor, lengths):
            outputs.append(
                torch.istft(
                    spec,
                    n_fft=self.n_fft,
                    hop_length=self.hop_length,
                    win_length=self.win_length,
                    window=self.window,
                    length=int(length.item()),
                )
            )
        return pad_sequence(outputs, batch_first=True)

    def waveform_lengths_to_frame_lengths(
        self,
        waveform_lengths: torch.Tensor | None,
        max_frames: int,
    ) -> torch.Tensor | None:
        if waveform_lengths is None:
            return None
        frame_lengths = torch.div(
            waveform_lengths + self.hop_length - 1,
            self.hop_length,
            rounding_mode="floor",
        ) + 1
        return torch.clamp(frame_lengths, min=1, max=max_frames)

    def masked_attention_pool(
        self,
        features: torch.Tensor,
        frame_lengths: torch.Tensor | None,
    ) -> torch.Tensor:
        scores = self.ref_attention(features).squeeze(-1)
        if frame_lengths is None:
            weights = torch.softmax(scores, dim=1)
            return torch.sum(features * weights.unsqueeze(-1), dim=1)

        time_axis = torch.arange(features.shape[1], device=features.device).unsqueeze(0)
        valid_mask = time_axis < frame_lengths.unsqueeze(1)
        masked_scores = scores.masked_fill(~valid_mask, -1e9)
        weights = torch.softmax(masked_scores, dim=1)
        weights = weights * valid_mask.float()
        weights = weights / weights.sum(dim=1, keepdim=True).clamp_min(1e-8)
        return torch.sum(features * weights.unsqueeze(-1), dim=1)

    def encode_reference(
        self,
        reference: torch.Tensor,
        reference_lengths: torch.Tensor | None = None,
    ) -> torch.Tensor:
        if self.conditioning_mode == "legacy_bias":
            ref_stft = self.stft(reference)
            ref_mag = torch.abs(ref_stft)
            ref_summary = torch.log1p(ref_mag).mean(dim=-1)
            return self.ref_encoder(ref_summary)

        ref_stft = self.stft(reference)
        ref_mag = torch.abs(ref_stft)
        ref_features = torch.log1p(ref_mag).transpose(1, 2)
        ref_encoded = self.ref_frame_encoder(ref_features)
        frame_lengths = self.waveform_lengths_to_frame_lengths(
            reference_lengths,
            max_frames=ref_encoded.shape[1],
        )
        ref_summary = self.masked_attention_pool(ref_encoded, frame_lengths)
        return self.ref_encoder(ref_summary)

    def forward(
        self,
        mixture: torch.Tensor,
        mixture_lengths: torch.Tensor,
        reference: torch.Tensor,
        reference_lengths: torch.Tensor | None = None,
    ) -> dict[str, torch.Tensor]:
        mix_stft = self.stft(mixture)
        mix_mag = torch.abs(mix_stft)
        mix_features = torch.log1p(mix_mag).transpose(1, 2)

        ref_embedding = self.encode_reference(reference, reference_lengths=reference_lengths)
        if self.conditioning_mode == "legacy_bias":
            temporal_input = self.mix_proj(mix_features) + self.condition_proj(ref_embedding).unsqueeze(1)
        else:
            ref_hidden = self.reference_to_hidden(ref_embedding)
            gamma = torch.tanh(self.condition_scale(ref_embedding)).unsqueeze(1)
            beta = self.condition_shift(ref_embedding).unsqueeze(1)

            mix_encoded = self.mix_proj(mix_features)
            conditioned = (mix_encoded * (1.0 + gamma)) + beta
            similarity = F.cosine_similarity(
                conditioned,
                ref_hidden.unsqueeze(1),
                dim=-1,
                eps=1e-8,
            ).unsqueeze(-1)
            temporal_input = torch.cat([conditioned, similarity], dim=-1)

        encoded, _ = self.temporal_model(temporal_input)
        mask = self.mask_head(encoded).transpose(1, 2)

        estimated_stft = mix_stft * mask
        estimated_waveform = self.istft(estimated_stft, mixture_lengths)

        return {
            "estimated_waveform": estimated_waveform,
            "mask": mask,
            "mixture_stft": mix_stft,
            "estimated_stft": estimated_stft,
        }
