from __future__ import annotations

from dataclasses import dataclass

import torch
import torch.nn.functional as F


@dataclass(frozen=True)
class LossBreakdown:
    total: torch.Tensor
    waveform_l1: torch.Tensor
    stft_l1: torch.Tensor
    sisdr_loss: torch.Tensor
    sisdr_db: torch.Tensor
    transient_presence_l1: torch.Tensor
    interference_projection_ratio: torch.Tensor
    absent_interval_l1: torch.Tensor


def align_waveforms(
    prediction: torch.Tensor,
    target: torch.Tensor,
    lengths: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    common_length = min(prediction.shape[-1], target.shape[-1])
    clipped_lengths = torch.clamp(lengths, max=common_length)
    return (
        prediction[..., :common_length],
        target[..., :common_length],
        clipped_lengths,
    )


def waveform_l1_loss(
    prediction: torch.Tensor,
    target: torch.Tensor,
    lengths: torch.Tensor,
) -> torch.Tensor:
    prediction, target, lengths = align_waveforms(prediction, target, lengths)
    max_len = prediction.shape[-1]
    mask = (
        torch.arange(max_len, device=prediction.device)
        .unsqueeze(0)
        .lt(lengths.unsqueeze(1))
        .float()
    )
    diff = torch.abs(prediction - target) * mask
    denom = mask.sum().clamp_min(1.0)
    return diff.sum() / denom


def stft_l1_loss(
    prediction: torch.Tensor,
    target: torch.Tensor,
    model,
) -> torch.Tensor:
    prediction, target, _ = align_waveforms(
        prediction,
        target,
        torch.full(
            (prediction.shape[0],),
            min(prediction.shape[-1], target.shape[-1]),
            device=prediction.device,
            dtype=torch.long,
        ),
    )
    pred_mag = torch.abs(model.stft(prediction))
    target_mag = torch.abs(model.stft(target))
    return F.l1_loss(torch.log1p(pred_mag), torch.log1p(target_mag))


def transient_presence_l1_loss(
    prediction: torch.Tensor,
    target: torch.Tensor,
    lengths: torch.Tensor,
    model,
    sample_weights: torch.Tensor | None = None,
    sample_rate: int = 16000,
    top_ratio: float = 0.12,
    min_count: int = 8,
    mid_low_hz: float = 800.0,
    mid_high_hz: float = 3000.0,
    presence_low_hz: float = 3000.0,
    presence_high_hz: float = 8000.0,
    ratio_weight: float = 0.5,
) -> torch.Tensor:
    prediction, target, lengths = align_waveforms(prediction, target, lengths)
    pred_mag = torch.abs(model.stft(prediction))
    target_mag = torch.abs(model.stft(target))
    pred_power = pred_mag.square()
    target_power = target_mag.square()

    max_frames = target_power.shape[-1]
    frame_lengths = model.waveform_lengths_to_frame_lengths(lengths, max_frames=max_frames)
    nyquist = sample_rate / 2.0
    freqs = torch.fft.rfftfreq(model.n_fft, d=1.0 / float(sample_rate)).to(prediction.device)

    mid_mask = (freqs >= mid_low_hz) & (freqs < mid_high_hz)
    presence_mask = (freqs >= presence_low_hz) & (freqs < min(presence_high_hz, nyquist))

    if not torch.any(mid_mask) or not torch.any(presence_mask):
        return prediction.new_tensor(0.0)

    sample_losses: list[torch.Tensor] = []
    eps = 1e-8

    for pred_item, target_item, frame_length in zip(pred_power, target_power, frame_lengths):
        valid_frames = int(frame_length.item())
        if valid_frames <= 1:
            sample_losses.append(prediction.new_tensor(0.0))
            continue

        pred_item = pred_item[:, :valid_frames]
        target_item = target_item[:, :valid_frames]

        target_presence = target_item[presence_mask].sum(dim=0)
        target_mid = target_item[mid_mask].sum(dim=0)
        pred_presence = pred_item[presence_mask].sum(dim=0)
        pred_mid = pred_item[mid_mask].sum(dim=0)

        flux = torch.relu(torch.log1p(target_presence[1:]) - torch.log1p(target_presence[:-1]))
        flux_count = int(flux.shape[0])
        keep = max(min_count, int((flux_count * top_ratio) + 0.999999))
        keep = min(max(1, keep), flux_count)
        _, top_indices = torch.topk(flux, k=keep)
        transient_indices = torch.sort(top_indices + 1).values

        target_presence_sel = target_presence[transient_indices]
        pred_presence_sel = pred_presence[transient_indices]
        target_mid_sel = target_mid[transient_indices]
        pred_mid_sel = pred_mid[transient_indices]

        presence_term = F.l1_loss(torch.log1p(pred_presence_sel), torch.log1p(target_presence_sel))
        target_ratio = torch.log((target_presence_sel + eps) / (target_mid_sel + eps))
        pred_ratio = torch.log((pred_presence_sel + eps) / (pred_mid_sel + eps))
        ratio_term = F.l1_loss(pred_ratio, target_ratio)
        sample_losses.append(presence_term + (ratio_term * ratio_weight))

    stacked_losses = torch.stack(sample_losses)
    if sample_weights is None:
        return stacked_losses.mean()

    weights = sample_weights.to(device=stacked_losses.device, dtype=stacked_losses.dtype)
    if weights.ndim != 1 or weights.shape[0] != stacked_losses.shape[0]:
        raise ValueError(
            "sample_weights must be a 1-D tensor with one entry per batch item"
        )
    weight_sum = weights.sum()
    if float(weight_sum.item()) <= 0.0:
        return prediction.new_tensor(0.0)
    return torch.sum(stacked_losses * weights) / weight_sum


def interference_projection_loss(
    prediction: torch.Tensor,
    mixture: torch.Tensor,
    target: torch.Tensor,
    lengths: torch.Tensor,
    sample_weights: torch.Tensor | None = None,
) -> torch.Tensor:
    prediction, target, lengths = align_waveforms(prediction, target, lengths)
    common_length = min(prediction.shape[-1], mixture.shape[-1])
    prediction = prediction[..., :common_length]
    target = target[..., :common_length]
    lengths = torch.clamp(lengths, max=common_length)
    mixture = mixture[..., :common_length]

    eps = 1e-8
    sample_losses: list[torch.Tensor] = []
    for pred, mix, tgt, length in zip(prediction, mixture, target, lengths):
        length_int = int(length.item())
        if length_int <= 0:
            sample_losses.append(prediction.new_tensor(0.0))
            continue

        pred = pred[:length_int]
        interference = mix[:length_int] - tgt[:length_int]
        interference_energy = torch.sum(interference * interference)
        if float(interference_energy.item()) <= eps:
            sample_losses.append(prediction.new_tensor(0.0))
            continue

        projection_scale = torch.sum(pred * interference) / interference_energy.clamp_min(eps)
        projection = projection_scale * interference
        pred_energy = torch.sum(pred * pred).clamp_min(eps)
        projection_ratio = torch.sum(projection * projection) / pred_energy
        sample_losses.append(projection_ratio)

    stacked_losses = torch.stack(sample_losses)
    if sample_weights is None:
        return stacked_losses.mean()

    weights = sample_weights.to(device=stacked_losses.device, dtype=stacked_losses.dtype)
    if weights.ndim != 1 or weights.shape[0] != stacked_losses.shape[0]:
        raise ValueError(
            "sample_weights must be a 1-D tensor with one entry per batch item"
        )
    weight_sum = weights.sum()
    if float(weight_sum.item()) <= 0.0:
        return prediction.new_tensor(0.0)
    return torch.sum(stacked_losses * weights) / weight_sum


def absent_interval_l1_loss(
    prediction: torch.Tensor,
    target: torch.Tensor,
    lengths: torch.Tensor,
    absent_intervals: list[list[dict[str, float]]],
    sample_rate: int = 16000,
    sample_weights: torch.Tensor | None = None,
) -> torch.Tensor:
    prediction, target, lengths = align_waveforms(prediction, target, lengths)
    sample_losses: list[torch.Tensor] = []

    for pred, tgt, length, intervals in zip(prediction, target, lengths, absent_intervals):
        length_int = int(length.item())
        if length_int <= 0 or not intervals:
            sample_losses.append(prediction.new_tensor(0.0))
            continue

        pred = pred[:length_int]
        tgt = tgt[:length_int]
        diff = torch.abs(pred - tgt)

        interval_losses: list[torch.Tensor] = []
        total_interval_samples = 0
        for interval in intervals:
            start_index = int(round(float(interval["start_sec"]) * sample_rate))
            end_index = int(round(float(interval["end_sec"]) * sample_rate))
            start_index = max(0, min(start_index, length_int))
            end_index = max(start_index, min(end_index, length_int))
            if end_index <= start_index:
                continue
            interval_slice = diff[start_index:end_index]
            interval_losses.append(interval_slice.sum())
            total_interval_samples += end_index - start_index

        if total_interval_samples <= 0:
            sample_losses.append(prediction.new_tensor(0.0))
            continue

        sample_losses.append(torch.stack(interval_losses).sum() / float(total_interval_samples))

    stacked_losses = torch.stack(sample_losses)
    if sample_weights is None:
        return stacked_losses.mean()

    weights = sample_weights.to(device=stacked_losses.device, dtype=stacked_losses.dtype)
    if weights.ndim != 1 or weights.shape[0] != stacked_losses.shape[0]:
        raise ValueError(
            "sample_weights must be a 1-D tensor with one entry per batch item"
        )
    weight_sum = weights.sum()
    if float(weight_sum.item()) <= 0.0:
        return prediction.new_tensor(0.0)
    return torch.sum(stacked_losses * weights) / weight_sum


def masked_sisdr(
    prediction: torch.Tensor,
    target: torch.Tensor,
    lengths: torch.Tensor,
    zero_mean: bool = False,
) -> torch.Tensor:
    prediction, target, lengths = align_waveforms(prediction, target, lengths)
    values = []
    eps = 1e-8
    for pred, tgt, length in zip(prediction, target, lengths):
        length_int = int(length.item())
        pred = pred[:length_int]
        tgt = tgt[:length_int]
        if zero_mean:
            pred = pred - pred.mean()
            tgt = tgt - tgt.mean()
        tgt_energy = torch.sum(tgt * tgt).clamp_min(eps)
        proj = torch.sum(pred * tgt) * tgt / tgt_energy
        noise = pred - proj
        ratio = torch.sum(proj * proj).clamp_min(eps) / torch.sum(noise * noise).clamp_min(eps)
        values.append(10.0 * torch.log10(ratio + eps))
    return torch.stack(values).mean()


def compute_losses(
    prediction: torch.Tensor,
    mixture: torch.Tensor,
    target: torch.Tensor,
    lengths: torch.Tensor,
    absent_intervals: list[list[dict[str, float]]],
    model,
    transient_sample_weights: torch.Tensor | None = None,
    interference_sample_weights: torch.Tensor | None = None,
    absent_sample_weights: torch.Tensor | None = None,
    sample_rate: int = 16000,
    stft_weight: float = 0.5,
    sisdr_weight: float = 0.0,
    transient_weight: float = 0.0,
    interference_weight: float = 0.0,
    absent_weight: float = 0.0,
    transient_top_ratio: float = 0.12,
    transient_min_count: int = 8,
    transient_mid_low_hz: float = 800.0,
    transient_mid_high_hz: float = 3000.0,
    transient_presence_low_hz: float = 3000.0,
    transient_presence_high_hz: float = 8000.0,
    transient_ratio_weight: float = 0.5,
) -> LossBreakdown:
    waveform_term = waveform_l1_loss(prediction, target, lengths)
    stft_term = stft_l1_loss(prediction, target, model)
    sisdr_db = masked_sisdr(prediction, target, lengths, zero_mean=True)
    sisdr_term = -sisdr_db
    transient_term = transient_presence_l1_loss(
        prediction=prediction,
        target=target,
        lengths=lengths,
        model=model,
        sample_weights=transient_sample_weights,
        sample_rate=sample_rate,
        top_ratio=transient_top_ratio,
        min_count=transient_min_count,
        mid_low_hz=transient_mid_low_hz,
        mid_high_hz=transient_mid_high_hz,
        presence_low_hz=transient_presence_low_hz,
        presence_high_hz=transient_presence_high_hz,
        ratio_weight=transient_ratio_weight,
    )
    interference_term = interference_projection_loss(
        prediction=prediction,
        mixture=mixture,
        target=target,
        lengths=lengths,
        sample_weights=interference_sample_weights,
    )
    absent_term = absent_interval_l1_loss(
        prediction=prediction,
        target=target,
        lengths=lengths,
        absent_intervals=absent_intervals,
        sample_rate=sample_rate,
        sample_weights=absent_sample_weights,
    )
    total = (
        waveform_term
        + (stft_term * stft_weight)
        + (sisdr_term * sisdr_weight)
        + (transient_term * transient_weight)
        + (interference_term * interference_weight)
        + (absent_term * absent_weight)
    )
    return LossBreakdown(
        total=total,
        waveform_l1=waveform_term,
        stft_l1=stft_term,
        sisdr_loss=sisdr_term,
        sisdr_db=sisdr_db,
        transient_presence_l1=transient_term,
        interference_projection_ratio=interference_term,
        absent_interval_l1=absent_term,
    )
