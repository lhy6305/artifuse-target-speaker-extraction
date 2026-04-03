from __future__ import annotations

from dataclasses import dataclass

import torch
import torch.nn.functional as F


@dataclass(frozen=True)
class LossBreakdown:
    total: torch.Tensor
    waveform_l1: torch.Tensor
    stft_l1: torch.Tensor
    reconstruction_waveform_l1: torch.Tensor
    reconstruction_stft_l1: torch.Tensor
    reconstruction_extra_waveform_l1: torch.Tensor
    reconstruction_extra_stft_l1: torch.Tensor
    extra_local_waveform_l1: torch.Tensor
    extra_local_waveform_extra_l1: torch.Tensor
    extra_local_teacher_waveform_extra_l1: torch.Tensor
    artifact_local_split_teacher_waveform_extra_l1: torch.Tensor
    artifact_local_bridge_teacher_waveform_extra_l1: torch.Tensor
    artifact_local_refine_teacher_waveform_extra_l1: torch.Tensor
    artifact_local_mask_adapter_teacher_waveform_extra_l1: torch.Tensor
    extra_local_nonlocal_waveform_l1: torch.Tensor
    pre_present_applied_delta_local_waveform_l1: torch.Tensor
    extra_local_sisdr_loss: torch.Tensor
    sisdr_loss: torch.Tensor
    branch_protect_guard_sisdr_loss: torch.Tensor
    branch_protect_overlap_base_align_l1: torch.Tensor
    branch_protect_teacher_overlap_l1: torch.Tensor
    branch_protect_teacher_overlap_extra_l1: torch.Tensor
    interference_extra_guard_sisdr_loss: torch.Tensor
    interference_extra_base_align_l1: torch.Tensor
    interference_extra_base_delta_projection_ratio: torch.Tensor
    sisdr_db: torch.Tensor
    transient_presence_l1: torch.Tensor
    transient_extra_presence_l1: torch.Tensor
    interference_projection_ratio: torch.Tensor
    interference_extra_projection_ratio: torch.Tensor
    overlap_interference_projection_ratio: torch.Tensor
    overlap_interference_extra_projection_ratio: torch.Tensor
    overlap_cancel_waveform_l1: torch.Tensor
    overlap_cancel_target_projection_ratio: torch.Tensor
    overlap_cancel_absent_mix_l1: torch.Tensor
    overlap_dual_mix_consistency_l1: torch.Tensor
    overlap_dual_residual_waveform_l1: torch.Tensor
    overlap_dual_monitor_waveform_l1: torch.Tensor
    overlap_dual_residual_correction_waveform_l1: torch.Tensor
    overlap_dual_residual_correction_local_waveform_l1: torch.Tensor
    overlap_dual_residual_correction_local_waveform_extra_l1: torch.Tensor
    overlap_dual_residual_correction_local_sisdr_loss: torch.Tensor
    overlap_dual_residual_correction_local_controller_l1: torch.Tensor
    overlap_dual_residual_correction_nonlocal_controller_l1: torch.Tensor
    overlap_dual_residual_correction_local_target_projection_ratio: torch.Tensor
    branch_overlap_dual_local_bridge_nonlocal_waveform_l1: torch.Tensor
    overlap_dual_controller_distill_l1: torch.Tensor
    overlap_dual_residual_target_projection_ratio: torch.Tensor
    overlap_dual_absent_mix_l1: torch.Tensor
    absent_interval_l1: torch.Tensor
    absent_extra_interval_l1: torch.Tensor
    gate_absent_mean: torch.Tensor
    gate_abstain_mean: torch.Tensor
    gate_keep_mean: torch.Tensor
    gate_pre_present_keep_mean: torch.Tensor
    gate_pre_present_abstain_mean: torch.Tensor
    gate_target_l1: torch.Tensor


INTERFERENCE_LOSS_MODES = (
    "prediction_projection_ratio",
    "residual_projection_ratio",
)


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


def weighted_waveform_l1_loss(
    prediction: torch.Tensor,
    target: torch.Tensor,
    lengths: torch.Tensor,
    sample_weights: torch.Tensor | None = None,
) -> torch.Tensor:
    prediction, target, lengths = align_waveforms(prediction, target, lengths)
    sample_losses: list[torch.Tensor] = []

    for pred, tgt, length in zip(prediction, target, lengths):
        length_int = int(length.item())
        if length_int <= 0:
            sample_losses.append(prediction.new_tensor(0.0))
            continue
        sample_losses.append(torch.mean(torch.abs(pred[:length_int] - tgt[:length_int])))

    return average_sample_losses(sample_losses, sample_weights, prediction)


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


def weighted_stft_l1_loss(
    prediction: torch.Tensor,
    target: torch.Tensor,
    lengths: torch.Tensor,
    model,
    sample_weights: torch.Tensor | None = None,
) -> torch.Tensor:
    prediction, target, lengths = align_waveforms(prediction, target, lengths)
    sample_losses: list[torch.Tensor] = []

    for pred, tgt, length in zip(prediction, target, lengths):
        length_int = int(length.item())
        if length_int <= 0:
            sample_losses.append(prediction.new_tensor(0.0))
            continue
        pred_mag = torch.abs(model.stft(pred[:length_int].unsqueeze(0)))
        target_mag = torch.abs(model.stft(tgt[:length_int].unsqueeze(0)))
        sample_losses.append(F.l1_loss(torch.log1p(pred_mag), torch.log1p(target_mag)))

    return average_sample_losses(sample_losses, sample_weights, prediction)


def average_sample_losses(
    sample_losses: list[torch.Tensor],
    sample_weights: torch.Tensor | None,
    reference: torch.Tensor,
) -> torch.Tensor:
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
        return reference.new_tensor(0.0)
    return torch.sum(stacked_losses * weights) / weight_sum


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

    return average_sample_losses(sample_losses, sample_weights, prediction)


def interference_projection_loss(
    prediction: torch.Tensor,
    mixture: torch.Tensor,
    target: torch.Tensor,
    lengths: torch.Tensor,
    sample_weights: torch.Tensor | None = None,
    mode: str = "prediction_projection_ratio",
) -> torch.Tensor:
    if mode not in INTERFERENCE_LOSS_MODES:
        raise ValueError(
            f"Unsupported interference loss mode: {mode}. Expected one of {INTERFERENCE_LOSS_MODES}."
        )

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

        if mode == "prediction_projection_ratio":
            signal = pred
            normalizer = torch.sum(signal * signal).clamp_min(eps)
        else:
            signal = pred - tgt[:length_int]
            normalizer = interference_energy.clamp_min(eps)

        projection_scale = torch.sum(signal * interference) / interference_energy.clamp_min(eps)
        projection = projection_scale * interference
        projection_ratio = torch.sum(projection * projection) / normalizer
        sample_losses.append(projection_ratio)

    return average_sample_losses(sample_losses, sample_weights, prediction)


def base_delta_interference_projection_loss(
    prediction: torch.Tensor,
    reference_prediction: torch.Tensor,
    mixture: torch.Tensor,
    target: torch.Tensor,
    lengths: torch.Tensor,
    sample_weights: torch.Tensor | None = None,
) -> torch.Tensor:
    prediction, reference_prediction, lengths = align_waveforms(prediction, reference_prediction, lengths)
    common_length = min(prediction.shape[-1], mixture.shape[-1], target.shape[-1])
    prediction = prediction[..., :common_length]
    reference_prediction = reference_prediction[..., :common_length]
    target = target[..., :common_length]
    mixture = mixture[..., :common_length]
    lengths = torch.clamp(lengths, max=common_length)

    eps = 1e-8
    sample_losses: list[torch.Tensor] = []
    for pred, ref_pred, mix, tgt, length in zip(prediction, reference_prediction, mixture, target, lengths):
        length_int = int(length.item())
        if length_int <= 0:
            sample_losses.append(prediction.new_tensor(0.0))
            continue

        delta = pred[:length_int] - ref_pred[:length_int]
        interference = mix[:length_int] - tgt[:length_int]
        interference_energy = torch.sum(interference * interference)
        if float(interference_energy.item()) <= eps:
            sample_losses.append(prediction.new_tensor(0.0))
            continue

        projection_scale = torch.sum(delta * interference) / interference_energy.clamp_min(eps)
        projection = projection_scale * interference
        projection_ratio = torch.sum(projection * projection) / interference_energy.clamp_min(eps)
        sample_losses.append(projection_ratio)

    return average_sample_losses(sample_losses, sample_weights, prediction)


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

    return average_sample_losses(sample_losses, sample_weights, prediction)


