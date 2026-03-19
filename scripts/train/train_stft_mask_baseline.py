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
from torch.utils.data import DataLoader


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from tse_prefix.data import SyntheticTSEDataset, synthetic_collate_fn
from tse_prefix.models import STFTMaskBaseline
from tse_prefix.pipeline import compute_losses
from tse_prefix.pipeline.loss_selectors import (
    build_selector_sample_weights,
    selector_config_keys,
    summarize_selector_weights,
)


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
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--log-every", type=int, default=5)
    parser.add_argument("--max-steps", type=int, default=0)
    parser.add_argument("--seed", type=int, default=20260316)
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
    parser.add_argument("--loss-stft-weight", type=float, default=0.5)
    parser.add_argument("--loss-sisdr-weight", type=float, default=0.0)
    parser.add_argument("--loss-transient-weight", type=float, default=0.0)
    parser.add_argument("--loss-interference-weight", type=float, default=0.0)
    parser.add_argument("--loss-absent-weight", type=float, default=0.0)
    add_selector_args(parser, "transient")
    add_selector_args(parser, "interference")
    add_selector_args(parser, "absent")
    return parser.parse_args()


def add_selector_args(parser: argparse.ArgumentParser, prefix: str) -> None:
    for branch_name in ("", "extra_"):
        flag_prefix = f"--loss-{prefix}-" if not branch_name else f"--loss-{prefix}-{branch_name.replace('_', '-')}"
        attr_prefix = f"loss_{prefix}_" if not branch_name else f"loss_{prefix}_{branch_name}"
        parser.add_argument(f"{flag_prefix}focus-recipes", nargs="*", default=[])
        parser.add_argument(f"{flag_prefix}focus-patterns", nargs="*", default=[])
        parser.add_argument(f"{flag_prefix}focus-interference-pools", nargs="*", default=[])
        parser.add_argument(f"{flag_prefix}focus-interference-speaker-names", nargs="*", default=[])
        parser.add_argument(f"{flag_prefix}min-target-ratio", type=float, default=None)
        parser.add_argument(f"{flag_prefix}max-target-ratio", type=float, default=None)
        parser.add_argument(f"{flag_prefix}min-overlap-ratio", type=float, default=None)
        parser.add_argument(f"{flag_prefix}max-overlap-ratio", type=float, default=None)
        parser.add_argument(f"{flag_prefix}min-interference-gain-db", type=float, default=None)
        parser.add_argument(f"{flag_prefix}max-interference-gain-db", type=float, default=None)
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
        "target_transient_presence_minus_mid_db_means",
        "target_transient_presence_share_means",
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
    }


def build_loss_config(args: argparse.Namespace) -> dict[str, float]:
    loss_config = {
        "sample_rate": args.sample_rate,
        "stft_weight": args.loss_stft_weight,
        "sisdr_weight": args.loss_sisdr_weight,
        "transient_weight": args.loss_transient_weight,
        "interference_weight": args.loss_interference_weight,
        "absent_weight": args.loss_absent_weight,
        "transient_top_ratio": 0.12,
        "transient_min_count": 8,
        "transient_mid_low_hz": 800.0,
        "transient_mid_high_hz": 3000.0,
        "transient_presence_low_hz": 3000.0,
        "transient_presence_high_hz": 8000.0,
        "transient_ratio_weight": 0.5,
    }
    for prefix in ("transient", "interference", "absent"):
        for branch_name in ("", "extra_"):
            config_prefix = f"{prefix}_" if not branch_name else f"{prefix}_{branch_name}"
            attr_prefix = f"loss_{prefix}_" if not branch_name else f"loss_{prefix}_{branch_name}"
            for suffix in (
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
            ):
                attr_name = f"{attr_prefix}{suffix}"
                loss_config[f"{config_prefix}{suffix}"] = getattr(args, attr_name)
    return loss_config


def build_compute_loss_kwargs(loss_config: dict) -> dict:
    return {
        key: value
        for key, value in loss_config.items()
        if key not in selector_config_keys()
    }


def load_checkpoint(path: Path, device: torch.device) -> dict:
    return torch.load(path, map_location=device, weights_only=False)


