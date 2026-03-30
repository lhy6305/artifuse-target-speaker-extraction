from __future__ import annotations

from typing import Any

import torch

from .loss_selectors import (
    build_branch_selector_sample_weights,
    build_selector_sample_weights,
    merge_selector_sample_weights,
    selector_config_keys,
)


SELECTOR_PREFIXES = (
    "reconstruction",
    "transient",
    "interference",
    "overlap_interference",
    "overlap_cancel",
    "overlap_dual",
    "absent",
    "branch_protect",
    "branch_protect_teacher",
)

GATE_TARGET_CONFIG_KEYS = {
    "gate_supervision_source",
    "gate_target_mode",
    "gate_target_energy_center",
    "gate_target_energy_scale",
    "gate_target_transient_share_center",
    "gate_target_transient_share_scale",
    "gate_target_transient_db_center",
    "gate_target_transient_db_scale",
    "gate_target_energy_weight",
    "gate_target_transient_share_weight",
    "gate_target_transient_db_weight",
    "gate_target_min_value",
    "gate_target_max_value",
    "use_branch_prerefine_as_primary_prediction",
    "overlap_dual_controller_distill_source",
    "extra_prediction_source",
}


def build_compute_loss_kwargs(loss_config: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in loss_config.items()
        if key not in selector_config_keys(prefixes=SELECTOR_PREFIXES)
        and key not in GATE_TARGET_CONFIG_KEYS
    }


def _sigmoid_score(values: torch.Tensor, center: float, scale: float) -> torch.Tensor:
    return torch.sigmoid((values - float(center)) / max(float(scale), 1e-6))


def build_gate_target_values(
    batch: dict[str, Any],
    device: torch.device,
    loss_config: dict[str, Any],
) -> torch.Tensor | None:
    if float(loss_config.get("gate_target_weight", 0.0)) <= 0.0:
        return None
    if str(loss_config.get("gate_target_mode", "none")) != "audibility":
        return None

    feature_specs = (
        (
            batch["target_energy_ratios"].to(device=device, dtype=torch.float32),
            float(loss_config.get("gate_target_energy_center", 0.13)),
            float(loss_config.get("gate_target_energy_scale", 0.035)),
            float(loss_config.get("gate_target_energy_weight", 0.75)),
        ),
        (
            batch["target_transient_presence_share_means"].to(device=device, dtype=torch.float32),
            float(loss_config.get("gate_target_transient_share_center", 0.01)),
            float(loss_config.get("gate_target_transient_share_scale", 0.006)),
            float(loss_config.get("gate_target_transient_share_weight", 0.15)),
        ),
        (
            batch["target_transient_presence_minus_mid_db_means"].to(device=device, dtype=torch.float32),
            float(loss_config.get("gate_target_transient_db_center", -13.0)),
            float(loss_config.get("gate_target_transient_db_scale", 2.5)),
            float(loss_config.get("gate_target_transient_db_weight", 0.10)),
        ),
    )

    weighted_sum = torch.zeros(len(batch["sample_ids"]), dtype=torch.float32, device=device)
    weight_sum = torch.zeros(len(batch["sample_ids"]), dtype=torch.float32, device=device)
    for values, center, scale, weight in feature_specs:
        if weight <= 0.0:
            continue
        valid_mask = ~torch.isnan(values)
        if not torch.any(valid_mask):
            continue
        scores = _sigmoid_score(values, center=center, scale=scale)
        weighted_sum = weighted_sum + (torch.where(valid_mask, scores, torch.zeros_like(scores)) * weight)
        weight_sum = weight_sum + (valid_mask.float() * weight)

    base_scores = torch.where(
        weight_sum > 0.0,
        weighted_sum / weight_sum.clamp_min(1e-6),
        torch.zeros_like(weighted_sum),
    )
    min_value = float(loss_config.get("gate_target_min_value", 0.0))
    max_value = float(loss_config.get("gate_target_max_value", 1.0))
    target_values = min_value + (base_scores * max(0.0, max_value - min_value))
    return torch.clamp(target_values, min=min_value, max=max_value)


def resolve_branch_extra_prediction(outputs: dict[str, torch.Tensor]) -> torch.Tensor | None:
    if outputs.get("branch_decoder_mask") is not None:
        return outputs["estimated_waveform"]
    return None


def resolve_prediction_source(
    outputs: dict[str, torch.Tensor],
    source: str,
) -> torch.Tensor | None:
    normalized = str(source).strip().lower()
    source_map = {
        "estimated_waveform": outputs.get("estimated_waveform"),
        "estimated_waveform_base": outputs.get("estimated_waveform_base"),
        "estimated_waveform_branch_base": outputs.get("estimated_waveform_branch_base"),
        "estimated_waveform_post_pre_present_controller": outputs.get(
            "estimated_waveform_post_pre_present_controller"
        ),
        "estimated_waveform_post_refine_present": outputs.get(
            "estimated_waveform_post_refine_present"
        ),
        "estimated_waveform_pre_dual_residual_correction": outputs.get(
            "estimated_waveform_pre_dual_residual_correction"
        ),
    }
    if normalized not in source_map:
        raise ValueError(
            "Unsupported extra prediction source: "
            f"{source}. Expected one of {tuple(source_map.keys())}."
        )
    resolved = source_map[normalized]
    if resolved is not None:
        return resolved
    return outputs.get("estimated_waveform")


def resolve_primary_prediction(
    outputs: dict[str, torch.Tensor],
    use_branch_prerefine_as_primary_prediction: bool,
) -> torch.Tensor:
    if use_branch_prerefine_as_primary_prediction and outputs.get("estimated_waveform_branch_base") is not None:
        return outputs["estimated_waveform_branch_base"]
    return outputs.get("estimated_waveform_base", outputs["estimated_waveform"])


def resolve_selector_sample_weights(
    batch: dict[str, Any],
    device: torch.device,
    loss_config: dict[str, Any],
    prefix: str,
    extra_weight_keys: tuple[str, ...],
) -> tuple[torch.Tensor | None, torch.Tensor | None, torch.Tensor | None]:
    if any(float(loss_config.get(key, 0.0)) > 0.0 for key in extra_weight_keys):
        base_sample_weights = build_branch_selector_sample_weights(
            batch=batch,
            device=device,
            loss_config=loss_config,
            prefix=prefix,
            branch_name="",
        )
        extra_sample_weights = build_branch_selector_sample_weights(
            batch=batch,
            device=device,
            loss_config=loss_config,
            prefix=prefix,
            branch_name="extra_",
        )
        union_sample_weights = merge_selector_sample_weights(
            base_sample_weights,
            extra_sample_weights,
        )
        return base_sample_weights, extra_sample_weights, union_sample_weights

    base_sample_weights = build_selector_sample_weights(
        batch=batch,
        device=device,
        loss_config=loss_config,
        prefix=prefix,
    )
    return base_sample_weights, None, base_sample_weights