def interval_waveform_l1_loss(
    prediction: torch.Tensor,
    target: torch.Tensor,
    lengths: torch.Tensor,
    intervals_batch: list[list[dict[str, float]]],
    sample_rate: int = 16000,
    sample_weights: torch.Tensor | None = None,
) -> torch.Tensor:
    prediction, target, lengths = align_waveforms(prediction, target, lengths)
    sample_losses: list[torch.Tensor] = []

    for pred, tgt, length, intervals in zip(prediction, target, lengths, intervals_batch):
        length_int = int(length.item())
        if length_int <= 0 or not intervals:
            sample_losses.append(prediction.new_tensor(0.0))
            continue

        pred = pred[:length_int]
        tgt = tgt[:length_int]

        interval_losses: list[torch.Tensor] = []
        total_interval_samples = 0
        for interval in intervals:
            start_index = int(round(float(interval["start_sec"]) * sample_rate))
            end_index = int(round(float(interval["end_sec"]) * sample_rate))
            start_index = max(0, min(start_index, length_int))
            end_index = max(start_index, min(end_index, length_int))
            if end_index <= start_index:
                continue
            interval_losses.append(torch.abs(pred[start_index:end_index] - tgt[start_index:end_index]).sum())
            total_interval_samples += end_index - start_index

        if total_interval_samples <= 0:
            sample_losses.append(prediction.new_tensor(0.0))
            continue

        sample_losses.append(torch.stack(interval_losses).sum() / float(total_interval_samples))

    return average_sample_losses(sample_losses, sample_weights, prediction)


def interval_sisdr_loss(
    prediction: torch.Tensor,
    target: torch.Tensor,
    lengths: torch.Tensor,
    intervals_batch: list[list[dict[str, float]]],
    sample_rate: int = 16000,
    sample_weights: torch.Tensor | None = None,
    zero_mean: bool = True,
) -> torch.Tensor:
    prediction, target, lengths = align_waveforms(prediction, target, lengths)
    eps = 1e-8
    sample_losses: list[torch.Tensor] = []

    for pred, tgt, length, intervals in zip(prediction, target, lengths, intervals_batch):
        length_int = int(length.item())
        if length_int <= 0 or not intervals:
            sample_losses.append(prediction.new_tensor(0.0))
            continue

        pred = pred[:length_int]
        tgt = tgt[:length_int]
        pred_slices: list[torch.Tensor] = []
        tgt_slices: list[torch.Tensor] = []
        for interval in intervals:
            start_index = int(round(float(interval["start_sec"]) * sample_rate))
            end_index = int(round(float(interval["end_sec"]) * sample_rate))
            start_index = max(0, min(start_index, length_int))
            end_index = max(start_index, min(end_index, length_int))
            if end_index <= start_index:
                continue
            pred_slices.append(pred[start_index:end_index])
            tgt_slices.append(tgt[start_index:end_index])

        if not pred_slices:
            sample_losses.append(prediction.new_tensor(0.0))
            continue

        pred_interval = torch.cat(pred_slices, dim=0)
        tgt_interval = torch.cat(tgt_slices, dim=0)
        if pred_interval.numel() <= 1 or tgt_interval.numel() <= 1:
            sample_losses.append(prediction.new_tensor(0.0))
            continue
        if zero_mean:
            pred_interval = pred_interval - pred_interval.mean()
            tgt_interval = tgt_interval - tgt_interval.mean()
        tgt_energy = torch.sum(tgt_interval * tgt_interval).clamp_min(eps)
        proj = torch.sum(pred_interval * tgt_interval) * tgt_interval / tgt_energy
        noise = pred_interval - proj
        ratio = torch.sum(proj * proj).clamp_min(eps) / torch.sum(noise * noise).clamp_min(eps)
        sample_losses.append(-(10.0 * torch.log10(ratio + eps)))

    return average_sample_losses(sample_losses, sample_weights, prediction)


