# Old Experiment Reevaluation

- Generated at: 2026-03-28T09:54:11
- Reevaluation root: `reports/eval/reeval_2026-03-28_active_overlap_family`
- Selected checkpoints: 38
- Successful reevaluations: 38
- Prior standalone eval summaries found: 0
- Selector fraction changes detected: 0

## Metric Delta Summary vs Best Train Val

- `loss`: compared=38, mean_abs_delta=0.0016429077705051465, max_abs_delta=0.006907685778357778, missing_old=0
- `waveform_l1`: compared=38, mean_abs_delta=0.00019361783025611883, max_abs_delta=0.0003170451488007202, missing_old=0
- `stft_l1`: compared=38, mean_abs_delta=0.00038128063145656386, max_abs_delta=0.0007311524653976637, missing_old=0
- `sisdr_loss`: compared=38, mean_abs_delta=0.862969028219489, max_abs_delta=1.5423174886992488, missing_old=0
- `branch_protect_teacher_overlap_l1`: compared=17, mean_abs_delta=2.88752244993494e-05, max_abs_delta=0.0002448017419682761, missing_old=21
- `overlap_dual_mix_consistency_l1`: compared=28, mean_abs_delta=0.0009794534653211776, max_abs_delta=0.0022329057030605545, missing_old=10
- `overlap_dual_residual_target_projection_ratio`: compared=28, mean_abs_delta=0.01114421199163047, max_abs_delta=0.026922785547195058, missing_old=10

## Ranking

- Old top5 by best train val loss: `['baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v84_v81_overlap_refiner_v2_prerefine_ft1_rerun2', 'baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v85_v81_overlap_refiner_v3_gatecomplement_ft1', 'baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v103_v102_speechonly_plusmusic_teacher_veto_ft1', 'baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v83_v81_overlap_refiner_v1_ft1', 'baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v82_v81_overlap_purify_v1_ft1']`
- New top5 by reeval loss: `['baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v84_v81_overlap_refiner_v2_prerefine_ft1_rerun2', 'baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v85_v81_overlap_refiner_v3_gatecomplement_ft1', 'baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v83_v81_overlap_refiner_v1_ft1', 'baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v103_v102_speechonly_plusmusic_teacher_veto_ft1', 'baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v82_v81_overlap_purify_v1_ft1']`
- Top5 overlap count: 5

## Largest Loss Deltas

- `baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v96_v81_overlap_aux_interference_decoder_v5_phasepreserve_ft1`: old=0.06410209611058235, new=0.07100978188894012, delta=0.006907685778357778
- `baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v97_v81_overlap_aux_interference_decoder_v5_phasepreserve_fixgrad_ft1`: old=0.06427108645439147, new=0.0711771177523064, delta=0.006906031297914922
- `baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v98_v81_overlap_canceller_v3_phasepreserve_subtract_ft1`: old=0.06426524817943573, new=0.07117021038676753, delta=0.006904962207331805
- `baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v95_v94_overlap_aux_interference_decoder_v4_hardpresentprotect_ft1`: old=0.06162963286042213, new=0.06771870081623395, delta=0.006089067955811815
- `baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v99_v95_hardpresent_artifact_veto_v1_ft1`: old=0.061570799350738524, new=0.06762663342735985, delta=0.006055834076621323
- `baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v100_v95_teacher_artifact_veto_v1_ft1`: old=0.061694346368312836, new=0.06774467037934245, delta=0.0060503240110296175
- `baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v93_v88_overlap_aux_interference_decoder_v2_priortransfer_ft1`: old=0.06530441418290138, new=0.07027209787206216, delta=0.0049676836891607845
- `baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v94_v88_overlap_aux_interference_decoder_v3_maskheadtransfer_ft1`: old=0.06446018889546394, new=0.06911236973422946, delta=0.004652180838765521
- `baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v91_v81_overlap_dual_decoder_v1_blendcap025_ft1`: old=0.03594115562736988, new=0.03722195959452427, delta=0.0012808039671543883
- `baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v90_v81_overlap_dual_decoder_v1_ft1`: old=0.050423432141542435, new=0.051661650226874786, delta=0.0012382180853323516

## Selector Fraction Changes

- None
