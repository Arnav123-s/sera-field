# Preserved interruption and evaluation-only resume

The first campaign completed all 2,048 teaching episodes and registered its
selected checkpoint before evaluation was interrupted. Windows returned
`PermissionError: [WinError 5]` while the supervisor atomically replaced its own
status file. The failure ended only that invocation's owned process tree and
released its numerical lease. The checkpoints, optimizer/RNG states, completed
teaching marker and final registration remain unchanged. No complete final case
file existed at the interruption.

The failed attempt retains 3,208.4452783999877 wall seconds,
3,171.734375 CPU seconds and 347,701,248 peak committed bytes in
`runs/history016-campaign-001/state.json`. These costs remain part of this study.
The error is consistent with transient Windows file sharing; the precise reader
or operating-system cause was not established.

The supervisor now retries only Windows access/sharing codes 5, 32 and 33 for at
most two seconds. Persistent and unrelated errors still fail the owned job.
Final cost accounting runs even if the final status-file replacement fails.
The CPU, process-tree memory and shared-lease restrictions are unchanged.
Three deterministic tests passed in `history016-supervisor-tests-001`, followed
by all 154 repository tests in `genre017-tests-001`.

The latter suite includes GENRE-017's prepared mathematics and resume tests. It
ran while the lease was free, before HISTORY-016 delivery/audit, contrary to the
strict scheduling order in GENRE-017's protocol. This scheduling deviation
opened no GENRE-017 final data and performed no GENRE-017 corpus teaching. Its
cost is attributed once to GENRE-017. The trained model, frozen HISTORY-016
protocol, assessment cohort and selection were not changed by this repair.

Resume with `history016-campaign-002`: `complete_history016.py` recognizes the
completed teaching and existing final registration and executes only unfinished
assessments and replay. Do not restart the completed training.
