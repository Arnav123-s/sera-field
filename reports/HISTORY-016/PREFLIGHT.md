# HISTORY-016 preparation record

The implementation is prepared against the continuing semantic/physical owner.
SEMANTIC-015 still owns the numerical lease; no HISTORY-016 model training or
numerical tests have run at this preparation checkpoint. Its protocol and source
identities will be committed before the first numerical test.

Static review added the following checks before numerical evaluation:

- The slow-rate parameterization remains strictly slower for every learned value.
- Spectral length, passive energy, injected mass, conserved relaxation and signal
  reconstruction are recorded separately from independent task progress.
- The flow identity includes its connection, and the scalar amplitude map must
  pass a round trip before retained state can change.
- Retained history stays scoped to the original goal. A current-owner check
  rejects stale evidence before entering the factual write path.
- Independent query annotations arrive after the proposed history; each query
  gets one assessment, including failures. A mismatched performed proposal earns
  no credit. Exact revisions preserve owner, source, original goal and evidence.
- A resumable selection pointer can recover a completed development assessment
  if interrupted between checkpoint commit and selection-pointer publication.

Source metadata checks found 2,048 training, 128 development and 256 sealed
episodes. Each contains four distinct support IDs; support and query source pools
are disjoint. These checks inspected record identities, not model outcomes.
Preparation costs and the producer identity are in [PREPARATION.json](PREPARATION.json).
The missing CPU instrumentation for that source preparation is recorded explicitly.

The upcoming evidence sequence is numerical tests, the qualified parent's finite
teaching campaign, frozen controls and exact replay, persistent delivery, then an
independent audit. A failed utility gate preserves the assessed candidate and its
costs; it does not silently replace the qualified owner.