def interval_gate_l1_loss(
    prediction: torch.Tensor | None,
    target: torch.Tensor | None,
    lengths: torch.Tensor,
    intervals_batch: list[list[dict[str, float]]],
    model,
    sample_rate: int = 16000,
    sample_weights: torch.Tensor | None = None,
) -> torch.Tensor:
    if prediction is None or target is None:
        reference = prediction if prediction is not None else (target if target is not None else lengths)
        return reference.new_tensor(0.0)

    if prediction.ndim != 3 or prediction.shape[1] != 1:
        raise ValueError("prediction gate tensor must have shape [batch, 1, frames]")
    if target.ndim != 3 or target.shape[1] != 1:
        raise ValueError("target gate tensor must have shape [batch, 1, frames]")

    max_frames = min(prediction.shape[-1], target.shape[-1])
    prediction = prediction[..., :max_frames]
    target = target[..., :max_frames].detach()
    frame_lengths = model.waveform_lengths_to_frame_lengths(lengths, max_frames=max_frames)
    if frame_lengths is None:
        return prediction.new_tensor(0.0)

    sample_losses: list[torch.Tensor] = []
    for pred_item, tgt_item, frame_length, intervals in zip(
        prediction[:, 0, :],
        target[:, 0, :],
        frame_lengths,
        intervals_batch,
    ):
        valid_frames = int(frame_length.item())
        if valid_frames <= 0 or not intervals:
            sample_losses.append(prediction.new_tensor(0.0))
            continue

        pred_item = pred_item[:valid_frames]
        tgt_item = tgt_item[:valid_frames]
        interval_losses: list[torch.Tensor] = []
        total_interval_frames = 0
        for interval in intervals:
            start_index = int(round(float(interval["start_sec"]) * sample_rate))
            end_index = int(round(float(interval["end_sec"]) * sample_rate))
            start_frame = max(0, min(start_index // model.hop_length, valid_frames))
            end_frame = max(
                start_frame,
                min(((end_index + model.hop_length - 1) // model.hop_length) + 1, valid_frames),
            )
            if end_frame <= start_frame:
                continue
            interval_losses.append(torch.abs(pred_item[start_frame:end_frame] - tgt_item[start_frame:end_frame]).sum())
            total_interval_frames += end_frame - start_frame

        if total_interval_frames <= 0:
            sample_losses.append(prediction.new_tensor(0.0))
            continue

        sample_losses.append(torch.stack(interval_losses).sum() / float(total_interval_frames))

    return average_sample_losses(sample_losses, sample_weights, prediction)


def interval_projection_ratio_loss(
    prediction: torch.Tensor,
    target: torch.Tensor,
    lengths: torch.Tensor,
    intervals_batch: list[list[dict[str, float]]],
    sample_rate: int = 16000,
    sample_weights: torch.Tensor | None = None,
) -> torch.Tensor:
    prediction, target, lengths = align_waveforms(prediction, target, lengths)
    eps = 1e-8
    sample_losses: list[torch.Tensor] = []

    for pred, tgt, length, intervals in zip(prediction, target, lengths, intervals_batch):
        length_int = int(length.item())
        if length_int <= 0 or not intervals:
            sample_losses.append(prediction.new_tensor(0.0))
            continue

        pred = pred[:length_int]
        tgt = tgt[:length_int]
        pred_slices: list[torch.Tensor] = []
        tgt_slices: list[torch.Tensor] = []
        for interval in intervals:
            start_index = int(round(float(interval["start_sec"]) * sample_rate))
            end_index = int(round(float(interval["end_sec"]) * sample_rate))
            start_index = max(0, min(start_index, length_int))
            end_index = max(start_index, min(end_index, length_int))
            if end_index <= start_index:
                continue
            pred_slices.append(pred[start_index:end_index])
            tgt_slices.append(tgt[start_index:end_index])

        if not pred_slices:
            sample_losses.append(prediction.new_tensor(0.0))
            continue

        pred_interval = torch.cat(pred_slices, dim=0)
        tgt_interval = torch.cat(tgt_slices, dim=0)
        target_energy = torch.sum(tgt_interval * tgt_interval)
        if float(target_energy.item()) <= eps:
            sample_losses.append(prediction.new_tensor(0.0))
            continue

        projection_scale = torch.sum(pred_interval * tgt_interval) / target_energy.clamp_min(eps)
        projection = projection_scale * tgt_interval
        projection_ratio = torch.sum(projection * projection) / target_energy.clamp_min(eps)
        sample_losses.append(projection_ratio)

    return average_sample_losses(sample_losses, sample_weights, prediction)


def overlap_interval_interference_projection_loss(
    prediction: torch.Tensor,
    mixture: torch.Tensor,
    target: torch.Tensor,
    lengths: torch.Tensor,
    overlap_intervals: list[list[dict[str, float]]],
    sample_rate: int = 16000,
    sample_weights: torch.Tensor | None = None,
    mode: str = "prediction_projection_ratio",
) -> torch.Tensor:
    if mode not in INTERFERENCE_LOSS_MODES:
        raise ValueError(
            f"Unsupported interference loss mode: {mode}. Expected one of {INTERFERENCE_LOSS_MODES}."
        )

    prediction, target, lengths = align_waveforms(prediction, target, lengths)
    common_length = min(prediction.shape[-1], mixture.shape[-1])
    prediction = prediction[..., :common_length]
    target = target[..., :common_length]
    lengths = torch.clamp(lengths, max=common_length)
    mixture = mixture[..., :common_length]

    eps = 1e-8
    sample_losses: list[torch.Tensor] = []
    for pred, mix, tgt, length, intervals in zip(prediction, mixture, target, lengths, overlap_intervals):
        length_int = int(length.item())
        if length_int <= 0 or not intervals:
            sample_losses.append(prediction.new_tensor(0.0))
            continue

        pred = pred[:length_int]
        mix = mix[:length_int]
        tgt = tgt[:length_int]

        pred_slices: list[torch.Tensor] = []
        tgt_slices: list[torch.Tensor] = []
        mix_slices: list[torch.Tensor] = []
        for interval in intervals:
            start_index = int(round(float(interval["start_sec"]) * sample_rate))
            end_index = int(round(float(interval["end_sec"]) * sample_rate))
            start_index = max(0, min(start_index, length_int))
            end_index = max(start_index, min(end_index, length_int))
            if end_index <= start_index:
                continue
            pred_slices.append(pred[start_index:end_index])
            tgt_slices.append(tgt[start_index:end_index])
            mix_slices.append(mix[start_index:end_index])

        if not pred_slices:
            sample_losses.append(prediction.new_tensor(0.0))
            continue

        pred_overlap = torch.cat(pred_slices, dim=0)
        tgt_overlap = torch.cat(tgt_slices, dim=0)
        mix_overlap = torch.cat(mix_slices, dim=0)
        interference = mix_overlap - tgt_overlap
        interference_energy = torch.sum(interference * interference)
        if float(interference_energy.item()) <= eps:
            sample_losses.append(prediction.new_tensor(0.0))
            continue

        if mode == "prediction_projection_ratio":
            signal = pred_overlap
            normalizer = torch.sum(signal * signal).clamp_min(eps)
        else:
            signal = pred_overlap - tgt_overlap
            normalizer = interference_energy.clamp_min(eps)

        projection_scale = torch.sum(signal * interference) / interference_energy.clamp_min(eps)
        projection = projection_scale * interference
        projection_ratio = torch.sum(projection * projection) / normalizer
        sample_losses.append(projection_ratio)

    return average_sample_losses(sample_losses, sample_weights, prediction)


def masked_sisdr(
    prediction: torch.Tensor,
    target: torch.Tensor,
    lengths: torch.Tensor,
    zero_mean: bool = False,
) -> torch.Tensor:
    return masked_sisdr_per_sample(
        prediction=prediction,
        target=target,
        lengths=lengths,
        zero_mean=zero_mean,
    ).mean()


def masked_sisdr_per_sample(
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
    return torch.stack(values)


def weighted_sisdr_loss(
    prediction: torch.Tensor,
    target: torch.Tensor,
    lengths: torch.Tensor,
    sample_weights: torch.Tensor | None = None,
    zero_mean: bool = True,
) -> torch.Tensor:
    sisdr_values = masked_sisdr_per_sample(
        prediction=prediction,
        target=target,
        lengths=lengths,
        zero_mean=zero_mean,
    )
    sisdr_losses = -sisdr_values
    return average_sample_losses(list(sisdr_losses), sample_weights, prediction)


def weighted_gate_target_loss(
    gate_values: torch.Tensor | None,
    lengths: torch.Tensor,
    model,
    *,
    target_value: float | None = None,
    target_values: torch.Tensor | None = None,
    sample_weights: torch.Tensor | None = None,
    intervals_batch: list[list[dict[str, float]]] | None = None,
    sample_rate: int = 16000,
) -> torch.Tensor:
    if gate_values is None or sample_weights is None:
        reference = gate_values if gate_values is not None else lengths
        return reference.new_tensor(0.0)

    if gate_values.ndim != 3 or gate_values.shape[1] != 1:
        raise ValueError("gate_values must have shape [batch, 1, frames]")
    if target_values is not None:
        if target_values.ndim != 1 or target_values.shape[0] != gate_values.shape[0]:
            raise ValueError("target_values must be a 1-D tensor with one entry per batch item")
        target_values = target_values.to(device=gate_values.device, dtype=gate_values.dtype)
    elif target_value is None:
        raise ValueError("Either target_value or target_values must be provided")

    frame_lengths = model.waveform_lengths_to_frame_lengths(lengths, max_frames=gate_values.shape[-1])
    if frame_lengths is None:
        return gate_values.new_tensor(0.0)

    sample_losses: list[torch.Tensor] = []
    target_scalar = float(target_value) if target_value is not None else None
    for sample_index, (gate_item, frame_length) in enumerate(zip(gate_values[:, 0, :], frame_lengths)):
        valid_frames = int(frame_length.item())
        if valid_frames <= 0:
            sample_losses.append(gate_values.new_tensor(0.0))
            continue
        valid_gate = gate_item[:valid_frames]
        if intervals_batch is not None:
            intervals = intervals_batch[sample_index]
            interval_losses: list[torch.Tensor] = []
            for interval in intervals:
                start_index = int(round(float(interval["start_sec"]) * sample_rate))
                end_index = int(round(float(interval["end_sec"]) * sample_rate))
                start_frame = max(0, min(start_index // model.hop_length, valid_frames))
                end_frame = max(
                    start_frame,
                    min(((end_index + model.hop_length - 1) // model.hop_length) + 1, valid_frames),
                )
                if end_frame <= start_frame:
                    continue
                gate_interval = valid_gate[start_frame:end_frame]
                if target_values is not None:
                    target_interval = torch.full_like(
                        gate_interval,
                        fill_value=float(target_values[sample_index].item()),
                    )
                else:
                    target_interval = torch.full_like(gate_interval, fill_value=target_scalar)
                interval_losses.append(F.l1_loss(gate_interval, target_interval))
            if interval_losses:
                sample_losses.append(torch.stack(interval_losses).mean())
            else:
                sample_losses.append(gate_values.new_tensor(0.0))
            continue
        if target_values is not None:
            target = torch.full_like(valid_gate, fill_value=float(target_values[sample_index].item()))
        else:
            target = torch.full_like(valid_gate, fill_value=target_scalar)
        sample_losses.append(F.l1_loss(valid_gate, target))

    return average_sample_losses(sample_losses, sample_weights, gate_values)


def build_complement_intervals(
    intervals_batch: list[list[dict[str, float]]],
    lengths: torch.Tensor,
    sample_rate: int,
) -> list[list[dict[str, float]]]:
    complement_batch: list[list[dict[str, float]]] = []
    for intervals, length in zip(intervals_batch, lengths.detach().cpu().tolist()):
        valid_duration_sec = max(0.0, float(length) / float(sample_rate))
        if valid_duration_sec <= 0.0:
            complement_batch.append([])
            continue

        normalized_intervals: list[tuple[float, float]] = []
        for interval in intervals:
            start_sec = max(0.0, min(valid_duration_sec, float(interval.get("start_sec", 0.0))))
            end_sec = max(start_sec, min(valid_duration_sec, float(interval.get("end_sec", start_sec))))
            if end_sec > start_sec:
                normalized_intervals.append((start_sec, end_sec))
        normalized_intervals.sort()

        merged_intervals: list[tuple[float, float]] = []
        for start_sec, end_sec in normalized_intervals:
            if not merged_intervals or start_sec > merged_intervals[-1][1]:
                merged_intervals.append((start_sec, end_sec))
            else:
                merged_intervals[-1] = (merged_intervals[-1][0], max(merged_intervals[-1][1], end_sec))

        cursor_sec = 0.0
        complement_intervals: list[dict[str, float]] = []
        for start_sec, end_sec in merged_intervals:
            if start_sec > cursor_sec:
                complement_intervals.append({"start_sec": cursor_sec, "end_sec": start_sec})
            cursor_sec = max(cursor_sec, end_sec)
        if cursor_sec < valid_duration_sec:
            complement_intervals.append({"start_sec": cursor_sec, "end_sec": valid_duration_sec})
        complement_batch.append(complement_intervals)

    return complement_batch


def compute_losses(
    prediction: torch.Tensor,
    mixture: torch.Tensor,
    target: torch.Tensor,
    lengths: torch.Tensor,
    absent_intervals: list[list[dict[str, float]]],
    overlap_intervals: list[list[dict[str, float]]],
    local_proxy_intervals: list[list[dict[str, float]]],
    artifact_local_proxy_intervals: list[list[dict[str, float]]],
    model,
    gate_values: torch.Tensor | None = None,
    gate_absent_values: torch.Tensor | None = None,
    gate_abstain_values: torch.Tensor | None = None,
    gate_keep_values: torch.Tensor | None = None,
    gate_pre_present_keep_values: torch.Tensor | None = None,
    gate_pre_present_abstain_values: torch.Tensor | None = None,
    gate_target_source_values: torch.Tensor | None = None,
    overlap_cancel_prediction: torch.Tensor | None = None,
    reconstruction_extra_prediction: torch.Tensor | None = None,
    extra_prediction: torch.Tensor | None = None,
    local_prediction: torch.Tensor | None = None,
    pre_present_base_prediction: torch.Tensor | None = None,
    pre_present_applied_delta_prediction: torch.Tensor | None = None,
    teacher_prediction: torch.Tensor | None = None,
    reconstruction_sample_weights: torch.Tensor | None = None,
    reconstruction_extra_sample_weights: torch.Tensor | None = None,
    transient_sample_weights: torch.Tensor | None = None,
    transient_extra_sample_weights: torch.Tensor | None = None,
    interference_sample_weights: torch.Tensor | None = None,
    interference_extra_sample_weights: torch.Tensor | None = None,
    overlap_interference_sample_weights: torch.Tensor | None = None,
    overlap_interference_extra_sample_weights: torch.Tensor | None = None,
    overlap_cancel_sample_weights: torch.Tensor | None = None,
    overlap_cancel_absent_mix_sample_weights: torch.Tensor | None = None,
    overlap_dual_sample_weights: torch.Tensor | None = None,
    overlap_dual_extra_sample_weights: torch.Tensor | None = None,
    overlap_dual_target_prediction: torch.Tensor | None = None,
    overlap_dual_residual_prediction: torch.Tensor | None = None,
    overlap_dual_monitor_prediction: torch.Tensor | None = None,
    overlap_dual_residual_correction_prediction: torch.Tensor | None = None,
    overlap_dual_residual_correction_controller_prediction: torch.Tensor | None = None,
    branch_overlap_dual_local_bridge_prediction: torch.Tensor | None = None,
    branch_overlap_artifact_local_bridge_prediction: torch.Tensor | None = None,
    branch_overlap_artifact_split_prediction: torch.Tensor | None = None,
    branch_overlap_artifact_refine_prediction: torch.Tensor | None = None,
    branch_overlap_artifact_mask_adapter_prediction: torch.Tensor | None = None,
    overlap_cancel_controller_prediction: torch.Tensor | None = None,
    overlap_dual_controller_prediction: torch.Tensor | None = None,
    overlap_dual_controller_target: torch.Tensor | None = None,
    branch_protect_sample_weights: torch.Tensor | None = None,
    branch_protect_teacher_sample_weights: torch.Tensor | None = None,
    branch_protect_teacher_extra_sample_weights: torch.Tensor | None = None,
    absent_sample_weights: torch.Tensor | None = None,
    absent_extra_sample_weights: torch.Tensor | None = None,
    gate_absent_sample_weights: torch.Tensor | None = None,
    gate_abstain_sample_weights: torch.Tensor | None = None,
    gate_keep_sample_weights: torch.Tensor | None = None,
    gate_pre_present_keep_sample_weights: torch.Tensor | None = None,
    gate_pre_present_abstain_sample_weights: torch.Tensor | None = None,
    gate_target_sample_weights: torch.Tensor | None = None,
    gate_target_values: torch.Tensor | None = None,
    gate_absent_intervals: list[list[dict[str, float]]] | None = None,
    gate_abstain_intervals: list[list[dict[str, float]]] | None = None,
    gate_keep_intervals: list[list[dict[str, float]]] | None = None,
    gate_pre_present_keep_intervals: list[list[dict[str, float]]] | None = None,
    gate_pre_present_abstain_intervals: list[list[dict[str, float]]] | None = None,
    gate_target_intervals: list[list[dict[str, float]]] | None = None,
    sample_rate: int = 16000,
    stft_weight: float = 0.5,
    reconstruction_waveform_weight: float = 0.0,
    reconstruction_stft_weight: float = 0.0,
    reconstruction_extra_waveform_weight: float = 0.0,
    reconstruction_extra_stft_weight: float = 0.0,
    extra_local_waveform_weight: float = 0.0,
    extra_local_waveform_extra_weight: float = 0.0,
    extra_local_teacher_waveform_extra_weight: float = 0.0,
    artifact_local_split_teacher_waveform_extra_weight: float = 0.0,
    artifact_local_bridge_teacher_waveform_extra_weight: float = 0.0,
    artifact_local_refine_teacher_waveform_extra_weight: float = 0.0,
    artifact_local_mask_adapter_teacher_waveform_extra_weight: float = 0.0,
    extra_local_nonlocal_waveform_weight: float = 0.0,
    pre_present_applied_delta_local_waveform_weight: float = 0.0,
    extra_local_sisdr_weight: float = 0.0,
    sisdr_weight: float = 0.0,
    branch_protect_guard_sisdr_weight: float = 0.0,
    branch_protect_overlap_base_align_weight: float = 0.0,
    branch_protect_teacher_overlap_weight: float = 0.0,
    branch_protect_teacher_overlap_extra_weight: float = 0.0,
    interference_extra_guard_sisdr_weight: float = 0.0,
    interference_extra_base_align_weight: float = 0.0,
    interference_extra_base_delta_projection_weight: float = 0.0,
    transient_weight: float = 0.0,
    transient_extra_weight: float = 0.0,
    interference_weight: float = 0.0,
    interference_extra_weight: float = 0.0,
    overlap_interference_weight: float = 0.0,
    overlap_interference_extra_weight: float = 0.0,
    overlap_cancel_waveform_weight: float = 0.0,
    overlap_cancel_target_projection_weight: float = 0.0,
    overlap_cancel_absent_mix_weight: float = 0.0,
    overlap_dual_mix_consistency_weight: float = 0.0,
    overlap_dual_residual_waveform_weight: float = 0.0,
    overlap_dual_monitor_waveform_weight: float = 0.0,
    overlap_dual_residual_correction_waveform_weight: float = 0.0,
    overlap_dual_residual_correction_local_waveform_weight: float = 0.0,
    overlap_dual_residual_correction_local_waveform_extra_weight: float = 0.0,
    overlap_dual_residual_correction_local_sisdr_weight: float = 0.0,
    overlap_dual_residual_correction_local_controller_weight: float = 0.0,
    overlap_dual_residual_correction_nonlocal_controller_weight: float = 0.0,
    overlap_dual_residual_correction_local_target_projection_weight: float = 0.0,
    branch_overlap_dual_local_bridge_nonlocal_waveform_weight: float = 0.0,
    overlap_dual_controller_distill_weight: float = 0.0,
    overlap_dual_residual_target_projection_weight: float = 0.0,
    overlap_dual_absent_mix_weight: float = 0.0,
    absent_weight: float = 0.0,
    absent_extra_weight: float = 0.0,
    gate_absent_weight: float = 0.0,
    gate_abstain_weight: float = 0.0,
    gate_keep_weight: float = 0.0,
    gate_pre_present_keep_weight: float = 0.0,
    gate_pre_present_abstain_weight: float = 0.0,
    gate_target_weight: float = 0.0,
    interference_loss_mode: str = "prediction_projection_ratio",
    interference_extra_loss_mode: str = "prediction_projection_ratio",
    overlap_interference_loss_mode: str = "prediction_projection_ratio",
    overlap_interference_extra_loss_mode: str = "prediction_projection_ratio",
    transient_top_ratio: float = 0.12,
    transient_min_count: int = 8,
    transient_mid_low_hz: float = 800.0,
    transient_mid_high_hz: float = 3000.0,
    transient_presence_low_hz: float = 3000.0,
    transient_presence_high_hz: float = 8000.0,
    transient_ratio_weight: float = 0.5,
) -> LossBreakdown:
    reconstruction_extra_prediction = prediction if reconstruction_extra_prediction is None else reconstruction_extra_prediction
    extra_prediction = prediction if extra_prediction is None else extra_prediction
    local_prediction = extra_prediction if local_prediction is None else local_prediction
    pre_present_base_prediction = prediction if pre_present_base_prediction is None else pre_present_base_prediction
    overlap_cancel_prediction = (
        prediction.new_zeros(prediction.shape)
        if overlap_cancel_prediction is None
        else overlap_cancel_prediction
    )
    overlap_dual_target_prediction = (
        prediction if overlap_dual_target_prediction is None else overlap_dual_target_prediction
    )
    overlap_dual_residual_prediction = (
        mixture - overlap_dual_target_prediction
        if overlap_dual_residual_prediction is None
        else overlap_dual_residual_prediction
    )
    waveform_term = waveform_l1_loss(prediction, target, lengths)
    stft_term = stft_l1_loss(prediction, target, model)
    nonlocal_proxy_intervals = build_complement_intervals(
        local_proxy_intervals,
        lengths,
        sample_rate,
    )
    if reconstruction_sample_weights is None:
        reconstruction_waveform_term = prediction.new_tensor(0.0)
        reconstruction_stft_term = prediction.new_tensor(0.0)
    else:
        reconstruction_waveform_term = weighted_waveform_l1_loss(
            prediction=prediction,
            target=target,
            lengths=lengths,
            sample_weights=reconstruction_sample_weights,
        )
        reconstruction_stft_term = weighted_stft_l1_loss(
            prediction=prediction,
            target=target,
            lengths=lengths,
            model=model,
            sample_weights=reconstruction_sample_weights,
        )
    if reconstruction_extra_sample_weights is None:
        reconstruction_extra_waveform_term = prediction.new_tensor(0.0)
        reconstruction_extra_stft_term = prediction.new_tensor(0.0)
    else:
        reconstruction_extra_waveform_term = weighted_waveform_l1_loss(
            prediction=reconstruction_extra_prediction,
            target=target,
            lengths=lengths,
            sample_weights=reconstruction_extra_sample_weights,
        )
        reconstruction_extra_stft_term = weighted_stft_l1_loss(
            prediction=reconstruction_extra_prediction,
            target=target,
            lengths=lengths,
            model=model,
            sample_weights=reconstruction_extra_sample_weights,
        )
    extra_local_waveform_term = interval_waveform_l1_loss(
        prediction=local_prediction,
        target=target,
        lengths=lengths,
        intervals_batch=local_proxy_intervals,
        sample_rate=sample_rate,
        sample_weights=overlap_dual_sample_weights,
    )
    extra_local_waveform_extra_term = interval_waveform_l1_loss(
        prediction=local_prediction,
        target=target,
        lengths=lengths,
        intervals_batch=local_proxy_intervals,
        sample_rate=sample_rate,
        sample_weights=overlap_dual_extra_sample_weights,
    )
    if teacher_prediction is None:
        extra_local_teacher_waveform_extra_term = prediction.new_tensor(0.0)
    else:
        extra_local_teacher_waveform_extra_term = interval_waveform_l1_loss(
            prediction=local_prediction,
            target=teacher_prediction,
            lengths=lengths,
            intervals_batch=local_proxy_intervals,
            sample_rate=sample_rate,
            sample_weights=overlap_dual_extra_sample_weights,
        )
    if teacher_prediction is None or branch_overlap_artifact_split_prediction is None:
        artifact_local_split_teacher_waveform_extra_term = prediction.new_tensor(0.0)
    else:
        artifact_local_split_teacher_waveform_extra_term = interval_waveform_l1_loss(
            prediction=branch_overlap_artifact_split_prediction,
            target=teacher_prediction,
            lengths=lengths,
            intervals_batch=artifact_local_proxy_intervals,
            sample_rate=sample_rate,
            sample_weights=overlap_dual_extra_sample_weights,
        )
    if (
        teacher_prediction is None
        or branch_overlap_artifact_local_bridge_prediction is None
    ):
        artifact_local_bridge_teacher_waveform_extra_term = prediction.new_tensor(0.0)
    else:
        artifact_local_bridge_teacher_waveform_extra_term = interval_waveform_l1_loss(
            prediction=branch_overlap_artifact_local_bridge_prediction,
            target=teacher_prediction,
            lengths=lengths,
            intervals_batch=artifact_local_proxy_intervals,
            sample_rate=sample_rate,
            sample_weights=overlap_dual_extra_sample_weights,
        )
    if (
        teacher_prediction is None
        or branch_overlap_artifact_refine_prediction is None
    ):
        artifact_local_refine_teacher_waveform_extra_term = prediction.new_tensor(0.0)
    else:
        artifact_local_refine_teacher_waveform_extra_term = interval_waveform_l1_loss(
            prediction=branch_overlap_artifact_refine_prediction,
            target=teacher_prediction,
            lengths=lengths,
            intervals_batch=artifact_local_proxy_intervals,
            sample_rate=sample_rate,
            sample_weights=overlap_dual_extra_sample_weights,
        )
    if (
        teacher_prediction is None
        or branch_overlap_artifact_mask_adapter_prediction is None
    ):
        artifact_local_mask_adapter_teacher_waveform_extra_term = prediction.new_tensor(0.0)
    else:
        artifact_local_mask_adapter_teacher_waveform_extra_term = interval_waveform_l1_loss(
            prediction=branch_overlap_artifact_mask_adapter_prediction,
            target=teacher_prediction,
            lengths=lengths,
            intervals_batch=artifact_local_proxy_intervals,
            sample_rate=sample_rate,
            sample_weights=overlap_dual_extra_sample_weights,
        )
    extra_local_nonlocal_waveform_term = interval_waveform_l1_loss(
        prediction=local_prediction,
        target=extra_prediction,
        lengths=lengths,
        intervals_batch=nonlocal_proxy_intervals,
        sample_rate=sample_rate,
        sample_weights=overlap_dual_sample_weights,
    )
    if pre_present_applied_delta_prediction is None:
        pre_present_applied_delta_local_waveform_term = prediction.new_tensor(0.0)
    else:
        (
            pre_present_base_prediction_aligned,
            pre_present_target_aligned,
            _,
        ) = align_waveforms(pre_present_base_prediction, target, lengths)
        pre_present_applied_delta_local_waveform_target = (
            pre_present_base_prediction_aligned - pre_present_target_aligned
        )
        pre_present_applied_delta_local_waveform_term = interval_waveform_l1_loss(
            prediction=pre_present_applied_delta_prediction,
            target=pre_present_applied_delta_local_waveform_target,
            lengths=lengths,
            intervals_batch=local_proxy_intervals,
            sample_rate=sample_rate,
            sample_weights=overlap_dual_sample_weights,
        )
    extra_local_sisdr_term = interval_sisdr_loss(
        prediction=local_prediction,
        target=target,
        lengths=lengths,
        intervals_batch=local_proxy_intervals,
        sample_rate=sample_rate,
        sample_weights=overlap_dual_sample_weights,
        zero_mean=True,
    )
    sisdr_db = masked_sisdr(prediction, target, lengths, zero_mean=True)
    sisdr_term = -sisdr_db
    branch_protect_guard_sisdr_term = weighted_sisdr_loss(
        prediction=extra_prediction,
        target=target,
        lengths=lengths,
        sample_weights=branch_protect_sample_weights,
        zero_mean=True,
    )
    branch_protect_overlap_base_align_term = interval_waveform_l1_loss(
        prediction=extra_prediction,
        target=prediction,
        lengths=lengths,
        intervals_batch=overlap_intervals,
        sample_rate=sample_rate,
        sample_weights=branch_protect_sample_weights,
    )
    if teacher_prediction is None:
        branch_protect_teacher_overlap_term = prediction.new_tensor(0.0)
        branch_protect_teacher_overlap_extra_term = prediction.new_tensor(0.0)
    else:
        branch_protect_teacher_overlap_term = interval_waveform_l1_loss(
            prediction=extra_prediction,
            target=teacher_prediction,
            lengths=lengths,
            intervals_batch=overlap_intervals,
            sample_rate=sample_rate,
            sample_weights=(
                branch_protect_teacher_sample_weights
                if branch_protect_teacher_sample_weights is not None
                else branch_protect_sample_weights
            ),
        )
        branch_protect_teacher_overlap_extra_term = interval_waveform_l1_loss(
            prediction=extra_prediction,
            target=teacher_prediction,
            lengths=lengths,
            intervals_batch=overlap_intervals,
            sample_rate=sample_rate,
            sample_weights=branch_protect_teacher_extra_sample_weights,
        )
    interference_extra_guard_sisdr_term = weighted_sisdr_loss(
        prediction=extra_prediction,
        target=target,
        lengths=lengths,
        sample_weights=interference_extra_sample_weights,
        zero_mean=True,
    )
    interference_extra_base_align_term = weighted_waveform_l1_loss(
        prediction=extra_prediction,
        target=prediction,
        lengths=lengths,
        sample_weights=interference_extra_sample_weights,
    )
    interference_extra_base_delta_projection_term = base_delta_interference_projection_loss(
        prediction=extra_prediction,
        reference_prediction=prediction,
        mixture=mixture,
        target=target,
        lengths=lengths,
        sample_weights=interference_extra_sample_weights,
    )
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
    transient_extra_term = transient_presence_l1_loss(
        prediction=extra_prediction,
        target=target,
        lengths=lengths,
        model=model,
        sample_weights=transient_extra_sample_weights,
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
        mode=interference_loss_mode,
    )
    interference_extra_term = interference_projection_loss(
        prediction=extra_prediction,
        mixture=mixture,
        target=target,
        lengths=lengths,
        sample_weights=interference_extra_sample_weights,
        mode=interference_extra_loss_mode,
    )
    overlap_interference_term = overlap_interval_interference_projection_loss(
        prediction=prediction,
        mixture=mixture,
        target=target,
        lengths=lengths,
        overlap_intervals=overlap_intervals,
        sample_rate=sample_rate,
        sample_weights=overlap_interference_sample_weights,
        mode=overlap_interference_loss_mode,
    )
    overlap_interference_extra_term = overlap_interval_interference_projection_loss(
        prediction=extra_prediction,
        mixture=mixture,
        target=target,
        lengths=lengths,
        overlap_intervals=overlap_intervals,
        sample_rate=sample_rate,
        sample_weights=overlap_interference_extra_sample_weights,
        mode=overlap_interference_extra_loss_mode,
    )
    prediction_aligned, _, _ = align_waveforms(prediction, target, lengths)
    mixture_aligned, target_aligned, _ = align_waveforms(mixture, target, lengths)
    overlap_cancel_target = mixture_aligned - target_aligned
    overlap_cancel_term = interval_waveform_l1_loss(
        prediction=overlap_cancel_prediction,
        target=overlap_cancel_target,
        lengths=lengths,
        intervals_batch=overlap_intervals,
        sample_rate=sample_rate,
        sample_weights=overlap_cancel_sample_weights,
    )
    overlap_cancel_target_projection_term = interval_projection_ratio_loss(
        prediction=overlap_cancel_prediction,
        target=target,
        lengths=lengths,
        intervals_batch=overlap_intervals,
        sample_rate=sample_rate,
        sample_weights=overlap_cancel_sample_weights,
    )
    overlap_cancel_absent_mix_term = interval_waveform_l1_loss(
        prediction=overlap_cancel_prediction,
        target=mixture,
        lengths=lengths,
        intervals_batch=absent_intervals,
        sample_rate=sample_rate,
        sample_weights=(
            overlap_cancel_absent_mix_sample_weights
            if overlap_cancel_absent_mix_sample_weights is not None
            else overlap_cancel_sample_weights
        ),
    )
    overlap_dual_mix_consistency_term = interval_waveform_l1_loss(
        prediction=overlap_dual_target_prediction + overlap_dual_residual_prediction,
        target=mixture,
        lengths=lengths,
        intervals_batch=overlap_intervals,
        sample_rate=sample_rate,
        sample_weights=overlap_dual_sample_weights,
    )
    overlap_dual_residual_target = mixture_aligned - target_aligned
    overlap_dual_residual_waveform_term = interval_waveform_l1_loss(
        prediction=overlap_dual_residual_prediction,
        target=overlap_dual_residual_target,
        lengths=lengths,
        intervals_batch=overlap_intervals,
        sample_rate=sample_rate,
        sample_weights=overlap_dual_sample_weights,
    )
    overlap_dual_monitor_target = prediction_aligned - target_aligned
    if overlap_dual_monitor_prediction is None:
        overlap_dual_monitor_term = prediction.new_tensor(0.0)
    else:
        overlap_dual_monitor_term = interval_waveform_l1_loss(
            prediction=overlap_dual_monitor_prediction,
            target=overlap_dual_monitor_target,
            lengths=lengths,
            intervals_batch=overlap_intervals,
            sample_rate=sample_rate,
            sample_weights=overlap_dual_sample_weights,
        )
    if overlap_dual_residual_correction_prediction is None:
        overlap_dual_residual_correction_term = prediction.new_tensor(0.0)
        overlap_dual_residual_correction_local_term = prediction.new_tensor(0.0)
        overlap_dual_residual_correction_local_extra_term = prediction.new_tensor(0.0)
        overlap_dual_residual_correction_local_sisdr_term = prediction.new_tensor(0.0)
        overlap_dual_residual_correction_local_target_projection_term = prediction.new_tensor(0.0)
    else:
        overlap_dual_residual_correction_term = interval_waveform_l1_loss(
            prediction=overlap_dual_residual_correction_prediction,
            target=overlap_dual_monitor_target,
            lengths=lengths,
            intervals_batch=overlap_intervals,
            sample_rate=sample_rate,
            sample_weights=overlap_dual_sample_weights,
        )
        overlap_dual_residual_correction_local_term = interval_waveform_l1_loss(
            prediction=overlap_dual_residual_correction_prediction,
            target=overlap_dual_monitor_target,
            lengths=lengths,
            intervals_batch=local_proxy_intervals,
            sample_rate=sample_rate,
            sample_weights=overlap_dual_sample_weights,
        )
        overlap_dual_residual_correction_local_extra_term = interval_waveform_l1_loss(
            prediction=overlap_dual_residual_correction_prediction,
            target=overlap_dual_monitor_target,
            lengths=lengths,
            intervals_batch=local_proxy_intervals,
            sample_rate=sample_rate,
            sample_weights=overlap_dual_extra_sample_weights,
        )
        overlap_dual_residual_correction_local_sisdr_term = interval_sisdr_loss(
            prediction=overlap_dual_residual_correction_prediction,
            target=overlap_dual_monitor_target,
            lengths=lengths,
            intervals_batch=local_proxy_intervals,
            sample_rate=sample_rate,
            sample_weights=overlap_dual_sample_weights,
            zero_mean=True,
        )
        overlap_dual_residual_correction_local_target_projection_term = interval_projection_ratio_loss(
            prediction=overlap_dual_residual_correction_prediction,
            target=target_aligned,
            lengths=lengths,
            intervals_batch=local_proxy_intervals,
            sample_rate=sample_rate,
            sample_weights=overlap_dual_sample_weights,
        )
    if branch_overlap_dual_local_bridge_prediction is None:
        branch_overlap_dual_local_bridge_nonlocal_term = prediction.new_tensor(0.0)
    else:
        branch_overlap_dual_local_bridge_nonlocal_term = interval_waveform_l1_loss(
            prediction=branch_overlap_dual_local_bridge_prediction,
            target=torch.zeros_like(branch_overlap_dual_local_bridge_prediction),
            lengths=lengths,
            intervals_batch=nonlocal_proxy_intervals,
            sample_rate=sample_rate,
            sample_weights=overlap_dual_sample_weights,
        )
    if overlap_dual_residual_correction_controller_prediction is None:
        overlap_dual_residual_correction_local_controller_term = prediction.new_tensor(0.0)
        overlap_dual_residual_correction_nonlocal_controller_term = prediction.new_tensor(0.0)
    else:
        overlap_dual_residual_correction_local_controller_term = weighted_gate_target_loss(
            gate_values=overlap_dual_residual_correction_controller_prediction,
            lengths=lengths,
            model=model,
            target_value=1.0,
            sample_weights=overlap_dual_sample_weights,
            intervals_batch=local_proxy_intervals,
            sample_rate=sample_rate,
        )
        overlap_dual_residual_correction_nonlocal_controller_term = weighted_gate_target_loss(
            gate_values=overlap_dual_residual_correction_controller_prediction,
            lengths=lengths,
            model=model,
            target_value=0.0,
            sample_weights=overlap_dual_sample_weights,
            intervals_batch=nonlocal_proxy_intervals,
            sample_rate=sample_rate,
        )
    resolved_overlap_dual_controller_prediction = (
        overlap_dual_controller_prediction
        if overlap_dual_controller_prediction is not None
        else overlap_cancel_controller_prediction
    )
    if (
        resolved_overlap_dual_controller_prediction is None
        or overlap_dual_controller_target is None
    ):
        overlap_dual_controller_distill_term = prediction.new_tensor(0.0)
    else:
        overlap_dual_controller_distill_term = interval_gate_l1_loss(
            prediction=resolved_overlap_dual_controller_prediction,
            target=overlap_dual_controller_target,
            lengths=lengths,
            intervals_batch=overlap_intervals,
            model=model,
            sample_rate=sample_rate,
            sample_weights=overlap_dual_sample_weights,
        )
    overlap_dual_residual_target_projection_term = interval_projection_ratio_loss(
        prediction=overlap_dual_residual_prediction,
        target=target_aligned,
        lengths=lengths,
        intervals_batch=overlap_intervals,
        sample_rate=sample_rate,
        sample_weights=overlap_dual_sample_weights,
    )
    overlap_dual_absent_mix_term = interval_waveform_l1_loss(
        prediction=overlap_dual_residual_prediction,
        target=mixture,
        lengths=lengths,
        intervals_batch=absent_intervals,
        sample_rate=sample_rate,
        sample_weights=overlap_dual_sample_weights,
    )
    absent_term = absent_interval_l1_loss(
        prediction=prediction,
        target=target,
        lengths=lengths,
        absent_intervals=absent_intervals,
        sample_rate=sample_rate,
        sample_weights=absent_sample_weights,
    )
    absent_extra_term = absent_interval_l1_loss(
        prediction=extra_prediction,
        target=target,
        lengths=lengths,
        absent_intervals=absent_intervals,
        sample_rate=sample_rate,
        sample_weights=absent_extra_sample_weights,
    )
    resolved_gate_absent_values = gate_absent_values if gate_absent_values is not None else gate_values
    resolved_gate_abstain_values = gate_abstain_values if gate_abstain_values is not None else gate_values
    resolved_gate_keep_values = gate_keep_values if gate_keep_values is not None else gate_values
    resolved_gate_pre_present_keep_values = (
        gate_pre_present_keep_values if gate_pre_present_keep_values is not None else gate_values
    )
    resolved_gate_pre_present_abstain_values = (
        gate_pre_present_abstain_values
        if gate_pre_present_abstain_values is not None
        else resolved_gate_pre_present_keep_values
    )
    resolved_gate_target_values = (
        gate_target_source_values if gate_target_source_values is not None else gate_values
    )
    gate_absent_term = weighted_gate_target_loss(
        gate_values=resolved_gate_absent_values,
        lengths=lengths,
        model=model,
        target_value=0.0,
        sample_weights=gate_absent_sample_weights,
        intervals_batch=gate_absent_intervals,
        sample_rate=sample_rate,
    )
    gate_abstain_term = weighted_gate_target_loss(
        gate_values=resolved_gate_abstain_values,
        lengths=lengths,
        model=model,
        target_value=0.0,
        sample_weights=gate_abstain_sample_weights,
        intervals_batch=gate_abstain_intervals,
        sample_rate=sample_rate,
    )
    gate_keep_term = weighted_gate_target_loss(
        gate_values=resolved_gate_keep_values,
        lengths=lengths,
        model=model,
        target_value=1.0,
        sample_weights=gate_keep_sample_weights,
        intervals_batch=gate_keep_intervals,
        sample_rate=sample_rate,
    )
    gate_pre_present_keep_term = weighted_gate_target_loss(
        gate_values=resolved_gate_pre_present_keep_values,
        lengths=lengths,
        model=model,
        target_value=1.0,
        sample_weights=gate_pre_present_keep_sample_weights,
        intervals_batch=gate_pre_present_keep_intervals,
        sample_rate=sample_rate,
    )
    gate_pre_present_abstain_term = weighted_gate_target_loss(
        gate_values=resolved_gate_pre_present_abstain_values,
        lengths=lengths,
        model=model,
        target_value=0.0,
        sample_weights=gate_pre_present_abstain_sample_weights,
        intervals_batch=gate_pre_present_abstain_intervals,
        sample_rate=sample_rate,
    )
    gate_target_term = weighted_gate_target_loss(
        gate_values=resolved_gate_target_values,
        lengths=lengths,
        model=model,
        target_values=gate_target_values,
        sample_weights=gate_target_sample_weights,
        intervals_batch=gate_target_intervals,
        sample_rate=sample_rate,
    )
    total = (
        waveform_term
        + (stft_term * stft_weight)
        + (reconstruction_waveform_term * reconstruction_waveform_weight)
        + (reconstruction_stft_term * reconstruction_stft_weight)
        + (reconstruction_extra_waveform_term * reconstruction_extra_waveform_weight)
        + (reconstruction_extra_stft_term * reconstruction_extra_stft_weight)
        + (extra_local_waveform_term * extra_local_waveform_weight)
        + (extra_local_waveform_extra_term * extra_local_waveform_extra_weight)
        + (extra_local_teacher_waveform_extra_term * extra_local_teacher_waveform_extra_weight)
        + (
            artifact_local_split_teacher_waveform_extra_term
            * artifact_local_split_teacher_waveform_extra_weight
        )
        + (
            artifact_local_bridge_teacher_waveform_extra_term
            * artifact_local_bridge_teacher_waveform_extra_weight
        )
        + (
            artifact_local_refine_teacher_waveform_extra_term
            * artifact_local_refine_teacher_waveform_extra_weight
        )
        + (
            artifact_local_mask_adapter_teacher_waveform_extra_term
            * artifact_local_mask_adapter_teacher_waveform_extra_weight
        )
        + (extra_local_nonlocal_waveform_term * extra_local_nonlocal_waveform_weight)
        + (
            pre_present_applied_delta_local_waveform_term
            * pre_present_applied_delta_local_waveform_weight
        )
        + (extra_local_sisdr_term * extra_local_sisdr_weight)
        + (sisdr_term * sisdr_weight)
        + (branch_protect_guard_sisdr_term * branch_protect_guard_sisdr_weight)
        + (branch_protect_overlap_base_align_term * branch_protect_overlap_base_align_weight)
        + (branch_protect_teacher_overlap_term * branch_protect_teacher_overlap_weight)
        + (
            branch_protect_teacher_overlap_extra_term
            * branch_protect_teacher_overlap_extra_weight
        )
        + (interference_extra_guard_sisdr_term * interference_extra_guard_sisdr_weight)
        + (interference_extra_base_align_term * interference_extra_base_align_weight)
        + (interference_extra_base_delta_projection_term * interference_extra_base_delta_projection_weight)
        + (transient_term * transient_weight)
        + (transient_extra_term * transient_extra_weight)
        + (interference_term * interference_weight)
        + (interference_extra_term * interference_extra_weight)
        + (overlap_interference_term * overlap_interference_weight)
        + (overlap_interference_extra_term * overlap_interference_extra_weight)
        + (overlap_cancel_term * overlap_cancel_waveform_weight)
        + (overlap_cancel_target_projection_term * overlap_cancel_target_projection_weight)
        + (overlap_cancel_absent_mix_term * overlap_cancel_absent_mix_weight)
        + (overlap_dual_mix_consistency_term * overlap_dual_mix_consistency_weight)
        + (overlap_dual_residual_waveform_term * overlap_dual_residual_waveform_weight)
        + (overlap_dual_monitor_term * overlap_dual_monitor_waveform_weight)
        + (
            overlap_dual_residual_correction_term
            * overlap_dual_residual_correction_waveform_weight
        )
        + (
            overlap_dual_residual_correction_local_term
            * overlap_dual_residual_correction_local_waveform_weight
        )
        + (
            overlap_dual_residual_correction_local_extra_term
            * overlap_dual_residual_correction_local_waveform_extra_weight
        )
        + (
            overlap_dual_residual_correction_local_sisdr_term
            * overlap_dual_residual_correction_local_sisdr_weight
        )
        + (
            overlap_dual_residual_correction_local_controller_term
            * overlap_dual_residual_correction_local_controller_weight
        )
        + (
            overlap_dual_residual_correction_nonlocal_controller_term
            * overlap_dual_residual_correction_nonlocal_controller_weight
        )
        + (
            overlap_dual_residual_correction_local_target_projection_term
            * overlap_dual_residual_correction_local_target_projection_weight
        )
        + (
            branch_overlap_dual_local_bridge_nonlocal_term
            * branch_overlap_dual_local_bridge_nonlocal_waveform_weight
        )
        + (overlap_dual_controller_distill_term * overlap_dual_controller_distill_weight)
        + (
            overlap_dual_residual_target_projection_term
            * overlap_dual_residual_target_projection_weight
        )
        + (overlap_dual_absent_mix_term * overlap_dual_absent_mix_weight)
        + (absent_term * absent_weight)
        + (absent_extra_term * absent_extra_weight)
        + (gate_absent_term * gate_absent_weight)
        + (gate_abstain_term * gate_abstain_weight)
        + (gate_keep_term * gate_keep_weight)
        + (gate_pre_present_keep_term * gate_pre_present_keep_weight)
        + (gate_pre_present_abstain_term * gate_pre_present_abstain_weight)
        + (gate_target_term * gate_target_weight)
    )
    return LossBreakdown(
        total=total,
        waveform_l1=waveform_term,
        stft_l1=stft_term,
        reconstruction_waveform_l1=reconstruction_waveform_term,
        reconstruction_stft_l1=reconstruction_stft_term,
        reconstruction_extra_waveform_l1=reconstruction_extra_waveform_term,
        reconstruction_extra_stft_l1=reconstruction_extra_stft_term,
        extra_local_waveform_l1=extra_local_waveform_term,
        extra_local_waveform_extra_l1=extra_local_waveform_extra_term,
        extra_local_teacher_waveform_extra_l1=extra_local_teacher_waveform_extra_term,
        artifact_local_split_teacher_waveform_extra_l1=(
            artifact_local_split_teacher_waveform_extra_term
        ),
        artifact_local_bridge_teacher_waveform_extra_l1=(
            artifact_local_bridge_teacher_waveform_extra_term
        ),
        artifact_local_refine_teacher_waveform_extra_l1=(
            artifact_local_refine_teacher_waveform_extra_term
        ),
        artifact_local_mask_adapter_teacher_waveform_extra_l1=(
            artifact_local_mask_adapter_teacher_waveform_extra_term
        ),
        extra_local_nonlocal_waveform_l1=extra_local_nonlocal_waveform_term,
        pre_present_applied_delta_local_waveform_l1=(
            pre_present_applied_delta_local_waveform_term
        ),
        extra_local_sisdr_loss=extra_local_sisdr_term,
        sisdr_loss=sisdr_term,
        branch_protect_guard_sisdr_loss=branch_protect_guard_sisdr_term,
        branch_protect_overlap_base_align_l1=branch_protect_overlap_base_align_term,
        branch_protect_teacher_overlap_l1=branch_protect_teacher_overlap_term,
        branch_protect_teacher_overlap_extra_l1=branch_protect_teacher_overlap_extra_term,
        interference_extra_guard_sisdr_loss=interference_extra_guard_sisdr_term,
        interference_extra_base_align_l1=interference_extra_base_align_term,
        interference_extra_base_delta_projection_ratio=interference_extra_base_delta_projection_term,
        sisdr_db=sisdr_db,
        transient_presence_l1=transient_term,
        transient_extra_presence_l1=transient_extra_term,
        interference_projection_ratio=interference_term,
        interference_extra_projection_ratio=interference_extra_term,
        overlap_interference_projection_ratio=overlap_interference_term,
        overlap_interference_extra_projection_ratio=overlap_interference_extra_term,
        overlap_cancel_waveform_l1=overlap_cancel_term,
        overlap_cancel_target_projection_ratio=overlap_cancel_target_projection_term,
        overlap_cancel_absent_mix_l1=overlap_cancel_absent_mix_term,
        overlap_dual_mix_consistency_l1=overlap_dual_mix_consistency_term,
        overlap_dual_residual_waveform_l1=overlap_dual_residual_waveform_term,
        overlap_dual_monitor_waveform_l1=overlap_dual_monitor_term,
        overlap_dual_residual_correction_waveform_l1=overlap_dual_residual_correction_term,
        overlap_dual_residual_correction_local_waveform_l1=(
            overlap_dual_residual_correction_local_term
        ),
        overlap_dual_residual_correction_local_waveform_extra_l1=(
            overlap_dual_residual_correction_local_extra_term
        ),
        overlap_dual_residual_correction_local_sisdr_loss=(
            overlap_dual_residual_correction_local_sisdr_term
        ),
        overlap_dual_residual_correction_local_controller_l1=(
            overlap_dual_residual_correction_local_controller_term
        ),
        overlap_dual_residual_correction_nonlocal_controller_l1=(
            overlap_dual_residual_correction_nonlocal_controller_term
        ),
        overlap_dual_residual_correction_local_target_projection_ratio=(
            overlap_dual_residual_correction_local_target_projection_term
        ),
        branch_overlap_dual_local_bridge_nonlocal_waveform_l1=(
            branch_overlap_dual_local_bridge_nonlocal_term
        ),
        overlap_dual_controller_distill_l1=overlap_dual_controller_distill_term,
        overlap_dual_residual_target_projection_ratio=overlap_dual_residual_target_projection_term,
        overlap_dual_absent_mix_l1=overlap_dual_absent_mix_term,
        absent_interval_l1=absent_term,
        absent_extra_interval_l1=absent_extra_term,
        gate_absent_mean=gate_absent_term,
        gate_abstain_mean=gate_abstain_term,
        gate_keep_mean=gate_keep_term,
        gate_pre_present_keep_mean=gate_pre_present_keep_term,
        gate_pre_present_abstain_mean=gate_pre_present_abstain_term,
        gate_target_l1=gate_target_term,
    )
