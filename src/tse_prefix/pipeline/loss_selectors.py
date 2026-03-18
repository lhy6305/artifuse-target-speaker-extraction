from typing import Any

import torch


SELECTOR_SUFFIXES = (
    "focus_recipes",
    "focus_patterns",
    "focus_interference_pools",
    "focus_interference_speaker_names",
    "min_target_ratio",
    "max_target_ratio",
    "min_overlap_ratio",
    "max_overlap_ratio",
    "min_interference_gain_db",
    "max_interference_gain_db",
    "min_target_transient_presence_minus_mid_db_mean",
    "max_target_transient_presence_minus_mid_db_mean",
    "min_target_transient_presence_share_mean",
    "max_target_transient_presence_share_mean",
)


def selector_config_keys(prefixes: tuple[str, ...] = ("transient", "interference", "absent")) -> set[str]:
    return {f"{prefix}_{suffix}" for prefix in prefixes for suffix in SELECTOR_SUFFIXES}


def build_selector_sample_weights(
    batch: dict[str, Any],
    device: torch.device,
    loss_config: dict[str, Any],
    prefix: str,
) -> torch.Tensor | None:
    recipes = set(loss_config.get(f"{prefix}_focus_recipes", []))
    patterns = set(loss_config.get(f"{prefix}_focus_patterns", []))
    pools = set(loss_config.get(f"{prefix}_focus_interference_pools", []))
    speaker_names = set(loss_config.get(f"{prefix}_focus_interference_speaker_names", []))
    min_ratio = loss_config.get(f"{prefix}_min_target_ratio")
    max_ratio = loss_config.get(f"{prefix}_max_target_ratio")
    min_overlap = loss_config.get(f"{prefix}_min_overlap_ratio")
    max_overlap = loss_config.get(f"{prefix}_max_overlap_ratio")
    min_gain = loss_config.get(f"{prefix}_min_interference_gain_db")
    max_gain = loss_config.get(f"{prefix}_max_interference_gain_db")
    min_transient_minus_mid = loss_config.get(f"{prefix}_min_target_transient_presence_minus_mid_db_mean")
    max_transient_minus_mid = loss_config.get(f"{prefix}_max_target_transient_presence_minus_mid_db_mean")
    min_transient_share = loss_config.get(f"{prefix}_min_target_transient_presence_share_mean")
    max_transient_share = loss_config.get(f"{prefix}_max_target_transient_presence_share_mean")
    has_selector = bool(
        recipes
        or patterns
        or pools
        or speaker_names
        or min_ratio is not None
        or max_ratio is not None
        or min_overlap is not None
        or max_overlap is not None
        or min_gain is not None
        or max_gain is not None
        or min_transient_minus_mid is not None
        or max_transient_minus_mid is not None
        or min_transient_share is not None
        or max_transient_share is not None
    )
    if not has_selector:
        return None

    weights = torch.ones(len(batch["sample_ids"]), dtype=torch.float32, device=device)
    if recipes:
        weights = weights * torch.tensor(
            [1.0 if recipe in recipes else 0.0 for recipe in batch["recipes"]],
            dtype=torch.float32,
            device=device,
        )
    if patterns:
        weights = weights * torch.tensor(
            [1.0 if pattern in patterns else 0.0 for pattern in batch["temporal_patterns"]],
            dtype=torch.float32,
            device=device,
        )
    if pools:
        weights = weights * torch.tensor(
            [1.0 if pool in pools else 0.0 for pool in batch["interference_pools"]],
            dtype=torch.float32,
            device=device,
        )
    if speaker_names:
        weights = weights * torch.tensor(
            [1.0 if name in speaker_names else 0.0 for name in batch["interference_speaker_names"]],
            dtype=torch.float32,
            device=device,
        )

    ratios = batch["target_present_ratios"].to(device=device, dtype=torch.float32)
    transient_minus_mid = batch["target_transient_presence_minus_mid_db_means"].to(device=device, dtype=torch.float32)
    transient_share = batch["target_transient_presence_share_means"].to(device=device, dtype=torch.float32)
    overlaps = batch["overlap_ratios"].to(device=device, dtype=torch.float32)
    gains = batch["interference_gain_dbs"].to(device=device, dtype=torch.float32)
    if min_ratio is not None:
        weights = weights * (ratios >= float(min_ratio)).float()
    if max_ratio is not None:
        weights = weights * (ratios <= float(max_ratio)).float()
    if min_overlap is not None:
        weights = weights * ((~torch.isnan(overlaps)) & (overlaps >= float(min_overlap))).float()
    if max_overlap is not None:
        weights = weights * ((~torch.isnan(overlaps)) & (overlaps <= float(max_overlap))).float()
    if min_gain is not None:
        weights = weights * ((~torch.isnan(gains)) & (gains >= float(min_gain))).float()
    if max_gain is not None:
        weights = weights * ((~torch.isnan(gains)) & (gains <= float(max_gain))).float()
    if min_transient_minus_mid is not None:
        weights = weights * (
            (~torch.isnan(transient_minus_mid)) & (transient_minus_mid >= float(min_transient_minus_mid))
        ).float()
    if max_transient_minus_mid is not None:
        weights = weights * (
            (~torch.isnan(transient_minus_mid)) & (transient_minus_mid <= float(max_transient_minus_mid))
        ).float()
    if min_transient_share is not None:
        weights = weights * ((~torch.isnan(transient_share)) & (transient_share >= float(min_transient_share))).float()
    if max_transient_share is not None:
        weights = weights * ((~torch.isnan(transient_share)) & (transient_share <= float(max_transient_share))).float()
    return weights


def summarize_selector_weights(
    weights: torch.Tensor | None,
    batch_size: int,
) -> dict[str, float | int | bool | None]:
    if weights is None:
        return {
            "active": False,
            "selected_count": 0,
            "total_count": 0,
            "selected_fraction": None,
        }

    selected_count = int((weights > 0).sum().item())
    return {
        "active": True,
        "selected_count": selected_count,
        "total_count": int(batch_size),
        "selected_fraction": (float(selected_count) / float(batch_size)) if batch_size > 0 else None,
    }
