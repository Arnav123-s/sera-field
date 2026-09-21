# Prespecified uncertainty summary for the frozen GENRE-017 outputs

This supplementary reporting analysis is recorded during the first training arm,
before final registration or any final prediction. It does not change the
curriculum, model selection, qualification gates, cohorts or active director.

After all registered predictions and the independent audit finish, compare the
fixed primary candidate with every declared control: exact_clean,
gaussian_noisy, parent, no_imagination and no_action. Report accuracy improvement
(primary minus control) and log-loss improvement (control minus primary).

Use 2,000 paired bootstrap replicates, seed 171170, sampling complete source-premise
groups with replacement within each cohort. All rows belonging to a sampled
premise travel together; all controls use the same resample. Recompute the
row-weighted mean in each replicate. Report percentile 2.5/97.5 intervals per
cohort and for the equally weighted mean of the two cohorts. Report the number
of rows and premise groups and identity of every input case file.

These are evaluation-sampling intervals for the fixed trained models. They do
not measure variation over training seeds, establish an architecture-wide ranking,
or change the frozen decisions. No model or final label is used for training,
selection or repair in this analysis. There is no significance-based choice among
mechanisms, and every specified comparison is retained.

Run once under the ordinary numerical supervisor after the current director.
If a reporting defect is repaired, preserve the original attempt and replay the
same registered inputs. Record all costs separately.
