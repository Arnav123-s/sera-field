# Paired uncertainty for the fixed GENRE-017 comparison

Positive differences favor the primary exact/noisy candidate. Accuracy is in
percentage points. Brackets contain the prespecified 95% percentile interval.
All sentences from a resampled source premise remain together and all controls
share the same resample. Both reserved cohorts contribute equally to the combined
estimate. These are fixed-model evaluation-sampling intervals; they do not
estimate variation over training seeds or change any frozen qualification gate.

| Cohort | Control | Accuracy improvement [95% interval] | Log-loss improvement [95% interval] |
|---|---|---:|---:|
| matched | exact_clean | +0.00 [-0.29, +0.30] | -0.00001 [-0.00033, +0.00033] |
| matched | gaussian_noisy | +0.00 [-0.97, +0.97] | +0.00158 [-0.00242, +0.00574] |
| matched | parent | +10.01 [+8.25, +11.73] | +0.11291 [+0.09836, +0.12634] |
| matched | no_imagination | +4.00 [+2.55, +5.48] | +0.28809 [+0.26354, +0.31253] |
| matched | no_action | +0.10 [-0.12, +0.37] | -0.00015 [-0.00038, +0.00009] |
| mismatched | exact_clean | +0.10 [-0.15, +0.34] | +0.00032 [+0.00002, +0.00063] |
| mismatched | gaussian_noisy | +0.27 [-0.63, +1.17] | +0.00308 [-0.00018, +0.00675] |
| mismatched | parent | +9.86 [+8.08, +11.55] | +0.12724 [+0.11368, +0.14043] |
| mismatched | no_imagination | +4.05 [+2.61, +5.51] | +0.26241 [+0.23917, +0.28563] |
| mismatched | no_action | +0.07 [-0.14, +0.27] | +0.00009 [-0.00014, +0.00032] |
| equal_cohort_mean | exact_clean | +0.05 [-0.14, +0.23] | +0.00015 [-0.00007, +0.00039] |
| equal_cohort_mean | gaussian_noisy | +0.13 [-0.54, +0.79] | +0.00233 [-0.00035, +0.00510] |
| equal_cohort_mean | parent | +9.94 [+8.72, +11.18] | +0.12007 [+0.11050, +0.12973] |
| equal_cohort_mean | no_imagination | +4.03 [+3.01, +5.07] | +0.27525 [+0.25774, +0.29181] |
| equal_cohort_mean | no_action | +0.09 [-0.07, +0.25] | -0.00003 [-0.00020, +0.00014] |

[Protocol](../../protocols/GENRE-017-UNCERTAINTY.md) and
[exact inputs, counts and arithmetic](UNCERTAINTY.json) preserve every comparison.
No training, checkpoint selection or repeated model evaluation occurs here.
