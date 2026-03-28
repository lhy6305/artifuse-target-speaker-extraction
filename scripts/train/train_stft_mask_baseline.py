from __future__ import annotations

import argparse
import json
import random
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from tse_prefix.data import SyntheticTSEDataset, synthetic_collate_fn
from tse_prefix.models import STFTMaskBaseline
from tse_prefix.pipeline import compute_losses
from tse_prefix.pipeline.baseline_train import INTERFERENCE_LOSS_MODES
from tse_prefix.pipeline.loss_selectors import (
    build_selector_sample_weights,
    summarize_selector_weights,
)
from tse_prefix.pipeline.runtime_helpers import (
    build_compute_loss_kwargs,
    build_gate_target_values,
    resolve_branch_extra_prediction,
    resolve_primary_prediction,
    resolve_selector_sample_weights,
)


def parse_optional_bool_arg(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes"}:
        return True
    if normalized in {"0", "false", "no"}:
        return False
    raise argparse.ArgumentTypeError(f"Expected one of: true, false, 1, 0, yes, no. Got: {value!r}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train the minimal TSE baseline.")
    parser.add_argument(
        "--train-manifest",
        type=Path,
        default=ROOT / "data" / "synthetic" / "train_manifest.jsonl",
    )
    parser.add_argument(
        "--val-manifest",
        type=Path,
        default=ROOT / "data" / "synthetic" / "val_manifest.jsonl",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "experiments" / "checkpoints" / "baseline_stft_mask_smoke",
    )
    parser.add_argument(
        "--init-checkpoint",
        type=Path,
        default=None,
        help="Optional checkpoint to initialize model weights from.",
    )
    parser.add_argument(
        "--teacher-checkpoint",
        type=Path,
        default=None,
        help="Optional frozen teacher checkpoint used for hard-present overlap teacher veto losses.",
    )
    parser.add_argument(
        "--disable-teacher-checkpoint-metadata-fallback",
        action="store_true",
        help=(
            "When set, only use an explicitly provided --teacher-checkpoint and do not inherit "
            "teacher_checkpoint metadata from the init checkpoint."
        ),
    )
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--log-every", type=int, default=5)
    parser.add_argument("--max-steps", type=int, default=0)
    parser.add_argument("--seed", type=int, default=20260316)
    parser.add_argument(
        "--trainable-module-prefixes",
        nargs="*",
        default=[],
        help=(
            "Optional module-name prefixes to keep trainable. "
            "When set, all other parameters are frozen."
        ),
    )
    parser.add_argument("--sample-rate", type=int, default=16000)
    parser.add_argument("--model-n-fft", type=int, default=512)
    parser.add_argument("--model-hop-length", type=int, default=128)
    parser.add_argument("--model-win-length", type=int, default=512)
    parser.add_argument("--model-hidden-dim", type=int, default=256)
    parser.add_argument("--model-reference-dim", type=int, default=128)
    parser.add_argument("--model-gru-layers", type=int, default=2)
    parser.add_argument(
        "--model-conditioning-mode",
        choices=["legacy_bias", "ref_film"],
        default="ref_film",
    )
    parser.add_argument(
        "--model-enable-adapter-mask-head",
        action="store_true",
        help="Enable a zero-init residual mask adapter head on top of the shared encoder output.",
    )
    parser.add_argument(
        "--model-enable-branch-decoder-head",
        action="store_true",
        help="Enable a second decoder branch with its own temporal model and mask head.",
    )
    parser.add_argument(
        "--model-enable-branch-abstention-gate",
        action="store_true",
        help="Add a per-frame scalar gate on top of the branch decoder mask for overlap abstention.",
    )
    parser.add_argument(
        "--model-enable-branch-overlap-refine-head",
        action="store_true",
        help="Add a zero-init complex residual canceller on top of the branch decoder output.",
    )
    parser.add_argument(
        "--model-enable-branch-overlap-refine-present-head",
        action="store_true",
        help=(
            "Add a second zero-init present-only residual refiner on top of the branch decoder output. "
            "This head always acts inside the branch gate region."
        ),
    )
    parser.add_argument(
        "--model-enable-branch-overlap-cancel-head",
        action="store_true",
        help="Add a dedicated overlap residual canceller head on top of the branch decoder output.",
    )
    parser.add_argument(
        "--model-enable-branch-overlap-cancel-apply-controller",
        action="store_true",
        help=(
            "Add a dedicated sigmoid controller head that scales overlap-cancel direct apply "
            "without changing the cancel estimate itself."
        ),
    )
    parser.add_argument(
        "--model-enable-branch-overlap-cancel-apply-absent-controller",
        action="store_true",
        help=(
            "Add a second sigmoid veto head for overlap-cancel direct apply so absent supervision "
            "does not share the same scalar controller with keep supervision."
        ),
    )
    parser.add_argument(
        "--model-enable-branch-overlap-dual-decoder-head",
        action="store_true",
        help=(
            "Add a dedicated overlap dual decoder that explicitly estimates residual interference "
            "and reconstructs target as mixture minus interference inside the selected overlap subdomain."
        ),
    )
    parser.add_argument(
        "--model-enable-adapter-temporal-model",
        action="store_true",
        help="Add a dedicated bidirectional GRU inside the adapter branch before adapter mask prediction.",
    )
    parser.add_argument("--model-adapter-gru-layers", type=int, default=1)
    parser.add_argument(
        "--model-adapter-conditioning-mode",
        choices=["none", "ref_bias", "ref_film"],
        default="none",
        help="Optional reference conditioning mode used only inside the adapter mask branch.",
    )
    parser.add_argument("--model-adapter-mask-max-delta", type=float, default=0.25)
    parser.add_argument("--model-branch-overlap-refine-max-delta", type=float, default=0.15)
    parser.add_argument(
        "--model-branch-overlap-refine-gate-mode",
        choices=["none", "gate", "complement"],
        default="gate",
    )
    parser.add_argument("--model-branch-overlap-refine-gate-power", type=float, default=1.0)
    parser.add_argument("--model-branch-overlap-refine-gate-floor", type=float, default=0.0)
    parser.add_argument(
        "--model-branch-overlap-refine-source-mode",
        choices=["mixture", "branch_base", "residual"],
        default="mixture",
    )
    parser.add_argument("--model-branch-overlap-refine-present-max-delta", type=float, default=0.15)
    parser.add_argument(
        "--model-branch-overlap-refine-present-source-mode",
        choices=["mixture", "branch_base", "residual", "current_residual"],
        default="residual",
    )
    parser.add_argument("--model-branch-overlap-refine-present-gate-power", type=float, default=1.0)
    parser.add_argument("--model-branch-overlap-refine-present-gate-floor", type=float, default=0.0)
    parser.add_argument(
        "--model-branch-overlap-refine-present-veto-mode",
        choices=["none", "complement_gate", "complement_ratio"],
        default="none",
    )
    parser.add_argument("--model-branch-overlap-refine-present-veto-strength", type=float, default=0.0)
    parser.add_argument("--model-branch-overlap-refine-present-veto-power", type=float, default=1.0)
    parser.add_argument("--model-branch-overlap-cancel-max-delta", type=float, default=0.15)
    parser.add_argument(
        "--model-branch-overlap-cancel-gate-mode",
        choices=["none", "gate", "complement"],
        default="complement",
    )
    parser.add_argument(
        "--model-branch-overlap-cancel-source-mode",
        choices=["mixture", "branch_base", "residual"],
        default="residual",
    )
    parser.add_argument(
        "--model-branch-overlap-cancel-apply-mode",
        choices=["subtract", "branch_base_blend", "auxiliary_only"],
        default="subtract",
    )
    parser.add_argument(
        "--model-branch-overlap-cancel-ratio-mode",
        choices=["complex", "phase_preserve"],
        default="complex",
    )
    parser.add_argument(
        "--model-branch-overlap-cancel-delta-blend-mode",
        choices=["none", "gate", "complement", "predicted_activity"],
        default="none",
    )
    parser.add_argument("--model-branch-overlap-cancel-max-blend", type=float, default=1.0)
    parser.add_argument("--model-branch-overlap-cancel-apply-controller-floor", type=float, default=0.0)
    parser.add_argument("--model-branch-overlap-cancel-apply-max-freq-ratio", type=float, default=1.0)
    parser.add_argument("--model-branch-overlap-dual-decoder-max-delta", type=float, default=0.15)
    parser.add_argument(
        "--model-branch-overlap-dual-decoder-gate-mode",
        choices=["none", "gate", "complement"],
        default="complement",
    )
    parser.add_argument(
        "--model-branch-overlap-dual-decoder-source-mode",
        choices=["mixture", "branch_base", "residual"],
        default="residual",
    )
    parser.add_argument(
        "--model-branch-overlap-dual-decoder-apply-mode",
        choices=["final_output", "current_output", "gate_controller"],
        default="final_output",
    )
    parser.add_argument("--model-branch-overlap-dual-decoder-max-blend", type=float, default=1.0)
    parser.add_argument("--model-branch-overlap-dual-decoder-gate-floor", type=float, default=0.0)
    parser.add_argument("--loss-stft-weight", type=float, default=0.5)
    parser.add_argument("--loss-sisdr-weight", type=float, default=0.0)
    parser.add_argument("--loss-branch-protect-guard-sisdr-weight", type=float, default=0.0)
    parser.add_argument("--loss-branch-protect-overlap-base-align-weight", type=float, default=0.0)
    parser.add_argument("--loss-branch-protect-teacher-overlap-weight", type=float, default=0.0)
    parser.add_argument("--loss-interference-extra-guard-sisdr-weight", type=float, default=0.0)
    parser.add_argument("--loss-interference-extra-base-align-weight", type=float, default=0.0)
    parser.add_argument("--loss-interference-extra-base-delta-projection-weight", type=float, default=0.0)
    parser.add_argument("--loss-transient-weight", type=float, default=0.0)
    parser.add_argument("--loss-transient-extra-weight", type=float, default=0.0)
    parser.add_argument("--loss-interference-weight", type=float, default=0.0)
    parser.add_argument("--loss-interference-extra-weight", type=float, default=0.0)
    parser.add_argument("--loss-overlap-interference-weight", type=float, default=0.0)
    parser.add_argument("--loss-overlap-interference-extra-weight", type=float, default=0.0)
    parser.add_argument("--loss-overlap-cancel-waveform-weight", type=float, default=0.0)
    parser.add_argument("--loss-overlap-cancel-target-projection-weight", type=float, default=0.0)
    parser.add_argument("--loss-overlap-cancel-absent-mix-weight", type=float, default=0.0)
    parser.add_argument("--loss-overlap-dual-mix-consistency-weight", type=float, default=0.0)
    parser.add_argument("--loss-overlap-dual-residual-target-projection-weight", type=float, default=0.0)
    parser.add_argument("--loss-overlap-dual-absent-mix-weight", type=float, default=0.0)
    parser.add_argument("--loss-absent-weight", type=float, default=0.0)
    parser.add_argument("--loss-absent-extra-weight", type=float, default=0.0)
    parser.add_argument("--loss-gate-absent-weight", type=float, default=0.0)
    parser.add_argument("--loss-gate-abstain-weight", type=float, default=0.0)
    parser.add_argument("--loss-gate-keep-weight", type=float, default=0.0)
    parser.add_argument("--loss-gate-target-weight", type=float, default=0.0)
    parser.add_argument(
        "--loss-gate-supervision-source",
        choices=[
            "branch_decoder_frame_gate",
            "overlap_cancel_apply_controller",
            "overlap_cancel_apply_controller_split",
        ],
        default="branch_decoder_frame_gate",
    )
    parser.add_argument(
        "--loss-gate-target-mode",
        choices=["none", "audibility"],
        default="none",
    )
    parser.add_argument("--loss-gate-target-energy-center", type=float, default=0.13)
    parser.add_argument("--loss-gate-target-energy-scale", type=float, default=0.035)
    parser.add_argument("--loss-gate-target-transient-share-center", type=float, default=0.01)
    parser.add_argument("--loss-gate-target-transient-share-scale", type=float, default=0.006)
    parser.add_argument("--loss-gate-target-transient-db-center", type=float, default=-13.0)
    parser.add_argument("--loss-gate-target-transient-db-scale", type=float, default=2.5)
    parser.add_argument("--loss-gate-target-energy-weight", type=float, default=0.75)
    parser.add_argument("--loss-gate-target-transient-share-weight", type=float, default=0.15)
    parser.add_argument("--loss-gate-target-transient-db-weight", type=float, default=0.10)
    parser.add_argument("--loss-gate-target-min-value", type=float, default=0.0)
    parser.add_argument("--loss-gate-target-max-value", type=float, default=1.0)
    parser.add_argument(
        "--loss-use-branch-prerefine-as-primary-prediction",
        action="store_true",
        help=(
            "When branch overlap refinement is enabled, use the branch pre-refine output as the "
            "primary prediction baseline inside compute_losses."
        ),
    )
    parser.add_argument("--loss-reconstruction-waveform-weight", type=float, default=0.0)
    parser.add_argument("--loss-reconstruction-stft-weight", type=float, default=0.0)
    parser.add_argument("--loss-reconstruction-extra-waveform-weight", type=float, default=0.0)
    parser.add_argument("--loss-reconstruction-extra-stft-weight", type=float, default=0.0)
    parser.add_argument(
        "--loss-interference-mode",
        choices=INTERFERENCE_LOSS_MODES,
        default="prediction_projection_ratio",
    )
    parser.add_argument(
        "--loss-interference-extra-mode",
        choices=INTERFERENCE_LOSS_MODES,
        default="prediction_projection_ratio",
    )
    parser.add_argument(
        "--loss-overlap-interference-mode",
        choices=INTERFERENCE_LOSS_MODES,
        default="prediction_projection_ratio",
    )
    parser.add_argument(
        "--loss-overlap-interference-extra-mode",
        choices=INTERFERENCE_LOSS_MODES,
        default="prediction_projection_ratio",
    )
    add_selector_args(parser, "reconstruction")
    add_selector_args(parser, "transient")
    add_selector_args(parser, "interference")
    add_selector_args(parser, "overlap_interference")
    add_selector_args(parser, "overlap_cancel")
    add_selector_args(parser, "overlap_dual")
    add_selector_args(parser, "absent")
    add_selector_args(parser, "branch_protect")
    add_selector_args(parser, "branch_protect_teacher")
    return parser.parse_args()


def add_selector_args(parser: argparse.ArgumentParser, prefix: str) -> None:
    flag_prefix_root = prefix.replace("_", "-")
    for branch_name in ("", "extra_"):
        flag_prefix = (
            f"--loss-{flag_prefix_root}-"
            if not branch_name
            else f"--loss-{flag_prefix_root}-{branch_name.replace('_', '-')}"
        )
        attr_prefix = f"loss_{prefix}_" if not branch_name else f"loss_{prefix}_{branch_name}"
        parser.add_argument(
            f"{flag_prefix}focus-sample-ids-file",
            dest=f"{attr_prefix}focus_sample_ids_file",
            type=Path,
            default=None,
        )
        parser.add_argument(f"{flag_prefix}focus-recipes", nargs="*", default=[])
        parser.add_argument(f"{flag_prefix}focus-patterns", nargs="*", default=[])
        parser.add_argument(f"{flag_prefix}focus-interference-pools", nargs="*", default=[])
        parser.add_argument(f"{flag_prefix}focus-interference-profiles", nargs="*", default=[])
        parser.add_argument(f"{flag_prefix}focus-interference-speaker-names", nargs="*", default=[])
        parser.add_argument(
            f"{flag_prefix}require-speech-interference",
            type=parse_optional_bool_arg,
            default=None,
        )
        parser.add_argument(
            f"{flag_prefix}require-music-interference",
            type=parse_optional_bool_arg,
            default=None,
        )
        parser.add_argument(
            f"{flag_prefix}require-other-interference",
            type=parse_optional_bool_arg,
            default=None,
        )
        parser.add_argument(f"{flag_prefix}min-target-ratio", type=float, default=None)
        parser.add_argument(f"{flag_prefix}max-target-ratio", type=float, default=None)
        parser.add_argument(f"{flag_prefix}min-target-energy-ratio", type=float, default=None)
        parser.add_argument(f"{flag_prefix}max-target-energy-ratio", type=float, default=None)
        parser.add_argument(f"{flag_prefix}min-overlap-ratio", type=float, default=None)
        parser.add_argument(f"{flag_prefix}max-overlap-ratio", type=float, default=None)
        parser.add_argument(f"{flag_prefix}min-interference-gain-db", type=float, default=None)
        parser.add_argument(f"{flag_prefix}max-interference-gain-db", type=float, default=None)
        parser.add_argument(f"{flag_prefix}min-interference-layer-count", type=int, default=None)
        parser.add_argument(f"{flag_prefix}max-interference-layer-count", type=int, default=None)
        parser.add_argument(
            f"{flag_prefix}min-target-transient-presence-minus-mid-db-mean",
            dest=f"{attr_prefix}min_target_transient_presence_minus_mid_db_mean",
            type=float,
            default=None,
        )
        parser.add_argument(
            f"{flag_prefix}max-target-transient-presence-minus-mid-db-mean",
            dest=f"{attr_prefix}max_target_transient_presence_minus_mid_db_mean",
            type=float,
            default=None,
        )
        parser.add_argument(
            f"{flag_prefix}min-target-transient-presence-share-mean",
            dest=f"{attr_prefix}min_target_transient_presence_share_mean",
            type=float,
            default=None,
        )
        parser.add_argument(
            f"{flag_prefix}max-target-transient-presence-share-mean",
            dest=f"{attr_prefix}max_target_transient_presence_share_mean",
            type=float,
            default=None,
        )
        parser.add_argument(
            f"{flag_prefix}min-interference-transient-presence-minus-mid-db-mean",
            dest=f"{attr_prefix}min_interference_transient_presence_minus_mid_db_mean",
            type=float,
            default=None,
        )
        parser.add_argument(
            f"{flag_prefix}max-interference-transient-presence-minus-mid-db-mean",
            dest=f"{attr_prefix}max_interference_transient_presence_minus_mid_db_mean",
            type=float,
            default=None,
        )
        parser.add_argument(
            f"{flag_prefix}min-interference-transient-presence-share-mean",
            dest=f"{attr_prefix}min_interference_transient_presence_share_mean",
            type=float,
            default=None,
        )
        parser.add_argument(
            f"{flag_prefix}max-interference-transient-presence-share-mean",
            dest=f"{attr_prefix}max_interference_transient_presence_share_mean",
            type=float,
            default=None,
        )
        parser.add_argument(
            f"{flag_prefix}min-target-interference-logspec-cosine",
            dest=f"{attr_prefix}min_target_interference_logspec_cosine",
            type=float,
            default=None,
        )
        parser.add_argument(
            f"{flag_prefix}max-target-interference-logspec-cosine",
            dest=f"{attr_prefix}max_target_interference_logspec_cosine",
            type=float,
            default=None,
        )


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def move_batch_to_device(batch: dict, device: torch.device) -> dict:
    moved = dict(batch)
    for key in [
        "mixture",
        "mixture_lengths",
        "target",
        "target_lengths",
        "reference",
        "reference_lengths",
        "target_present_ratios",
        "target_energy_ratios",
        "target_transient_presence_minus_mid_db_means",
        "target_transient_presence_share_means",
        "interference_transient_presence_minus_mid_db_means",
        "interference_transient_presence_share_means",
        "target_interference_logspec_cosines",
        "overlap_ratios",
        "interference_gain_dbs",
    ]:
        moved[key] = batch[key].to(device)
    return moved


def build_model_config(args: argparse.Namespace) -> dict[str, int]:
    return {
        "n_fft": args.model_n_fft,
        "hop_length": args.model_hop_length,
        "win_length": args.model_win_length,
        "hidden_dim": args.model_hidden_dim,
        "reference_dim": args.model_reference_dim,
        "gru_layers": args.model_gru_layers,
        "conditioning_mode": args.model_conditioning_mode,
        "enable_adapter_mask_head": args.model_enable_adapter_mask_head,
        "enable_branch_decoder_head": args.model_enable_branch_decoder_head,
        "enable_branch_abstention_gate": args.model_enable_branch_abstention_gate,
        "enable_branch_overlap_refine_head": args.model_enable_branch_overlap_refine_head,
        "enable_branch_overlap_refine_present_head": args.model_enable_branch_overlap_refine_present_head,
        "enable_branch_overlap_cancel_head": args.model_enable_branch_overlap_cancel_head,
        "enable_branch_overlap_cancel_apply_controller": (
            args.model_enable_branch_overlap_cancel_apply_controller
        ),
        "enable_branch_overlap_cancel_apply_absent_controller": (
            args.model_enable_branch_overlap_cancel_apply_absent_controller
        ),
        "enable_branch_overlap_dual_decoder_head": args.model_enable_branch_overlap_dual_decoder_head,
        "enable_adapter_temporal_model": args.model_enable_adapter_temporal_model,
        "adapter_gru_layers": args.model_adapter_gru_layers,
        "adapter_conditioning_mode": args.model_adapter_conditioning_mode,
        "adapter_mask_max_delta": args.model_adapter_mask_max_delta,
        "branch_overlap_refine_max_delta": args.model_branch_overlap_refine_max_delta,
        "branch_overlap_refine_gate_mode": args.model_branch_overlap_refine_gate_mode,
        "branch_overlap_refine_gate_power": args.model_branch_overlap_refine_gate_power,
        "branch_overlap_refine_gate_floor": args.model_branch_overlap_refine_gate_floor,
        "branch_overlap_refine_source_mode": args.model_branch_overlap_refine_source_mode,
        "branch_overlap_refine_present_max_delta": args.model_branch_overlap_refine_present_max_delta,
        "branch_overlap_refine_present_source_mode": args.model_branch_overlap_refine_present_source_mode,
        "branch_overlap_refine_present_gate_power": args.model_branch_overlap_refine_present_gate_power,
        "branch_overlap_refine_present_gate_floor": args.model_branch_overlap_refine_present_gate_floor,
        "branch_overlap_refine_present_veto_mode": args.model_branch_overlap_refine_present_veto_mode,
        "branch_overlap_refine_present_veto_strength": args.model_branch_overlap_refine_present_veto_strength,
        "branch_overlap_refine_present_veto_power": args.model_branch_overlap_refine_present_veto_power,
        "branch_overlap_cancel_max_delta": args.model_branch_overlap_cancel_max_delta,
        "branch_overlap_cancel_gate_mode": args.model_branch_overlap_cancel_gate_mode,
        "branch_overlap_cancel_source_mode": args.model_branch_overlap_cancel_source_mode,
        "branch_overlap_cancel_apply_mode": args.model_branch_overlap_cancel_apply_mode,
        "branch_overlap_cancel_ratio_mode": args.model_branch_overlap_cancel_ratio_mode,
        "branch_overlap_cancel_delta_blend_mode": args.model_branch_overlap_cancel_delta_blend_mode,
        "branch_overlap_cancel_max_blend": args.model_branch_overlap_cancel_max_blend,
        "branch_overlap_cancel_apply_controller_floor": (
            args.model_branch_overlap_cancel_apply_controller_floor
        ),
        "branch_overlap_cancel_apply_max_freq_ratio": args.model_branch_overlap_cancel_apply_max_freq_ratio,
        "branch_overlap_dual_decoder_max_delta": args.model_branch_overlap_dual_decoder_max_delta,
        "branch_overlap_dual_decoder_gate_mode": args.model_branch_overlap_dual_decoder_gate_mode,
        "branch_overlap_dual_decoder_source_mode": args.model_branch_overlap_dual_decoder_source_mode,
        "branch_overlap_dual_decoder_apply_mode": args.model_branch_overlap_dual_decoder_apply_mode,
        "branch_overlap_dual_decoder_max_blend": args.model_branch_overlap_dual_decoder_max_blend,
        "branch_overlap_dual_decoder_gate_floor": args.model_branch_overlap_dual_decoder_gate_floor,
    }


def load_optional_sample_ids(path: Path | None) -> list[str]:
    if path is None:
        return []
    sample_ids: list[str] = []
    with path.open("r", encoding="utf-8-sig") as fh:
        for line in fh:
            value = line.strip()
            if value:
                sample_ids.append(value)
    return sample_ids


def build_loss_config(args: argparse.Namespace) -> dict[str, float]:
    loss_config = {
        "sample_rate": args.sample_rate,
        "stft_weight": args.loss_stft_weight,
        "reconstruction_waveform_weight": args.loss_reconstruction_waveform_weight,
        "reconstruction_stft_weight": args.loss_reconstruction_stft_weight,
        "reconstruction_extra_waveform_weight": args.loss_reconstruction_extra_waveform_weight,
        "reconstruction_extra_stft_weight": args.loss_reconstruction_extra_stft_weight,
        "sisdr_weight": args.loss_sisdr_weight,
        "branch_protect_guard_sisdr_weight": args.loss_branch_protect_guard_sisdr_weight,
        "branch_protect_overlap_base_align_weight": (
            args.loss_branch_protect_overlap_base_align_weight
        ),
        "branch_protect_teacher_overlap_weight": (
            args.loss_branch_protect_teacher_overlap_weight
        ),
        "interference_extra_guard_sisdr_weight": args.loss_interference_extra_guard_sisdr_weight,
        "interference_extra_base_align_weight": args.loss_interference_extra_base_align_weight,
        "interference_extra_base_delta_projection_weight": (
            args.loss_interference_extra_base_delta_projection_weight
        ),
        "transient_weight": args.loss_transient_weight,
        "transient_extra_weight": args.loss_transient_extra_weight,
        "interference_weight": args.loss_interference_weight,
        "interference_extra_weight": args.loss_interference_extra_weight,
        "overlap_interference_weight": args.loss_overlap_interference_weight,
        "overlap_interference_extra_weight": args.loss_overlap_interference_extra_weight,
        "overlap_cancel_waveform_weight": args.loss_overlap_cancel_waveform_weight,
        "overlap_cancel_target_projection_weight": args.loss_overlap_cancel_target_projection_weight,
        "overlap_cancel_absent_mix_weight": args.loss_overlap_cancel_absent_mix_weight,
        "overlap_dual_mix_consistency_weight": args.loss_overlap_dual_mix_consistency_weight,
        "overlap_dual_residual_target_projection_weight": (
            args.loss_overlap_dual_residual_target_projection_weight
        ),
        "overlap_dual_absent_mix_weight": args.loss_overlap_dual_absent_mix_weight,
        "absent_weight": args.loss_absent_weight,
        "absent_extra_weight": args.loss_absent_extra_weight,
        "gate_absent_weight": args.loss_gate_absent_weight,
        "gate_abstain_weight": args.loss_gate_abstain_weight,
        "gate_keep_weight": args.loss_gate_keep_weight,
        "gate_target_weight": args.loss_gate_target_weight,
        "gate_supervision_source": args.loss_gate_supervision_source,
        "gate_target_mode": args.loss_gate_target_mode,
        "gate_target_energy_center": args.loss_gate_target_energy_center,
        "gate_target_energy_scale": args.loss_gate_target_energy_scale,
        "gate_target_transient_share_center": args.loss_gate_target_transient_share_center,
        "gate_target_transient_share_scale": args.loss_gate_target_transient_share_scale,
        "gate_target_transient_db_center": args.loss_gate_target_transient_db_center,
        "gate_target_transient_db_scale": args.loss_gate_target_transient_db_scale,
        "gate_target_energy_weight": args.loss_gate_target_energy_weight,
        "gate_target_transient_share_weight": args.loss_gate_target_transient_share_weight,
        "gate_target_transient_db_weight": args.loss_gate_target_transient_db_weight,
        "gate_target_min_value": args.loss_gate_target_min_value,
        "gate_target_max_value": args.loss_gate_target_max_value,
        "use_branch_prerefine_as_primary_prediction": args.loss_use_branch_prerefine_as_primary_prediction,
        "interference_loss_mode": args.loss_interference_mode,
        "interference_extra_loss_mode": args.loss_interference_extra_mode,
        "overlap_interference_loss_mode": args.loss_overlap_interference_mode,
        "overlap_interference_extra_loss_mode": args.loss_overlap_interference_extra_mode,
        "transient_top_ratio": 0.12,
        "transient_min_count": 8,
        "transient_mid_low_hz": 800.0,
        "transient_mid_high_hz": 3000.0,
        "transient_presence_low_hz": 3000.0,
        "transient_presence_high_hz": 8000.0,
        "transient_ratio_weight": 0.5,
    }
    for prefix in (
        "reconstruction",
        "transient",
        "interference",
        "overlap_interference",
        "overlap_cancel",
        "overlap_dual",
        "absent",
        "branch_protect",
        "branch_protect_teacher",
    ):
        for branch_name in ("", "extra_"):
            config_prefix = f"{prefix}_" if not branch_name else f"{prefix}_{branch_name}"
            attr_prefix = f"loss_{prefix}_" if not branch_name else f"loss_{prefix}_{branch_name}"
            loss_config[f"{config_prefix}focus_sample_ids"] = load_optional_sample_ids(
                getattr(args, f"{attr_prefix}focus_sample_ids_file")
            )
            for suffix in (
                "focus_recipes",
                "focus_patterns",
                "focus_interference_pools",
                "focus_interference_profiles",
                "focus_interference_speaker_names",
                "require_speech_interference",
                "require_music_interference",
                "require_other_interference",
                "min_target_ratio",
                "max_target_ratio",
                "min_target_energy_ratio",
                "max_target_energy_ratio",
                "min_overlap_ratio",
                "max_overlap_ratio",
                "min_interference_gain_db",
                "max_interference_gain_db",
                "min_interference_layer_count",
                "max_interference_layer_count",
                "min_target_transient_presence_minus_mid_db_mean",
                "max_target_transient_presence_minus_mid_db_mean",
                "min_target_transient_presence_share_mean",
                "max_target_transient_presence_share_mean",
                "min_interference_transient_presence_minus_mid_db_mean",
                "max_interference_transient_presence_minus_mid_db_mean",
                "min_interference_transient_presence_share_mean",
                "max_interference_transient_presence_share_mean",
                "min_target_interference_logspec_cosine",
                "max_target_interference_logspec_cosine",
            ):
                attr_name = f"{attr_prefix}{suffix}"
                loss_config[f"{config_prefix}{suffix}"] = getattr(args, attr_name)
    return loss_config


def load_checkpoint(path: Path, device: torch.device) -> dict:
    return torch.load(path, map_location=device, weights_only=False)


def resolve_model_config_from_checkpoint(checkpoint: dict) -> dict:
    model_config = dict(checkpoint.get("model_config", {}))
    if "conditioning_mode" not in model_config:
        state_dict = checkpoint["model_state_dict"]
        if "condition_proj.weight" in state_dict:
            model_config["conditioning_mode"] = "legacy_bias"
    return model_config


def serialize_repo_path(path: Path | None) -> str | None:
    if path is None:
        return None
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def resolve_teacher_checkpoint_path(
    explicit_path: Path | None,
    checkpoint: dict | None,
    checkpoint_path: Path | None,
    allow_metadata_fallback: bool = True,
) -> Path | None:
    if explicit_path is not None:
        return explicit_path.resolve()
    if not allow_metadata_fallback:
        return None
    if checkpoint is None:
        return None

    metadata_path = checkpoint.get("teacher_checkpoint")
    if not metadata_path:
        return None

    candidate = Path(str(metadata_path))
    if candidate.is_absolute():
        return candidate.resolve()

    search_roots = [ROOT]
    if checkpoint_path is not None:
        search_roots.append(checkpoint_path.parent)
    for base_dir in search_roots:
        resolved = (base_dir / candidate).resolve()
        if resolved.exists():
            return resolved
    return (ROOT / candidate).resolve()


def load_model_state_dict_for_init(model: nn.Module, checkpoint_state_dict: dict[str, torch.Tensor]) -> None:
    missing_keys, unexpected_keys = model.load_state_dict(checkpoint_state_dict, strict=False)
    allowed_missing_prefixes = (
        "branch_decoder_temporal_model.",
        "branch_decoder_mask_head.",
        "branch_decoder_gate_head.",
        "branch_overlap_refine_head.",
        "branch_overlap_refine_present_head.",
        "branch_overlap_cancel_head.",
        "branch_overlap_cancel_apply_controller_head.",
        "branch_overlap_cancel_apply_absent_controller_head.",
        "branch_overlap_dual_decoder_temporal_model.",
        "branch_overlap_dual_decoder_head.",
        "adapter_mask_head.",
        "adapter_condition_proj.",
        "adapter_condition_scale.",
        "adapter_condition_shift.",
        "adapter_temporal_model.",
    )
    disallowed_missing = [
        key for key in missing_keys if not any(key.startswith(prefix) for prefix in allowed_missing_prefixes)
    ]
    if disallowed_missing or unexpected_keys:
        raise RuntimeError(
            "Unexpected state-dict mismatch when loading init checkpoint: "
            f"missing={disallowed_missing}, unexpected={unexpected_keys}"
        )
    if any(key.startswith("branch_decoder_") for key in missing_keys) and hasattr(model, "reset_branch_decoder_from_base"):
        model.reset_branch_decoder_from_base()
    if any(key.startswith("branch_overlap_dual_decoder_") for key in missing_keys) and hasattr(
        model,
        "reset_branch_overlap_dual_decoder_from_branch",
    ):
        model.reset_branch_overlap_dual_decoder_from_branch()


def _matches_module_prefix(parameter_name: str, module_prefix: str) -> bool:
    return parameter_name == module_prefix or parameter_name.startswith(f"{module_prefix}.")


def configure_trainable_parameters(
    model: nn.Module,
    module_prefixes: list[str],
) -> tuple[list[nn.Parameter], dict[str, object]]:
    normalized_prefixes = [prefix.strip() for prefix in module_prefixes if prefix and prefix.strip()]
    named_parameters = list(model.named_parameters())
    total_param_count = int(sum(parameter.numel() for _, parameter in named_parameters))

    if not normalized_prefixes:
        for _, parameter in named_parameters:
            parameter.requires_grad = True
        return list(model.parameters()), {
            "mode": "all",
            "trainable_module_prefixes": [],
            "matched_module_prefixes": [],
            "frozen_module_prefixes": [],
            "trainable_parameter_count": total_param_count,
            "total_parameter_count": total_param_count,
            "trainable_parameter_fraction": 1.0,
            "trainable_parameter_names": [name for name, _ in named_parameters],
        }

    matched_prefixes: list[str] = []
    trainable_parameter_names: list[str] = []
    trainable_parameters: list[nn.Parameter] = []
    trainable_param_count = 0

    for name, parameter in named_parameters:
        is_trainable = any(_matches_module_prefix(name, prefix) for prefix in normalized_prefixes)
        parameter.requires_grad = is_trainable
        if is_trainable:
            trainable_parameter_names.append(name)
            trainable_parameters.append(parameter)
            trainable_param_count += int(parameter.numel())

    for prefix in normalized_prefixes:
        if any(_matches_module_prefix(name, prefix) for name, _ in named_parameters):
            matched_prefixes.append(prefix)

    unmatched_prefixes = [prefix for prefix in normalized_prefixes if prefix not in matched_prefixes]
    if unmatched_prefixes:
        raise ValueError(f"Unknown trainable module prefixes: {unmatched_prefixes}")
    if not trainable_parameters:
        raise ValueError("No trainable parameters remain after applying trainable module prefixes.")

    return trainable_parameters, {
        "mode": "module_prefix_subset",
        "trainable_module_prefixes": normalized_prefixes,
        "matched_module_prefixes": matched_prefixes,
        "frozen_module_prefixes": [
            name for name, _ in named_parameters if not any(_matches_module_prefix(name, prefix) for prefix in normalized_prefixes)
        ],
        "trainable_parameter_count": trainable_param_count,
        "total_parameter_count": total_param_count,
        "trainable_parameter_fraction": float(trainable_param_count) / float(total_param_count),
        "trainable_parameter_names": trainable_parameter_names,
    }


def build_interval_presence_sample_weights(
    intervals_batch: list[list[dict[str, float]]],
    device: torch.device,
) -> torch.Tensor:
    return torch.tensor(
        [1.0 if intervals else 0.0 for intervals in intervals_batch],
        dtype=torch.float32,
        device=device,
    )


def evaluate(
    model: STFTMaskBaseline,
    dataloader: DataLoader,
    device: torch.device,
    loss_config: dict[str, float],
    teacher_model: STFTMaskBaseline | None = None,
) -> tuple[dict[str, float], dict[str, dict[str, float | int | bool | None]]]:
    model.eval()
    total_loss = 0.0
    total_wave = 0.0
    total_stft = 0.0
    total_reconstruction_wave = 0.0
    total_reconstruction_stft = 0.0
    total_reconstruction_extra_wave = 0.0
    total_reconstruction_extra_stft = 0.0
    total_sisdr_loss = 0.0
    total_branch_protect_guard_sisdr_loss = 0.0
    total_branch_protect_overlap_base_align_l1 = 0.0
    total_branch_protect_teacher_overlap_l1 = 0.0
    total_interference_extra_guard_sisdr_loss = 0.0
    total_interference_extra_base_align_l1 = 0.0
    total_interference_extra_base_delta_projection_ratio = 0.0
    total_sisdr_db = 0.0
    total_transient = 0.0
    total_transient_extra = 0.0
    total_interference = 0.0
    total_interference_extra = 0.0
    total_overlap_interference = 0.0
    total_overlap_interference_extra = 0.0
    total_overlap_cancel = 0.0
    total_overlap_cancel_target_projection = 0.0
    total_overlap_cancel_absent_mix = 0.0
    total_overlap_dual_mix_consistency = 0.0
    total_overlap_dual_residual_target_projection = 0.0
    total_overlap_dual_absent_mix = 0.0
    total_absent = 0.0
    total_absent_extra = 0.0
    total_gate_absent = 0.0
    total_gate_abstain = 0.0
    total_gate_keep = 0.0
    total_gate_target = 0.0
    batch_count = 0
    sample_count = 0
    compute_loss_kwargs = build_compute_loss_kwargs(loss_config)
    selector_totals = {
        prefix: {"active": False, "selected_count": 0, "total_count": 0}
             for prefix in (
                 "reconstruction",
                 "reconstruction_extra",
                 "transient",
                 "transient_extra",
            "interference",
            "interference_extra",
            "overlap_interference",
            "overlap_interference_extra",
            "overlap_cancel",
            "overlap_dual",
            "absent",
            "absent_extra",
            "branch_protect",
            "branch_protect_teacher",
        )
    }
    with torch.no_grad():
        for batch in dataloader:
            batch = move_batch_to_device(batch, device)
            batch_size = len(batch["sample_ids"])
            outputs = model(
                mixture=batch["mixture"],
                mixture_lengths=batch["mixture_lengths"],
                reference=batch["reference"],
                reference_lengths=batch["reference_lengths"],
            )
            teacher_prediction = None
            if teacher_model is not None:
                teacher_outputs = teacher_model(
                    mixture=batch["mixture"],
                    mixture_lengths=batch["mixture_lengths"],
                    reference=batch["reference"],
                    reference_lengths=batch["reference_lengths"],
                )
                teacher_prediction = teacher_outputs["estimated_waveform"]
            reconstruction_sample_weights, reconstruction_extra_sample_weights, reconstruction_union_sample_weights = (
                resolve_selector_sample_weights(
                    batch=batch,
                    device=device,
                    loss_config=loss_config,
                    prefix="reconstruction",
                    extra_weight_keys=("reconstruction_extra_waveform_weight", "reconstruction_extra_stft_weight"),
                )
            )
            transient_sample_weights, transient_extra_sample_weights, transient_union_sample_weights = (
                resolve_selector_sample_weights(
                    batch=batch,
                    device=device,
                    loss_config=loss_config,
                    prefix="transient",
                    extra_weight_keys=("transient_extra_weight",),
                )
            )
            interference_sample_weights, interference_extra_sample_weights, interference_union_sample_weights = (
                resolve_selector_sample_weights(
                    batch=batch,
                    device=device,
                    loss_config=loss_config,
                    prefix="interference",
                    extra_weight_keys=(
                        "interference_extra_weight",
                        "interference_extra_guard_sisdr_weight",
                        "interference_extra_base_align_weight",
                        "interference_extra_base_delta_projection_weight",
                    ),
                )
            )
            overlap_interference_sample_weights, overlap_interference_extra_sample_weights, overlap_interference_union_sample_weights = (
                resolve_selector_sample_weights(
                    batch=batch,
                    device=device,
                    loss_config=loss_config,
                    prefix="overlap_interference",
                    extra_weight_keys=(
                        "overlap_interference_weight",
                        "overlap_interference_extra_weight",
                    ),
                )
            )
            overlap_cancel_sample_weights = build_selector_sample_weights(
                batch=batch,
                device=device,
                loss_config=loss_config,
                prefix="overlap_cancel",
            )
            overlap_dual_sample_weights = build_selector_sample_weights(
                batch=batch,
                device=device,
                loss_config=loss_config,
                prefix="overlap_dual",
            )
            absent_sample_weights, absent_extra_sample_weights, absent_union_sample_weights = (
                resolve_selector_sample_weights(
                    batch=batch,
                    device=device,
                    loss_config=loss_config,
                    prefix="absent",
                    extra_weight_keys=("absent_extra_weight",),
                )
            )
            absent_presence_sample_weights = build_interval_presence_sample_weights(
                batch["target_absent_intervals"],
                device=device,
            )
            branch_protect_sample_weights = build_selector_sample_weights(
                batch=batch,
                device=device,
                loss_config=loss_config,
                prefix="branch_protect",
            )
            branch_protect_teacher_sample_weights = build_selector_sample_weights(
                batch=batch,
                device=device,
                loss_config=loss_config,
                prefix="branch_protect_teacher",
            )
            gate_target_values = build_gate_target_values(batch=batch, device=device, loss_config=loss_config)
            gate_target_sample_weights = (
                torch.ones(len(batch["sample_ids"]), dtype=torch.float32, device=device)
                if gate_target_values is not None
                else None
            )
            gate_supervision_source = str(
                loss_config.get("gate_supervision_source", "branch_decoder_frame_gate")
            )
            gate_values = outputs.get("branch_decoder_frame_gate")
            gate_absent_values = None
            gate_abstain_values = None
            gate_keep_values = None
            gate_target_source_values = None
            gate_absent_sample_weights = absent_presence_sample_weights
            gate_abstain_sample_weights = interference_extra_sample_weights
            gate_keep_sample_weights = branch_protect_sample_weights
            gate_target_intervals = None
            gate_absent_intervals = None
            gate_abstain_intervals = None
            gate_keep_intervals = None
            if gate_supervision_source == "overlap_cancel_apply_controller":
                gate_values = outputs.get("branch_overlap_cancel_apply_controller")
                gate_absent_sample_weights = absent_union_sample_weights
                gate_abstain_sample_weights = None
                gate_keep_sample_weights = overlap_cancel_sample_weights
                gate_absent_intervals = batch["target_absent_intervals"]
                gate_keep_intervals = batch["target_overlap_intervals"]
            elif gate_supervision_source == "overlap_cancel_apply_controller_split":
                gate_values = outputs.get("branch_overlap_cancel_apply_controller")
                gate_absent_values = outputs.get("branch_overlap_cancel_apply_absent_controller")
                gate_keep_values = outputs.get("branch_overlap_cancel_apply_keep_controller")
                gate_target_source_values = gate_values
                gate_absent_sample_weights = absent_union_sample_weights
                gate_abstain_sample_weights = None
                gate_keep_sample_weights = overlap_cancel_sample_weights
                gate_absent_intervals = batch["target_absent_intervals"]
                gate_keep_intervals = batch["target_overlap_intervals"]
            for prefix, weights in (
                ("reconstruction", reconstruction_union_sample_weights),
                ("reconstruction_extra", reconstruction_extra_sample_weights),
                ("transient", transient_union_sample_weights),
                ("transient_extra", transient_extra_sample_weights),
                ("interference", interference_union_sample_weights),
                ("interference_extra", interference_extra_sample_weights),
                ("overlap_interference", overlap_interference_union_sample_weights),
                ("overlap_interference_extra", overlap_interference_extra_sample_weights),
                ("overlap_cancel", overlap_cancel_sample_weights),
                ("overlap_dual", overlap_dual_sample_weights),
                ("absent", absent_union_sample_weights),
                ("absent_extra", absent_extra_sample_weights),
                ("branch_protect", branch_protect_sample_weights),
                ("branch_protect_teacher", branch_protect_teacher_sample_weights),
            ):
                stats = summarize_selector_weights(weights, len(batch["sample_ids"]))
                selector_totals[prefix]["active"] = selector_totals[prefix]["active"] or bool(stats["active"])
                selector_totals[prefix]["selected_count"] += int(stats["selected_count"])
                selector_totals[prefix]["total_count"] += int(stats["total_count"])
            losses = compute_losses(
                prediction=resolve_primary_prediction(
                    outputs,
                    use_branch_prerefine_as_primary_prediction=bool(
                        loss_config.get("use_branch_prerefine_as_primary_prediction", False)
                    ),
                ),
                reconstruction_extra_prediction=outputs["estimated_waveform"],
                extra_prediction=resolve_branch_extra_prediction(outputs),
                teacher_prediction=teacher_prediction,
                overlap_cancel_prediction=outputs.get("branch_overlap_cancel_estimate_waveform"),
                overlap_dual_target_prediction=outputs.get("branch_overlap_dual_target_waveform"),
                overlap_dual_residual_prediction=outputs.get("branch_overlap_dual_residual_waveform"),
                mixture=batch["mixture"],
                target=batch["target"],
                lengths=batch["target_lengths"],
                absent_intervals=batch["target_absent_intervals"],
                overlap_intervals=batch["target_overlap_intervals"],
                model=model,
                gate_values=gate_values,
                gate_absent_values=gate_absent_values,
                gate_abstain_values=gate_abstain_values,
                gate_keep_values=gate_keep_values,
                gate_target_source_values=gate_target_source_values,
                reconstruction_sample_weights=reconstruction_sample_weights,
                reconstruction_extra_sample_weights=reconstruction_extra_sample_weights,
                transient_sample_weights=transient_sample_weights,
                transient_extra_sample_weights=transient_extra_sample_weights,
                interference_sample_weights=interference_sample_weights,
                interference_extra_sample_weights=interference_extra_sample_weights,
                overlap_interference_sample_weights=overlap_interference_sample_weights,
                overlap_interference_extra_sample_weights=overlap_interference_extra_sample_weights,
                overlap_cancel_sample_weights=overlap_cancel_sample_weights,
                overlap_cancel_absent_mix_sample_weights=absent_union_sample_weights,
                overlap_dual_sample_weights=overlap_dual_sample_weights,
                branch_protect_sample_weights=branch_protect_sample_weights,
                branch_protect_teacher_sample_weights=branch_protect_teacher_sample_weights,
                absent_sample_weights=absent_sample_weights,
                absent_extra_sample_weights=absent_extra_sample_weights,
                gate_absent_sample_weights=gate_absent_sample_weights,
                gate_abstain_sample_weights=gate_abstain_sample_weights,
                gate_keep_sample_weights=gate_keep_sample_weights,
                gate_target_sample_weights=gate_target_sample_weights,
                gate_target_values=gate_target_values,
                gate_absent_intervals=gate_absent_intervals,
                gate_abstain_intervals=gate_abstain_intervals,
                gate_keep_intervals=gate_keep_intervals,
                gate_target_intervals=gate_target_intervals,
                **compute_loss_kwargs,
            )
            total_loss += float(losses.total.item()) * batch_size
            total_wave += float(losses.waveform_l1.item()) * batch_size
            total_stft += float(losses.stft_l1.item()) * batch_size
            total_reconstruction_wave += float(losses.reconstruction_waveform_l1.item()) * batch_size
            total_reconstruction_stft += float(losses.reconstruction_stft_l1.item()) * batch_size
            total_reconstruction_extra_wave += float(losses.reconstruction_extra_waveform_l1.item()) * batch_size
            total_reconstruction_extra_stft += float(losses.reconstruction_extra_stft_l1.item()) * batch_size
            total_sisdr_loss += float(losses.sisdr_loss.item()) * batch_size
            total_branch_protect_guard_sisdr_loss += (
                float(losses.branch_protect_guard_sisdr_loss.item()) * batch_size
            )
            total_branch_protect_overlap_base_align_l1 += float(
                losses.branch_protect_overlap_base_align_l1.item()
            ) * batch_size
            total_branch_protect_teacher_overlap_l1 += float(
                losses.branch_protect_teacher_overlap_l1.item()
            ) * batch_size
            total_interference_extra_guard_sisdr_loss += (
                float(losses.interference_extra_guard_sisdr_loss.item()) * batch_size
            )
            total_interference_extra_base_align_l1 += (
                float(losses.interference_extra_base_align_l1.item()) * batch_size
            )
            total_interference_extra_base_delta_projection_ratio += float(
                losses.interference_extra_base_delta_projection_ratio.item()
            ) * batch_size
            total_sisdr_db += float(losses.sisdr_db.item()) * batch_size
            total_transient += float(losses.transient_presence_l1.item()) * batch_size
            total_transient_extra += float(losses.transient_extra_presence_l1.item()) * batch_size
            total_interference += float(losses.interference_projection_ratio.item()) * batch_size
            total_interference_extra += float(losses.interference_extra_projection_ratio.item()) * batch_size
            total_overlap_interference += float(losses.overlap_interference_projection_ratio.item()) * batch_size
            total_overlap_interference_extra += (
                float(losses.overlap_interference_extra_projection_ratio.item()) * batch_size
            )
            total_overlap_cancel += float(losses.overlap_cancel_waveform_l1.item()) * batch_size
            total_overlap_cancel_target_projection += float(
                losses.overlap_cancel_target_projection_ratio.item()
            ) * batch_size
            total_overlap_cancel_absent_mix += float(
                losses.overlap_cancel_absent_mix_l1.item()
            ) * batch_size
            total_overlap_dual_mix_consistency += (
                float(losses.overlap_dual_mix_consistency_l1.item()) * batch_size
            )
            total_overlap_dual_residual_target_projection += float(
                losses.overlap_dual_residual_target_projection_ratio.item()
            ) * batch_size
            total_overlap_dual_absent_mix += float(
                losses.overlap_dual_absent_mix_l1.item()
            ) * batch_size
            total_absent += float(losses.absent_interval_l1.item()) * batch_size
            total_absent_extra += float(losses.absent_extra_interval_l1.item()) * batch_size
            total_gate_absent += float(losses.gate_absent_mean.item()) * batch_size
            total_gate_abstain += float(losses.gate_abstain_mean.item()) * batch_size
            total_gate_keep += float(losses.gate_keep_mean.item()) * batch_size
            total_gate_target += float(losses.gate_target_l1.item()) * batch_size
            batch_count += 1
            sample_count += batch_size
    if sample_count == 0:
        metrics = {
            "loss": 0.0,
            "waveform_l1": 0.0,
            "stft_l1": 0.0,
            "reconstruction_waveform_l1": 0.0,
            "reconstruction_stft_l1": 0.0,
            "reconstruction_extra_waveform_l1": 0.0,
            "reconstruction_extra_stft_l1": 0.0,
            "sisdr_loss": 0.0,
            "branch_protect_guard_sisdr_loss": 0.0,
            "branch_protect_overlap_base_align_l1": 0.0,
            "branch_protect_teacher_overlap_l1": 0.0,
            "interference_extra_guard_sisdr_loss": 0.0,
            "interference_extra_base_align_l1": 0.0,
            "interference_extra_base_delta_projection_ratio": 0.0,
            "sisdr_db": 0.0,
            "transient_presence_l1": 0.0,
            "transient_extra_presence_l1": 0.0,
            "interference_projection_ratio": 0.0,
            "interference_extra_projection_ratio": 0.0,
            "overlap_interference_projection_ratio": 0.0,
            "overlap_interference_extra_projection_ratio": 0.0,
            "overlap_cancel_waveform_l1": 0.0,
            "overlap_cancel_target_projection_ratio": 0.0,
            "overlap_cancel_absent_mix_l1": 0.0,
            "overlap_dual_mix_consistency_l1": 0.0,
            "overlap_dual_residual_target_projection_ratio": 0.0,
            "overlap_dual_absent_mix_l1": 0.0,
            "absent_interval_l1": 0.0,
            "absent_extra_interval_l1": 0.0,
            "gate_absent_mean": 0.0,
            "gate_abstain_mean": 0.0,
            "gate_keep_mean": 0.0,
            "gate_target_l1": 0.0,
        }
    else:
        metrics = {
            "loss": total_loss / sample_count,
            "waveform_l1": total_wave / sample_count,
            "stft_l1": total_stft / sample_count,
            "reconstruction_waveform_l1": total_reconstruction_wave / sample_count,
            "reconstruction_stft_l1": total_reconstruction_stft / sample_count,
            "reconstruction_extra_waveform_l1": total_reconstruction_extra_wave / sample_count,
            "reconstruction_extra_stft_l1": total_reconstruction_extra_stft / sample_count,
            "sisdr_loss": total_sisdr_loss / sample_count,
            "branch_protect_guard_sisdr_loss": total_branch_protect_guard_sisdr_loss / sample_count,
            "branch_protect_overlap_base_align_l1": (
                total_branch_protect_overlap_base_align_l1 / sample_count
            ),
            "branch_protect_teacher_overlap_l1": (
                total_branch_protect_teacher_overlap_l1 / sample_count
            ),
            "interference_extra_guard_sisdr_loss": total_interference_extra_guard_sisdr_loss / sample_count,
            "interference_extra_base_align_l1": total_interference_extra_base_align_l1 / sample_count,
            "interference_extra_base_delta_projection_ratio": (
                total_interference_extra_base_delta_projection_ratio / sample_count
            ),
            "sisdr_db": total_sisdr_db / sample_count,
            "transient_presence_l1": total_transient / sample_count,
            "transient_extra_presence_l1": total_transient_extra / sample_count,
            "interference_projection_ratio": total_interference / sample_count,
            "interference_extra_projection_ratio": total_interference_extra / sample_count,
            "overlap_interference_projection_ratio": total_overlap_interference / sample_count,
            "overlap_interference_extra_projection_ratio": total_overlap_interference_extra / sample_count,
            "overlap_cancel_waveform_l1": total_overlap_cancel / sample_count,
            "overlap_cancel_target_projection_ratio": (
                total_overlap_cancel_target_projection / sample_count
            ),
            "overlap_cancel_absent_mix_l1": (
                total_overlap_cancel_absent_mix / sample_count
            ),
            "overlap_dual_mix_consistency_l1": (
                total_overlap_dual_mix_consistency / sample_count
            ),
            "overlap_dual_residual_target_projection_ratio": (
                total_overlap_dual_residual_target_projection / sample_count
            ),
            "overlap_dual_absent_mix_l1": (
                total_overlap_dual_absent_mix / sample_count
            ),
            "absent_interval_l1": total_absent / sample_count,
            "absent_extra_interval_l1": total_absent_extra / sample_count,
            "gate_absent_mean": total_gate_absent / sample_count,
            "gate_abstain_mean": total_gate_abstain / sample_count,
            "gate_keep_mean": total_gate_keep / sample_count,
            "gate_target_l1": total_gate_target / sample_count,
        }
    selector_metrics = {}
    for prefix, totals in selector_totals.items():
        total_count = int(totals["total_count"])
        selected_count = int(totals["selected_count"])
        selector_metrics[prefix] = {
            "active": bool(totals["active"]),
            "selected_count": selected_count,
            "total_count": total_count,
            "selected_fraction": (float(selected_count) / float(total_count)) if total_count > 0 else None,
        }
    return metrics, selector_metrics


def main() -> None:
    args = parse_args()
    set_seed(args.seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    start_ts = time.time()
    start_dt = datetime.now()
    print(f"train_start={start_dt.isoformat(timespec='seconds')}")
    print(f"device={device.type}")

    train_dataset = SyntheticTSEDataset(args.train_manifest, sample_rate=args.sample_rate)
    val_dataset = SyntheticTSEDataset(args.val_manifest, sample_rate=args.sample_rate)

    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=args.num_workers,
        collate_fn=synthetic_collate_fn,
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        collate_fn=synthetic_collate_fn,
    )

    model_config = build_model_config(args)
    loss_config = build_loss_config(args)
    compute_loss_kwargs = build_compute_loss_kwargs(loss_config)
    model = STFTMaskBaseline(**model_config).to(device)
    init_checkpoint_path: str | None = None
    init_checkpoint: dict | None = None
    if args.init_checkpoint is not None:
        init_checkpoint = load_checkpoint(args.init_checkpoint, device)
        load_model_state_dict_for_init(model, init_checkpoint["model_state_dict"])
        init_checkpoint_path = str(args.init_checkpoint)
    teacher_checkpoint = None
    resolved_teacher_checkpoint_path = resolve_teacher_checkpoint_path(
        explicit_path=args.teacher_checkpoint,
        checkpoint=init_checkpoint,
        checkpoint_path=args.init_checkpoint,
        allow_metadata_fallback=not args.disable_teacher_checkpoint_metadata_fallback,
    )
    teacher_checkpoint_path: str | None = None
    teacher_model: STFTMaskBaseline | None = None
    if resolved_teacher_checkpoint_path is not None:
        teacher_checkpoint = load_checkpoint(resolved_teacher_checkpoint_path, device)
        teacher_model = STFTMaskBaseline(
            **resolve_model_config_from_checkpoint(teacher_checkpoint)
        ).to(device)
        teacher_model.load_state_dict(teacher_checkpoint["model_state_dict"])
        teacher_model.eval()
        for parameter in teacher_model.parameters():
            parameter.requires_grad_(False)
        teacher_checkpoint_path = str(resolved_teacher_checkpoint_path)
    trainable_parameters, trainable_config = configure_trainable_parameters(
        model=model,
        module_prefixes=args.trainable_module_prefixes,
    )
    print(
        json.dumps(
            {
                "trainable_mode": trainable_config["mode"],
                "trainable_module_prefixes": trainable_config["trainable_module_prefixes"],
                "trainable_parameter_count": trainable_config["trainable_parameter_count"],
                "total_parameter_count": trainable_config["total_parameter_count"],
                "trainable_parameter_fraction": round(float(trainable_config["trainable_parameter_fraction"]), 6),
            },
            ensure_ascii=False,
        )
    )
    optimizer = torch.optim.Adam(trainable_parameters, lr=args.lr)

    history: list[dict[str, float | int]] = []
    global_step = 0
    best_val_loss = float("inf")

    for epoch in range(1, args.epochs + 1):
        model.train()
        epoch_loss = 0.0
        epoch_wave = 0.0
        epoch_stft = 0.0
        epoch_reconstruction_wave = 0.0
        epoch_reconstruction_stft = 0.0
        epoch_reconstruction_extra_wave = 0.0
        epoch_reconstruction_extra_stft = 0.0
        epoch_sisdr_loss = 0.0
        epoch_branch_protect_guard_sisdr_loss = 0.0
        epoch_branch_protect_overlap_base_align_l1 = 0.0
        epoch_branch_protect_teacher_overlap_l1 = 0.0
        epoch_interference_extra_guard_sisdr_loss = 0.0
        epoch_interference_extra_base_align_l1 = 0.0
        epoch_interference_extra_base_delta_projection_ratio = 0.0
        epoch_sisdr_db = 0.0
        epoch_transient = 0.0
        epoch_transient_extra = 0.0
        epoch_interference = 0.0
        epoch_interference_extra = 0.0
        epoch_overlap_interference = 0.0
        epoch_overlap_interference_extra = 0.0
        epoch_overlap_cancel = 0.0
        epoch_overlap_cancel_target_projection = 0.0
        epoch_overlap_cancel_absent_mix = 0.0
        epoch_overlap_dual_mix_consistency = 0.0
        epoch_overlap_dual_residual_target_projection = 0.0
        epoch_overlap_dual_absent_mix = 0.0
        epoch_absent = 0.0
        epoch_absent_extra = 0.0
        epoch_gate_absent = 0.0
        epoch_gate_abstain = 0.0
        epoch_gate_keep = 0.0
        epoch_gate_target = 0.0
        step_count = 0
        epoch_sample_count = 0
        train_selector_totals = {
            prefix: {"active": False, "selected_count": 0, "total_count": 0}
            for prefix in (
                "reconstruction",
                "reconstruction_extra",
                "transient",
                "transient_extra",
                "interference",
                "interference_extra",
                "overlap_interference",
                "overlap_interference_extra",
                "overlap_cancel",
                 "overlap_dual",
                 "absent",
                 "absent_extra",
                 "branch_protect",
                 "branch_protect_teacher",
             )
         }

        for batch in train_loader:
            batch = move_batch_to_device(batch, device)
            batch_size = len(batch["sample_ids"])
            outputs = model(
                mixture=batch["mixture"],
                mixture_lengths=batch["mixture_lengths"],
                reference=batch["reference"],
                reference_lengths=batch["reference_lengths"],
            )
            teacher_prediction = None
            if teacher_model is not None:
                with torch.no_grad():
                    teacher_outputs = teacher_model(
                        mixture=batch["mixture"],
                        mixture_lengths=batch["mixture_lengths"],
                        reference=batch["reference"],
                        reference_lengths=batch["reference_lengths"],
                    )
                teacher_prediction = teacher_outputs["estimated_waveform"]
            reconstruction_sample_weights, reconstruction_extra_sample_weights, reconstruction_union_sample_weights = (
                resolve_selector_sample_weights(
                    batch=batch,
                    device=device,
                    loss_config=loss_config,
                    prefix="reconstruction",
                    extra_weight_keys=("reconstruction_extra_waveform_weight", "reconstruction_extra_stft_weight"),
                )
            )
            transient_sample_weights, transient_extra_sample_weights, transient_union_sample_weights = (
                resolve_selector_sample_weights(
                    batch=batch,
                    device=device,
                    loss_config=loss_config,
                    prefix="transient",
                    extra_weight_keys=("transient_extra_weight",),
                )
            )
            interference_sample_weights, interference_extra_sample_weights, interference_union_sample_weights = (
                resolve_selector_sample_weights(
                    batch=batch,
                    device=device,
                    loss_config=loss_config,
                    prefix="interference",
                    extra_weight_keys=(
                        "interference_extra_weight",
                        "interference_extra_guard_sisdr_weight",
                        "interference_extra_base_align_weight",
                        "interference_extra_base_delta_projection_weight",
                    ),
                )
            )
            overlap_interference_sample_weights, overlap_interference_extra_sample_weights, overlap_interference_union_sample_weights = (
                resolve_selector_sample_weights(
                    batch=batch,
                    device=device,
                    loss_config=loss_config,
                    prefix="overlap_interference",
                    extra_weight_keys=(
                        "overlap_interference_weight",
                        "overlap_interference_extra_weight",
                    ),
                )
            )
            overlap_cancel_sample_weights = build_selector_sample_weights(
                batch=batch,
                device=device,
                loss_config=loss_config,
                prefix="overlap_cancel",
            )
            overlap_dual_sample_weights = build_selector_sample_weights(
                batch=batch,
                device=device,
                loss_config=loss_config,
                prefix="overlap_dual",
            )
            absent_sample_weights, absent_extra_sample_weights, absent_union_sample_weights = (
                resolve_selector_sample_weights(
                    batch=batch,
                    device=device,
                    loss_config=loss_config,
                    prefix="absent",
                    extra_weight_keys=("absent_extra_weight",),
                )
            )
            absent_presence_sample_weights = build_interval_presence_sample_weights(
                batch["target_absent_intervals"],
                device=device,
            )
            branch_protect_sample_weights = build_selector_sample_weights(
                batch=batch,
                device=device,
                loss_config=loss_config,
                prefix="branch_protect",
            )
            branch_protect_teacher_sample_weights = build_selector_sample_weights(
                batch=batch,
                device=device,
                loss_config=loss_config,
                prefix="branch_protect_teacher",
            )
            gate_target_values = build_gate_target_values(batch=batch, device=device, loss_config=loss_config)
            gate_target_sample_weights = (
                torch.ones(len(batch["sample_ids"]), dtype=torch.float32, device=device)
                if gate_target_values is not None
                else None
            )
            gate_supervision_source = str(
                loss_config.get("gate_supervision_source", "branch_decoder_frame_gate")
            )
            gate_values = outputs.get("branch_decoder_frame_gate")
            gate_absent_values = None
            gate_abstain_values = None
            gate_keep_values = None
            gate_target_source_values = None
            gate_absent_sample_weights = absent_presence_sample_weights
            gate_abstain_sample_weights = interference_extra_sample_weights
            gate_keep_sample_weights = branch_protect_sample_weights
            gate_target_intervals = None
            gate_absent_intervals = None
            gate_abstain_intervals = None
            gate_keep_intervals = None
            if gate_supervision_source == "overlap_cancel_apply_controller":
                gate_values = outputs.get("branch_overlap_cancel_apply_controller")
                gate_absent_sample_weights = absent_union_sample_weights
                gate_abstain_sample_weights = None
                gate_keep_sample_weights = overlap_cancel_sample_weights
                gate_absent_intervals = batch["target_absent_intervals"]
                gate_keep_intervals = batch["target_overlap_intervals"]
            elif gate_supervision_source == "overlap_cancel_apply_controller_split":
                gate_values = outputs.get("branch_overlap_cancel_apply_controller")
                gate_absent_values = outputs.get("branch_overlap_cancel_apply_absent_controller")
                gate_keep_values = outputs.get("branch_overlap_cancel_apply_keep_controller")
                gate_target_source_values = gate_values
                gate_absent_sample_weights = absent_union_sample_weights
                gate_abstain_sample_weights = None
                gate_keep_sample_weights = overlap_cancel_sample_weights
                gate_absent_intervals = batch["target_absent_intervals"]
                gate_keep_intervals = batch["target_overlap_intervals"]
            for prefix, weights in (
                ("reconstruction", reconstruction_union_sample_weights),
                ("reconstruction_extra", reconstruction_extra_sample_weights),
                ("transient", transient_union_sample_weights),
                ("transient_extra", transient_extra_sample_weights),
                ("interference", interference_union_sample_weights),
                ("interference_extra", interference_extra_sample_weights),
                ("overlap_interference", overlap_interference_union_sample_weights),
                ("overlap_interference_extra", overlap_interference_extra_sample_weights),
                ("overlap_cancel", overlap_cancel_sample_weights),
                ("overlap_dual", overlap_dual_sample_weights),
                ("absent", absent_union_sample_weights),
                ("absent_extra", absent_extra_sample_weights),
                ("branch_protect", branch_protect_sample_weights),
                ("branch_protect_teacher", branch_protect_teacher_sample_weights),
            ):
                stats = summarize_selector_weights(weights, len(batch["sample_ids"]))
                train_selector_totals[prefix]["active"] = train_selector_totals[prefix]["active"] or bool(stats["active"])
                train_selector_totals[prefix]["selected_count"] += int(stats["selected_count"])
                train_selector_totals[prefix]["total_count"] += int(stats["total_count"])
            losses = compute_losses(
                prediction=resolve_primary_prediction(
                    outputs,
                    use_branch_prerefine_as_primary_prediction=bool(
                        loss_config.get("use_branch_prerefine_as_primary_prediction", False)
                    ),
                ),
                reconstruction_extra_prediction=outputs["estimated_waveform"],
                extra_prediction=resolve_branch_extra_prediction(outputs),
                teacher_prediction=teacher_prediction,
                overlap_cancel_prediction=outputs.get("branch_overlap_cancel_estimate_waveform"),
                overlap_dual_target_prediction=outputs.get("branch_overlap_dual_target_waveform"),
                overlap_dual_residual_prediction=outputs.get("branch_overlap_dual_residual_waveform"),
                mixture=batch["mixture"],
                target=batch["target"],
                lengths=batch["target_lengths"],
                absent_intervals=batch["target_absent_intervals"],
                overlap_intervals=batch["target_overlap_intervals"],
                model=model,
                gate_values=gate_values,
                gate_absent_values=gate_absent_values,
                gate_abstain_values=gate_abstain_values,
                gate_keep_values=gate_keep_values,
                gate_target_source_values=gate_target_source_values,
                reconstruction_sample_weights=reconstruction_sample_weights,
                reconstruction_extra_sample_weights=reconstruction_extra_sample_weights,
                transient_sample_weights=transient_sample_weights,
                transient_extra_sample_weights=transient_extra_sample_weights,
                interference_sample_weights=interference_sample_weights,
                interference_extra_sample_weights=interference_extra_sample_weights,
                overlap_interference_sample_weights=overlap_interference_sample_weights,
                overlap_interference_extra_sample_weights=overlap_interference_extra_sample_weights,
                overlap_cancel_sample_weights=overlap_cancel_sample_weights,
                overlap_cancel_absent_mix_sample_weights=absent_union_sample_weights,
                overlap_dual_sample_weights=overlap_dual_sample_weights,
                branch_protect_sample_weights=branch_protect_sample_weights,
                branch_protect_teacher_sample_weights=branch_protect_teacher_sample_weights,
                absent_sample_weights=absent_sample_weights,
                absent_extra_sample_weights=absent_extra_sample_weights,
                gate_absent_sample_weights=gate_absent_sample_weights,
                gate_abstain_sample_weights=gate_abstain_sample_weights,
                gate_keep_sample_weights=gate_keep_sample_weights,
                gate_target_sample_weights=gate_target_sample_weights,
                gate_target_values=gate_target_values,
                gate_absent_intervals=gate_absent_intervals,
                gate_abstain_intervals=gate_abstain_intervals,
                gate_keep_intervals=gate_keep_intervals,
                gate_target_intervals=gate_target_intervals,
                **compute_loss_kwargs,
            )

            optimizer.zero_grad(set_to_none=True)
            if losses.total.requires_grad:
                losses.total.backward()
                torch.nn.utils.clip_grad_norm_(trainable_parameters, max_norm=5.0)
                optimizer.step()

            global_step += 1
            step_count += 1
            epoch_loss += float(losses.total.item()) * batch_size
            epoch_wave += float(losses.waveform_l1.item()) * batch_size
            epoch_stft += float(losses.stft_l1.item()) * batch_size
            epoch_reconstruction_wave += float(losses.reconstruction_waveform_l1.item()) * batch_size
            epoch_reconstruction_stft += float(losses.reconstruction_stft_l1.item()) * batch_size
            epoch_reconstruction_extra_wave += float(losses.reconstruction_extra_waveform_l1.item()) * batch_size
            epoch_reconstruction_extra_stft += float(losses.reconstruction_extra_stft_l1.item()) * batch_size
            epoch_sisdr_loss += float(losses.sisdr_loss.item()) * batch_size
            epoch_branch_protect_guard_sisdr_loss += (
                float(losses.branch_protect_guard_sisdr_loss.item()) * batch_size
            )
            epoch_branch_protect_overlap_base_align_l1 += float(
                losses.branch_protect_overlap_base_align_l1.item()
            ) * batch_size
            epoch_branch_protect_teacher_overlap_l1 += float(
                losses.branch_protect_teacher_overlap_l1.item()
            ) * batch_size
            epoch_interference_extra_guard_sisdr_loss += (
                float(losses.interference_extra_guard_sisdr_loss.item()) * batch_size
            )
            epoch_interference_extra_base_align_l1 += (
                float(losses.interference_extra_base_align_l1.item()) * batch_size
            )
            epoch_interference_extra_base_delta_projection_ratio += float(
                losses.interference_extra_base_delta_projection_ratio.item()
            ) * batch_size
            epoch_sisdr_db += float(losses.sisdr_db.item()) * batch_size
            epoch_transient += float(losses.transient_presence_l1.item()) * batch_size
            epoch_transient_extra += float(losses.transient_extra_presence_l1.item()) * batch_size
            epoch_interference += float(losses.interference_projection_ratio.item()) * batch_size
            epoch_interference_extra += float(losses.interference_extra_projection_ratio.item()) * batch_size
            epoch_overlap_interference += float(losses.overlap_interference_projection_ratio.item()) * batch_size
            epoch_overlap_interference_extra += float(
                losses.overlap_interference_extra_projection_ratio.item()
            ) * batch_size
            epoch_overlap_cancel += float(losses.overlap_cancel_waveform_l1.item()) * batch_size
            epoch_overlap_cancel_target_projection += float(
                losses.overlap_cancel_target_projection_ratio.item()
            ) * batch_size
            epoch_overlap_cancel_absent_mix += float(
                losses.overlap_cancel_absent_mix_l1.item()
            ) * batch_size
            epoch_overlap_dual_mix_consistency += (
                float(losses.overlap_dual_mix_consistency_l1.item()) * batch_size
            )
            epoch_overlap_dual_residual_target_projection += float(
                losses.overlap_dual_residual_target_projection_ratio.item()
            ) * batch_size
            epoch_overlap_dual_absent_mix += float(
                losses.overlap_dual_absent_mix_l1.item()
            ) * batch_size
            epoch_absent += float(losses.absent_interval_l1.item()) * batch_size
            epoch_absent_extra += float(losses.absent_extra_interval_l1.item()) * batch_size
            epoch_gate_absent += float(losses.gate_absent_mean.item()) * batch_size
            epoch_gate_abstain += float(losses.gate_abstain_mean.item()) * batch_size
            epoch_gate_keep += float(losses.gate_keep_mean.item()) * batch_size
            epoch_gate_target += float(losses.gate_target_l1.item()) * batch_size
            epoch_sample_count += batch_size

            if global_step % args.log_every == 0:
                print(
                    json.dumps(
                        {
                            "epoch": epoch,
                            "step": global_step,
                            "train_loss": round(float(losses.total.item()), 6),
                            "waveform_l1": round(float(losses.waveform_l1.item()), 6),
                            "stft_l1": round(float(losses.stft_l1.item()), 6),
                            "reconstruction_waveform_l1": round(
                                float(losses.reconstruction_waveform_l1.item()), 6
                            ),
                            "reconstruction_stft_l1": round(float(losses.reconstruction_stft_l1.item()), 6),
                            "reconstruction_extra_waveform_l1": round(
                                float(losses.reconstruction_extra_waveform_l1.item()), 6
                            ),
                            "reconstruction_extra_stft_l1": round(
                                float(losses.reconstruction_extra_stft_l1.item()), 6
                            ),
                            "sisdr_loss": round(float(losses.sisdr_loss.item()), 6),
                            "branch_protect_guard_sisdr_loss": round(
                                float(losses.branch_protect_guard_sisdr_loss.item()), 6
                            ),
                            "branch_protect_overlap_base_align_l1": round(
                                float(losses.branch_protect_overlap_base_align_l1.item()), 6
                            ),
                            "branch_protect_teacher_overlap_l1": round(
                                float(losses.branch_protect_teacher_overlap_l1.item()), 6
                            ),
                            "interference_extra_guard_sisdr_loss": round(
                                float(losses.interference_extra_guard_sisdr_loss.item()), 6
                            ),
                            "interference_extra_base_align_l1": round(
                                float(losses.interference_extra_base_align_l1.item()), 6
                            ),
                            "interference_extra_base_delta_projection_ratio": round(
                                float(losses.interference_extra_base_delta_projection_ratio.item()), 6
                            ),
                            "sisdr_db": round(float(losses.sisdr_db.item()), 6),
                            "transient_presence_l1": round(float(losses.transient_presence_l1.item()), 6),
                            "transient_extra_presence_l1": round(
                                float(losses.transient_extra_presence_l1.item()), 6
                            ),
                            "interference_projection_ratio": round(
                                float(losses.interference_projection_ratio.item()), 6
                            ),
                            "interference_extra_projection_ratio": round(
                                float(losses.interference_extra_projection_ratio.item()), 6
                            ),
                            "overlap_interference_projection_ratio": round(
                                float(losses.overlap_interference_projection_ratio.item()), 6
                            ),
                            "overlap_interference_extra_projection_ratio": round(
                                float(losses.overlap_interference_extra_projection_ratio.item()), 6
                            ),
                            "overlap_cancel_waveform_l1": round(
                                float(losses.overlap_cancel_waveform_l1.item()), 6
                            ),
                            "overlap_cancel_target_projection_ratio": round(
                                float(losses.overlap_cancel_target_projection_ratio.item()), 6
                            ),
                            "overlap_cancel_absent_mix_l1": round(
                                float(losses.overlap_cancel_absent_mix_l1.item()), 6
                            ),
                            "overlap_dual_mix_consistency_l1": round(
                                float(losses.overlap_dual_mix_consistency_l1.item()), 6
                            ),
                            "overlap_dual_residual_target_projection_ratio": round(
                                float(losses.overlap_dual_residual_target_projection_ratio.item()), 6
                            ),
                            "overlap_dual_absent_mix_l1": round(
                                float(losses.overlap_dual_absent_mix_l1.item()), 6
                            ),
                            "absent_interval_l1": round(float(losses.absent_interval_l1.item()), 6),
                            "absent_extra_interval_l1": round(
                                float(losses.absent_extra_interval_l1.item()), 6
                            ),
                            "gate_absent_mean": round(float(losses.gate_absent_mean.item()), 6),
                            "gate_abstain_mean": round(float(losses.gate_abstain_mean.item()), 6),
                            "gate_keep_mean": round(float(losses.gate_keep_mean.item()), 6),
                            "gate_target_l1": round(float(losses.gate_target_l1.item()), 6),
                        },
                        ensure_ascii=False,
                    )
                )

            if args.max_steps > 0 and global_step >= args.max_steps:
                break

        train_metrics = {
            "loss": epoch_loss / max(1, epoch_sample_count),
            "waveform_l1": epoch_wave / max(1, epoch_sample_count),
            "stft_l1": epoch_stft / max(1, epoch_sample_count),
            "reconstruction_waveform_l1": epoch_reconstruction_wave / max(1, epoch_sample_count),
            "reconstruction_stft_l1": epoch_reconstruction_stft / max(1, epoch_sample_count),
            "reconstruction_extra_waveform_l1": epoch_reconstruction_extra_wave / max(1, epoch_sample_count),
            "reconstruction_extra_stft_l1": epoch_reconstruction_extra_stft / max(1, epoch_sample_count),
            "sisdr_loss": epoch_sisdr_loss / max(1, epoch_sample_count),
            "branch_protect_guard_sisdr_loss": epoch_branch_protect_guard_sisdr_loss / max(1, epoch_sample_count),
            "branch_protect_overlap_base_align_l1": (
                epoch_branch_protect_overlap_base_align_l1 / max(1, epoch_sample_count)
            ),
            "branch_protect_teacher_overlap_l1": (
                epoch_branch_protect_teacher_overlap_l1 / max(1, epoch_sample_count)
            ),
            "interference_extra_guard_sisdr_loss": epoch_interference_extra_guard_sisdr_loss / max(1, epoch_sample_count),
            "interference_extra_base_align_l1": epoch_interference_extra_base_align_l1 / max(1, epoch_sample_count),
            "interference_extra_base_delta_projection_ratio": (
                epoch_interference_extra_base_delta_projection_ratio / max(1, epoch_sample_count)
            ),
            "sisdr_db": epoch_sisdr_db / max(1, epoch_sample_count),
            "transient_presence_l1": epoch_transient / max(1, epoch_sample_count),
            "transient_extra_presence_l1": epoch_transient_extra / max(1, epoch_sample_count),
            "interference_projection_ratio": epoch_interference / max(1, epoch_sample_count),
            "interference_extra_projection_ratio": epoch_interference_extra / max(1, epoch_sample_count),
            "overlap_interference_projection_ratio": epoch_overlap_interference / max(1, epoch_sample_count),
            "overlap_interference_extra_projection_ratio": (
                epoch_overlap_interference_extra / max(1, epoch_sample_count)
            ),
            "overlap_cancel_waveform_l1": epoch_overlap_cancel / max(1, epoch_sample_count),
            "overlap_cancel_target_projection_ratio": (
                epoch_overlap_cancel_target_projection / max(1, epoch_sample_count)
            ),
            "overlap_cancel_absent_mix_l1": (
                epoch_overlap_cancel_absent_mix / max(1, epoch_sample_count)
            ),
            "overlap_dual_mix_consistency_l1": (
                epoch_overlap_dual_mix_consistency / max(1, epoch_sample_count)
            ),
            "overlap_dual_residual_target_projection_ratio": (
                epoch_overlap_dual_residual_target_projection / max(1, epoch_sample_count)
            ),
            "overlap_dual_absent_mix_l1": (
                epoch_overlap_dual_absent_mix / max(1, epoch_sample_count)
            ),
            "absent_interval_l1": epoch_absent / max(1, epoch_sample_count),
            "absent_extra_interval_l1": epoch_absent_extra / max(1, epoch_sample_count),
            "gate_absent_mean": epoch_gate_absent / max(1, epoch_sample_count),
            "gate_abstain_mean": epoch_gate_abstain / max(1, epoch_sample_count),
            "gate_keep_mean": epoch_gate_keep / max(1, epoch_sample_count),
            "gate_target_l1": epoch_gate_target / max(1, epoch_sample_count),
        }
        train_selector_metrics = {
            prefix: {
                "active": bool(totals["active"]),
                "selected_count": int(totals["selected_count"]),
                "total_count": int(totals["total_count"]),
                "selected_fraction": (
                    float(totals["selected_count"]) / float(totals["total_count"])
                    if int(totals["total_count"]) > 0
                    else None
                ),
            }
            for prefix, totals in train_selector_totals.items()
        }
        val_metrics, val_selector_metrics = evaluate(
            model,
            val_loader,
            device,
            loss_config=loss_config,
            teacher_model=teacher_model,
        )
        history.append(
            {
                "epoch": epoch,
                "global_step": global_step,
                "train_loss": train_metrics["loss"],
                "train_waveform_l1": train_metrics["waveform_l1"],
                "train_stft_l1": train_metrics["stft_l1"],
                "train_reconstruction_waveform_l1": train_metrics["reconstruction_waveform_l1"],
                "train_reconstruction_stft_l1": train_metrics["reconstruction_stft_l1"],
                "train_reconstruction_extra_waveform_l1": train_metrics["reconstruction_extra_waveform_l1"],
                "train_reconstruction_extra_stft_l1": train_metrics["reconstruction_extra_stft_l1"],
                "train_sisdr_loss": train_metrics["sisdr_loss"],
                "train_branch_protect_guard_sisdr_loss": train_metrics["branch_protect_guard_sisdr_loss"],
                "train_branch_protect_overlap_base_align_l1": (
                    train_metrics["branch_protect_overlap_base_align_l1"]
                ),
                "train_branch_protect_teacher_overlap_l1": (
                    train_metrics["branch_protect_teacher_overlap_l1"]
                ),
                "train_interference_extra_guard_sisdr_loss": train_metrics["interference_extra_guard_sisdr_loss"],
                "train_interference_extra_base_align_l1": train_metrics["interference_extra_base_align_l1"],
                "train_interference_extra_base_delta_projection_ratio": (
                    train_metrics["interference_extra_base_delta_projection_ratio"]
                ),
                "train_sisdr_db": train_metrics["sisdr_db"],
                "train_transient_presence_l1": train_metrics["transient_presence_l1"],
                "train_transient_extra_presence_l1": train_metrics["transient_extra_presence_l1"],
                "train_interference_projection_ratio": train_metrics["interference_projection_ratio"],
                "train_interference_extra_projection_ratio": train_metrics["interference_extra_projection_ratio"],
                "train_overlap_interference_projection_ratio": (
                    train_metrics["overlap_interference_projection_ratio"]
                ),
                "train_overlap_interference_extra_projection_ratio": (
                    train_metrics["overlap_interference_extra_projection_ratio"]
                ),
                "train_overlap_cancel_waveform_l1": train_metrics["overlap_cancel_waveform_l1"],
                "train_overlap_cancel_target_projection_ratio": (
                    train_metrics["overlap_cancel_target_projection_ratio"]
                ),
                "train_overlap_cancel_absent_mix_l1": (
                    train_metrics["overlap_cancel_absent_mix_l1"]
                ),
                "train_overlap_dual_mix_consistency_l1": (
                    train_metrics["overlap_dual_mix_consistency_l1"]
                ),
                "train_overlap_dual_residual_target_projection_ratio": (
                    train_metrics["overlap_dual_residual_target_projection_ratio"]
                ),
                "train_overlap_dual_absent_mix_l1": (
                    train_metrics["overlap_dual_absent_mix_l1"]
                ),
                "train_absent_interval_l1": train_metrics["absent_interval_l1"],
                "train_absent_extra_interval_l1": train_metrics["absent_extra_interval_l1"],
                "train_gate_absent_mean": train_metrics["gate_absent_mean"],
                "train_gate_abstain_mean": train_metrics["gate_abstain_mean"],
                "train_gate_keep_mean": train_metrics["gate_keep_mean"],
                "train_gate_target_l1": train_metrics["gate_target_l1"],
                "train_selector_metrics": train_selector_metrics,
                "val_loss": val_metrics["loss"],
                "val_waveform_l1": val_metrics["waveform_l1"],
                "val_stft_l1": val_metrics["stft_l1"],
                "val_reconstruction_waveform_l1": val_metrics["reconstruction_waveform_l1"],
                "val_reconstruction_stft_l1": val_metrics["reconstruction_stft_l1"],
                "val_reconstruction_extra_waveform_l1": val_metrics["reconstruction_extra_waveform_l1"],
                "val_reconstruction_extra_stft_l1": val_metrics["reconstruction_extra_stft_l1"],
                "val_sisdr_loss": val_metrics["sisdr_loss"],
                "val_branch_protect_guard_sisdr_loss": val_metrics["branch_protect_guard_sisdr_loss"],
                "val_branch_protect_overlap_base_align_l1": (
                    val_metrics["branch_protect_overlap_base_align_l1"]
                ),
                "val_branch_protect_teacher_overlap_l1": (
                    val_metrics["branch_protect_teacher_overlap_l1"]
                ),
                "val_interference_extra_guard_sisdr_loss": val_metrics["interference_extra_guard_sisdr_loss"],
                "val_interference_extra_base_align_l1": val_metrics["interference_extra_base_align_l1"],
                "val_interference_extra_base_delta_projection_ratio": (
                    val_metrics["interference_extra_base_delta_projection_ratio"]
                ),
                "val_sisdr_db": val_metrics["sisdr_db"],
                "val_transient_presence_l1": val_metrics["transient_presence_l1"],
                "val_transient_extra_presence_l1": val_metrics["transient_extra_presence_l1"],
                "val_interference_projection_ratio": val_metrics["interference_projection_ratio"],
                "val_interference_extra_projection_ratio": val_metrics["interference_extra_projection_ratio"],
                "val_overlap_interference_projection_ratio": (
                    val_metrics["overlap_interference_projection_ratio"]
                ),
                "val_overlap_interference_extra_projection_ratio": (
                    val_metrics["overlap_interference_extra_projection_ratio"]
                ),
                "val_overlap_cancel_waveform_l1": val_metrics["overlap_cancel_waveform_l1"],
                "val_overlap_cancel_target_projection_ratio": (
                    val_metrics["overlap_cancel_target_projection_ratio"]
                ),
                "val_overlap_cancel_absent_mix_l1": (
                    val_metrics["overlap_cancel_absent_mix_l1"]
                ),
                "val_overlap_dual_mix_consistency_l1": (
                    val_metrics["overlap_dual_mix_consistency_l1"]
                ),
                "val_overlap_dual_residual_target_projection_ratio": (
                    val_metrics["overlap_dual_residual_target_projection_ratio"]
                ),
                "val_overlap_dual_absent_mix_l1": (
                    val_metrics["overlap_dual_absent_mix_l1"]
                ),
                "val_absent_interval_l1": val_metrics["absent_interval_l1"],
                "val_absent_extra_interval_l1": val_metrics["absent_extra_interval_l1"],
                "val_gate_absent_mean": val_metrics["gate_absent_mean"],
                "val_gate_abstain_mean": val_metrics["gate_abstain_mean"],
                "val_gate_keep_mean": val_metrics["gate_keep_mean"],
                "val_gate_target_l1": val_metrics["gate_target_l1"],
                "val_selector_metrics": val_selector_metrics,
            }
        )

        print(
            json.dumps(
                {
                    "epoch": epoch,
                    "global_step": global_step,
                    "train": {k: round(v, 6) for k, v in train_metrics.items()},
                    "val": {k: round(v, 6) for k, v in val_metrics.items()},
                    "train_selector_metrics": train_selector_metrics,
                    "val_selector_metrics": val_selector_metrics,
                },
                ensure_ascii=False,
            )
        )

        checkpoint = {
            "epoch": epoch,
            "global_step": global_step,
            "model_config": model_config,
            "loss_config": loss_config,
            "trainable_config": trainable_config,
            "init_checkpoint": init_checkpoint_path,
            "teacher_checkpoint": teacher_checkpoint_path,
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "args": vars(args),
            "history": history,
        }
        torch.save(checkpoint, args.output_dir / "latest.pt")
        if val_metrics["loss"] < best_val_loss:
            best_val_loss = val_metrics["loss"]
            torch.save(checkpoint, args.output_dir / "best.pt")

        if args.max_steps > 0 and global_step >= args.max_steps:
            break

    end_ts = time.time()
    end_dt = datetime.now()
    summary = {
        "train_manifest": serialize_repo_path(args.train_manifest),
        "val_manifest": serialize_repo_path(args.val_manifest),
        "output_dir": serialize_repo_path(args.output_dir),
        "device": device.type,
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "learning_rate": args.lr,
        "model_config": model_config,
        "loss_config": loss_config,
        "trainable_config": trainable_config,
        "init_checkpoint": serialize_repo_path(Path(init_checkpoint_path)) if init_checkpoint_path else None,
        "teacher_checkpoint": (
            serialize_repo_path(Path(teacher_checkpoint_path))
            if teacher_checkpoint_path
            else None
        ),
        "global_steps": global_step,
        "start_time": start_dt.isoformat(timespec="seconds"),
        "end_time": end_dt.isoformat(timespec="seconds"),
        "elapsed_sec": round(end_ts - start_ts, 3),
        "best_val_loss": best_val_loss,
        "selector_metrics": {
            "train": history[-1]["train_selector_metrics"] if history else {},
            "val": history[-1]["val_selector_metrics"] if history else {},
        },
        "history": history,
    }
    (args.output_dir / "train_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"train_end={end_dt.isoformat(timespec='seconds')}")
    print(f"elapsed_sec={summary['elapsed_sec']}")


if __name__ == "__main__":
    main()
