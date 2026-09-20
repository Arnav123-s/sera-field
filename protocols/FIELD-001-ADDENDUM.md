# Prospective control and sampling audit — before final opening

The first protocol and source manifest remain preserved in the initial training attempt. No final cohort has been opened when this addendum is written.

## Stronger mechanism control

I add an invariant-input classical network with 783 trainable parameters, the same 8-20-25-3 dimensions as the raw-input dense control. It receives the same scalar contractions as the field model and predicts coefficients multiplying the same physical vector basis. It is initialized independently at the same seeds and trained on the same examples, 3,000 updates, optimizer and development cases. This isolates the group-link parameterization from the supplied physical invariance. No existing checkpoint is retrained or replaced. Results are appended before the selection manifest is sealed for finals.

## Rotation sampling correction

The initial observation generator uses proper QR rotations, but QR without the diagonal-sign correction is not uniform Haar sampling. This was identified by code inspection before final evaluation. Preserve the original training/development cohorts and their identities. Add an explicit Haar option with diagonal-sign correction before the determinant correction, and use it for the previously unopened final rotation and mass-extension cohorts and final context episodes. Test orthogonality, determinant and the absence of a forced first-column sign. This corrects the sampling claim without reusing final observations or unnecessarily restarting completed training.

The original final seeds and cohort counts remain fixed. Every outcome is reported, including the stronger invariant control. Candidate selection still uses only the original development cohorts. Publish both original and amended source identities.
