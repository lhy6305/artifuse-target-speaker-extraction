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
    sisdr_loss: torch.Tensor
    interference_extra_guard_sisdr_loss: torch.Tensor
    interference_extra_base_align_l1: torch.Tensor
    interference_extra_base_delta_projection_ratio: torch.Tensor
    sisdr_db: torch.Tensor
    transient_presence_l1: torch.Tensor
    transient_extra_presence_l1: torch.Tensor
    interference_projection_ratio: torch.Tensor
    interference_extra_projection_ratio: torch.Tensor
    absent_interval_l1: torch.Tensor
    absent_extra_interval_l1: torch.Tensor


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


def compute_losses(
    prediction: torch.Tensor,
    mixture: torch.Tensor,
    target: torch.Tensor,
    lengths: torch.Tensor,
    absent_intervals: list[list[dict[str, float]]],
    model,
    reconstruction_extra_prediction: torch.Tensor | None = None,
    extra_prediction: torch.Tensor | None = None,
    reconstruction_sample_weights: torch.Tensor | None = None,
    reconstruction_extra_sample_weights: torch.Tensor | None = None,
    transient_sample_weights: torch.Tensor | None = None,
    transient_extra_sample_weights: torch.Tensor | None = None,
    interference_sample_weights: torch.Tensor | None = None,
    interference_extra_sample_weights: torch.Tensor | None = None,
    absent_sample_weights: torch.Tensor | None = None,
    absent_extra_sample_weights: torch.Tensor | None = None,
    sample_rate: int = 16000,
    stft_weight: float = 0.5,
    reconstruction_waveform_weight: float = 0.0,
    reconstruction_stft_weight: float = 0.0,
    reconstruction_extra_waveform_weight: float = 0.0,
    reconstruction_extra_stft_weight: float = 0.0,
    sisdr_weight: float = 0.0,
    interference_extra_guard_sisdr_weight: float = 0.0,
    interference_extra_base_align_weight: float = 0.0,
    interference_extra_base_delta_projection_weight: float = 0.0,
    transient_weight: float = 0.0,
    transient_extra_weight: float = 0.0,
    interference_weight: float = 0.0,
    interference_extra_weight: float = 0.0,
    absent_weight: float = 0.0,
    absent_extra_weight: float = 0.0,
    interference_loss_mode: str = "prediction_projection_ratio",
    interference_extra_loss_mode: str = "prediction_projection_ratio",
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
    waveform_term = waveform_l1_loss(prediction, target, lengths)
    stft_term = stft_l1_loss(prediction, target, model)
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
    sisdr_db = masked_sisdr(prediction, target, lengths, zero_mean=True)
    sisdr_term = -sisdr_db
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
    total = (
        waveform_term
        + (stft_term * stft_weight)
        + (reconstruction_waveform_term * reconstruction_waveform_weight)
        + (reconstruction_stft_term * reconstruction_stft_weight)
        + (reconstruction_extra_waveform_term * reconstruction_extra_waveform_weight)
        + (reconstruction_extra_stft_term * reconstruction_extra_stft_weight)
        + (sisdr_term * sisdr_weight)
        + (interference_extra_guard_sisdr_term * interference_extra_guard_sisdr_weight)
        + (interference_extra_base_align_term * interference_extra_base_align_weight)
        + (interference_extra_base_delta_projection_term * interference_extra_base_delta_projection_weight)
        + (transient_term * transient_weight)
        + (transient_extra_term * transient_extra_weight)
        + (interference_term * interference_weight)
        + (interference_extra_term * interference_extra_weight)
        + (absent_term * absent_weight)
        + (absent_extra_term * absent_extra_weight)
    )
    return LossBreakdown(
        total=total,
        waveform_l1=waveform_term,
        stft_l1=stft_term,
        reconstruction_waveform_l1=reconstruction_waveform_term,
        reconstruction_stft_l1=reconstruction_stft_term,
        reconstruction_extra_waveform_l1=reconstruction_extra_waveform_term,
        reconstruction_extra_stft_l1=reconstruction_extra_stft_term,
        sisdr_loss=sisdr_term,
        interference_extra_guard_sisdr_loss=interference_extra_guard_sisdr_term,
        interference_extra_base_align_l1=interference_extra_base_align_term,
        interference_extra_base_delta_projection_ratio=interference_extra_base_delta_projection_term,
        sisdr_db=sisdr_db,
        transient_presence_l1=transient_term,
        transient_extra_presence_l1=transient_extra_term,
        interference_projection_ratio=interference_term,
        interference_extra_projection_ratio=interference_extra_term,
        absent_interval_l1=absent_term,
        absent_extra_interval_l1=absent_extra_term,
    )
