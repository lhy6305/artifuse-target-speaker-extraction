from __future__ import annotations

import math

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
        enable_adapter_mask_head: bool = False,
        enable_branch_decoder_head: bool = False,
        enable_branch_abstention_gate: bool = False,
        enable_branch_overlap_refine_head: bool = False,
        enable_branch_overlap_refine_present_head: bool = False,
        enable_branch_overlap_cancel_head: bool = False,
        enable_branch_overlap_cancel_apply_controller: bool = False,
        enable_branch_overlap_cancel_apply_absent_controller: bool = False,
        enable_branch_overlap_cancel_pre_present_controller: bool = False,
        enable_branch_overlap_dual_decoder_head: bool = False,
        enable_branch_overlap_dual_monitor_controller: bool = False,
        enable_branch_overlap_dual_cancel_controller: bool = False,
        enable_branch_overlap_dual_residual_correction_head: bool = False,
        enable_adapter_temporal_model: bool = False,
        adapter_gru_layers: int = 1,
        adapter_conditioning_mode: str = "none",
        adapter_mask_max_delta: float = 0.25,
        branch_overlap_refine_max_delta: float = 0.15,
        branch_overlap_refine_gate_mode: str = "gate",
        branch_overlap_refine_gate_power: float = 1.0,
        branch_overlap_refine_gate_floor: float = 0.0,
        branch_overlap_refine_source_mode: str = "mixture",
        branch_overlap_refine_present_max_delta: float = 0.15,
        branch_overlap_refine_present_source_mode: str = "residual",
        branch_overlap_refine_present_gate_power: float = 1.0,
        branch_overlap_refine_present_gate_floor: float = 0.0,
        branch_overlap_refine_present_veto_mode: str = "none",
        branch_overlap_refine_present_veto_strength: float = 0.0,
        branch_overlap_refine_present_veto_power: float = 1.0,
        branch_overlap_cancel_max_delta: float = 0.15,
        branch_overlap_cancel_gate_mode: str = "complement",
        branch_overlap_cancel_source_mode: str = "residual",
        branch_overlap_cancel_apply_mode: str = "subtract",
        branch_overlap_cancel_ratio_mode: str = "complex",
        branch_overlap_cancel_delta_blend_mode: str = "none",
        branch_overlap_cancel_max_blend: float = 1.0,
        branch_overlap_cancel_pre_present_max_blend: float = 0.0,
        branch_overlap_cancel_pre_present_controller_floor: float = 0.0,
        branch_overlap_cancel_apply_controller_floor: float = 0.0,
        branch_overlap_cancel_apply_max_freq_ratio: float = 1.0,
        branch_overlap_dual_decoder_max_delta: float = 0.15,
        branch_overlap_dual_decoder_gate_mode: str = "complement",
        branch_overlap_dual_decoder_source_mode: str = "residual",
        branch_overlap_dual_decoder_apply_mode: str = "final_output",
        branch_overlap_dual_decoder_max_blend: float = 1.0,
        branch_overlap_dual_decoder_gate_floor: float = 0.0,
        branch_overlap_dual_monitor_max_blend: float = 0.0,
        branch_overlap_dual_cancel_max_blend: float = 0.0,
        branch_overlap_dual_residual_correction_max_delta: float = 0.15,
        branch_overlap_dual_residual_correction_max_blend: float = 0.0,
    ) -> None:
        super().__init__()
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.win_length = win_length
        self.freq_bins = (n_fft // 2) + 1
        self.conditioning_mode = conditioning_mode
        self.enable_adapter_mask_head = enable_adapter_mask_head
        self.enable_branch_decoder_head = enable_branch_decoder_head
        self.enable_branch_abstention_gate = enable_branch_abstention_gate
        self.enable_branch_overlap_refine_head = enable_branch_overlap_refine_head
        self.enable_branch_overlap_refine_present_head = enable_branch_overlap_refine_present_head
        self.enable_branch_overlap_cancel_head = enable_branch_overlap_cancel_head
        self.enable_branch_overlap_cancel_apply_controller = enable_branch_overlap_cancel_apply_controller
        self.enable_branch_overlap_cancel_apply_absent_controller = (
            enable_branch_overlap_cancel_apply_absent_controller
        )
        self.enable_branch_overlap_cancel_pre_present_controller = (
            enable_branch_overlap_cancel_pre_present_controller
        )
        self.enable_branch_overlap_dual_decoder_head = enable_branch_overlap_dual_decoder_head
        self.enable_branch_overlap_dual_monitor_controller = enable_branch_overlap_dual_monitor_controller
        self.enable_branch_overlap_dual_cancel_controller = enable_branch_overlap_dual_cancel_controller
        self.enable_branch_overlap_dual_residual_correction_head = (
            enable_branch_overlap_dual_residual_correction_head
        )
        self.enable_adapter_temporal_model = enable_adapter_temporal_model
        self.adapter_conditioning_mode = adapter_conditioning_mode
        self.adapter_mask_max_delta = adapter_mask_max_delta
        self.branch_overlap_refine_max_delta = branch_overlap_refine_max_delta
        self.branch_overlap_refine_gate_mode = branch_overlap_refine_gate_mode
        self.branch_overlap_refine_gate_power = branch_overlap_refine_gate_power
        self.branch_overlap_refine_gate_floor = branch_overlap_refine_gate_floor
        self.branch_overlap_refine_source_mode = branch_overlap_refine_source_mode
        self.branch_overlap_refine_present_max_delta = branch_overlap_refine_present_max_delta
        self.branch_overlap_refine_present_source_mode = branch_overlap_refine_present_source_mode
        self.branch_overlap_refine_present_gate_power = branch_overlap_refine_present_gate_power
        self.branch_overlap_refine_present_gate_floor = branch_overlap_refine_present_gate_floor
        self.branch_overlap_refine_present_veto_mode = branch_overlap_refine_present_veto_mode
        self.branch_overlap_refine_present_veto_strength = branch_overlap_refine_present_veto_strength
        self.branch_overlap_refine_present_veto_power = branch_overlap_refine_present_veto_power
        self.branch_overlap_cancel_max_delta = branch_overlap_cancel_max_delta
        self.branch_overlap_cancel_gate_mode = branch_overlap_cancel_gate_mode
        self.branch_overlap_cancel_source_mode = branch_overlap_cancel_source_mode
        self.branch_overlap_cancel_apply_mode = branch_overlap_cancel_apply_mode
        self.branch_overlap_cancel_ratio_mode = branch_overlap_cancel_ratio_mode
        self.branch_overlap_cancel_delta_blend_mode = branch_overlap_cancel_delta_blend_mode
        self.branch_overlap_cancel_max_blend = branch_overlap_cancel_max_blend
        self.branch_overlap_cancel_pre_present_max_blend = branch_overlap_cancel_pre_present_max_blend
        self.branch_overlap_cancel_pre_present_controller_floor = (
            branch_overlap_cancel_pre_present_controller_floor
        )
        self.branch_overlap_cancel_apply_controller_floor = branch_overlap_cancel_apply_controller_floor
        self.branch_overlap_cancel_apply_max_freq_ratio = branch_overlap_cancel_apply_max_freq_ratio
        self.branch_overlap_dual_decoder_max_delta = branch_overlap_dual_decoder_max_delta
        self.branch_overlap_dual_decoder_gate_mode = branch_overlap_dual_decoder_gate_mode
        self.branch_overlap_dual_decoder_source_mode = branch_overlap_dual_decoder_source_mode
        self.branch_overlap_dual_decoder_apply_mode = branch_overlap_dual_decoder_apply_mode
        self.branch_overlap_dual_decoder_max_blend = branch_overlap_dual_decoder_max_blend
        self.branch_overlap_dual_decoder_gate_floor = branch_overlap_dual_decoder_gate_floor
        self.branch_overlap_dual_monitor_max_blend = branch_overlap_dual_monitor_max_blend
        self.branch_overlap_dual_cancel_max_blend = branch_overlap_dual_cancel_max_blend
        self.branch_overlap_dual_residual_correction_max_delta = (
            branch_overlap_dual_residual_correction_max_delta
        )
        self.branch_overlap_dual_residual_correction_max_blend = (
            branch_overlap_dual_residual_correction_max_blend
        )

        if enable_adapter_mask_head and enable_branch_decoder_head:
            raise ValueError("Adapter mask head and branch decoder head are mutually exclusive for now.")
        if enable_branch_abstention_gate and not enable_branch_decoder_head:
            raise ValueError("Branch abstention gate requires enable_branch_decoder_head.")
        if enable_branch_overlap_refine_head and not enable_branch_decoder_head:
            raise ValueError("Branch overlap refiner requires enable_branch_decoder_head.")
        if enable_branch_overlap_refine_present_head and not enable_branch_overlap_refine_head:
            raise ValueError("Branch overlap present refiner requires enable_branch_overlap_refine_head.")
        if enable_branch_overlap_refine_present_head and not enable_branch_abstention_gate:
            raise ValueError("Branch overlap present refiner requires enable_branch_abstention_gate.")
        if enable_branch_overlap_cancel_head and not enable_branch_decoder_head:
            raise ValueError("Branch overlap canceller requires enable_branch_decoder_head.")
        if enable_branch_overlap_cancel_apply_controller and not enable_branch_overlap_cancel_head:
            raise ValueError(
                "Branch overlap cancel apply controller requires enable_branch_overlap_cancel_head."
            )
        if enable_branch_overlap_cancel_apply_absent_controller and not enable_branch_overlap_cancel_apply_controller:
            raise ValueError(
                "Branch overlap cancel apply absent controller requires enable_branch_overlap_cancel_apply_controller."
            )
        if enable_branch_overlap_cancel_pre_present_controller and not enable_branch_overlap_cancel_head:
            raise ValueError(
                "Branch overlap cancel pre-present controller requires enable_branch_overlap_cancel_head."
            )
        if enable_branch_overlap_dual_decoder_head and not enable_branch_decoder_head:
            raise ValueError("Branch overlap dual decoder requires enable_branch_decoder_head.")
        if enable_branch_overlap_dual_monitor_controller and not enable_branch_overlap_dual_decoder_head:
            raise ValueError("Branch overlap dual monitor controller requires enable_branch_overlap_dual_decoder_head.")
        if enable_branch_overlap_dual_cancel_controller and not enable_branch_overlap_dual_decoder_head:
            raise ValueError("Branch overlap dual cancel controller requires enable_branch_overlap_dual_decoder_head.")
        if enable_branch_overlap_dual_cancel_controller and not enable_branch_overlap_cancel_head:
            raise ValueError("Branch overlap dual cancel controller requires enable_branch_overlap_cancel_head.")
        if enable_branch_overlap_dual_residual_correction_head and not enable_branch_overlap_dual_decoder_head:
            raise ValueError(
                "Branch overlap dual residual correction head requires enable_branch_overlap_dual_decoder_head."
            )
        if branch_overlap_refine_gate_mode not in ("none", "gate", "complement"):
            raise ValueError(
                "branch_overlap_refine_gate_mode must be one of: none, gate, complement."
            )
        if branch_overlap_refine_gate_power <= 0.0:
            raise ValueError(
                "branch_overlap_refine_gate_power must be strictly positive."
            )
        if not 0.0 <= branch_overlap_refine_gate_floor < 1.0:
            raise ValueError(
                "branch_overlap_refine_gate_floor must satisfy 0.0 <= floor < 1.0."
            )
        if branch_overlap_refine_source_mode not in ("mixture", "branch_base", "residual"):
            raise ValueError(
                "branch_overlap_refine_source_mode must be one of: mixture, branch_base, residual."
            )
        if branch_overlap_refine_present_source_mode not in (
            "mixture",
            "branch_base",
            "residual",
            "current_residual",
        ):
            raise ValueError(
                "branch_overlap_refine_present_source_mode must be one of: "
                "mixture, branch_base, residual, current_residual."
            )
        if branch_overlap_refine_present_gate_power <= 0.0:
            raise ValueError(
                "branch_overlap_refine_present_gate_power must be strictly positive."
            )
        if not 0.0 <= branch_overlap_refine_present_gate_floor < 1.0:
            raise ValueError(
                "branch_overlap_refine_present_gate_floor must satisfy 0.0 <= floor < 1.0."
            )
        if branch_overlap_refine_present_veto_mode not in ("none", "complement_gate", "complement_ratio"):
            raise ValueError(
                "branch_overlap_refine_present_veto_mode must be one of: "
                "none, complement_gate, complement_ratio."
            )
        if not 0.0 <= branch_overlap_refine_present_veto_strength <= 1.0:
            raise ValueError(
                "branch_overlap_refine_present_veto_strength must satisfy 0.0 <= strength <= 1.0."
            )
        if branch_overlap_refine_present_veto_power <= 0.0:
            raise ValueError(
                "branch_overlap_refine_present_veto_power must be strictly positive."
            )
        if (
            branch_overlap_refine_present_veto_mode == "complement_ratio"
            and enable_branch_overlap_refine_present_head
            and not enable_branch_overlap_refine_head
        ):
            raise ValueError(
                "branch_overlap_refine_present_veto_mode=complement_ratio "
                "requires enable_branch_overlap_refine_head."
            )
        if branch_overlap_cancel_gate_mode not in ("none", "gate", "complement"):
            raise ValueError(
                "branch_overlap_cancel_gate_mode must be one of: none, gate, complement."
            )
        if branch_overlap_cancel_source_mode not in ("mixture", "branch_base", "residual"):
            raise ValueError(
                "branch_overlap_cancel_source_mode must be one of: mixture, branch_base, residual."
            )
        if branch_overlap_cancel_apply_mode not in (
            "subtract",
            "pre_present_subtract",
            "branch_base_blend",
            "refine_base_blend",
            "auxiliary_only",
        ):
            raise ValueError(
                "branch_overlap_cancel_apply_mode must be one of: "
                "subtract, pre_present_subtract, branch_base_blend, refine_base_blend, auxiliary_only."
            )
        if branch_overlap_cancel_ratio_mode not in ("complex", "phase_preserve"):
            raise ValueError(
                "branch_overlap_cancel_ratio_mode must be one of: complex, phase_preserve."
            )
        if branch_overlap_cancel_delta_blend_mode not in ("none", "gate", "complement", "predicted_activity"):
            raise ValueError(
                "branch_overlap_cancel_delta_blend_mode must be one of: "
                "none, gate, complement, predicted_activity."
            )
        if not 0.0 <= branch_overlap_cancel_apply_controller_floor < 1.0:
            raise ValueError(
                "branch_overlap_cancel_apply_controller_floor must satisfy 0.0 <= floor < 1.0."
            )
        if not 0.0 <= branch_overlap_cancel_pre_present_controller_floor < 1.0:
            raise ValueError(
                "branch_overlap_cancel_pre_present_controller_floor must satisfy 0.0 <= floor < 1.0."
            )
        if not 0.0 < branch_overlap_cancel_apply_max_freq_ratio <= 1.0:
            raise ValueError(
                "branch_overlap_cancel_apply_max_freq_ratio must satisfy 0.0 < ratio <= 1.0."
            )
        if branch_overlap_dual_decoder_gate_mode not in ("none", "gate", "complement"):
            raise ValueError(
                "branch_overlap_dual_decoder_gate_mode must be one of: none, gate, complement."
            )
        if branch_overlap_dual_decoder_source_mode not in ("mixture", "branch_base", "residual"):
            raise ValueError(
                "branch_overlap_dual_decoder_source_mode must be one of: mixture, branch_base, residual."
            )
        if branch_overlap_dual_decoder_apply_mode not in ("final_output", "current_output", "gate_controller"):
            raise ValueError(
                "branch_overlap_dual_decoder_apply_mode must be one of: "
                "final_output, current_output, gate_controller."
            )
        if not 0.0 <= branch_overlap_dual_decoder_gate_floor < 1.0:
            raise ValueError("branch_overlap_dual_decoder_gate_floor must satisfy 0.0 <= floor < 1.0.")
        if not 0.0 <= branch_overlap_dual_monitor_max_blend <= 1.0:
            raise ValueError("branch_overlap_dual_monitor_max_blend must satisfy 0.0 <= blend <= 1.0.")
        if not 0.0 <= branch_overlap_dual_cancel_max_blend <= 1.0:
            raise ValueError("branch_overlap_dual_cancel_max_blend must satisfy 0.0 <= blend <= 1.0.")
        if branch_overlap_dual_residual_correction_max_delta <= 0.0:
            raise ValueError("branch_overlap_dual_residual_correction_max_delta must be positive.")
        if not 0.0 <= branch_overlap_dual_residual_correction_max_blend <= 1.0:
            raise ValueError(
                "branch_overlap_dual_residual_correction_max_blend must satisfy 0.0 <= blend <= 1.0."
            )
        if branch_overlap_dual_decoder_apply_mode == "gate_controller" and not enable_branch_abstention_gate:
            raise ValueError("branch_overlap_dual_decoder_apply_mode=gate_controller requires enable_branch_abstention_gate.")

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
        if enable_branch_decoder_head:
            self.branch_decoder_temporal_model = nn.GRU(
                input_size=gru_input_dim,
                hidden_size=hidden_dim,
                num_layers=gru_layers,
                batch_first=True,
                bidirectional=True,
            )
            self.branch_decoder_mask_head = nn.Sequential(
                nn.Linear(hidden_dim * 2, hidden_dim),
                nn.ReLU(),
                nn.Linear(hidden_dim, self.freq_bins),
                nn.Sigmoid(),
            )
            if enable_branch_abstention_gate:
                self.branch_decoder_gate_head = nn.Sequential(
                    nn.Linear(hidden_dim * 2, hidden_dim),
                    nn.ReLU(),
                    nn.Linear(hidden_dim, 1),
                )
                self.reset_branch_abstention_gate()
            else:
                self.branch_decoder_gate_head = None
            if enable_branch_overlap_refine_head:
                self.branch_overlap_refine_head = nn.Sequential(
                    nn.Linear(hidden_dim * 2, hidden_dim),
                    nn.ReLU(),
                    nn.Linear(hidden_dim, self.freq_bins * 2),
                )
                self.reset_branch_overlap_refine_head()
            else:
                self.branch_overlap_refine_head = None
            if enable_branch_overlap_refine_present_head:
                self.branch_overlap_refine_present_head = nn.Sequential(
                    nn.Linear(hidden_dim * 2, hidden_dim),
                    nn.ReLU(),
                    nn.Linear(hidden_dim, self.freq_bins * 2),
                )
                self.reset_branch_overlap_refine_present_head()
            else:
                self.branch_overlap_refine_present_head = None
            if enable_branch_overlap_cancel_head:
                cancel_head_out_dim = (
                    self.freq_bins * 2
                    if self.branch_overlap_cancel_ratio_mode == "complex"
                    else self.freq_bins
                )
                self.branch_overlap_cancel_head = nn.Sequential(
                    nn.Linear(hidden_dim * 2, hidden_dim),
                    nn.ReLU(),
                    nn.Linear(hidden_dim, cancel_head_out_dim),
                )
                self.reset_branch_overlap_cancel_head()
            else:
                self.branch_overlap_cancel_head = None
            if enable_branch_overlap_cancel_apply_controller:
                self.branch_overlap_cancel_apply_controller_head = nn.Sequential(
                    nn.Linear(hidden_dim * 2, hidden_dim),
                    nn.ReLU(),
                    nn.Linear(hidden_dim, 1),
                )
                self.reset_branch_overlap_cancel_apply_controller_head()
            else:
                self.branch_overlap_cancel_apply_controller_head = None
            if enable_branch_overlap_cancel_apply_absent_controller:
                self.branch_overlap_cancel_apply_absent_controller_head = nn.Sequential(
                    nn.Linear(hidden_dim * 2, hidden_dim),
                    nn.ReLU(),
                    nn.Linear(hidden_dim, 1),
                )
                self.reset_branch_overlap_cancel_apply_absent_controller_head()
            else:
                self.branch_overlap_cancel_apply_absent_controller_head = None
            if enable_branch_overlap_cancel_pre_present_controller:
                self.branch_overlap_cancel_pre_present_controller_head = nn.Sequential(
                    nn.Linear(hidden_dim * 2, hidden_dim),
                    nn.ReLU(),
                    nn.Linear(hidden_dim, 1),
                )
                self.reset_branch_overlap_cancel_pre_present_controller_head()
            else:
                self.branch_overlap_cancel_pre_present_controller_head = None
            if enable_branch_overlap_dual_decoder_head:
                self.branch_overlap_dual_decoder_temporal_model = nn.GRU(
                    input_size=gru_input_dim,
                    hidden_size=hidden_dim,
                    num_layers=gru_layers,
                    batch_first=True,
                    bidirectional=True,
                )
                self.branch_overlap_dual_decoder_head = nn.Sequential(
                    nn.Linear(hidden_dim * 2, hidden_dim),
                    nn.ReLU(),
                    nn.Linear(hidden_dim, self.freq_bins * 2),
                )
                self.reset_branch_overlap_dual_decoder_head()
                if enable_branch_overlap_dual_monitor_controller:
                    self.branch_overlap_dual_monitor_controller_head = nn.Sequential(
                        nn.Linear(hidden_dim * 2, hidden_dim),
                        nn.ReLU(),
                        nn.Linear(hidden_dim, 1),
                    )
                    self.reset_branch_overlap_dual_monitor_controller_head()
                else:
                    self.branch_overlap_dual_monitor_controller_head = None
                if enable_branch_overlap_dual_cancel_controller:
                    self.branch_overlap_dual_cancel_controller_head = nn.Sequential(
                        nn.Linear(hidden_dim * 2, hidden_dim),
                        nn.ReLU(),
                        nn.Linear(hidden_dim, 1),
                    )
                    self.reset_branch_overlap_dual_cancel_controller_head()
                else:
                    self.branch_overlap_dual_cancel_controller_head = None
                if enable_branch_overlap_dual_residual_correction_head:
                    self.branch_overlap_dual_residual_correction_head = nn.Sequential(
                        nn.Linear(hidden_dim * 2, hidden_dim),
                        nn.ReLU(),
                        nn.Linear(hidden_dim, self.freq_bins * 2),
                    )
                    self.branch_overlap_dual_residual_correction_controller_head = nn.Sequential(
                        nn.Linear(hidden_dim * 2, hidden_dim),
                        nn.ReLU(),
                        nn.Linear(hidden_dim, 1),
                    )
                    self.reset_branch_overlap_dual_residual_correction_head()
                    self.reset_branch_overlap_dual_residual_correction_controller_head()
                else:
                    self.branch_overlap_dual_residual_correction_head = None
                    self.branch_overlap_dual_residual_correction_controller_head = None
            else:
                self.branch_overlap_dual_decoder_temporal_model = None
                self.branch_overlap_dual_decoder_head = None
                self.branch_overlap_dual_monitor_controller_head = None
                self.branch_overlap_dual_cancel_controller_head = None
                self.branch_overlap_dual_residual_correction_head = None
                self.branch_overlap_dual_residual_correction_controller_head = None
            self.reset_branch_decoder_from_base()
            self.reset_branch_overlap_dual_decoder_from_branch()
        else:
            self.branch_decoder_temporal_model = None
            self.branch_decoder_mask_head = None
            self.branch_decoder_gate_head = None
            self.branch_overlap_refine_head = None
            self.branch_overlap_refine_present_head = None
            self.branch_overlap_cancel_head = None
            self.branch_overlap_cancel_apply_controller_head = None
            self.branch_overlap_cancel_apply_absent_controller_head = None
            self.branch_overlap_cancel_pre_present_controller_head = None
            self.branch_overlap_dual_decoder_temporal_model = None
            self.branch_overlap_dual_decoder_head = None
            self.branch_overlap_dual_monitor_controller_head = None
            self.branch_overlap_dual_cancel_controller_head = None
            self.branch_overlap_dual_residual_correction_head = None
            self.branch_overlap_dual_residual_correction_controller_head = None
        apply_band_bins = max(1, int(math.ceil(self.freq_bins * self.branch_overlap_cancel_apply_max_freq_ratio)))
        apply_band_mask = torch.zeros(1, self.freq_bins, 1)
        apply_band_mask[:, :apply_band_bins, :] = 1.0
        self.register_buffer(
            "branch_overlap_cancel_apply_band_mask",
            apply_band_mask,
            persistent=False,
        )
        if enable_adapter_mask_head:
            adapter_hidden_dim = hidden_dim * 2
            if enable_adapter_temporal_model:
                self.adapter_temporal_model = nn.GRU(
                    input_size=gru_input_dim,
                    hidden_size=hidden_dim,
                    num_layers=adapter_gru_layers,
                    batch_first=True,
                    bidirectional=True,
                )
            else:
                self.adapter_temporal_model = None
            if adapter_conditioning_mode == "none":
                self.adapter_condition_proj = None
                self.adapter_condition_scale = None
                self.adapter_condition_shift = None
            elif adapter_conditioning_mode == "ref_bias":
                self.adapter_condition_proj = nn.Linear(reference_dim, adapter_hidden_dim)
                self.adapter_condition_scale = None
                self.adapter_condition_shift = None
            elif adapter_conditioning_mode == "ref_film":
                self.adapter_condition_proj = None
                self.adapter_condition_scale = nn.Linear(reference_dim, adapter_hidden_dim)
                self.adapter_condition_shift = nn.Linear(reference_dim, adapter_hidden_dim)
            else:
                raise ValueError(f"Unsupported adapter_conditioning_mode: {adapter_conditioning_mode}")
            self.adapter_mask_head = nn.Sequential(
                nn.Linear(adapter_hidden_dim, hidden_dim),
                nn.ReLU(),
                nn.Linear(hidden_dim, self.freq_bins),
            )
            final_layer = self.adapter_mask_head[-1]
            nn.init.zeros_(final_layer.weight)
            nn.init.zeros_(final_layer.bias)
        else:
            self.adapter_temporal_model = None
            self.adapter_condition_proj = None
            self.adapter_condition_scale = None
            self.adapter_condition_shift = None
            self.adapter_mask_head = None

        self.register_buffer("window", torch.hann_window(win_length), persistent=False)

    def reset_branch_decoder_from_base(self) -> None:
        if self.branch_decoder_temporal_model is None or self.branch_decoder_mask_head is None:
            return
        self.branch_decoder_temporal_model.load_state_dict(self.temporal_model.state_dict())
        self.branch_decoder_mask_head.load_state_dict(self.mask_head.state_dict())

    def reset_branch_abstention_gate(self) -> None:
        if self.branch_decoder_gate_head is None:
            return
        final_layer = self.branch_decoder_gate_head[-1]
        nn.init.zeros_(final_layer.weight)
        nn.init.constant_(final_layer.bias, 4.0)

    def reset_branch_overlap_refine_head(self) -> None:
        if self.branch_overlap_refine_head is None:
            return
        final_layer = self.branch_overlap_refine_head[-1]
        nn.init.zeros_(final_layer.weight)
        nn.init.zeros_(final_layer.bias)

    def reset_branch_overlap_refine_present_head(self) -> None:
        if self.branch_overlap_refine_present_head is None:
            return
        final_layer = self.branch_overlap_refine_present_head[-1]
        nn.init.zeros_(final_layer.weight)
        nn.init.zeros_(final_layer.bias)

    def reset_branch_overlap_cancel_head(self) -> None:
        if self.branch_overlap_cancel_head is None:
            return
        final_layer = self.branch_overlap_cancel_head[-1]
        nn.init.zeros_(final_layer.weight)
        if self.branch_overlap_cancel_ratio_mode == "phase_preserve":
            nn.init.constant_(final_layer.bias, -8.0)
        else:
            nn.init.zeros_(final_layer.bias)

    def reset_branch_overlap_cancel_apply_controller_head(self) -> None:
        if self.branch_overlap_cancel_apply_controller_head is None:
            return
        final_layer = self.branch_overlap_cancel_apply_controller_head[-1]
        nn.init.zeros_(final_layer.weight)
        nn.init.constant_(final_layer.bias, 4.0)

    def reset_branch_overlap_cancel_apply_absent_controller_head(self) -> None:
        if self.branch_overlap_cancel_apply_absent_controller_head is None:
            return
        final_layer = self.branch_overlap_cancel_apply_absent_controller_head[-1]
        nn.init.zeros_(final_layer.weight)
        nn.init.constant_(final_layer.bias, -4.0)

    def reset_branch_overlap_cancel_pre_present_controller_head(self) -> None:
        if self.branch_overlap_cancel_pre_present_controller_head is None:
            return
        final_layer = self.branch_overlap_cancel_pre_present_controller_head[-1]
        nn.init.zeros_(final_layer.weight)
        nn.init.constant_(final_layer.bias, -4.0)

    def reset_branch_overlap_dual_decoder_from_branch(self) -> None:
        if (
            self.branch_overlap_dual_decoder_temporal_model is None
            or self.branch_decoder_temporal_model is None
        ):
            return
        self.branch_overlap_dual_decoder_temporal_model.load_state_dict(
            self.branch_decoder_temporal_model.state_dict()
        )

    def reset_branch_overlap_dual_decoder_head(self) -> None:
        if self.branch_overlap_dual_decoder_head is None:
            return
        final_layer = self.branch_overlap_dual_decoder_head[-1]
        nn.init.zeros_(final_layer.weight)
        nn.init.zeros_(final_layer.bias)

    def reset_branch_overlap_dual_monitor_controller_head(self) -> None:
        if self.branch_overlap_dual_monitor_controller_head is None:
            return
        final_layer = self.branch_overlap_dual_monitor_controller_head[-1]
        nn.init.zeros_(final_layer.weight)
        nn.init.constant_(final_layer.bias, -4.0)

    def reset_branch_overlap_dual_cancel_controller_head(self) -> None:
        if self.branch_overlap_dual_cancel_controller_head is None:
            return
        final_layer = self.branch_overlap_dual_cancel_controller_head[-1]
        nn.init.zeros_(final_layer.weight)
        nn.init.constant_(final_layer.bias, -4.0)

    def reset_branch_overlap_dual_residual_correction_head(self) -> None:
        if self.branch_overlap_dual_residual_correction_head is None:
            return
        final_layer = self.branch_overlap_dual_residual_correction_head[-1]
        nn.init.zeros_(final_layer.weight)
        nn.init.zeros_(final_layer.bias)

    def reset_branch_overlap_dual_residual_correction_controller_head(self) -> None:
        if self.branch_overlap_dual_residual_correction_controller_head is None:
            return
        final_layer = self.branch_overlap_dual_residual_correction_controller_head[-1]
        nn.init.zeros_(final_layer.weight)
        nn.init.constant_(final_layer.bias, -4.0)

    @staticmethod
    def apply_blend_floor(
        blend: torch.Tensor,
        floor: float,
    ) -> torch.Tensor:
        if floor <= 0.0:
            return blend
        scaled = (blend - floor) / (1.0 - floor)
        return torch.clamp(scaled, min=0.0, max=1.0)

    @staticmethod
    def apply_blend_power(
        blend: torch.Tensor,
        power: float,
    ) -> torch.Tensor:
        if power == 1.0:
            return blend
        return torch.clamp(blend, min=0.0, max=1.0).pow(power)

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
        base_mask = self.mask_head(encoded).transpose(1, 2)
        adapter_mask_delta = None
        mask = base_mask
        if self.adapter_mask_head is not None:
            adapter_features = encoded
            if self.adapter_temporal_model is not None:
                adapter_features, _ = self.adapter_temporal_model(temporal_input)
            if self.adapter_conditioning_mode == "ref_bias":
                adapter_features = adapter_features + self.adapter_condition_proj(ref_embedding).unsqueeze(1)
            elif self.adapter_conditioning_mode == "ref_film":
                adapter_gamma = torch.tanh(self.adapter_condition_scale(ref_embedding)).unsqueeze(1)
                adapter_beta = self.adapter_condition_shift(ref_embedding).unsqueeze(1)
                adapter_features = (adapter_features * (1.0 + adapter_gamma)) + adapter_beta
            adapter_mask_delta = (
                torch.tanh(self.adapter_mask_head(adapter_features)).transpose(1, 2) * self.adapter_mask_max_delta
            )
            mask = torch.clamp(base_mask + adapter_mask_delta, min=0.0, max=1.0)

        estimated_stft_base = mix_stft * base_mask
        estimated_waveform_base = self.istft(estimated_stft_base, mixture_lengths)
        estimated_stft = estimated_stft_base
        estimated_waveform = estimated_waveform_base
        branch_decoder_mask = None
        branch_decoder_frame_gate = None
        branch_overlap_refine_ratio = None
        branch_overlap_refine_present_ratio = None
        branch_overlap_refine_present_veto = None
        branch_overlap_cancel_ratio = None
        branch_overlap_cancel_delta_blend = None
        branch_overlap_cancel_apply_controller = None
        branch_overlap_cancel_apply_keep_controller = None
        branch_overlap_cancel_apply_absent_controller = None
        branch_overlap_cancel_pre_present_controller = None
        estimated_stft_branch_base = None
        estimated_waveform_branch_base = None
        branch_overlap_cancel_estimate_stft = None
        branch_overlap_cancel_estimate_waveform = None
        estimated_stft_refine_base = None
        branch_overlap_refine_present_ratio = None
        branch_overlap_dual_target_stft = None
        branch_overlap_dual_target_waveform = None
        branch_overlap_dual_residual_stft = None
        branch_overlap_dual_residual_waveform = None
        branch_overlap_dual_monitor_estimate_stft = None
        branch_overlap_dual_monitor_estimate_waveform = None
        branch_overlap_dual_controller = None
        branch_overlap_dual_monitor_controller = None
        branch_overlap_dual_cancel_controller = None
        branch_overlap_dual_cancel_estimate_stft = None
        branch_overlap_dual_cancel_estimate_waveform = None
        estimated_stft_post_pre_present_controller = None
        estimated_waveform_post_pre_present_controller = None
        estimated_stft_post_refine_present = None
        estimated_waveform_post_refine_present = None
        estimated_stft_pre_dual_residual_correction = None
        estimated_waveform_pre_dual_residual_correction = None
        branch_overlap_dual_residual_correction_controller = None
        branch_overlap_dual_residual_correction_estimate_stft = None
        branch_overlap_dual_residual_correction_estimate_waveform = None
        branch_overlap_dual_controlled_gate = None
        if self.branch_decoder_temporal_model is not None and self.branch_decoder_mask_head is not None:
            branch_encoded, _ = self.branch_decoder_temporal_model(temporal_input)
            branch_decoder_mask = self.branch_decoder_mask_head(branch_encoded).transpose(1, 2)
            if self.branch_decoder_gate_head is not None:
                branch_decoder_frame_gate = torch.sigmoid(self.branch_decoder_gate_head(branch_encoded)).transpose(1, 2)
                mask = branch_decoder_mask * branch_decoder_frame_gate
            else:
                mask = branch_decoder_mask
            estimated_stft = mix_stft * mask
            estimated_stft_branch_base = estimated_stft
            estimated_waveform_branch_base = self.istft(estimated_stft_branch_base, mixture_lengths)
            if self.branch_overlap_refine_head is not None:
                branch_overlap_refine_params = (
                    torch.tanh(self.branch_overlap_refine_head(branch_encoded)).transpose(1, 2)
                    * self.branch_overlap_refine_max_delta
                )
                refine_real, refine_imag = torch.chunk(branch_overlap_refine_params, 2, dim=1)
                branch_overlap_refine_ratio = torch.complex(refine_real, refine_imag)
                if branch_decoder_frame_gate is not None:
                    refine_gate = branch_decoder_frame_gate
                    if self.branch_overlap_refine_gate_mode == "gate":
                        if self.branch_overlap_refine_gate_power != 1.0:
                            refine_gate = self.apply_blend_power(
                                refine_gate,
                                self.branch_overlap_refine_gate_power,
                            )
                        if self.branch_overlap_refine_gate_floor > 0.0:
                            refine_gate = self.apply_blend_floor(
                                refine_gate,
                                self.branch_overlap_refine_gate_floor,
                            )
                        branch_overlap_refine_ratio = branch_overlap_refine_ratio * refine_gate
                    elif self.branch_overlap_refine_gate_mode == "complement":
                        refine_gate = 1.0 - refine_gate
                        if self.branch_overlap_refine_gate_power != 1.0:
                            refine_gate = self.apply_blend_power(
                                refine_gate,
                                self.branch_overlap_refine_gate_power,
                            )
                        if self.branch_overlap_refine_gate_floor > 0.0:
                            refine_gate = self.apply_blend_floor(
                                refine_gate,
                                self.branch_overlap_refine_gate_floor,
                            )
                        branch_overlap_refine_ratio = branch_overlap_refine_ratio * refine_gate
                refine_source_stft = mix_stft
                if self.branch_overlap_refine_source_mode == "branch_base":
                    refine_source_stft = estimated_stft_branch_base
                elif self.branch_overlap_refine_source_mode == "residual":
                    refine_source_stft = mix_stft - estimated_stft_branch_base
            estimated_stft = estimated_stft - (refine_source_stft * branch_overlap_refine_ratio)
            estimated_stft_refine_base = estimated_stft
            if (
                self.branch_overlap_cancel_head is not None
                and self.branch_overlap_cancel_pre_present_controller_head is not None
                and self.branch_overlap_cancel_pre_present_max_blend > 0.0
            ):
                pre_present_cancel_logits = self.branch_overlap_cancel_head(branch_encoded).transpose(1, 2)
                if self.branch_overlap_cancel_ratio_mode == "phase_preserve":
                    pre_present_cancel_params = (
                        torch.sigmoid(pre_present_cancel_logits) * self.branch_overlap_cancel_max_delta
                    )
                    pre_present_cancel_ratio = torch.complex(
                        pre_present_cancel_params,
                        torch.zeros_like(pre_present_cancel_params),
                    )
                else:
                    pre_present_cancel_params = (
                        torch.tanh(pre_present_cancel_logits) * self.branch_overlap_cancel_max_delta
                    )
                    pre_present_cancel_real, pre_present_cancel_imag = torch.chunk(
                        pre_present_cancel_params,
                        2,
                        dim=1,
                    )
                    pre_present_cancel_ratio = torch.complex(
                        pre_present_cancel_real,
                        pre_present_cancel_imag,
                    )
                if branch_decoder_frame_gate is not None:
                    if self.branch_overlap_cancel_gate_mode == "gate":
                        pre_present_cancel_ratio = pre_present_cancel_ratio * branch_decoder_frame_gate
                    elif self.branch_overlap_cancel_gate_mode == "complement":
                        pre_present_cancel_ratio = pre_present_cancel_ratio * (1.0 - branch_decoder_frame_gate)
                pre_present_cancel_source_stft = mix_stft
                if self.branch_overlap_cancel_source_mode == "branch_base":
                    pre_present_cancel_source_stft = estimated_stft_branch_base
                elif self.branch_overlap_cancel_source_mode == "residual":
                    pre_present_cancel_source_stft = mix_stft - estimated_stft_branch_base
                pre_present_cancel_estimate_stft = (
                    pre_present_cancel_source_stft * pre_present_cancel_ratio
                )
                pre_present_delta_blend = None
                if branch_decoder_frame_gate is not None:
                    if self.branch_overlap_cancel_delta_blend_mode == "gate":
                        pre_present_delta_blend = branch_decoder_frame_gate
                    elif self.branch_overlap_cancel_delta_blend_mode == "complement":
                        pre_present_delta_blend = 1.0 - branch_decoder_frame_gate
                if self.branch_overlap_cancel_delta_blend_mode == "predicted_activity":
                    cancel_scale = max(self.branch_overlap_cancel_max_delta, 1e-6)
                    pre_present_delta_blend = torch.clamp(
                        torch.abs(pre_present_cancel_ratio) / cancel_scale,
                        min=0.0,
                        max=1.0,
                    )
                if pre_present_delta_blend is None:
                    pre_present_delta_blend = torch.ones_like(branch_decoder_mask[:, :1, :])
                branch_overlap_cancel_pre_present_controller = torch.sigmoid(
                    self.branch_overlap_cancel_pre_present_controller_head(branch_encoded)
                ).transpose(1, 2)
                if self.branch_overlap_cancel_pre_present_controller_floor > 0.0:
                    floor = self.branch_overlap_cancel_pre_present_controller_floor
                    branch_overlap_cancel_pre_present_controller = torch.clamp(
                        (branch_overlap_cancel_pre_present_controller - floor) / (1.0 - floor),
                        min=0.0,
                        max=1.0,
                    )
                pre_present_delta_blend = (
                    pre_present_delta_blend
                    * branch_overlap_cancel_pre_present_controller
                    * self.branch_overlap_cancel_pre_present_max_blend
                    * self.branch_overlap_cancel_apply_band_mask
                )
                estimated_stft = estimated_stft - (
                    pre_present_cancel_estimate_stft * pre_present_delta_blend
                )
            estimated_stft_post_pre_present_controller = estimated_stft
            if self.branch_overlap_refine_present_head is not None:
                branch_overlap_refine_present_params = (
                    torch.tanh(self.branch_overlap_refine_present_head(branch_encoded)).transpose(1, 2)
                    * self.branch_overlap_refine_present_max_delta
                )
                present_real, present_imag = torch.chunk(branch_overlap_refine_present_params, 2, dim=1)
                branch_overlap_refine_present_ratio = torch.complex(present_real, present_imag)
                present_gate = branch_decoder_frame_gate
                if self.branch_overlap_refine_present_gate_power != 1.0:
                    present_gate = self.apply_blend_power(
                        present_gate,
                        self.branch_overlap_refine_present_gate_power,
                    )
                if self.branch_overlap_refine_present_gate_floor > 0.0:
                    present_gate = self.apply_blend_floor(
                        present_gate,
                        self.branch_overlap_refine_present_gate_floor,
                    )
                if self.branch_overlap_refine_present_veto_mode != "none":
                    veto_activity = None
                    if self.branch_overlap_refine_present_veto_mode == "complement_gate":
                        veto_activity = 1.0 - branch_decoder_frame_gate
                    elif branch_overlap_refine_ratio is not None:
                        veto_scale = max(self.branch_overlap_refine_max_delta, 1e-6)
                        veto_activity = torch.abs(branch_overlap_refine_ratio) / veto_scale
                    if veto_activity is not None:
                        veto_activity = torch.clamp(veto_activity, min=0.0, max=1.0)
                        if self.branch_overlap_refine_present_veto_power != 1.0:
                            veto_activity = self.apply_blend_power(
                                veto_activity,
                                self.branch_overlap_refine_present_veto_power,
                            )
                        branch_overlap_refine_present_veto = 1.0 - (
                            veto_activity * self.branch_overlap_refine_present_veto_strength
                        )
                        branch_overlap_refine_present_veto = torch.clamp(
                            branch_overlap_refine_present_veto,
                            min=0.0,
                            max=1.0,
                        )
                        present_gate = present_gate * branch_overlap_refine_present_veto
                branch_overlap_refine_present_ratio = branch_overlap_refine_present_ratio * present_gate
                if self.branch_overlap_cancel_apply_mode != "pre_present_subtract":
                    refine_present_source_stft = mix_stft
                    if self.branch_overlap_refine_present_source_mode == "branch_base":
                        refine_present_source_stft = estimated_stft_branch_base
                    elif self.branch_overlap_refine_present_source_mode == "residual":
                        refine_present_source_stft = mix_stft - estimated_stft_branch_base
                    elif self.branch_overlap_refine_present_source_mode == "current_residual":
                        refine_present_source_stft = mix_stft - estimated_stft
                    estimated_stft = estimated_stft - (
                        refine_present_source_stft * branch_overlap_refine_present_ratio
                    )
            estimated_stft_post_refine_present = estimated_stft
            if self.branch_overlap_cancel_head is not None:
                branch_overlap_cancel_logits = self.branch_overlap_cancel_head(branch_encoded).transpose(1, 2)
                if self.branch_overlap_cancel_ratio_mode == "phase_preserve":
                    branch_overlap_cancel_params = (
                        torch.sigmoid(branch_overlap_cancel_logits) * self.branch_overlap_cancel_max_delta
                    )
                    branch_overlap_cancel_ratio = torch.complex(
                        branch_overlap_cancel_params,
                        torch.zeros_like(branch_overlap_cancel_params),
                    )
                else:
                    branch_overlap_cancel_params = (
                        torch.tanh(branch_overlap_cancel_logits) * self.branch_overlap_cancel_max_delta
                    )
                    cancel_real, cancel_imag = torch.chunk(branch_overlap_cancel_params, 2, dim=1)
                    branch_overlap_cancel_ratio = torch.complex(cancel_real, cancel_imag)
                if branch_decoder_frame_gate is not None:
                    if self.branch_overlap_cancel_gate_mode == "gate":
                        branch_overlap_cancel_ratio = branch_overlap_cancel_ratio * branch_decoder_frame_gate
                    elif self.branch_overlap_cancel_gate_mode == "complement":
                        branch_overlap_cancel_ratio = branch_overlap_cancel_ratio * (1.0 - branch_decoder_frame_gate)
                cancel_source_stft = mix_stft
                if self.branch_overlap_cancel_source_mode == "branch_base":
                    cancel_source_stft = estimated_stft_branch_base
                elif self.branch_overlap_cancel_source_mode == "residual":
                    cancel_source_stft = mix_stft - estimated_stft_branch_base
                branch_overlap_cancel_estimate_stft = cancel_source_stft * branch_overlap_cancel_ratio
                if self.branch_overlap_cancel_apply_mode in (
                    "subtract",
                    "pre_present_subtract",
                    "branch_base_blend",
                    "refine_base_blend",
                ):
                    if branch_decoder_frame_gate is not None:
                        if self.branch_overlap_cancel_delta_blend_mode == "gate":
                            branch_overlap_cancel_delta_blend = branch_decoder_frame_gate
                        elif self.branch_overlap_cancel_delta_blend_mode == "complement":
                            branch_overlap_cancel_delta_blend = 1.0 - branch_decoder_frame_gate
                    if self.branch_overlap_cancel_delta_blend_mode == "predicted_activity":
                        cancel_scale = max(self.branch_overlap_cancel_max_delta, 1e-6)
                        branch_overlap_cancel_delta_blend = torch.clamp(
                            torch.abs(branch_overlap_cancel_ratio) / cancel_scale,
                            min=0.0,
                            max=1.0,
                        )
                    if branch_overlap_cancel_delta_blend is None:
                        branch_overlap_cancel_delta_blend = torch.ones_like(branch_decoder_mask[:, :1, :])
                    if self.branch_overlap_cancel_apply_controller_head is not None:
                        branch_overlap_cancel_apply_keep_controller = torch.sigmoid(
                            self.branch_overlap_cancel_apply_controller_head(branch_encoded)
                        ).transpose(1, 2)
                        if self.branch_overlap_cancel_apply_controller_floor > 0.0:
                            floor = self.branch_overlap_cancel_apply_controller_floor
                            branch_overlap_cancel_apply_keep_controller = torch.clamp(
                                (branch_overlap_cancel_apply_keep_controller - floor) / (1.0 - floor),
                                min=0.0,
                                max=1.0,
                            )
                        branch_overlap_cancel_apply_controller = branch_overlap_cancel_apply_keep_controller
                        if self.branch_overlap_cancel_apply_absent_controller_head is not None:
                            branch_overlap_cancel_apply_absent_controller = torch.sigmoid(
                                self.branch_overlap_cancel_apply_absent_controller_head(branch_encoded)
                            ).transpose(1, 2)
                            branch_overlap_cancel_apply_controller = (
                                branch_overlap_cancel_apply_controller
                                * (1.0 - branch_overlap_cancel_apply_absent_controller)
                            )
                        if self.branch_overlap_cancel_apply_mode == "subtract":
                            branch_overlap_cancel_delta_blend = (
                                branch_overlap_cancel_delta_blend * branch_overlap_cancel_apply_controller
                            )
                    branch_overlap_cancel_delta_blend = (
                        branch_overlap_cancel_delta_blend * self.branch_overlap_cancel_max_blend
                    )
                    branch_overlap_cancel_delta_blend = (
                        branch_overlap_cancel_delta_blend * self.branch_overlap_cancel_apply_band_mask
                    )
                    if self.branch_overlap_cancel_apply_mode in ("subtract", "pre_present_subtract"):
                        subtract_base = estimated_stft
                        if self.branch_overlap_cancel_apply_mode == "pre_present_subtract":
                            subtract_base = (
                                estimated_stft_refine_base
                                if estimated_stft_refine_base is not None
                                else estimated_stft
                            )
                        estimated_stft = subtract_base - (
                            branch_overlap_cancel_estimate_stft * branch_overlap_cancel_delta_blend
                        )
                        if (
                            self.branch_overlap_cancel_apply_mode == "pre_present_subtract"
                            and branch_overlap_refine_present_ratio is not None
                        ):
                            refine_present_source_stft = mix_stft
                            if self.branch_overlap_refine_present_source_mode == "branch_base":
                                refine_present_source_stft = estimated_stft_branch_base
                            elif self.branch_overlap_refine_present_source_mode == "residual":
                                refine_present_source_stft = mix_stft - estimated_stft_branch_base
                            elif self.branch_overlap_refine_present_source_mode == "current_residual":
                                refine_present_source_stft = mix_stft - estimated_stft
                            estimated_stft = estimated_stft - (
                                refine_present_source_stft * branch_overlap_refine_present_ratio
                            )
                    else:
                        cancel_blend_base = estimated_stft_branch_base
                        if self.branch_overlap_cancel_apply_mode == "refine_base_blend":
                            cancel_blend_base = (
                                estimated_stft_refine_base
                                if estimated_stft_refine_base is not None
                                else estimated_stft
                            )
                        cancel_candidate = cancel_blend_base - (
                            branch_overlap_cancel_estimate_stft * branch_overlap_cancel_delta_blend
                        )
                        controller_blend = branch_overlap_cancel_apply_controller
                        if controller_blend is None:
                            controller_blend = torch.ones_like(branch_overlap_cancel_delta_blend)
                        estimated_stft = estimated_stft + (
                            controller_blend * (cancel_candidate - estimated_stft)
                        )
            if (
                self.branch_overlap_dual_decoder_temporal_model is not None
                and self.branch_overlap_dual_decoder_head is not None
            ):
                dual_encoded, _ = self.branch_overlap_dual_decoder_temporal_model(temporal_input)
                branch_overlap_dual_params = (
                    torch.tanh(self.branch_overlap_dual_decoder_head(dual_encoded)).transpose(1, 2)
                    * self.branch_overlap_dual_decoder_max_delta
                )
                dual_real, dual_imag = torch.chunk(branch_overlap_dual_params, 2, dim=1)
                branch_overlap_cancel_ratio = torch.complex(dual_real, dual_imag)
                dual_source_stft = mix_stft
                if self.branch_overlap_dual_decoder_source_mode == "branch_base":
                    dual_source_stft = estimated_stft_branch_base
                elif self.branch_overlap_dual_decoder_source_mode == "residual":
                    dual_source_stft = mix_stft - estimated_stft_branch_base
                branch_overlap_dual_residual_stft = dual_source_stft * branch_overlap_cancel_ratio
                branch_overlap_dual_target_stft = mix_stft - branch_overlap_dual_residual_stft
                dual_controller_strength = torch.abs(branch_overlap_dual_residual_stft).mean(
                    dim=1,
                    keepdim=True,
                )
                dual_source_strength = torch.abs(dual_source_stft).mean(dim=1, keepdim=True).clamp_min(1e-6)
                branch_overlap_dual_controller = torch.clamp(
                    dual_controller_strength / dual_source_strength,
                    min=0.0,
                    max=1.0,
                )
                dual_blend = None
                if branch_decoder_frame_gate is not None:
                    if self.branch_overlap_dual_decoder_gate_mode == "gate":
                        dual_blend = branch_decoder_frame_gate
                    elif self.branch_overlap_dual_decoder_gate_mode == "complement":
                        dual_blend = 1.0 - branch_decoder_frame_gate
                if dual_blend is None:
                    dual_blend = torch.ones_like(branch_decoder_mask[:, :1, :])
                dual_blend = self.apply_blend_floor(
                    dual_blend,
                    self.branch_overlap_dual_decoder_gate_floor,
                )
                dual_blend = dual_blend * self.branch_overlap_dual_decoder_max_blend
                if self.branch_overlap_dual_decoder_apply_mode == "final_output":
                    estimated_stft = estimated_stft_branch_base + (
                        dual_blend * (branch_overlap_dual_target_stft - estimated_stft_branch_base)
                    )
                elif self.branch_overlap_dual_decoder_apply_mode == "current_output":
                    estimated_stft = estimated_stft + (
                        dual_blend * (branch_overlap_dual_target_stft - estimated_stft)
                    )
                else:
                    branch_overlap_dual_controlled_gate = branch_decoder_frame_gate * (
                        1.0 - (dual_blend * branch_overlap_dual_controller)
                    )
                    estimated_stft = mix_stft * (
                        branch_decoder_mask * branch_overlap_dual_controlled_gate
                    )
                if self.branch_overlap_dual_monitor_controller_head is not None:
                    dual_monitor_base = torch.sigmoid(
                        self.branch_overlap_dual_monitor_controller_head(dual_encoded)
                    ).transpose(1, 2)
                    branch_overlap_dual_monitor_controller = (
                        dual_monitor_base * branch_overlap_dual_controller
                    )
                    if self.branch_overlap_dual_monitor_max_blend > 0.0:
                        branch_overlap_dual_monitor_estimate_stft = (
                            branch_overlap_dual_residual_stft
                            * branch_overlap_dual_monitor_controller
                            * self.branch_overlap_dual_monitor_max_blend
                        )
                        estimated_stft = estimated_stft - (
                            branch_overlap_dual_monitor_estimate_stft
                        )
                if (
                    self.branch_overlap_dual_cancel_controller_head is not None
                    and branch_overlap_cancel_estimate_stft is not None
                ):
                    dual_cancel_base = torch.sigmoid(
                        self.branch_overlap_dual_cancel_controller_head(dual_encoded)
                    ).transpose(1, 2)
                    branch_overlap_dual_cancel_controller = (
                        dual_cancel_base * branch_overlap_dual_controller
                    )
                    if self.branch_overlap_dual_cancel_max_blend > 0.0:
                        branch_overlap_dual_cancel_estimate_stft = (
                            branch_overlap_cancel_estimate_stft
                            * branch_overlap_dual_cancel_controller
                            * self.branch_overlap_dual_cancel_max_blend
                            * self.branch_overlap_cancel_apply_band_mask
                        )
                        estimated_stft = estimated_stft - (
                            branch_overlap_dual_cancel_estimate_stft
                        )
                estimated_stft_pre_dual_residual_correction = estimated_stft
                if (
                    self.branch_overlap_dual_residual_correction_head is not None
                    and self.branch_overlap_dual_residual_correction_controller_head is not None
                ):
                    current_output_residual_stft = mix_stft - estimated_stft
                    dual_residual_correction_params = (
                        torch.tanh(
                            self.branch_overlap_dual_residual_correction_head(dual_encoded)
                        ).transpose(1, 2)
                        * self.branch_overlap_dual_residual_correction_max_delta
                    )
                    dual_correction_real, dual_correction_imag = torch.chunk(
                        dual_residual_correction_params,
                        2,
                        dim=1,
                    )
                    dual_residual_correction_ratio = torch.complex(
                        dual_correction_real,
                        dual_correction_imag,
                    )
                    dual_residual_correction_base = torch.sigmoid(
                        self.branch_overlap_dual_residual_correction_controller_head(dual_encoded)
                    ).transpose(1, 2)
                    branch_overlap_dual_residual_correction_controller = (
                        dual_residual_correction_base * branch_overlap_dual_controller
                    )
                    if self.branch_overlap_dual_residual_correction_max_blend > 0.0:
                        branch_overlap_dual_residual_correction_estimate_stft = (
                            current_output_residual_stft
                            * dual_residual_correction_ratio
                            * branch_overlap_dual_residual_correction_controller
                            * self.branch_overlap_dual_residual_correction_max_blend
                        )
                        estimated_stft = estimated_stft - (
                            branch_overlap_dual_residual_correction_estimate_stft
                        )
            estimated_waveform = self.istft(estimated_stft, mixture_lengths)
            if branch_overlap_cancel_estimate_stft is not None:
                branch_overlap_cancel_estimate_waveform = self.istft(
                    branch_overlap_cancel_estimate_stft,
                    mixture_lengths,
                )
            if branch_overlap_dual_residual_stft is not None:
                branch_overlap_dual_residual_waveform = self.istft(
                    branch_overlap_dual_residual_stft,
                    mixture_lengths,
                )
            if branch_overlap_dual_target_stft is not None:
                branch_overlap_dual_target_waveform = self.istft(
                    branch_overlap_dual_target_stft,
                    mixture_lengths,
                )
            if branch_overlap_dual_monitor_estimate_stft is not None:
                branch_overlap_dual_monitor_estimate_waveform = self.istft(
                    branch_overlap_dual_monitor_estimate_stft,
                    mixture_lengths,
                )
            if branch_overlap_dual_cancel_estimate_stft is not None:
                branch_overlap_dual_cancel_estimate_waveform = self.istft(
                    branch_overlap_dual_cancel_estimate_stft,
                    mixture_lengths,
                )
            if estimated_stft_post_pre_present_controller is not None:
                estimated_waveform_post_pre_present_controller = self.istft(
                    estimated_stft_post_pre_present_controller,
                    mixture_lengths,
                )
            if estimated_stft_post_refine_present is not None:
                estimated_waveform_post_refine_present = self.istft(
                    estimated_stft_post_refine_present,
                    mixture_lengths,
                )
            if estimated_stft_pre_dual_residual_correction is not None:
                estimated_waveform_pre_dual_residual_correction = self.istft(
                    estimated_stft_pre_dual_residual_correction,
                    mixture_lengths,
                )
            if branch_overlap_dual_residual_correction_estimate_stft is not None:
                branch_overlap_dual_residual_correction_estimate_waveform = self.istft(
                    branch_overlap_dual_residual_correction_estimate_stft,
                    mixture_lengths,
                )
        elif self.adapter_mask_head is not None:
            estimated_stft = mix_stft * mask
            estimated_waveform = self.istft(estimated_stft, mixture_lengths)

        return {
            "estimated_waveform": estimated_waveform,
            "estimated_waveform_base": estimated_waveform_base,
            "mask": mask,
            "base_mask": base_mask,
            "adapter_mask_delta": adapter_mask_delta,
            "branch_decoder_mask": branch_decoder_mask,
            "branch_decoder_frame_gate": branch_decoder_frame_gate,
            "branch_overlap_refine_ratio": branch_overlap_refine_ratio,
            "branch_overlap_refine_present_ratio": branch_overlap_refine_present_ratio,
            "branch_overlap_refine_present_veto": branch_overlap_refine_present_veto,
            "branch_overlap_cancel_ratio": branch_overlap_cancel_ratio,
            "branch_overlap_cancel_delta_blend": branch_overlap_cancel_delta_blend,
            "branch_overlap_cancel_apply_controller": branch_overlap_cancel_apply_controller,
            "branch_overlap_cancel_apply_keep_controller": branch_overlap_cancel_apply_keep_controller,
            "branch_overlap_cancel_apply_absent_controller": branch_overlap_cancel_apply_absent_controller,
            "branch_overlap_cancel_pre_present_controller": branch_overlap_cancel_pre_present_controller,
            "mixture_stft": mix_stft,
            "estimated_stft": estimated_stft,
            "estimated_stft_base": estimated_stft_base,
            "estimated_stft_branch_base": estimated_stft_branch_base,
            "estimated_waveform_branch_base": estimated_waveform_branch_base,
            "branch_overlap_cancel_estimate_stft": branch_overlap_cancel_estimate_stft,
            "branch_overlap_cancel_estimate_waveform": branch_overlap_cancel_estimate_waveform,
            "branch_overlap_dual_target_stft": branch_overlap_dual_target_stft,
            "branch_overlap_dual_target_waveform": branch_overlap_dual_target_waveform,
            "branch_overlap_dual_residual_waveform": branch_overlap_dual_residual_waveform,
            "branch_overlap_dual_monitor_estimate_waveform": branch_overlap_dual_monitor_estimate_waveform,
            "branch_overlap_dual_controller": branch_overlap_dual_controller,
            "branch_overlap_dual_monitor_controller": branch_overlap_dual_monitor_controller,
            "branch_overlap_dual_cancel_controller": branch_overlap_dual_cancel_controller,
            "branch_overlap_dual_cancel_estimate_waveform": branch_overlap_dual_cancel_estimate_waveform,
            "estimated_waveform_post_pre_present_controller": (
                estimated_waveform_post_pre_present_controller
            ),
            "estimated_waveform_post_refine_present": estimated_waveform_post_refine_present,
            "estimated_waveform_pre_dual_residual_correction": (
                estimated_waveform_pre_dual_residual_correction
            ),
            "branch_overlap_dual_residual_correction_controller": (
                branch_overlap_dual_residual_correction_controller
            ),
            "branch_overlap_dual_residual_correction_estimate_waveform": (
                branch_overlap_dual_residual_correction_estimate_waveform
            ),
            "branch_overlap_dual_controlled_gate": branch_overlap_dual_controlled_gate,
        }