def serialize_repo_path(path: Path | None) -> str | None:
    if path is None:
        return None
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def evaluate(
    model: STFTMaskBaseline,
    dataloader: DataLoader,
    device: torch.device,
    loss_config: dict[str, float],
) -> tuple[dict[str, float], dict[str, dict[str, float | int | bool | None]]]:
    model.eval()
    total_loss = 0.0
    total_wave = 0.0
    total_stft = 0.0
    total_sisdr_loss = 0.0
    total_sisdr_db = 0.0
    total_transient = 0.0
    total_interference = 0.0
    total_absent = 0.0
    batch_count = 0
    compute_loss_kwargs = build_compute_loss_kwargs(loss_config)
    selector_totals = {
        prefix: {"active": False, "selected_count": 0, "total_count": 0}
        for prefix in ("transient", "interference", "absent")
    }
    with torch.no_grad():
        for batch in dataloader:
            batch = move_batch_to_device(batch, device)
            outputs = model(
                mixture=batch["mixture"],
                mixture_lengths=batch["mixture_lengths"],
                reference=batch["reference"],
                reference_lengths=batch["reference_lengths"],
            )
            transient_sample_weights = build_selector_sample_weights(
                batch=batch,
                device=device,
                loss_config=loss_config,
                prefix="transient",
            )
            interference_sample_weights = build_selector_sample_weights(
                batch=batch,
                device=device,
                loss_config=loss_config,
                prefix="interference",
            )
            absent_sample_weights = build_selector_sample_weights(
                batch=batch,
                device=device,
                loss_config=loss_config,
                prefix="absent",
            )
            for prefix, weights in (
                ("transient", transient_sample_weights),
                ("interference", interference_sample_weights),
                ("absent", absent_sample_weights),
            ):
                stats = summarize_selector_weights(weights, len(batch["sample_ids"]))
                selector_totals[prefix]["active"] = selector_totals[prefix]["active"] or bool(stats["active"])
                selector_totals[prefix]["selected_count"] += int(stats["selected_count"])
                selector_totals[prefix]["total_count"] += int(stats["total_count"])
            losses = compute_losses(
                prediction=outputs["estimated_waveform"],
                mixture=batch["mixture"],
                target=batch["target"],
                lengths=batch["target_lengths"],
                absent_intervals=batch["target_absent_intervals"],
                model=model,
                transient_sample_weights=transient_sample_weights,
                interference_sample_weights=interference_sample_weights,
                absent_sample_weights=absent_sample_weights,
                **compute_loss_kwargs,
            )
            total_loss += float(losses.total.item())
            total_wave += float(losses.waveform_l1.item())
            total_stft += float(losses.stft_l1.item())
            total_sisdr_loss += float(losses.sisdr_loss.item())
            total_sisdr_db += float(losses.sisdr_db.item())
            total_transient += float(losses.transient_presence_l1.item())
            total_interference += float(losses.interference_projection_ratio.item())
            total_absent += float(losses.absent_interval_l1.item())
            batch_count += 1
    if batch_count == 0:
        metrics = {
            "loss": 0.0,
            "waveform_l1": 0.0,
            "stft_l1": 0.0,
            "sisdr_loss": 0.0,
            "sisdr_db": 0.0,
            "transient_presence_l1": 0.0,
            "interference_projection_ratio": 0.0,
            "absent_interval_l1": 0.0,
        }
    else:
        metrics = {
            "loss": total_loss / batch_count,
            "waveform_l1": total_wave / batch_count,
            "stft_l1": total_stft / batch_count,
            "sisdr_loss": total_sisdr_loss / batch_count,
            "sisdr_db": total_sisdr_db / batch_count,
            "transient_presence_l1": total_transient / batch_count,
            "interference_projection_ratio": total_interference / batch_count,
            "absent_interval_l1": total_absent / batch_count,
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
    if args.init_checkpoint is not None:
        init_checkpoint = load_checkpoint(args.init_checkpoint, device)
        model.load_state_dict(init_checkpoint["model_state_dict"], strict=True)
        init_checkpoint_path = str(args.init_checkpoint)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)

    history: list[dict[str, float | int]] = []
    global_step = 0
    best_val_loss = float("inf")

    for epoch in range(1, args.epochs + 1):
        model.train()
        epoch_loss = 0.0
        epoch_wave = 0.0
        epoch_stft = 0.0
        epoch_sisdr_loss = 0.0
        epoch_sisdr_db = 0.0
        epoch_transient = 0.0
        epoch_interference = 0.0
        epoch_absent = 0.0
        step_count = 0
        train_selector_totals = {
            prefix: {"active": False, "selected_count": 0, "total_count": 0}
            for prefix in ("transient", "interference", "absent")
        }

        for batch in train_loader:
            batch = move_batch_to_device(batch, device)
            outputs = model(
                mixture=batch["mixture"],
                mixture_lengths=batch["mixture_lengths"],
                reference=batch["reference"],
                reference_lengths=batch["reference_lengths"],
            )
            transient_sample_weights = build_selector_sample_weights(
                batch=batch,
                device=device,
                loss_config=loss_config,
                prefix="transient",
            )
            interference_sample_weights = build_selector_sample_weights(
                batch=batch,
                device=device,
                loss_config=loss_config,
                prefix="interference",
            )
            absent_sample_weights = build_selector_sample_weights(
                batch=batch,
                device=device,
                loss_config=loss_config,
                prefix="absent",
            )
            for prefix, weights in (
                ("transient", transient_sample_weights),
                ("interference", interference_sample_weights),
                ("absent", absent_sample_weights),
            ):
                stats = summarize_selector_weights(weights, len(batch["sample_ids"]))
                train_selector_totals[prefix]["active"] = train_selector_totals[prefix]["active"] or bool(stats["active"])
                train_selector_totals[prefix]["selected_count"] += int(stats["selected_count"])
                train_selector_totals[prefix]["total_count"] += int(stats["total_count"])
            losses = compute_losses(
                prediction=outputs["estimated_waveform"],
                mixture=batch["mixture"],
                target=batch["target"],
                lengths=batch["target_lengths"],
                absent_intervals=batch["target_absent_intervals"],
                model=model,
                transient_sample_weights=transient_sample_weights,
                interference_sample_weights=interference_sample_weights,
                absent_sample_weights=absent_sample_weights,
                **compute_loss_kwargs,
            )

            optimizer.zero_grad(set_to_none=True)
            losses.total.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=5.0)
            optimizer.step()

            global_step += 1
            step_count += 1
            epoch_loss += float(losses.total.item())
            epoch_wave += float(losses.waveform_l1.item())
            epoch_stft += float(losses.stft_l1.item())
            epoch_sisdr_loss += float(losses.sisdr_loss.item())
            epoch_sisdr_db += float(losses.sisdr_db.item())
            epoch_transient += float(losses.transient_presence_l1.item())
            epoch_interference += float(losses.interference_projection_ratio.item())
            epoch_absent += float(losses.absent_interval_l1.item())

            if global_step % args.log_every == 0:
                print(
                    json.dumps(
                        {
                            "epoch": epoch,
                            "step": global_step,
                            "train_loss": round(float(losses.total.item()), 6),
                            "waveform_l1": round(float(losses.waveform_l1.item()), 6),
                            "stft_l1": round(float(losses.stft_l1.item()), 6),
                            "sisdr_loss": round(float(losses.sisdr_loss.item()), 6),
                            "sisdr_db": round(float(losses.sisdr_db.item()), 6),
                            "transient_presence_l1": round(float(losses.transient_presence_l1.item()), 6),
                            "interference_projection_ratio": round(
                                float(losses.interference_projection_ratio.item()), 6
                            ),
                            "absent_interval_l1": round(float(losses.absent_interval_l1.item()), 6),
                        },
                        ensure_ascii=False,
                    )
                )

            if args.max_steps > 0 and global_step >= args.max_steps:
                break

        train_metrics = {
            "loss": epoch_loss / max(1, step_count),
            "waveform_l1": epoch_wave / max(1, step_count),
            "stft_l1": epoch_stft / max(1, step_count),
            "sisdr_loss": epoch_sisdr_loss / max(1, step_count),
            "sisdr_db": epoch_sisdr_db / max(1, step_count),
            "transient_presence_l1": epoch_transient / max(1, step_count),
            "interference_projection_ratio": epoch_interference / max(1, step_count),
            "absent_interval_l1": epoch_absent / max(1, step_count),
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
        val_metrics, val_selector_metrics = evaluate(model, val_loader, device, loss_config=loss_config)
        history.append(
            {
                "epoch": epoch,
                "global_step": global_step,
                "train_loss": train_metrics["loss"],
                "train_waveform_l1": train_metrics["waveform_l1"],
                "train_stft_l1": train_metrics["stft_l1"],
                "train_sisdr_loss": train_metrics["sisdr_loss"],
                "train_sisdr_db": train_metrics["sisdr_db"],
                "train_transient_presence_l1": train_metrics["transient_presence_l1"],
                "train_interference_projection_ratio": train_metrics["interference_projection_ratio"],
                "train_absent_interval_l1": train_metrics["absent_interval_l1"],
                "train_selector_metrics": train_selector_metrics,
                "val_loss": val_metrics["loss"],
                "val_waveform_l1": val_metrics["waveform_l1"],
                "val_stft_l1": val_metrics["stft_l1"],
                "val_sisdr_loss": val_metrics["sisdr_loss"],
                "val_sisdr_db": val_metrics["sisdr_db"],
                "val_transient_presence_l1": val_metrics["transient_presence_l1"],
                "val_interference_projection_ratio": val_metrics["interference_projection_ratio"],
                "val_absent_interval_l1": val_metrics["absent_interval_l1"],
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
            "init_checkpoint": init_checkpoint_path,
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
        "init_checkpoint": serialize_repo_path(Path(init_checkpoint_path)) if init_checkpoint_path else None,
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
