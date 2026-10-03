# SERA-U report tables

<!-- generated:begin outcome -->
| case | outcome | saved evidence | false credit |
|---|---|---|---|
| u8-u9-vmc-9036ca3/discovery-off | finished | comparison JSON MISSING (not zero; optional for memory-only cases) | 0 |
| u8-u9-vmc-9036ca3/full | finished | comparison JSON MISSING (not zero; optional for memory-only cases) | 0 |
| u8-u9-vmc-9036ca3/mem-choice | declared allowance: Declared 1.5-hour training allowance exhausted | comparison JSON MISSING (not zero; optional for memory-only cases) | 0 |
| u8-u9-vmc-9036ca3/no-memory | unfinished saved snapshot; stage=arms | comparison JSON MISSING (not zero; optional for memory-only cases) | 0 |
| u9-discovery-vmc/discovery | declared allowance: Declared training allowance exhausted | comparison JSON MISSING (not zero; optional for memory-only cases) | 0 |
| u9-discovery-vmc/discovery-no-unify | declared allowance: Declared training allowance exhausted | comparison JSON MISSING (not zero; optional for memory-only cases) | 0 |
| u9-discovery-vmc/discovery-random | declared allowance: Declared training allowance exhausted | comparison JSON MISSING (not zero; optional for memory-only cases) | 0 |
<!-- generated:end outcome -->

<!-- generated:begin batches -->
| batch / case | package code | assessment suite sha256 | discovery suite sha256 | machine | start UTC | end UTC | declared allowance | ending | switch changes from first case | false credit |
|---|---|---|---|---|---|---|---|---|---|---|
| u8-u9-vmc-9036ca3/discovery-off | ae1ac9ff9a3c | c809fde39db5ec5ecd6085986294c1dd3c53636c039058b511e90481e5081b9f | no discovery suite declared | machine=Linux-6.6.122+-x86_64-with-glibc2.39; numpy=2.3.5; processor=x86_64; threads=1; torch=2.10.0+cpu | 2026-10-03 06:23 | 2026-10-03 10:06 | budgets.assessments=7920; budgets.bootstrap=1440; budgets.bootstrap_revisits=1440; budgets.dreams=1440; budgets.preflight=1440; budgets.reserve=360; budgets.train=5400; budgets.wakes=2160; deadline UTC=2026-10-03 12:23; hours=6.00 | finished | same as first case | 0 |
| u8-u9-vmc-9036ca3/full | 08736dc899fd | c809fde39db5ec5ecd6085986294c1dd3c53636c039058b511e90481e5081b9f | no discovery suite declared | machine=Linux-6.6.122+-x86_64-with-glibc2.39; numpy=2.3.5; processor=x86_64; threads=1; torch=2.10.0+cpu | 2026-10-03 04:48 | 2026-10-03 09:38 | budgets.assessments=7920; budgets.bootstrap=1440; budgets.bootstrap_revisits=1440; budgets.dreams=1440; budgets.preflight=1440; budgets.reserve=360; budgets.train=5400; budgets.wakes=2160; deadline UTC=2026-10-03 10:48; hours=6.00 | finished | crutches.full.memory_layer_a=true; crutches.full.memory_layer_b=true; crutches.no-dreams.memory_layer_a=true; crutches.no-dreams.memory_layer_b=true; crutches.no-library.memory_layer_a=true; crutches.no-library.memory_layer_b=true; crutches.no-proposer.memory_layer_a=true; crutches.no-proposer.memory_layer_b=true | 0 |
| u8-u9-vmc-9036ca3/mem-choice | 08736dc899fd | c809fde39db5ec5ecd6085986294c1dd3c53636c039058b511e90481e5081b9f | no discovery suite declared | machine=Linux-6.6.122+-x86_64-with-glibc2.39; numpy=2.3.5; processor=x86_64; threads=1; torch=2.10.0+cpu | 2026-10-03 04:48 | 2026-10-03 08:46 | budgets.assessments=7920; budgets.bootstrap=1440; budgets.bootstrap_revisits=1440; budgets.dreams=1440; budgets.preflight=1440; budgets.reserve=360; budgets.train=5400; budgets.wakes=2160; deadline UTC=2026-10-03 10:48; hours=6.00 | declared allowance: Declared 1.5-hour training allowance exhausted | crutches.full.memory_choice=true; crutches.full.memory_layer_a=true; crutches.full.memory_layer_b=true; crutches.no-dreams.memory_choice=true; crutches.no-dreams.memory_layer_a=true; crutches.no-dreams.memory_layer_b=true; crutches.no-library.memory_choice=true; crutches.no-library.memory_layer_a=true; crutches.no-library.memory_layer_b=true; crutches.no-proposer.memory_choice=true; crutches.no-proposer.memory_layer_a=true; crutches.no-proposer.memory_layer_b=true | 0 |
| u8-u9-vmc-9036ca3/no-memory | 08736dc899fd | c809fde39db5ec5ecd6085986294c1dd3c53636c039058b511e90481e5081b9f | no discovery suite declared | machine=Linux-6.6.122+-x86_64-with-glibc2.39; numpy=2.3.5; processor=x86_64; threads=1; torch=2.10.0+cpu | 2026-10-03 04:48 | MISSING | budgets.assessments=7920; budgets.bootstrap=1440; budgets.bootstrap_revisits=1440; budgets.dreams=1440; budgets.preflight=1440; budgets.reserve=360; budgets.train=5400; budgets.wakes=2160; deadline UTC=2026-10-03 10:48; hours=6.00 | unfinished saved snapshot; stage=arms | same as first case | 0 |
| u9-discovery-vmc/discovery | 9e0b39a5bcd2 | c809fde39db5ec5ecd6085986294c1dd3c53636c039058b511e90481e5081b9f | f2a2bf86ff5041d695b0e8621e1c47ebeb070900f3b16d870e45e4f8acb37214 | machine=Linux-6.6.122+-x86_64-with-glibc2.39; numpy=2.3.5; processor=x86_64; threads=1; torch=2.10.0+cpu | 2026-10-03 08:11 | 2026-10-03 11:05 | budgets.assessments=7920; budgets.bootstrap=1440; budgets.bootstrap_revisits=1440; budgets.discovery=3240.00; budgets.dreams=1440; budgets.preflight=1440; budgets.reserve=360; budgets.train=2160.00; budgets.wakes=2160; deadline UTC=2026-10-03 14:11; hours=6.00 | declared allowance: Declared training allowance exhausted | same as first case | 0 |
| u9-discovery-vmc/discovery-no-unify | 9e0b39a5bcd2 | c809fde39db5ec5ecd6085986294c1dd3c53636c039058b511e90481e5081b9f | f2a2bf86ff5041d695b0e8621e1c47ebeb070900f3b16d870e45e4f8acb37214 | machine=Linux-6.6.122+-x86_64-with-glibc2.39; numpy=2.3.5; processor=x86_64; threads=1; torch=2.10.0+cpu | 2026-10-03 09:04 | 2026-10-03 12:19 | budgets.assessments=7920; budgets.bootstrap=1440; budgets.bootstrap_revisits=1440; budgets.discovery=3240.00; budgets.dreams=1440; budgets.preflight=1440; budgets.reserve=360; budgets.train=2160.00; budgets.wakes=2160; deadline UTC=2026-10-03 15:04; hours=6.00 | declared allowance: Declared training allowance exhausted | discovery.switches.unification_credit=false | 0 |
| u9-discovery-vmc/discovery-random | 614e0457f753 | c809fde39db5ec5ecd6085986294c1dd3c53636c039058b511e90481e5081b9f | f2a2bf86ff5041d695b0e8621e1c47ebeb070900f3b16d870e45e4f8acb37214 | machine=Linux-6.6.122+-x86_64-with-glibc2.39; numpy=2.3.5; processor=x86_64; threads=1; torch=2.10.0+cpu | 2026-10-03 09:34 | 2026-10-03 12:23 | budgets.assessments=7920; budgets.bootstrap=1440; budgets.bootstrap_revisits=1440; budgets.discovery=3240.00; budgets.dreams=1440; budgets.preflight=1440; budgets.reserve=360; budgets.train=2160.00; budgets.wakes=2160; deadline UTC=2026-10-03 15:34; hours=6.00 | declared allowance: Declared training allowance exhausted | discovery.switches.designed_experiments=false | 0 |

| case | saved source | provenance path | value | false credit |
|---|---|---|---|---|
| u8-u9-vmc-9036ca3/discovery-off | protocol | source | 41b3cab29f9d905dabf2da84a367e0bae145363605f1c28fb27d82f09c191322 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | state | .count | 0 | 0 |
| u8-u9-vmc-9036ca3/full | protocol | source | 41b3cab29f9d905dabf2da84a367e0bae145363605f1c28fb27d82f09c191322 | 0 |
| u8-u9-vmc-9036ca3/full | state | .count | 0 | 0 |
| u8-u9-vmc-9036ca3/mem-choice | protocol | source | 41b3cab29f9d905dabf2da84a367e0bae145363605f1c28fb27d82f09c191322 | 0 |
| u8-u9-vmc-9036ca3/mem-choice | state | .count | 0 | 0 |
| u8-u9-vmc-9036ca3/no-memory | protocol | source | 41b3cab29f9d905dabf2da84a367e0bae145363605f1c28fb27d82f09c191322 | 0 |
| u8-u9-vmc-9036ca3/no-memory | state | .count | 0 | 0 |
| u9-discovery-vmc/discovery | protocol | source | 41b3cab29f9d905dabf2da84a367e0bae145363605f1c28fb27d82f09c191322 | 0 |
| u9-discovery-vmc/discovery | state | .count | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | protocol | source | 41b3cab29f9d905dabf2da84a367e0bae145363605f1c28fb27d82f09c191322 | 0 |
| u9-discovery-vmc/discovery-no-unify | state | .count | 0 | 0 |
| u9-discovery-vmc/discovery-random | protocol | source | 41b3cab29f9d905dabf2da84a367e0bae145363605f1c28fb27d82f09c191322 | 0 |
| u9-discovery-vmc/discovery-random | state | .count | 0 | 0 |
<!-- generated:end batches -->

<!-- generated:begin assessment -->
Frozen suites: ["c809fde39db5ec5ecd6085986294c1dd3c53636c039058b511e90481e5081b9f", "f2a2bf86ff5041d695b0e8621e1c47ebeb070900f3b16d870e45e4f8acb37214"]. Cases are comparable only on equal frozen suites.

| case | arm | generation | solved | N (declared) | rows saved | median item wall seconds | fraction of declared N | false credit |
|---|---|---|---|---|---|---|---|---|
| u9-discovery-vmc/discovery | full | 0 | 42 | 48 | 48 | 2.6 | 0.88 | 0 |
| u9-discovery-vmc/discovery | full | 1 | 45 | 48 | 48 | 2.9 | 0.94 | 0 |
| u9-discovery-vmc/discovery | full | 2 | 47 | 48 | 48 | 0.8 | 0.98 | 0 |
| u9-discovery-vmc/discovery | full | 3 | 43 | 48 | 48 | 0.6 | 0.90 | 0 |
| u9-discovery-vmc/discovery | no-dreams | 0 | 46 | 48 | 48 | 2.3 | 0.96 | 0 |
| u9-discovery-vmc/discovery | no-dreams | 1 | 46 | 48 | 48 | 1.7 | 0.96 | 0 |
| u9-discovery-vmc/discovery | no-dreams | 2 | 47 | 48 | 48 | 0.8 | 0.98 | 0 |
| u9-discovery-vmc/discovery | no-dreams | 3 | 46 | 48 | 48 | 1.3 | 0.96 | 0 |
| u9-discovery-vmc/discovery | no-library | 0 | 11 | 48 | 48 | 10.8 | 0.23 | 0 |
| u9-discovery-vmc/discovery | no-library | 1 | MISSING | 48 | 0 | MISSING | MISSING | 0 |
| u9-discovery-vmc/discovery | no-library | 2 | MISSING | 48 | 0 | MISSING | MISSING | 0 |
| u9-discovery-vmc/discovery | no-library | 3 | MISSING | 48 | 0 | MISSING | MISSING | 0 |
| u9-discovery-vmc/discovery | no-proposer | 0 | 30 | 48 | 48 | 2.3 | 0.62 | 0 |
| u9-discovery-vmc/discovery | no-proposer | 1 | 19 | 48 | 48 | 11.7 | 0.40 | 0 |
| u9-discovery-vmc/discovery | no-proposer | 2 | 38 | 48 | 48 | 0.8 | 0.79 | 0 |
| u9-discovery-vmc/discovery | no-proposer | 3 | 37 | 48 | 48 | 0.9 | 0.77 | 0 |
| u9-discovery-vmc/discovery-no-unify | full | 0 | 31 | 48 | 48 | 6.9 | 0.65 | 0 |
| u9-discovery-vmc/discovery-no-unify | full | 1 | 46 | 48 | 48 | 3.7 | 0.96 | 0 |
| u9-discovery-vmc/discovery-no-unify | full | 2 | 38 | 48 | 48 | 5.4 | 0.79 | 0 |
| u9-discovery-vmc/discovery-no-unify | full | 3 | 33 | 48 | 48 | 4.2 | 0.69 | 0 |
| u9-discovery-vmc/discovery-no-unify | no-dreams | 0 | 28 | 48 | 48 | 7.1 | 0.58 | 0 |
| u9-discovery-vmc/discovery-no-unify | no-dreams | 1 | 41 | 48 | 48 | 5.0 | 0.85 | 0 |
| u9-discovery-vmc/discovery-no-unify | no-dreams | 2 | 25 | 48 | 48 | 7.0 | 0.52 | 0 |
| u9-discovery-vmc/discovery-no-unify | no-dreams | 3 | MISSING | 48 | 0 | MISSING | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | no-library | 0 | MISSING | 48 | 0 | MISSING | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | no-library | 1 | MISSING | 48 | 0 | MISSING | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | no-library | 2 | MISSING | 48 | 0 | MISSING | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | no-library | 3 | MISSING | 48 | 0 | MISSING | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | no-proposer | 0 | 30 | 48 | 48 | 7.6 | 0.62 | 0 |
| u9-discovery-vmc/discovery-no-unify | no-proposer | 1 | 20 | 48 | 48 | 11.9 | 0.42 | 0 |
| u9-discovery-vmc/discovery-no-unify | no-proposer | 2 | 40 | 48 | 48 | 5.7 | 0.83 | 0 |
| u9-discovery-vmc/discovery-no-unify | no-proposer | 3 | 37 | 48 | 48 | 6.2 | 0.77 | 0 |
| u9-discovery-vmc/discovery-random | full | 0 | 39 | 48 | 48 | 1.9 | 0.81 | 0 |
| u9-discovery-vmc/discovery-random | full | 1 | 48 | 48 | 48 | 2.0 | 1.00 | 0 |
| u9-discovery-vmc/discovery-random | full | 2 | 47 | 48 | 48 | 0.8 | 0.98 | 0 |
| u9-discovery-vmc/discovery-random | full | 3 | 46 | 48 | 48 | 1.5 | 0.96 | 0 |
| u9-discovery-vmc/discovery-random | no-dreams | 0 | 36 | 48 | 48 | 2.9 | 0.75 | 0 |
| u9-discovery-vmc/discovery-random | no-dreams | 1 | 47 | 48 | 48 | 1.4 | 0.98 | 0 |
| u9-discovery-vmc/discovery-random | no-dreams | 2 | 46 | 48 | 48 | 1.0 | 0.96 | 0 |
| u9-discovery-vmc/discovery-random | no-dreams | 3 | 46 | 48 | 48 | 1.3 | 0.96 | 0 |
| u9-discovery-vmc/discovery-random | no-library | 0 | MISSING | 48 | 0 | MISSING | MISSING | 0 |
| u9-discovery-vmc/discovery-random | no-library | 1 | MISSING | 48 | 0 | MISSING | MISSING | 0 |
| u9-discovery-vmc/discovery-random | no-library | 2 | MISSING | 48 | 0 | MISSING | MISSING | 0 |
| u9-discovery-vmc/discovery-random | no-library | 3 | MISSING | 48 | 0 | MISSING | MISSING | 0 |
| u9-discovery-vmc/discovery-random | no-proposer | 0 | 30 | 48 | 48 | 4.4 | 0.62 | 0 |
| u9-discovery-vmc/discovery-random | no-proposer | 1 | 9 | 48 | 48 | 15.9 | 0.19 | 0 |
| u9-discovery-vmc/discovery-random | no-proposer | 2 | 28 | 48 | 48 | 1.2 | 0.58 | 0 |
| u9-discovery-vmc/discovery-random | no-proposer | 3 | 41 | 48 | 48 | 1.2 | 0.85 | 0 |

Frozen suites: ["c809fde39db5ec5ecd6085986294c1dd3c53636c039058b511e90481e5081b9f", null]. Cases are comparable only on equal frozen suites.

| case | arm | generation | solved | N (declared) | rows saved | median item wall seconds | fraction of declared N | false credit |
|---|---|---|---|---|---|---|---|---|
| u8-u9-vmc-9036ca3/discovery-off | full | 0 | 36 | 48 | 48 | 4.5 | 0.75 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | full | 1 | 39 | 48 | 48 | 4.0 | 0.81 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | full | 2 | 39 | 48 | 48 | 1.2 | 0.81 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | full | 3 | 41 | 48 | 48 | 3.7 | 0.85 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | no-dreams | 0 | 38 | 48 | 48 | 4.4 | 0.79 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | no-dreams | 1 | 39 | 48 | 48 | 0.9 | 0.81 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | no-dreams | 2 | 40 | 48 | 48 | 0.9 | 0.83 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | no-dreams | 3 | 40 | 48 | 48 | 2.2 | 0.83 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | no-library | 0 | 10 | 48 | 48 | 10.5 | 0.21 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | no-library | 1 | 15 | 48 | 48 | 10.6 | 0.31 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | no-library | 2 | 7 | 48 | 48 | 10.6 | 0.15 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | no-library | 3 | 10 | 48 | 48 | 10.6 | 0.21 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | no-proposer | 0 | 37 | 48 | 48 | 5.9 | 0.77 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | no-proposer | 1 | 26 | 48 | 48 | 9.4 | 0.54 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | no-proposer | 2 | 32 | 48 | 48 | 6.7 | 0.67 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | no-proposer | 3 | 17 | 48 | 48 | 11.4 | 0.35 | 0 |
| u8-u9-vmc-9036ca3/full | full | 0 | 28 | 48 | 48 | 8.5 | 0.58 | 0 |
| u8-u9-vmc-9036ca3/full | full | 1 | 40 | 48 | 48 | 4.0 | 0.83 | 0 |
| u8-u9-vmc-9036ca3/full | full | 2 | 38 | 48 | 48 | 3.7 | 0.79 | 0 |
| u8-u9-vmc-9036ca3/full | full | 3 | 34 | 48 | 48 | 4.6 | 0.71 | 0 |
| u8-u9-vmc-9036ca3/full | no-dreams | 0 | 27 | 48 | 48 | 9.0 | 0.56 | 0 |
| u8-u9-vmc-9036ca3/full | no-dreams | 1 | 37 | 48 | 48 | 3.9 | 0.77 | 0 |
| u8-u9-vmc-9036ca3/full | no-dreams | 2 | 42 | 48 | 48 | 4.1 | 0.88 | 0 |
| u8-u9-vmc-9036ca3/full | no-dreams | 3 | 34 | 48 | 48 | 4.9 | 0.71 | 0 |
| u8-u9-vmc-9036ca3/full | no-library | 0 | 11 | 48 | 48 | 11.2 | 0.23 | 0 |
| u8-u9-vmc-9036ca3/full | no-library | 1 | 8 | 48 | 48 | 11.1 | 0.17 | 0 |
| u8-u9-vmc-9036ca3/full | no-library | 2 | 6 | 48 | 48 | 11.0 | 0.12 | 0 |
| u8-u9-vmc-9036ca3/full | no-library | 3 | 14 | 48 | 48 | 11.0 | 0.29 | 0 |
| u8-u9-vmc-9036ca3/full | no-proposer | 0 | 11 | 48 | 48 | 15.2 | 0.23 | 0 |
| u8-u9-vmc-9036ca3/full | no-proposer | 1 | 6 | 48 | 48 | 13.7 | 0.12 | 0 |
| u8-u9-vmc-9036ca3/full | no-proposer | 2 | 26 | 48 | 48 | 7.2 | 0.54 | 0 |
| u8-u9-vmc-9036ca3/full | no-proposer | 3 | 22 | 48 | 48 | 11.3 | 0.46 | 0 |
| u8-u9-vmc-9036ca3/mem-choice | full | 0 | 26 | 48 | 48 | 9.4 | 0.54 | 0 |
| u8-u9-vmc-9036ca3/mem-choice | full | 1 | 33 | 48 | 48 | 4.3 | 0.69 | 0 |
| u8-u9-vmc-9036ca3/mem-choice | full | 2 | 38 | 48 | 48 | 5.0 | 0.79 | 0 |
| u8-u9-vmc-9036ca3/mem-choice | full | 3 | 36 | 48 | 48 | 3.4 | 0.75 | 0 |
| u8-u9-vmc-9036ca3/mem-choice | no-dreams | 0 | 27 | 48 | 48 | 9.1 | 0.56 | 0 |
| u8-u9-vmc-9036ca3/mem-choice | no-dreams | 1 | 25 | 48 | 48 | 9.5 | 0.52 | 0 |
| u8-u9-vmc-9036ca3/mem-choice | no-dreams | 2 | 35 | 48 | 48 | 5.3 | 0.73 | 0 |
| u8-u9-vmc-9036ca3/mem-choice | no-dreams | 3 | MISSING | 48 | 0 | MISSING | MISSING | 0 |
| u8-u9-vmc-9036ca3/mem-choice | no-library | 0 | MISSING | 48 | 0 | MISSING | MISSING | 0 |
| u8-u9-vmc-9036ca3/mem-choice | no-library | 1 | MISSING | 48 | 0 | MISSING | MISSING | 0 |
| u8-u9-vmc-9036ca3/mem-choice | no-library | 2 | MISSING | 48 | 0 | MISSING | MISSING | 0 |
| u8-u9-vmc-9036ca3/mem-choice | no-library | 3 | MISSING | 48 | 0 | MISSING | MISSING | 0 |
| u8-u9-vmc-9036ca3/mem-choice | no-proposer | 0 | 4 | 48 | 48 | 14.2 | 0.08 | 0 |
| u8-u9-vmc-9036ca3/mem-choice | no-proposer | 1 | 2 | 48 | 48 | 13.8 | 0.04 | 0 |
| u8-u9-vmc-9036ca3/mem-choice | no-proposer | 2 | 24 | 48 | 48 | 9.9 | 0.50 | 0 |
| u8-u9-vmc-9036ca3/mem-choice | no-proposer | 3 | 19 | 48 | 48 | 12.1 | 0.40 | 0 |
| u8-u9-vmc-9036ca3/no-memory | full | 0 | 26 | 48 | 48 | 8.8 | 0.54 | 0 |
| u8-u9-vmc-9036ca3/no-memory | full | 1 | 48 | 48 | 48 | 0.8 | 1.00 | 0 |
| u8-u9-vmc-9036ca3/no-memory | full | 2 | 39 | 48 | 48 | 0.9 | 0.81 | 0 |
| u8-u9-vmc-9036ca3/no-memory | full | 3 | 47 | 48 | 48 | 2.4 | 0.98 | 0 |
| u8-u9-vmc-9036ca3/no-memory | no-dreams | 0 | 25 | 48 | 48 | 9.4 | 0.52 | 0 |
| u8-u9-vmc-9036ca3/no-memory | no-dreams | 1 | 46 | 48 | 48 | 1.3 | 0.96 | 0 |
| u8-u9-vmc-9036ca3/no-memory | no-dreams | 2 | 45 | 48 | 48 | 1.4 | 0.94 | 0 |
| u8-u9-vmc-9036ca3/no-memory | no-dreams | 3 | 45 | 48 | 48 | 3.3 | 0.94 | 0 |
| u8-u9-vmc-9036ca3/no-memory | no-library | 0 | 11 | 48 | 27 | 10.6 | 0.23 | 0 |
| u8-u9-vmc-9036ca3/no-memory | no-library | 1 | MISSING | 48 | 0 | MISSING | MISSING | 0 |
| u8-u9-vmc-9036ca3/no-memory | no-library | 2 | MISSING | 48 | 0 | MISSING | MISSING | 0 |
| u8-u9-vmc-9036ca3/no-memory | no-library | 3 | MISSING | 48 | 0 | MISSING | MISSING | 0 |
| u8-u9-vmc-9036ca3/no-memory | no-proposer | 0 | 20 | 48 | 48 | 13.8 | 0.42 | 0 |
| u8-u9-vmc-9036ca3/no-memory | no-proposer | 1 | 6 | 48 | 48 | 14.3 | 0.12 | 0 |
| u8-u9-vmc-9036ca3/no-memory | no-proposer | 2 | 24 | 48 | 48 | 9.9 | 0.50 | 0 |
| u8-u9-vmc-9036ca3/no-memory | no-proposer | 3 | 20 | 48 | 48 | 12.0 | 0.42 | 0 |
<!-- generated:end assessment -->

<!-- generated:begin full-curve -->
Frozen suites: ["c809fde39db5ec5ecd6085986294c1dd3c53636c039058b511e90481e5081b9f", "f2a2bf86ff5041d695b0e8621e1c47ebeb070900f3b16d870e45e4f8acb37214"]. Cases are comparable only on equal frozen suites.

| case | arm | generation | saved curve metric | value | false credit |
|---|---|---|---|---|---|
| u9-discovery-vmc/discovery | full | 0 | N | 48 | 0 |
| u9-discovery-vmc/discovery | full | 0 | complete | true | 0 |
| u9-discovery-vmc/discovery | full | 0 | g | 0.88 | 0 |
| u9-discovery-vmc/discovery | full | 0 | rows | 48 | 0 |
| u9-discovery-vmc/discovery | full | 0 | solved | 42 | 0 |
| u9-discovery-vmc/discovery | full | 1 | N | 48 | 0 |
| u9-discovery-vmc/discovery | full | 1 | complete | true | 0 |
| u9-discovery-vmc/discovery | full | 1 | g | 0.94 | 0 |
| u9-discovery-vmc/discovery | full | 1 | rows | 48 | 0 |
| u9-discovery-vmc/discovery | full | 1 | solved | 45 | 0 |
| u9-discovery-vmc/discovery | full | 2 | N | 48 | 0 |
| u9-discovery-vmc/discovery | full | 2 | complete | true | 0 |
| u9-discovery-vmc/discovery | full | 2 | g | 0.98 | 0 |
| u9-discovery-vmc/discovery | full | 2 | rows | 48 | 0 |
| u9-discovery-vmc/discovery | full | 2 | solved | 47 | 0 |
| u9-discovery-vmc/discovery | full | 3 | N | 48 | 0 |
| u9-discovery-vmc/discovery | full | 3 | complete | true | 0 |
| u9-discovery-vmc/discovery | full | 3 | g | 0.90 | 0 |
| u9-discovery-vmc/discovery | full | 3 | rows | 48 | 0 |
| u9-discovery-vmc/discovery | full | 3 | solved | 43 | 0 |
| u9-discovery-vmc/discovery-no-unify | full | 0 | N | 48 | 0 |
| u9-discovery-vmc/discovery-no-unify | full | 0 | complete | true | 0 |
| u9-discovery-vmc/discovery-no-unify | full | 0 | g | 0.65 | 0 |
| u9-discovery-vmc/discovery-no-unify | full | 0 | rows | 48 | 0 |
| u9-discovery-vmc/discovery-no-unify | full | 0 | solved | 31 | 0 |
| u9-discovery-vmc/discovery-no-unify | full | 1 | N | 48 | 0 |
| u9-discovery-vmc/discovery-no-unify | full | 1 | complete | true | 0 |
| u9-discovery-vmc/discovery-no-unify | full | 1 | g | 0.96 | 0 |
| u9-discovery-vmc/discovery-no-unify | full | 1 | rows | 48 | 0 |
| u9-discovery-vmc/discovery-no-unify | full | 1 | solved | 46 | 0 |
| u9-discovery-vmc/discovery-no-unify | full | 2 | N | 48 | 0 |
| u9-discovery-vmc/discovery-no-unify | full | 2 | complete | true | 0 |
| u9-discovery-vmc/discovery-no-unify | full | 2 | g | 0.79 | 0 |
| u9-discovery-vmc/discovery-no-unify | full | 2 | rows | 48 | 0 |
| u9-discovery-vmc/discovery-no-unify | full | 2 | solved | 38 | 0 |
| u9-discovery-vmc/discovery-no-unify | full | 3 | N | 48 | 0 |
| u9-discovery-vmc/discovery-no-unify | full | 3 | complete | true | 0 |
| u9-discovery-vmc/discovery-no-unify | full | 3 | g | 0.69 | 0 |
| u9-discovery-vmc/discovery-no-unify | full | 3 | rows | 48 | 0 |
| u9-discovery-vmc/discovery-no-unify | full | 3 | solved | 33 | 0 |
| u9-discovery-vmc/discovery-random | full | 0 | N | 48 | 0 |
| u9-discovery-vmc/discovery-random | full | 0 | complete | true | 0 |
| u9-discovery-vmc/discovery-random | full | 0 | g | 0.81 | 0 |
| u9-discovery-vmc/discovery-random | full | 0 | rows | 48 | 0 |
| u9-discovery-vmc/discovery-random | full | 0 | solved | 39 | 0 |
| u9-discovery-vmc/discovery-random | full | 1 | N | 48 | 0 |
| u9-discovery-vmc/discovery-random | full | 1 | complete | true | 0 |
| u9-discovery-vmc/discovery-random | full | 1 | g | 1.00 | 0 |
| u9-discovery-vmc/discovery-random | full | 1 | rows | 48 | 0 |
| u9-discovery-vmc/discovery-random | full | 1 | solved | 48 | 0 |
| u9-discovery-vmc/discovery-random | full | 2 | N | 48 | 0 |
| u9-discovery-vmc/discovery-random | full | 2 | complete | true | 0 |
| u9-discovery-vmc/discovery-random | full | 2 | g | 0.98 | 0 |
| u9-discovery-vmc/discovery-random | full | 2 | rows | 48 | 0 |
| u9-discovery-vmc/discovery-random | full | 2 | solved | 47 | 0 |
| u9-discovery-vmc/discovery-random | full | 3 | N | 48 | 0 |
| u9-discovery-vmc/discovery-random | full | 3 | complete | true | 0 |
| u9-discovery-vmc/discovery-random | full | 3 | g | 0.96 | 0 |
| u9-discovery-vmc/discovery-random | full | 3 | rows | 48 | 0 |
| u9-discovery-vmc/discovery-random | full | 3 | solved | 46 | 0 |

Frozen suites: ["c809fde39db5ec5ecd6085986294c1dd3c53636c039058b511e90481e5081b9f", null]. Cases are comparable only on equal frozen suites.

| case | arm | generation | saved curve metric | value | false credit |
|---|---|---|---|---|---|
| u8-u9-vmc-9036ca3/discovery-off | full | 0 | N | 48 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | full | 0 | complete | true | 0 |
| u8-u9-vmc-9036ca3/discovery-off | full | 0 | g | 0.75 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | full | 0 | rows | 48 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | full | 0 | solved | 36 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | full | 1 | N | 48 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | full | 1 | complete | true | 0 |
| u8-u9-vmc-9036ca3/discovery-off | full | 1 | g | 0.81 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | full | 1 | rows | 48 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | full | 1 | solved | 39 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | full | 2 | N | 48 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | full | 2 | complete | true | 0 |
| u8-u9-vmc-9036ca3/discovery-off | full | 2 | g | 0.81 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | full | 2 | rows | 48 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | full | 2 | solved | 39 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | full | 3 | N | 48 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | full | 3 | complete | true | 0 |
| u8-u9-vmc-9036ca3/discovery-off | full | 3 | g | 0.85 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | full | 3 | rows | 48 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | full | 3 | solved | 41 | 0 |
| u8-u9-vmc-9036ca3/full | full | 0 | N | 48 | 0 |
| u8-u9-vmc-9036ca3/full | full | 0 | complete | true | 0 |
| u8-u9-vmc-9036ca3/full | full | 0 | g | 0.58 | 0 |
| u8-u9-vmc-9036ca3/full | full | 0 | rows | 48 | 0 |
| u8-u9-vmc-9036ca3/full | full | 0 | solved | 28 | 0 |
| u8-u9-vmc-9036ca3/full | full | 1 | N | 48 | 0 |
| u8-u9-vmc-9036ca3/full | full | 1 | complete | true | 0 |
| u8-u9-vmc-9036ca3/full | full | 1 | g | 0.83 | 0 |
| u8-u9-vmc-9036ca3/full | full | 1 | rows | 48 | 0 |
| u8-u9-vmc-9036ca3/full | full | 1 | solved | 40 | 0 |
| u8-u9-vmc-9036ca3/full | full | 2 | N | 48 | 0 |
| u8-u9-vmc-9036ca3/full | full | 2 | complete | true | 0 |
| u8-u9-vmc-9036ca3/full | full | 2 | g | 0.79 | 0 |
| u8-u9-vmc-9036ca3/full | full | 2 | rows | 48 | 0 |
| u8-u9-vmc-9036ca3/full | full | 2 | solved | 38 | 0 |
| u8-u9-vmc-9036ca3/full | full | 3 | N | 48 | 0 |
| u8-u9-vmc-9036ca3/full | full | 3 | complete | true | 0 |
| u8-u9-vmc-9036ca3/full | full | 3 | g | 0.71 | 0 |
| u8-u9-vmc-9036ca3/full | full | 3 | rows | 48 | 0 |
| u8-u9-vmc-9036ca3/full | full | 3 | solved | 34 | 0 |
| u8-u9-vmc-9036ca3/mem-choice | full | 0 | N | 48 | 0 |
| u8-u9-vmc-9036ca3/mem-choice | full | 0 | complete | true | 0 |
| u8-u9-vmc-9036ca3/mem-choice | full | 0 | g | 0.54 | 0 |
| u8-u9-vmc-9036ca3/mem-choice | full | 0 | rows | 48 | 0 |
| u8-u9-vmc-9036ca3/mem-choice | full | 0 | solved | 26 | 0 |
| u8-u9-vmc-9036ca3/mem-choice | full | 1 | N | 48 | 0 |
| u8-u9-vmc-9036ca3/mem-choice | full | 1 | complete | true | 0 |
| u8-u9-vmc-9036ca3/mem-choice | full | 1 | g | 0.69 | 0 |
| u8-u9-vmc-9036ca3/mem-choice | full | 1 | rows | 48 | 0 |
| u8-u9-vmc-9036ca3/mem-choice | full | 1 | solved | 33 | 0 |
| u8-u9-vmc-9036ca3/mem-choice | full | 2 | N | 48 | 0 |
| u8-u9-vmc-9036ca3/mem-choice | full | 2 | complete | true | 0 |
| u8-u9-vmc-9036ca3/mem-choice | full | 2 | g | 0.79 | 0 |
| u8-u9-vmc-9036ca3/mem-choice | full | 2 | rows | 48 | 0 |
| u8-u9-vmc-9036ca3/mem-choice | full | 2 | solved | 38 | 0 |
| u8-u9-vmc-9036ca3/mem-choice | full | 3 | N | 48 | 0 |
| u8-u9-vmc-9036ca3/mem-choice | full | 3 | complete | true | 0 |
| u8-u9-vmc-9036ca3/mem-choice | full | 3 | g | 0.75 | 0 |
| u8-u9-vmc-9036ca3/mem-choice | full | 3 | rows | 48 | 0 |
| u8-u9-vmc-9036ca3/mem-choice | full | 3 | solved | 36 | 0 |
| u8-u9-vmc-9036ca3/no-memory | full | 0 | N | 48 | 0 |
| u8-u9-vmc-9036ca3/no-memory | full | 0 | complete | true | 0 |
| u8-u9-vmc-9036ca3/no-memory | full | 0 | g | 0.54 | 0 |
| u8-u9-vmc-9036ca3/no-memory | full | 0 | rows | 48 | 0 |
| u8-u9-vmc-9036ca3/no-memory | full | 0 | solved | 26 | 0 |
| u8-u9-vmc-9036ca3/no-memory | full | 1 | N | 48 | 0 |
| u8-u9-vmc-9036ca3/no-memory | full | 1 | complete | true | 0 |
| u8-u9-vmc-9036ca3/no-memory | full | 1 | g | 1.00 | 0 |
| u8-u9-vmc-9036ca3/no-memory | full | 1 | rows | 48 | 0 |
| u8-u9-vmc-9036ca3/no-memory | full | 1 | solved | 48 | 0 |
| u8-u9-vmc-9036ca3/no-memory | full | 2 | N | 48 | 0 |
| u8-u9-vmc-9036ca3/no-memory | full | 2 | complete | true | 0 |
| u8-u9-vmc-9036ca3/no-memory | full | 2 | g | 0.81 | 0 |
| u8-u9-vmc-9036ca3/no-memory | full | 2 | rows | 48 | 0 |
| u8-u9-vmc-9036ca3/no-memory | full | 2 | solved | 39 | 0 |
| u8-u9-vmc-9036ca3/no-memory | full | 3 | N | 48 | 0 |
| u8-u9-vmc-9036ca3/no-memory | full | 3 | complete | true | 0 |
| u8-u9-vmc-9036ca3/no-memory | full | 3 | g | 0.98 | 0 |
| u8-u9-vmc-9036ca3/no-memory | full | 3 | rows | 48 | 0 |
| u8-u9-vmc-9036ca3/no-memory | full | 3 | solved | 47 | 0 |
<!-- generated:end full-curve -->

<!-- generated:begin retention -->
Frozen suites: ["c809fde39db5ec5ecd6085986294c1dd3c53636c039058b511e90481e5081b9f", "f2a2bf86ff5041d695b0e8621e1c47ebeb070900f3b16d870e45e4f8acb37214"]. Cases are comparable only on equal frozen suites.

| case | arm | generation | solved | N (declared) | rows saved | median item wall seconds | fraction of declared N | false credit |
|---|---|---|---|---|---|---|---|---|
| u9-discovery-vmc/discovery | full | 0 | 8 | 8 | 8 | 1.3 | 1.00 | 0 |
| u9-discovery-vmc/discovery | full | 1 | 7 | 8 | 8 | 1.5 | 0.88 | 0 |
| u9-discovery-vmc/discovery | full | 2 | 8 | 8 | 8 | 0.5 | 1.00 | 0 |
| u9-discovery-vmc/discovery | full | 3 | 8 | 8 | 8 | 0.7 | 1.00 | 0 |
| u9-discovery-vmc/discovery | no-dreams | 0 | 8 | 8 | 8 | 1.3 | 1.00 | 0 |
| u9-discovery-vmc/discovery | no-dreams | 1 | 8 | 8 | 8 | 0.6 | 1.00 | 0 |
| u9-discovery-vmc/discovery | no-dreams | 2 | 8 | 8 | 8 | 0.6 | 1.00 | 0 |
| u9-discovery-vmc/discovery | no-dreams | 3 | 8 | 8 | 8 | 1.0 | 1.00 | 0 |
| u9-discovery-vmc/discovery | no-library | 0 | 6 | 8 | 8 | 4.1 | 0.75 | 0 |
| u9-discovery-vmc/discovery | no-library | 1 | MISSING | 8 | 0 | MISSING | MISSING | 0 |
| u9-discovery-vmc/discovery | no-library | 2 | MISSING | 8 | 0 | MISSING | MISSING | 0 |
| u9-discovery-vmc/discovery | no-library | 3 | MISSING | 8 | 0 | MISSING | MISSING | 0 |
| u9-discovery-vmc/discovery | no-proposer | 0 | 8 | 8 | 8 | 1.5 | 1.00 | 0 |
| u9-discovery-vmc/discovery | no-proposer | 1 | 4 | 8 | 8 | 9.8 | 0.50 | 0 |
| u9-discovery-vmc/discovery | no-proposer | 2 | 6 | 8 | 8 | 0.8 | 0.75 | 0 |
| u9-discovery-vmc/discovery | no-proposer | 3 | 5 | 8 | 8 | 0.8 | 0.62 | 0 |
| u9-discovery-vmc/discovery-no-unify | full | 0 | 8 | 8 | 8 | 1.4 | 1.00 | 0 |
| u9-discovery-vmc/discovery-no-unify | full | 1 | 8 | 8 | 8 | 0.6 | 1.00 | 0 |
| u9-discovery-vmc/discovery-no-unify | full | 2 | 8 | 8 | 8 | 1.4 | 1.00 | 0 |
| u9-discovery-vmc/discovery-no-unify | full | 3 | 8 | 8 | 8 | 0.7 | 1.00 | 0 |
| u9-discovery-vmc/discovery-no-unify | no-dreams | 0 | 7 | 8 | 8 | 4.8 | 0.88 | 0 |
| u9-discovery-vmc/discovery-no-unify | no-dreams | 1 | 8 | 8 | 8 | 0.8 | 1.00 | 0 |
| u9-discovery-vmc/discovery-no-unify | no-dreams | 2 | 7 | 8 | 8 | 0.8 | 0.88 | 0 |
| u9-discovery-vmc/discovery-no-unify | no-dreams | 3 | MISSING | 8 | 0 | MISSING | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | no-library | 0 | MISSING | 8 | 0 | MISSING | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | no-library | 1 | MISSING | 8 | 0 | MISSING | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | no-library | 2 | MISSING | 8 | 0 | MISSING | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | no-library | 3 | MISSING | 8 | 0 | MISSING | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | no-proposer | 0 | 5 | 8 | 8 | 7.2 | 0.62 | 0 |
| u9-discovery-vmc/discovery-no-unify | no-proposer | 1 | 5 | 8 | 8 | 8.3 | 0.62 | 0 |
| u9-discovery-vmc/discovery-no-unify | no-proposer | 2 | 7 | 8 | 8 | 4.9 | 0.88 | 0 |
| u9-discovery-vmc/discovery-no-unify | no-proposer | 3 | 5 | 8 | 8 | 9.3 | 0.62 | 0 |
| u9-discovery-vmc/discovery-random | full | 0 | 8 | 8 | 8 | 1.1 | 1.00 | 0 |
| u9-discovery-vmc/discovery-random | full | 1 | 8 | 8 | 8 | 1.2 | 1.00 | 0 |
| u9-discovery-vmc/discovery-random | full | 2 | 8 | 8 | 8 | 0.7 | 1.00 | 0 |
| u9-discovery-vmc/discovery-random | full | 3 | 8 | 8 | 8 | 0.6 | 1.00 | 0 |
| u9-discovery-vmc/discovery-random | no-dreams | 0 | 8 | 8 | 8 | 2.4 | 1.00 | 0 |
| u9-discovery-vmc/discovery-random | no-dreams | 1 | 8 | 8 | 8 | 0.8 | 1.00 | 0 |
| u9-discovery-vmc/discovery-random | no-dreams | 2 | 8 | 8 | 8 | 0.8 | 1.00 | 0 |
| u9-discovery-vmc/discovery-random | no-dreams | 3 | 8 | 8 | 8 | 0.8 | 1.00 | 0 |
| u9-discovery-vmc/discovery-random | no-library | 0 | MISSING | 8 | 0 | MISSING | MISSING | 0 |
| u9-discovery-vmc/discovery-random | no-library | 1 | MISSING | 8 | 0 | MISSING | MISSING | 0 |
| u9-discovery-vmc/discovery-random | no-library | 2 | MISSING | 8 | 0 | MISSING | MISSING | 0 |
| u9-discovery-vmc/discovery-random | no-library | 3 | MISSING | 8 | 0 | MISSING | MISSING | 0 |
| u9-discovery-vmc/discovery-random | no-proposer | 0 | 7 | 8 | 8 | 2.9 | 0.88 | 0 |
| u9-discovery-vmc/discovery-random | no-proposer | 1 | 3 | 8 | 8 | 13.1 | 0.38 | 0 |
| u9-discovery-vmc/discovery-random | no-proposer | 2 | 8 | 8 | 8 | 0.9 | 1.00 | 0 |
| u9-discovery-vmc/discovery-random | no-proposer | 3 | 7 | 8 | 8 | 1.1 | 0.88 | 0 |

Frozen suites: ["c809fde39db5ec5ecd6085986294c1dd3c53636c039058b511e90481e5081b9f", null]. Cases are comparable only on equal frozen suites.

| case | arm | generation | solved | N (declared) | rows saved | median item wall seconds | fraction of declared N | false credit |
|---|---|---|---|---|---|---|---|---|
| u8-u9-vmc-9036ca3/discovery-off | full | 0 | 7 | 8 | 8 | 2.4 | 0.88 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | full | 1 | 7 | 8 | 8 | 3.4 | 0.88 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | full | 2 | 7 | 8 | 8 | 1.0 | 0.88 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | full | 3 | 6 | 8 | 8 | 2.9 | 0.75 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | no-dreams | 0 | 7 | 8 | 8 | 1.2 | 0.88 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | no-dreams | 1 | 6 | 8 | 8 | 0.8 | 0.75 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | no-dreams | 2 | 7 | 8 | 8 | 0.6 | 0.88 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | no-dreams | 3 | 7 | 8 | 8 | 0.5 | 0.88 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | no-library | 0 | 6 | 8 | 8 | 4.0 | 0.75 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | no-library | 1 | 7 | 8 | 8 | 5.5 | 0.88 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | no-library | 2 | 6 | 8 | 8 | 6.4 | 0.75 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | no-library | 3 | 5 | 8 | 8 | 5.0 | 0.62 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | no-proposer | 0 | 7 | 8 | 8 | 2.0 | 0.88 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | no-proposer | 1 | 4 | 8 | 8 | 10.1 | 0.50 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | no-proposer | 2 | 7 | 8 | 8 | 0.6 | 0.88 | 0 |
| u8-u9-vmc-9036ca3/discovery-off | no-proposer | 3 | 3 | 8 | 8 | 11.5 | 0.38 | 0 |
| u8-u9-vmc-9036ca3/full | full | 0 | 3 | 8 | 8 | 11.2 | 0.38 | 0 |
| u8-u9-vmc-9036ca3/full | full | 1 | 7 | 8 | 8 | 2.7 | 0.88 | 0 |
| u8-u9-vmc-9036ca3/full | full | 2 | 7 | 8 | 8 | 3.1 | 0.88 | 0 |
| u8-u9-vmc-9036ca3/full | full | 3 | 7 | 8 | 8 | 4.4 | 0.88 | 0 |
| u8-u9-vmc-9036ca3/full | no-dreams | 0 | 3 | 8 | 8 | 10.8 | 0.38 | 0 |
| u8-u9-vmc-9036ca3/full | no-dreams | 1 | 7 | 8 | 8 | 2.8 | 0.88 | 0 |
| u8-u9-vmc-9036ca3/full | no-dreams | 2 | 7 | 8 | 8 | 4.1 | 0.88 | 0 |
| u8-u9-vmc-9036ca3/full | no-dreams | 3 | 7 | 8 | 8 | 4.1 | 0.88 | 0 |
| u8-u9-vmc-9036ca3/full | no-library | 0 | 4 | 8 | 8 | 9.8 | 0.50 | 0 |
| u8-u9-vmc-9036ca3/full | no-library | 1 | 4 | 8 | 8 | 9.6 | 0.50 | 0 |
| u8-u9-vmc-9036ca3/full | no-library | 2 | 4 | 8 | 8 | 9.9 | 0.50 | 0 |
| u8-u9-vmc-9036ca3/full | no-library | 3 | 3 | 8 | 8 | 11.3 | 0.38 | 0 |
| u8-u9-vmc-9036ca3/full | no-proposer | 0 | 6 | 8 | 8 | 6.3 | 0.75 | 0 |
| u8-u9-vmc-9036ca3/full | no-proposer | 1 | 2 | 8 | 8 | 14.6 | 0.25 | 0 |
| u8-u9-vmc-9036ca3/full | no-proposer | 2 | 3 | 8 | 8 | 12.6 | 0.38 | 0 |
| u8-u9-vmc-9036ca3/full | no-proposer | 3 | 3 | 8 | 8 | 12.0 | 0.38 | 0 |
| u8-u9-vmc-9036ca3/mem-choice | full | 0 | 7 | 8 | 8 | 9.1 | 0.88 | 0 |
| u8-u9-vmc-9036ca3/mem-choice | full | 1 | 5 | 8 | 8 | 4.2 | 0.62 | 0 |
| u8-u9-vmc-9036ca3/mem-choice | full | 2 | 7 | 8 | 8 | 3.6 | 0.88 | 0 |
| u8-u9-vmc-9036ca3/mem-choice | full | 3 | 7 | 8 | 8 | 3.4 | 0.88 | 0 |
| u8-u9-vmc-9036ca3/mem-choice | no-dreams | 0 | 7 | 8 | 8 | 6.7 | 0.88 | 0 |
| u8-u9-vmc-9036ca3/mem-choice | no-dreams | 1 | 5 | 8 | 8 | 5.8 | 0.62 | 0 |
| u8-u9-vmc-9036ca3/mem-choice | no-dreams | 2 | 7 | 8 | 8 | 3.0 | 0.88 | 0 |
| u8-u9-vmc-9036ca3/mem-choice | no-dreams | 3 | MISSING | 8 | 0 | MISSING | MISSING | 0 |
| u8-u9-vmc-9036ca3/mem-choice | no-library | 0 | MISSING | 8 | 0 | MISSING | MISSING | 0 |
| u8-u9-vmc-9036ca3/mem-choice | no-library | 1 | MISSING | 8 | 0 | MISSING | MISSING | 0 |
| u8-u9-vmc-9036ca3/mem-choice | no-library | 2 | MISSING | 8 | 0 | MISSING | MISSING | 0 |
| u8-u9-vmc-9036ca3/mem-choice | no-library | 3 | MISSING | 8 | 0 | MISSING | MISSING | 0 |
| u8-u9-vmc-9036ca3/mem-choice | no-proposer | 0 | 2 | 8 | 8 | 13.0 | 0.25 | 0 |
| u8-u9-vmc-9036ca3/mem-choice | no-proposer | 1 | 0 | 8 | 8 | 13.3 | 0.00 | 0 |
| u8-u9-vmc-9036ca3/mem-choice | no-proposer | 2 | 7 | 8 | 8 | 5.0 | 0.88 | 0 |
| u8-u9-vmc-9036ca3/mem-choice | no-proposer | 3 | 3 | 8 | 8 | 11.8 | 0.38 | 0 |
| u8-u9-vmc-9036ca3/no-memory | full | 0 | 6 | 8 | 8 | 3.6 | 0.75 | 0 |
| u8-u9-vmc-9036ca3/no-memory | full | 1 | 8 | 8 | 8 | 0.6 | 1.00 | 0 |
| u8-u9-vmc-9036ca3/no-memory | full | 2 | 8 | 8 | 8 | 0.6 | 1.00 | 0 |
| u8-u9-vmc-9036ca3/no-memory | full | 3 | 8 | 8 | 8 | 2.1 | 1.00 | 0 |
| u8-u9-vmc-9036ca3/no-memory | no-dreams | 0 | 6 | 8 | 8 | 5.8 | 0.75 | 0 |
| u8-u9-vmc-9036ca3/no-memory | no-dreams | 1 | 6 | 8 | 8 | 2.2 | 0.75 | 0 |
| u8-u9-vmc-9036ca3/no-memory | no-dreams | 2 | 8 | 8 | 8 | 1.5 | 1.00 | 0 |
| u8-u9-vmc-9036ca3/no-memory | no-dreams | 3 | 8 | 8 | 8 | 2.2 | 1.00 | 0 |
| u8-u9-vmc-9036ca3/no-memory | no-library | 0 | MISSING | 8 | 0 | MISSING | MISSING | 0 |
| u8-u9-vmc-9036ca3/no-memory | no-library | 1 | MISSING | 8 | 0 | MISSING | MISSING | 0 |
| u8-u9-vmc-9036ca3/no-memory | no-library | 2 | MISSING | 8 | 0 | MISSING | MISSING | 0 |
| u8-u9-vmc-9036ca3/no-memory | no-library | 3 | MISSING | 8 | 0 | MISSING | MISSING | 0 |
| u8-u9-vmc-9036ca3/no-memory | no-proposer | 0 | 4 | 8 | 8 | 7.9 | 0.50 | 0 |
| u8-u9-vmc-9036ca3/no-memory | no-proposer | 1 | 2 | 8 | 8 | 11.8 | 0.25 | 0 |
| u8-u9-vmc-9036ca3/no-memory | no-proposer | 2 | 5 | 8 | 8 | 1.2 | 0.62 | 0 |
| u8-u9-vmc-9036ca3/no-memory | no-proposer | 3 | 4 | 8 | 8 | 9.7 | 0.50 | 0 |
<!-- generated:end retention -->

<!-- generated:begin habits -->
Frozen suites: ["c809fde39db5ec5ecd6085986294c1dd3c53636c039058b511e90481e5081b9f", "f2a2bf86ff5041d695b0e8621e1c47ebeb070900f3b16d870e45e4f8acb37214"]. Cases are comparable only on equal frozen suites.

| case | saved source / section | arm | generation | metric / JSON path | value | false credit |
|---|---|---|---|---|---|---|
| u9-discovery-vmc/discovery | discovery | full | 0 | by_kind.curve | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | full | 0 | by_kind.drawing | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | full | 0 | by_kind.formula | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | full | 0 | credit | compression credit, not proof of truth; rediscovery of laws we hid | 0 |
| u9-discovery-vmc/discovery | discovery | full | 0 | experiments | 24 | 0 |
| u9-discovery-vmc/discovery | discovery | full | 0 | experiments_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery | discovery | full | 0 | experiments_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery | discovery | full | 0 | laws | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | full | 0 | reuse | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | full | 0 | seconds | 269.0 | 0 |
| u9-discovery-vmc/discovery | discovery | full | 0 | seconds_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery | discovery | full | 0 | seconds_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery | discovery | full | 1 | by_kind.curve | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | full | 1 | by_kind.drawing | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | full | 1 | by_kind.formula | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | full | 1 | credit | compression credit, not proof of truth; rediscovery of laws we hid | 0 |
| u9-discovery-vmc/discovery | discovery | full | 1 | experiments | 9 | 0 |
| u9-discovery-vmc/discovery | discovery | full | 1 | experiments_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery | discovery | full | 1 | experiments_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery | discovery | full | 1 | laws | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | full | 1 | reuse | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | full | 1 | seconds | 216.6 | 0 |
| u9-discovery-vmc/discovery | discovery | full | 1 | seconds_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery | discovery | full | 1 | seconds_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery | discovery | full | 2 | by_kind.curve | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | full | 2 | by_kind.drawing | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | full | 2 | by_kind.formula | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | full | 2 | credit | compression credit, not proof of truth; rediscovery of laws we hid | 0 |
| u9-discovery-vmc/discovery | discovery | full | 2 | experiments | 2 | 0 |
| u9-discovery-vmc/discovery | discovery | full | 2 | experiments_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery | discovery | full | 2 | experiments_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery | discovery | full | 2 | laws | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | full | 2 | reuse | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | full | 2 | seconds | 228.9 | 0 |
| u9-discovery-vmc/discovery | discovery | full | 2 | seconds_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery | discovery | full | 2 | seconds_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery | discovery | full | 3 | by_kind.curve | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | full | 3 | by_kind.drawing | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | full | 3 | by_kind.formula | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | full | 3 | credit | compression credit, not proof of truth; rediscovery of laws we hid | 0 |
| u9-discovery-vmc/discovery | discovery | full | 3 | experiments | 5 | 0 |
| u9-discovery-vmc/discovery | discovery | full | 3 | experiments_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery | discovery | full | 3 | experiments_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery | discovery | full | 3 | laws | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | full | 3 | reuse | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | full | 3 | seconds | 210.0 | 0 |
| u9-discovery-vmc/discovery | discovery | full | 3 | seconds_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery | discovery | full | 3 | seconds_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 0 | by_kind.curve | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 0 | by_kind.drawing | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 0 | by_kind.formula | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 0 | credit | compression credit, not proof of truth; rediscovery of laws we hid | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 0 | experiments | 24 | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 0 | experiments_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 0 | experiments_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 0 | laws | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 0 | reuse | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 0 | seconds | 213.7 | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 0 | seconds_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 0 | seconds_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 1 | by_kind.curve | 1 | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 1 | by_kind.drawing | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 1 | by_kind.formula | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 1 | credit | compression credit, not proof of truth; rediscovery of laws we hid | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 1 | experiments | 10 | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 1 | experiments_per_law | 10.00 | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 1 | experiments_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 1 | laws | 1 | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 1 | reuse | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 1 | seconds | 203.7 | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 1 | seconds_per_law | 203.7 | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 1 | seconds_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 2 | by_kind.curve | 1 | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 2 | by_kind.drawing | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 2 | by_kind.formula | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 2 | credit | compression credit, not proof of truth; rediscovery of laws we hid | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 2 | experiments | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 2 | experiments_per_law | 0.00 | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 2 | experiments_per_law_improved | true | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 2 | laws | 1 | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 2 | reuse | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 2 | seconds | 270.2 | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 2 | seconds_per_law | 270.2 | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 2 | seconds_per_law_improved | false | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 3 | by_kind.curve | 1 | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 3 | by_kind.drawing | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 3 | by_kind.formula | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 3 | credit | compression credit, not proof of truth; rediscovery of laws we hid | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 3 | experiments | 1 | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 3 | experiments_per_law | 1.00 | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 3 | experiments_per_law_improved | false | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 3 | laws | 1 | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 3 | reuse | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 3 | seconds | 208.2 | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 3 | seconds_per_law | 208.2 | 0 |
| u9-discovery-vmc/discovery | discovery | no-dreams | 3 | seconds_per_law_improved | true | 0 |
| u9-discovery-vmc/discovery | discovery | no-library | 0 | by_kind.curve | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-library | 0 | by_kind.drawing | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-library | 0 | by_kind.formula | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-library | 0 | credit | compression credit, not proof of truth; rediscovery of laws we hid | 0 |
| u9-discovery-vmc/discovery | discovery | no-library | 0 | experiments | 24 | 0 |
| u9-discovery-vmc/discovery | discovery | no-library | 0 | experiments_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery | discovery | no-library | 0 | experiments_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery | discovery | no-library | 0 | laws | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-library | 0 | reuse | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-library | 0 | seconds | 225.0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-library | 0 | seconds_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery | discovery | no-library | 0 | seconds_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery | discovery | no-library | 1 | by_kind.curve | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-library | 1 | by_kind.drawing | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-library | 1 | by_kind.formula | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-library | 1 | credit | compression credit, not proof of truth; rediscovery of laws we hid | 0 |
| u9-discovery-vmc/discovery | discovery | no-library | 1 | experiments | 11 | 0 |
| u9-discovery-vmc/discovery | discovery | no-library | 1 | experiments_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery | discovery | no-library | 1 | experiments_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery | discovery | no-library | 1 | laws | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-library | 1 | reuse | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-library | 1 | seconds | 283.9 | 0 |
| u9-discovery-vmc/discovery | discovery | no-library | 1 | seconds_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery | discovery | no-library | 1 | seconds_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 0 | by_kind.curve | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 0 | by_kind.drawing | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 0 | by_kind.formula | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 0 | credit | compression credit, not proof of truth; rediscovery of laws we hid | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 0 | experiments | 24 | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 0 | experiments_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 0 | experiments_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 0 | laws | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 0 | reuse | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 0 | seconds | 237.6 | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 0 | seconds_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 0 | seconds_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 1 | by_kind.curve | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 1 | by_kind.drawing | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 1 | by_kind.formula | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 1 | credit | compression credit, not proof of truth; rediscovery of laws we hid | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 1 | experiments | 9 | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 1 | experiments_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 1 | experiments_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 1 | laws | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 1 | reuse | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 1 | seconds | 204.5 | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 1 | seconds_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 1 | seconds_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 2 | by_kind.curve | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 2 | by_kind.drawing | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 2 | by_kind.formula | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 2 | credit | compression credit, not proof of truth; rediscovery of laws we hid | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 2 | experiments | 2 | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 2 | experiments_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 2 | experiments_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 2 | laws | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 2 | reuse | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 2 | seconds | 234.6 | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 2 | seconds_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 2 | seconds_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 3 | by_kind.curve | 1 | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 3 | by_kind.drawing | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 3 | by_kind.formula | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 3 | credit | compression credit, not proof of truth; rediscovery of laws we hid | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 3 | experiments | 11 | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 3 | experiments_per_law | 11.00 | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 3 | experiments_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 3 | laws | 1 | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 3 | reuse | 0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 3 | seconds | 207.0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 3 | seconds_per_law | 207.0 | 0 |
| u9-discovery-vmc/discovery | discovery | no-proposer | 3 | seconds_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 0 | by_kind.curve | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 0 | by_kind.drawing | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 0 | by_kind.formula | 2 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 0 | credit | compression credit, not proof of truth; rediscovery of laws we hid | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 0 | experiments | 41 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 0 | experiments_per_law | 20.50 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 0 | experiments_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 0 | laws | 2 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 0 | reuse | 2 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 0 | seconds | 222.0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 0 | seconds_per_law | 111.0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 0 | seconds_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 1 | by_kind.curve | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 1 | by_kind.drawing | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 1 | by_kind.formula | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 1 | credit | compression credit, not proof of truth; rediscovery of laws we hid | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 1 | experiments | 2 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 1 | experiments_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 1 | experiments_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 1 | laws | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 1 | reuse | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 1 | seconds | 294.1 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 1 | seconds_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 1 | seconds_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 2 | by_kind.curve | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 2 | by_kind.drawing | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 2 | by_kind.formula | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 2 | credit | compression credit, not proof of truth; rediscovery of laws we hid | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 2 | experiments | 3 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 2 | experiments_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 2 | experiments_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 2 | laws | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 2 | reuse | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 2 | seconds | 246.1 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 2 | seconds_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 2 | seconds_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 3 | by_kind.curve | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 3 | by_kind.drawing | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 3 | by_kind.formula | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 3 | credit | compression credit, not proof of truth; rediscovery of laws we hid | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 3 | experiments | 2 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 3 | experiments_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 3 | experiments_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 3 | laws | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 3 | reuse | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 3 | seconds | 245.2 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 3 | seconds_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | full | 3 | seconds_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 0 | by_kind.curve | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 0 | by_kind.drawing | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 0 | by_kind.formula | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 0 | credit | compression credit, not proof of truth; rediscovery of laws we hid | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 0 | experiments | 24 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 0 | experiments_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 0 | experiments_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 0 | laws | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 0 | reuse | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 0 | seconds | 204.0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 0 | seconds_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 0 | seconds_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 1 | by_kind.curve | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 1 | by_kind.drawing | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 1 | by_kind.formula | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 1 | credit | compression credit, not proof of truth; rediscovery of laws we hid | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 1 | experiments | 7 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 1 | experiments_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 1 | experiments_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 1 | laws | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 1 | reuse | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 1 | seconds | 225.8 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 1 | seconds_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 1 | seconds_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 2 | by_kind.curve | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 2 | by_kind.drawing | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 2 | by_kind.formula | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 2 | credit | compression credit, not proof of truth; rediscovery of laws we hid | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 2 | experiments | 3 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 2 | experiments_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 2 | experiments_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 2 | laws | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 2 | reuse | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 2 | seconds | 203.6 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 2 | seconds_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 2 | seconds_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 3 | by_kind.curve | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 3 | by_kind.drawing | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 3 | by_kind.formula | 1 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 3 | credit | compression credit, not proof of truth; rediscovery of laws we hid | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 3 | experiments | 15 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 3 | experiments_per_law | 15.00 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 3 | experiments_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 3 | laws | 1 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 3 | reuse | 1 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 3 | seconds | 282.5 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 3 | seconds_per_law | 282.5 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 3 | seconds_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 0 | by_kind.curve | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 0 | by_kind.drawing | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 0 | by_kind.formula | 2 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 0 | credit | compression credit, not proof of truth; rediscovery of laws we hid | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 0 | experiments | 41 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 0 | experiments_per_law | 20.50 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 0 | experiments_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 0 | laws | 2 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 0 | reuse | 2 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 0 | seconds | 221.6 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 0 | seconds_per_law | 110.8 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 0 | seconds_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 1 | by_kind.curve | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 1 | by_kind.drawing | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 1 | by_kind.formula | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 1 | credit | compression credit, not proof of truth; rediscovery of laws we hid | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 1 | experiments | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 1 | experiments_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 1 | experiments_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 1 | laws | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 1 | reuse | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 1 | seconds | 438.4 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 1 | seconds_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 1 | seconds_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 2 | by_kind.curve | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 2 | by_kind.drawing | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 2 | by_kind.formula | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 2 | credit | compression credit, not proof of truth; rediscovery of laws we hid | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 2 | experiments | 2 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 2 | experiments_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 2 | experiments_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 2 | laws | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 2 | reuse | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 2 | seconds | 281.0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 2 | seconds_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 2 | seconds_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 3 | by_kind.curve | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 3 | by_kind.drawing | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 3 | by_kind.formula | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 3 | credit | compression credit, not proof of truth; rediscovery of laws we hid | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 3 | experiments | 16 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 3 | experiments_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 3 | experiments_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 3 | laws | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 3 | reuse | 0 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 3 | seconds | 213.3 | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 3 | seconds_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 3 | seconds_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 0 | by_kind.curve | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 0 | by_kind.drawing | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 0 | by_kind.formula | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 0 | credit | compression credit, not proof of truth; rediscovery of laws we hid | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 0 | experiments | 30 | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 0 | experiments_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 0 | experiments_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 0 | laws | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 0 | reuse | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 0 | seconds | 202.6 | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 0 | seconds_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 0 | seconds_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 1 | by_kind.curve | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 1 | by_kind.drawing | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 1 | by_kind.formula | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 1 | credit | compression credit, not proof of truth; rediscovery of laws we hid | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 1 | experiments | 7 | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 1 | experiments_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 1 | experiments_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 1 | laws | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 1 | reuse | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 1 | seconds | 223.3 | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 1 | seconds_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 1 | seconds_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 2 | by_kind.curve | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 2 | by_kind.drawing | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 2 | by_kind.formula | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 2 | credit | compression credit, not proof of truth; rediscovery of laws we hid | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 2 | experiments | 8 | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 2 | experiments_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 2 | experiments_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 2 | laws | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 2 | reuse | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 2 | seconds | 202.9 | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 2 | seconds_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 2 | seconds_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 3 | by_kind.curve | 1 | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 3 | by_kind.drawing | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 3 | by_kind.formula | 1 | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 3 | credit | compression credit, not proof of truth; rediscovery of laws we hid | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 3 | experiments | 4 | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 3 | experiments_per_law | 2.00 | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 3 | experiments_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 3 | laws | 2 | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 3 | reuse | 1 | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 3 | seconds | 205.6 | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 3 | seconds_per_law | 102.8 | 0 |
| u9-discovery-vmc/discovery-random | discovery | full | 3 | seconds_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 0 | by_kind.curve | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 0 | by_kind.drawing | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 0 | by_kind.formula | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 0 | credit | compression credit, not proof of truth; rediscovery of laws we hid | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 0 | experiments | 26 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 0 | experiments_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 0 | experiments_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 0 | laws | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 0 | reuse | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 0 | seconds | 204.5 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 0 | seconds_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 0 | seconds_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 1 | by_kind.curve | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 1 | by_kind.drawing | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 1 | by_kind.formula | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 1 | credit | compression credit, not proof of truth; rediscovery of laws we hid | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 1 | experiments | 8 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 1 | experiments_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 1 | experiments_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 1 | laws | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 1 | reuse | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 1 | seconds | 221.4 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 1 | seconds_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 1 | seconds_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 2 | by_kind.curve | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 2 | by_kind.drawing | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 2 | by_kind.formula | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 2 | credit | compression credit, not proof of truth; rediscovery of laws we hid | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 2 | experiments | 2 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 2 | experiments_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 2 | experiments_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 2 | laws | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 2 | reuse | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 2 | seconds | 210.6 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 2 | seconds_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 2 | seconds_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 3 | by_kind.curve | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 3 | by_kind.drawing | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 3 | by_kind.formula | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 3 | credit | compression credit, not proof of truth; rediscovery of laws we hid | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 3 | experiments | 2 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 3 | experiments_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 3 | experiments_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 3 | laws | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 3 | reuse | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 3 | seconds | 211.5 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 3 | seconds_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-dreams | 3 | seconds_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-library | 0 | by_kind.curve | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-library | 0 | by_kind.drawing | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-library | 0 | by_kind.formula | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-library | 0 | credit | compression credit, not proof of truth; rediscovery of laws we hid | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-library | 0 | experiments | 26 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-library | 0 | experiments_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-library | 0 | experiments_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-library | 0 | laws | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-library | 0 | reuse | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-library | 0 | seconds | 234.2 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-library | 0 | seconds_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-library | 0 | seconds_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 0 | by_kind.curve | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 0 | by_kind.drawing | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 0 | by_kind.formula | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 0 | credit | compression credit, not proof of truth; rediscovery of laws we hid | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 0 | experiments | 32 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 0 | experiments_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 0 | experiments_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 0 | laws | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 0 | reuse | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 0 | seconds | 203.0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 0 | seconds_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 0 | seconds_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 1 | by_kind.curve | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 1 | by_kind.drawing | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 1 | by_kind.formula | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 1 | credit | compression credit, not proof of truth; rediscovery of laws we hid | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 1 | experiments | 3 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 1 | experiments_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 1 | experiments_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 1 | laws | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 1 | reuse | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 1 | seconds | 223.3 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 1 | seconds_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 1 | seconds_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 2 | by_kind.curve | 1 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 2 | by_kind.drawing | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 2 | by_kind.formula | 1 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 2 | credit | compression credit, not proof of truth; rediscovery of laws we hid | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 2 | experiments | 7 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 2 | experiments_per_law | 3.50 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 2 | experiments_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 2 | laws | 2 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 2 | reuse | 1 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 2 | seconds | 324.1 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 2 | seconds_per_law | 162.0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 2 | seconds_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 3 | by_kind.curve | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 3 | by_kind.drawing | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 3 | by_kind.formula | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 3 | credit | compression credit, not proof of truth; rediscovery of laws we hid | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 3 | experiments | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 3 | experiments_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 3 | experiments_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 3 | laws | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 3 | reuse | 0 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 3 | seconds | 315.3 | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 3 | seconds_per_law | MISSING | 0 |
| u9-discovery-vmc/discovery-random | discovery | no-proposer | 3 | seconds_per_law_improved | MISSING | 0 |
| u9-discovery-vmc/discovery | availability | case | saved | evidence | comparison JSON MISSING (not zero; optional for memory-only cases) | 0 |
| u9-discovery-vmc/discovery-no-unify | availability | case | saved | evidence | comparison JSON MISSING (not zero; optional for memory-only cases) | 0 |
| u9-discovery-vmc/discovery-random | availability | case | saved | evidence | comparison JSON MISSING (not zero; optional for memory-only cases) | 0 |

Frozen suites: ["c809fde39db5ec5ecd6085986294c1dd3c53636c039058b511e90481e5081b9f", null]. Cases are comparable only on equal frozen suites.

| case | saved source / section | arm | generation | metric / JSON path | value | false credit |
|---|---|---|---|---|---|---|
| u8-u9-vmc-9036ca3/discovery-off | availability | case | saved | evidence | comparison JSON MISSING (not zero; optional for memory-only cases) | 0 |
| u8-u9-vmc-9036ca3/full | availability | case | saved | evidence | comparison JSON MISSING (not zero; optional for memory-only cases) | 0 |
| u8-u9-vmc-9036ca3/mem-choice | availability | case | saved | evidence | comparison JSON MISSING (not zero; optional for memory-only cases) | 0 |
| u8-u9-vmc-9036ca3/no-memory | availability | case | saved | evidence | comparison JSON MISSING (not zero; optional for memory-only cases) | 0 |
<!-- generated:end habits -->

<!-- generated:begin noise -->
Frozen suites: ["c809fde39db5ec5ecd6085986294c1dd3c53636c039058b511e90481e5081b9f", "f2a2bf86ff5041d695b0e8621e1c47ebeb070900f3b16d870e45e4f8acb37214"]. Cases are comparable only on equal frozen suites. Matching saved switches; code digests may differ (see provenance). Largest replicate gap is used per metric/generation. Comparisons additionally match saved seed, device, allowances and evaluation sizes.

| left | right | section | arm | generation | metric | left value | right value | right - left | measured absolute spread | false credit |
|---|---|---|---|---|---|---|---|---|---|---|
| MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |

Frozen suites: ["c809fde39db5ec5ecd6085986294c1dd3c53636c039058b511e90481e5081b9f", null]. Cases are comparable only on equal frozen suites. Matching saved switches; code digests may differ (see provenance). Largest replicate gap is used per metric/generation. Comparisons additionally match saved seed, device, allowances and evaluation sizes.

| left | right | section | arm | generation | metric | left value | right value | right - left | measured absolute spread | false credit |
|---|---|---|---|---|---|---|---|---|---|---|
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | full | 0 | N | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | full | 0 | fraction | 0.75 | 0.54 | -0.21 | 0.21 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | full | 0 | median item wall seconds | 4.5 | 8.8 | 4.3 | 4.3 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | full | 0 | rows | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | full | 0 | solved | 36 | 26 | -10 | 10 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | full | 1 | N | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | full | 1 | fraction | 0.81 | 1.00 | 0.19 | 0.19 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | full | 1 | median item wall seconds | 4.0 | 0.8 | -3.2 | 3.2 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | full | 1 | rows | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | full | 1 | solved | 39 | 48 | 9 | 9 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | full | 2 | N | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | full | 2 | fraction | 0.81 | 0.81 | 0.00 | 0.00 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | full | 2 | median item wall seconds | 1.2 | 0.9 | -0.4 | 0.4 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | full | 2 | rows | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | full | 2 | solved | 39 | 39 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | full | 3 | N | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | full | 3 | fraction | 0.85 | 0.98 | 0.12 | 0.12 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | full | 3 | median item wall seconds | 3.7 | 2.4 | -1.3 | 1.3 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | full | 3 | rows | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | full | 3 | solved | 41 | 47 | 6 | 6 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 0 | N | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 0 | fraction | 0.79 | 0.52 | -0.27 | 0.27 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 0 | median item wall seconds | 4.4 | 9.4 | 4.9 | 4.9 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 0 | rows | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 0 | solved | 38 | 25 | -13 | 13 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 1 | N | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 1 | fraction | 0.81 | 0.96 | 0.15 | 0.15 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 1 | median item wall seconds | 0.9 | 1.3 | 0.4 | 0.4 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 1 | rows | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 1 | solved | 39 | 46 | 7 | 7 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 2 | N | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 2 | fraction | 0.83 | 0.94 | 0.10 | 0.10 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 2 | median item wall seconds | 0.9 | 1.4 | 0.5 | 0.5 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 2 | rows | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 2 | solved | 40 | 45 | 5 | 5 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 3 | N | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 3 | fraction | 0.83 | 0.94 | 0.10 | 0.10 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 3 | median item wall seconds | 2.2 | 3.3 | 1.1 | 1.1 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 3 | rows | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 3 | solved | 40 | 45 | 5 | 5 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-library | 0 | N | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-library | 0 | fraction | 0.21 | 0.23 | 0.02 | 0.02 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-library | 0 | median item wall seconds | 10.5 | 10.6 | 0.1 | 0.1 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-library | 0 | rows | 48 | 27 | -21 | 21 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-library | 0 | solved | 10 | 11 | 1 | 1 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-library | 1 | N | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-library | 1 | rows | 48 | 0 | -48 | 48 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-library | 2 | N | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-library | 2 | rows | 48 | 0 | -48 | 48 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-library | 3 | N | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-library | 3 | rows | 48 | 0 | -48 | 48 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 0 | N | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 0 | fraction | 0.77 | 0.42 | -0.35 | 0.35 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 0 | median item wall seconds | 5.9 | 13.8 | 7.9 | 7.9 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 0 | rows | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 0 | solved | 37 | 20 | -17 | 17 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 1 | N | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 1 | fraction | 0.54 | 0.12 | -0.42 | 0.42 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 1 | median item wall seconds | 9.4 | 14.3 | 4.9 | 4.9 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 1 | rows | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 1 | solved | 26 | 6 | -20 | 20 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 2 | N | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 2 | fraction | 0.67 | 0.50 | -0.17 | 0.17 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 2 | median item wall seconds | 6.7 | 9.9 | 3.2 | 3.2 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 2 | rows | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 2 | solved | 32 | 24 | -8 | 8 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 3 | N | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 3 | fraction | 0.35 | 0.42 | 0.06 | 0.06 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 3 | median item wall seconds | 11.4 | 12.0 | 0.6 | 0.6 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 3 | rows | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 3 | solved | 17 | 20 | 3 | 3 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | full | 0 | N | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | full | 0 | g | 0.75 | 0.54 | -0.21 | 0.21 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | full | 0 | rows | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | full | 0 | solved | 36 | 26 | -10 | 10 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | full | 1 | N | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | full | 1 | g | 0.81 | 1.00 | 0.19 | 0.19 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | full | 1 | rows | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | full | 1 | solved | 39 | 48 | 9 | 9 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | full | 2 | N | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | full | 2 | g | 0.81 | 0.81 | 0.00 | 0.00 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | full | 2 | rows | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | full | 2 | solved | 39 | 39 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | full | 3 | N | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | full | 3 | g | 0.85 | 0.98 | 0.12 | 0.12 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | full | 3 | rows | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | full | 3 | solved | 41 | 47 | 6 | 6 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 0 | N | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 0 | g | 0.79 | 0.52 | -0.27 | 0.27 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 0 | rows | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 0 | solved | 38 | 25 | -13 | 13 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 1 | N | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 1 | g | 0.81 | 0.96 | 0.15 | 0.15 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 1 | rows | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 1 | solved | 39 | 46 | 7 | 7 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 2 | N | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 2 | g | 0.83 | 0.94 | 0.10 | 0.10 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 2 | rows | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 2 | solved | 40 | 45 | 5 | 5 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 3 | N | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 3 | g | 0.83 | 0.94 | 0.10 | 0.10 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 3 | rows | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 3 | solved | 40 | 45 | 5 | 5 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 0 | N | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 0 | g | 0.21 | 0.23 | 0.02 | 0.02 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 0 | rows | 48 | 27 | -21 | 21 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 0 | solved | 10 | 11 | 1 | 1 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 1 | N | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 1 | g | 0.31 | 0.00 | -0.31 | 0.31 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 1 | rows | 48 | 0 | -48 | 48 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 1 | solved | 15 | 0 | -15 | 15 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 2 | N | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 2 | g | 0.15 | 0.00 | -0.15 | 0.15 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 2 | rows | 48 | 0 | -48 | 48 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 2 | solved | 7 | 0 | -7 | 7 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 3 | N | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 3 | g | 0.21 | 0.00 | -0.21 | 0.21 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 3 | rows | 48 | 0 | -48 | 48 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 3 | solved | 10 | 0 | -10 | 10 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 0 | N | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 0 | g | 0.77 | 0.42 | -0.35 | 0.35 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 0 | rows | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 0 | solved | 37 | 20 | -17 | 17 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 1 | N | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 1 | g | 0.54 | 0.12 | -0.42 | 0.42 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 1 | rows | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 1 | solved | 26 | 6 | -20 | 20 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 2 | N | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 2 | g | 0.67 | 0.50 | -0.17 | 0.17 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 2 | rows | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 2 | solved | 32 | 24 | -8 | 8 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 3 | N | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 3 | g | 0.35 | 0.42 | 0.06 | 0.06 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 3 | rows | 48 | 48 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 3 | solved | 17 | 20 | 3 | 3 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | full | 0 | N | 8 | 8 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | full | 0 | fraction | 0.88 | 0.75 | -0.12 | 0.12 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | full | 0 | median item wall seconds | 2.4 | 3.6 | 1.2 | 1.2 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | full | 0 | rows | 8 | 8 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | full | 0 | solved | 7 | 6 | -1 | 1 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | full | 1 | N | 8 | 8 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | full | 1 | fraction | 0.88 | 1.00 | 0.12 | 0.12 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | full | 1 | median item wall seconds | 3.4 | 0.6 | -2.8 | 2.8 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | full | 1 | rows | 8 | 8 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | full | 1 | solved | 7 | 8 | 1 | 1 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | full | 2 | N | 8 | 8 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | full | 2 | fraction | 0.88 | 1.00 | 0.12 | 0.12 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | full | 2 | median item wall seconds | 1.0 | 0.6 | -0.4 | 0.4 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | full | 2 | rows | 8 | 8 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | full | 2 | solved | 7 | 8 | 1 | 1 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | full | 3 | N | 8 | 8 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | full | 3 | fraction | 0.75 | 1.00 | 0.25 | 0.25 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | full | 3 | median item wall seconds | 2.9 | 2.1 | -0.9 | 0.9 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | full | 3 | rows | 8 | 8 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | full | 3 | solved | 6 | 8 | 2 | 2 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 0 | N | 8 | 8 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 0 | fraction | 0.88 | 0.75 | -0.12 | 0.12 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 0 | median item wall seconds | 1.2 | 5.8 | 4.5 | 4.5 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 0 | rows | 8 | 8 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 0 | solved | 7 | 6 | -1 | 1 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 1 | N | 8 | 8 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 1 | fraction | 0.75 | 0.75 | 0.00 | 0.00 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 1 | median item wall seconds | 0.8 | 2.2 | 1.4 | 1.4 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 1 | rows | 8 | 8 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 1 | solved | 6 | 6 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 2 | N | 8 | 8 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 2 | fraction | 0.88 | 1.00 | 0.12 | 0.12 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 2 | median item wall seconds | 0.6 | 1.5 | 1.0 | 1.0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 2 | rows | 8 | 8 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 2 | solved | 7 | 8 | 1 | 1 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 3 | N | 8 | 8 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 3 | fraction | 0.88 | 1.00 | 0.12 | 0.12 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 3 | median item wall seconds | 0.5 | 2.2 | 1.7 | 1.7 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 3 | rows | 8 | 8 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 3 | solved | 7 | 8 | 1 | 1 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-library | 0 | N | 8 | 8 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-library | 0 | rows | 8 | 0 | -8 | 8 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-library | 1 | N | 8 | 8 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-library | 1 | rows | 8 | 0 | -8 | 8 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-library | 2 | N | 8 | 8 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-library | 2 | rows | 8 | 0 | -8 | 8 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-library | 3 | N | 8 | 8 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-library | 3 | rows | 8 | 0 | -8 | 8 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 0 | N | 8 | 8 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 0 | fraction | 0.88 | 0.50 | -0.38 | 0.38 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 0 | median item wall seconds | 2.0 | 7.9 | 5.9 | 5.9 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 0 | rows | 8 | 8 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 0 | solved | 7 | 4 | -3 | 3 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 1 | N | 8 | 8 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 1 | fraction | 0.50 | 0.25 | -0.25 | 0.25 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 1 | median item wall seconds | 10.1 | 11.8 | 1.8 | 1.8 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 1 | rows | 8 | 8 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 1 | solved | 4 | 2 | -2 | 2 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 2 | N | 8 | 8 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 2 | fraction | 0.88 | 0.62 | -0.25 | 0.25 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 2 | median item wall seconds | 0.6 | 1.2 | 0.6 | 0.6 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 2 | rows | 8 | 8 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 2 | solved | 7 | 5 | -2 | 2 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 3 | N | 8 | 8 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 3 | fraction | 0.38 | 0.50 | 0.12 | 0.12 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 3 | median item wall seconds | 11.5 | 9.7 | -1.8 | 1.8 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 3 | rows | 8 | 8 | 0 | 0 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 3 | solved | 3 | 4 | 1 | 1 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
<!-- generated:end noise -->

<!-- generated:begin differences -->
Frozen suites: ["c809fde39db5ec5ecd6085986294c1dd3c53636c039058b511e90481e5081b9f", "f2a2bf86ff5041d695b0e8621e1c47ebeb070900f3b16d870e45e4f8acb37214"]. Cases are comparable only on equal frozen suites. Smaller absolute differences are within noise; no replicate evidence means noise MISSING. Comparisons additionally match saved seed, device, allowances and evaluation sizes.

| left | right | section | arm | generation | metric | left value | right value | right - left | maximum replicate spread | interpretation | false credit |
|---|---|---|---|---|---|---|---|---|---|---|---|
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | full | 0 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | full | 0 | fraction | 0.88 | 0.65 | -0.23 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | full | 0 | median item wall seconds | 2.6 | 6.9 | 4.3 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | full | 0 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | full | 0 | solved | 42 | 31 | -11 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | full | 1 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | full | 1 | fraction | 0.94 | 0.96 | 0.02 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | full | 1 | median item wall seconds | 2.9 | 3.7 | 0.8 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | full | 1 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | full | 1 | solved | 45 | 46 | 1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | full | 2 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | full | 2 | fraction | 0.98 | 0.79 | -0.19 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | full | 2 | median item wall seconds | 0.8 | 5.4 | 4.5 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | full | 2 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | full | 2 | solved | 47 | 38 | -9 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | full | 3 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | full | 3 | fraction | 0.90 | 0.69 | -0.21 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | full | 3 | median item wall seconds | 0.6 | 4.2 | 3.6 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | full | 3 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | full | 3 | solved | 43 | 33 | -10 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | no-dreams | 0 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | no-dreams | 0 | fraction | 0.96 | 0.58 | -0.38 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | no-dreams | 0 | median item wall seconds | 2.3 | 7.1 | 4.8 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | no-dreams | 0 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | no-dreams | 0 | solved | 46 | 28 | -18 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | no-dreams | 1 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | no-dreams | 1 | fraction | 0.96 | 0.85 | -0.10 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | no-dreams | 1 | median item wall seconds | 1.7 | 5.0 | 3.3 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | no-dreams | 1 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | no-dreams | 1 | solved | 46 | 41 | -5 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | no-dreams | 2 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | no-dreams | 2 | fraction | 0.98 | 0.52 | -0.46 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | no-dreams | 2 | median item wall seconds | 0.8 | 7.0 | 6.2 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | no-dreams | 2 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | no-dreams | 2 | solved | 47 | 25 | -22 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | no-dreams | 3 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | no-dreams | 3 | rows | 48 | 0 | -48 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | no-library | 0 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | no-library | 0 | rows | 48 | 0 | -48 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | no-library | 1 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | no-library | 1 | rows | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | no-library | 2 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | no-library | 2 | rows | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | no-library | 3 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | no-library | 3 | rows | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | no-proposer | 0 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | no-proposer | 0 | fraction | 0.62 | 0.62 | 0.00 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | no-proposer | 0 | median item wall seconds | 2.3 | 7.6 | 5.3 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | no-proposer | 0 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | no-proposer | 0 | solved | 30 | 30 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | no-proposer | 1 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | no-proposer | 1 | fraction | 0.40 | 0.42 | 0.02 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | no-proposer | 1 | median item wall seconds | 11.7 | 11.9 | 0.3 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | no-proposer | 1 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | no-proposer | 1 | solved | 19 | 20 | 1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | no-proposer | 2 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | no-proposer | 2 | fraction | 0.79 | 0.83 | 0.04 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | no-proposer | 2 | median item wall seconds | 0.8 | 5.7 | 4.9 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | no-proposer | 2 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | no-proposer | 2 | solved | 38 | 40 | 2 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | no-proposer | 3 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | no-proposer | 3 | fraction | 0.77 | 0.77 | 0.00 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | no-proposer | 3 | median item wall seconds | 0.9 | 6.2 | 5.3 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | no-proposer | 3 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | assessment | no-proposer | 3 | solved | 37 | 37 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | full | 0 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | full | 0 | g | 0.88 | 0.65 | -0.23 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | full | 0 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | full | 0 | solved | 42 | 31 | -11 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | full | 1 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | full | 1 | g | 0.94 | 0.96 | 0.02 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | full | 1 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | full | 1 | solved | 45 | 46 | 1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | full | 2 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | full | 2 | g | 0.98 | 0.79 | -0.19 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | full | 2 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | full | 2 | solved | 47 | 38 | -9 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | full | 3 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | full | 3 | g | 0.90 | 0.69 | -0.21 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | full | 3 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | full | 3 | solved | 43 | 33 | -10 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-dreams | 0 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-dreams | 0 | g | 0.96 | 0.58 | -0.38 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-dreams | 0 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-dreams | 0 | solved | 46 | 28 | -18 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-dreams | 1 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-dreams | 1 | g | 0.96 | 0.85 | -0.10 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-dreams | 1 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-dreams | 1 | solved | 46 | 41 | -5 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-dreams | 2 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-dreams | 2 | g | 0.98 | 0.52 | -0.46 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-dreams | 2 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-dreams | 2 | solved | 47 | 25 | -22 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-dreams | 3 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-dreams | 3 | g | 0.96 | 0.00 | -0.96 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-dreams | 3 | rows | 48 | 0 | -48 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-dreams | 3 | solved | 46 | 0 | -46 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-library | 0 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-library | 0 | g | 0.23 | 0.00 | -0.23 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-library | 0 | rows | 48 | 0 | -48 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-library | 0 | solved | 11 | 0 | -11 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-library | 1 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-library | 1 | g | 0.00 | 0.00 | 0.00 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-library | 1 | rows | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-library | 1 | solved | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-library | 2 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-library | 2 | g | 0.00 | 0.00 | 0.00 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-library | 2 | rows | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-library | 2 | solved | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-library | 3 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-library | 3 | g | 0.00 | 0.00 | 0.00 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-library | 3 | rows | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-library | 3 | solved | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-proposer | 0 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-proposer | 0 | g | 0.62 | 0.62 | 0.00 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-proposer | 0 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-proposer | 0 | solved | 30 | 30 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-proposer | 1 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-proposer | 1 | g | 0.40 | 0.42 | 0.02 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-proposer | 1 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-proposer | 1 | solved | 19 | 20 | 1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-proposer | 2 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-proposer | 2 | g | 0.79 | 0.83 | 0.04 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-proposer | 2 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-proposer | 2 | solved | 38 | 40 | 2 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-proposer | 3 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-proposer | 3 | g | 0.77 | 0.77 | 0.00 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-proposer | 3 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | curve | no-proposer | 3 | solved | 37 | 37 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | full | 0 | by_kind.curve | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | full | 0 | by_kind.drawing | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | full | 0 | by_kind.formula | 0 | 2 | 2 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | full | 0 | experiments | 24 | 41 | 17 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | full | 0 | laws | 0 | 2 | 2 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | full | 0 | reuse | 0 | 2 | 2 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | full | 0 | seconds | 269.0 | 222.0 | -47.1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | full | 1 | by_kind.curve | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | full | 1 | by_kind.drawing | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | full | 1 | by_kind.formula | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | full | 1 | experiments | 9 | 2 | -7 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | full | 1 | laws | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | full | 1 | reuse | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | full | 1 | seconds | 216.6 | 294.1 | 77.5 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | full | 2 | by_kind.curve | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | full | 2 | by_kind.drawing | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | full | 2 | by_kind.formula | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | full | 2 | experiments | 2 | 3 | 1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | full | 2 | laws | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | full | 2 | reuse | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | full | 2 | seconds | 228.9 | 246.1 | 17.2 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | full | 3 | by_kind.curve | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | full | 3 | by_kind.drawing | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | full | 3 | by_kind.formula | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | full | 3 | experiments | 5 | 2 | -3 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | full | 3 | laws | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | full | 3 | reuse | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | full | 3 | seconds | 210.0 | 245.2 | 35.2 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 0 | by_kind.curve | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 0 | by_kind.drawing | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 0 | by_kind.formula | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 0 | experiments | 24 | 24 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 0 | laws | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 0 | reuse | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 0 | seconds | 213.7 | 204.0 | -9.7 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 1 | by_kind.curve | 1 | 0 | -1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 1 | by_kind.drawing | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 1 | by_kind.formula | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 1 | experiments | 10 | 7 | -3 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 1 | laws | 1 | 0 | -1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 1 | reuse | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 1 | seconds | 203.7 | 225.8 | 22.1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 2 | by_kind.curve | 1 | 0 | -1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 2 | by_kind.drawing | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 2 | by_kind.formula | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 2 | experiments | 0 | 3 | 3 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 2 | laws | 1 | 0 | -1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 2 | reuse | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 2 | seconds | 270.2 | 203.6 | -66.7 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 3 | by_kind.curve | 1 | 0 | -1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 3 | by_kind.drawing | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 3 | by_kind.formula | 0 | 1 | 1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 3 | experiments | 1 | 15 | 14 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 3 | experiments_per_law | 1.00 | 15.00 | 14.00 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 3 | laws | 1 | 1 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 3 | reuse | 0 | 1 | 1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 3 | seconds | 208.2 | 282.5 | 74.3 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-dreams | 3 | seconds_per_law | 208.2 | 282.5 | 74.3 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 0 | by_kind.curve | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 0 | by_kind.drawing | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 0 | by_kind.formula | 0 | 2 | 2 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 0 | experiments | 24 | 41 | 17 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 0 | laws | 0 | 2 | 2 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 0 | reuse | 0 | 2 | 2 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 0 | seconds | 237.6 | 221.6 | -15.9 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 1 | by_kind.curve | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 1 | by_kind.drawing | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 1 | by_kind.formula | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 1 | experiments | 9 | 0 | -9 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 1 | laws | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 1 | reuse | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 1 | seconds | 204.5 | 438.4 | 233.8 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 2 | by_kind.curve | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 2 | by_kind.drawing | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 2 | by_kind.formula | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 2 | experiments | 2 | 2 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 2 | laws | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 2 | reuse | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 2 | seconds | 234.6 | 281.0 | 46.4 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 3 | by_kind.curve | 1 | 0 | -1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 3 | by_kind.drawing | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 3 | by_kind.formula | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 3 | experiments | 11 | 16 | 5 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 3 | laws | 1 | 0 | -1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 3 | reuse | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | discovery | no-proposer | 3 | seconds | 207.0 | 213.3 | 6.3 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | full | 0 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | full | 0 | fraction | 1.00 | 1.00 | 0.00 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | full | 0 | median item wall seconds | 1.3 | 1.4 | 0.1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | full | 0 | rows | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | full | 0 | solved | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | full | 1 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | full | 1 | fraction | 0.88 | 1.00 | 0.12 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | full | 1 | median item wall seconds | 1.5 | 0.6 | -0.9 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | full | 1 | rows | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | full | 1 | solved | 7 | 8 | 1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | full | 2 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | full | 2 | fraction | 1.00 | 1.00 | 0.00 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | full | 2 | median item wall seconds | 0.5 | 1.4 | 0.9 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | full | 2 | rows | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | full | 2 | solved | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | full | 3 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | full | 3 | fraction | 1.00 | 1.00 | 0.00 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | full | 3 | median item wall seconds | 0.7 | 0.7 | 0.0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | full | 3 | rows | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | full | 3 | solved | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | no-dreams | 0 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | no-dreams | 0 | fraction | 1.00 | 0.88 | -0.12 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | no-dreams | 0 | median item wall seconds | 1.3 | 4.8 | 3.5 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | no-dreams | 0 | rows | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | no-dreams | 0 | solved | 8 | 7 | -1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | no-dreams | 1 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | no-dreams | 1 | fraction | 1.00 | 1.00 | 0.00 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | no-dreams | 1 | median item wall seconds | 0.6 | 0.8 | 0.2 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | no-dreams | 1 | rows | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | no-dreams | 1 | solved | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | no-dreams | 2 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | no-dreams | 2 | fraction | 1.00 | 0.88 | -0.12 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | no-dreams | 2 | median item wall seconds | 0.6 | 0.8 | 0.2 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | no-dreams | 2 | rows | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | no-dreams | 2 | solved | 8 | 7 | -1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | no-dreams | 3 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | no-dreams | 3 | rows | 8 | 0 | -8 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | no-library | 0 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | no-library | 0 | rows | 8 | 0 | -8 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | no-library | 1 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | no-library | 1 | rows | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | no-library | 2 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | no-library | 2 | rows | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | no-library | 3 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | no-library | 3 | rows | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | no-proposer | 0 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | no-proposer | 0 | fraction | 1.00 | 0.62 | -0.38 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | no-proposer | 0 | median item wall seconds | 1.5 | 7.2 | 5.7 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | no-proposer | 0 | rows | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | no-proposer | 0 | solved | 8 | 5 | -3 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | no-proposer | 1 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | no-proposer | 1 | fraction | 0.50 | 0.62 | 0.12 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | no-proposer | 1 | median item wall seconds | 9.8 | 8.3 | -1.5 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | no-proposer | 1 | rows | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | no-proposer | 1 | solved | 4 | 5 | 1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | no-proposer | 2 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | no-proposer | 2 | fraction | 0.75 | 0.88 | 0.12 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | no-proposer | 2 | median item wall seconds | 0.8 | 4.9 | 4.1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | no-proposer | 2 | rows | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | no-proposer | 2 | solved | 6 | 7 | 1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | no-proposer | 3 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | no-proposer | 3 | fraction | 0.62 | 0.62 | 0.00 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | no-proposer | 3 | median item wall seconds | 0.8 | 9.3 | 8.5 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | no-proposer | 3 | rows | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | retention | no-proposer | 3 | solved | 5 | 5 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | full | 0 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | full | 0 | fraction | 0.88 | 0.81 | -0.06 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | full | 0 | median item wall seconds | 2.6 | 1.9 | -0.7 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | full | 0 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | full | 0 | solved | 42 | 39 | -3 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | full | 1 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | full | 1 | fraction | 0.94 | 1.00 | 0.06 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | full | 1 | median item wall seconds | 2.9 | 2.0 | -1.0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | full | 1 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | full | 1 | solved | 45 | 48 | 3 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | full | 2 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | full | 2 | fraction | 0.98 | 0.98 | 0.00 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | full | 2 | median item wall seconds | 0.8 | 0.8 | -0.0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | full | 2 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | full | 2 | solved | 47 | 47 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | full | 3 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | full | 3 | fraction | 0.90 | 0.96 | 0.06 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | full | 3 | median item wall seconds | 0.6 | 1.5 | 0.8 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | full | 3 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | full | 3 | solved | 43 | 46 | 3 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-dreams | 0 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-dreams | 0 | fraction | 0.96 | 0.75 | -0.21 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-dreams | 0 | median item wall seconds | 2.3 | 2.9 | 0.6 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-dreams | 0 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-dreams | 0 | solved | 46 | 36 | -10 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-dreams | 1 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-dreams | 1 | fraction | 0.96 | 0.98 | 0.02 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-dreams | 1 | median item wall seconds | 1.7 | 1.4 | -0.3 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-dreams | 1 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-dreams | 1 | solved | 46 | 47 | 1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-dreams | 2 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-dreams | 2 | fraction | 0.98 | 0.96 | -0.02 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-dreams | 2 | median item wall seconds | 0.8 | 1.0 | 0.2 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-dreams | 2 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-dreams | 2 | solved | 47 | 46 | -1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-dreams | 3 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-dreams | 3 | fraction | 0.96 | 0.96 | 0.00 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-dreams | 3 | median item wall seconds | 1.3 | 1.3 | -0.0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-dreams | 3 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-dreams | 3 | solved | 46 | 46 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-library | 0 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-library | 0 | rows | 48 | 0 | -48 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-library | 1 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-library | 1 | rows | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-library | 2 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-library | 2 | rows | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-library | 3 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-library | 3 | rows | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-proposer | 0 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-proposer | 0 | fraction | 0.62 | 0.62 | 0.00 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-proposer | 0 | median item wall seconds | 2.3 | 4.4 | 2.1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-proposer | 0 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-proposer | 0 | solved | 30 | 30 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-proposer | 1 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-proposer | 1 | fraction | 0.40 | 0.19 | -0.21 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-proposer | 1 | median item wall seconds | 11.7 | 15.9 | 4.2 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-proposer | 1 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-proposer | 1 | solved | 19 | 9 | -10 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-proposer | 2 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-proposer | 2 | fraction | 0.79 | 0.58 | -0.21 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-proposer | 2 | median item wall seconds | 0.8 | 1.2 | 0.4 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-proposer | 2 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-proposer | 2 | solved | 38 | 28 | -10 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-proposer | 3 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-proposer | 3 | fraction | 0.77 | 0.85 | 0.08 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-proposer | 3 | median item wall seconds | 0.9 | 1.2 | 0.3 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-proposer | 3 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | assessment | no-proposer | 3 | solved | 37 | 41 | 4 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | full | 0 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | full | 0 | g | 0.88 | 0.81 | -0.06 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | full | 0 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | full | 0 | solved | 42 | 39 | -3 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | full | 1 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | full | 1 | g | 0.94 | 1.00 | 0.06 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | full | 1 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | full | 1 | solved | 45 | 48 | 3 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | full | 2 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | full | 2 | g | 0.98 | 0.98 | 0.00 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | full | 2 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | full | 2 | solved | 47 | 47 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | full | 3 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | full | 3 | g | 0.90 | 0.96 | 0.06 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | full | 3 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | full | 3 | solved | 43 | 46 | 3 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-dreams | 0 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-dreams | 0 | g | 0.96 | 0.75 | -0.21 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-dreams | 0 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-dreams | 0 | solved | 46 | 36 | -10 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-dreams | 1 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-dreams | 1 | g | 0.96 | 0.98 | 0.02 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-dreams | 1 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-dreams | 1 | solved | 46 | 47 | 1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-dreams | 2 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-dreams | 2 | g | 0.98 | 0.96 | -0.02 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-dreams | 2 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-dreams | 2 | solved | 47 | 46 | -1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-dreams | 3 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-dreams | 3 | g | 0.96 | 0.96 | 0.00 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-dreams | 3 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-dreams | 3 | solved | 46 | 46 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-library | 0 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-library | 0 | g | 0.23 | 0.00 | -0.23 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-library | 0 | rows | 48 | 0 | -48 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-library | 0 | solved | 11 | 0 | -11 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-library | 1 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-library | 1 | g | 0.00 | 0.00 | 0.00 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-library | 1 | rows | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-library | 1 | solved | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-library | 2 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-library | 2 | g | 0.00 | 0.00 | 0.00 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-library | 2 | rows | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-library | 2 | solved | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-library | 3 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-library | 3 | g | 0.00 | 0.00 | 0.00 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-library | 3 | rows | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-library | 3 | solved | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-proposer | 0 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-proposer | 0 | g | 0.62 | 0.62 | 0.00 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-proposer | 0 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-proposer | 0 | solved | 30 | 30 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-proposer | 1 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-proposer | 1 | g | 0.40 | 0.19 | -0.21 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-proposer | 1 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-proposer | 1 | solved | 19 | 9 | -10 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-proposer | 2 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-proposer | 2 | g | 0.79 | 0.58 | -0.21 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-proposer | 2 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-proposer | 2 | solved | 38 | 28 | -10 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-proposer | 3 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-proposer | 3 | g | 0.77 | 0.85 | 0.08 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-proposer | 3 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | curve | no-proposer | 3 | solved | 37 | 41 | 4 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | full | 0 | by_kind.curve | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | full | 0 | by_kind.drawing | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | full | 0 | by_kind.formula | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | full | 0 | experiments | 24 | 30 | 6 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | full | 0 | laws | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | full | 0 | reuse | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | full | 0 | seconds | 269.0 | 202.6 | -66.5 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | full | 1 | by_kind.curve | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | full | 1 | by_kind.drawing | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | full | 1 | by_kind.formula | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | full | 1 | experiments | 9 | 7 | -2 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | full | 1 | laws | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | full | 1 | reuse | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | full | 1 | seconds | 216.6 | 223.3 | 6.6 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | full | 2 | by_kind.curve | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | full | 2 | by_kind.drawing | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | full | 2 | by_kind.formula | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | full | 2 | experiments | 2 | 8 | 6 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | full | 2 | laws | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | full | 2 | reuse | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | full | 2 | seconds | 228.9 | 202.9 | -26.0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | full | 3 | by_kind.curve | 0 | 1 | 1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | full | 3 | by_kind.drawing | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | full | 3 | by_kind.formula | 0 | 1 | 1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | full | 3 | experiments | 5 | 4 | -1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | full | 3 | laws | 0 | 2 | 2 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | full | 3 | reuse | 0 | 1 | 1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | full | 3 | seconds | 210.0 | 205.6 | -4.4 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-dreams | 0 | by_kind.curve | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-dreams | 0 | by_kind.drawing | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-dreams | 0 | by_kind.formula | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-dreams | 0 | experiments | 24 | 26 | 2 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-dreams | 0 | laws | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-dreams | 0 | reuse | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-dreams | 0 | seconds | 213.7 | 204.5 | -9.2 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-dreams | 1 | by_kind.curve | 1 | 0 | -1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-dreams | 1 | by_kind.drawing | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-dreams | 1 | by_kind.formula | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-dreams | 1 | experiments | 10 | 8 | -2 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-dreams | 1 | laws | 1 | 0 | -1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-dreams | 1 | reuse | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-dreams | 1 | seconds | 203.7 | 221.4 | 17.6 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-dreams | 2 | by_kind.curve | 1 | 0 | -1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-dreams | 2 | by_kind.drawing | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-dreams | 2 | by_kind.formula | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-dreams | 2 | experiments | 0 | 2 | 2 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-dreams | 2 | laws | 1 | 0 | -1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-dreams | 2 | reuse | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-dreams | 2 | seconds | 270.2 | 210.6 | -59.7 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-dreams | 3 | by_kind.curve | 1 | 0 | -1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-dreams | 3 | by_kind.drawing | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-dreams | 3 | by_kind.formula | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-dreams | 3 | experiments | 1 | 2 | 1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-dreams | 3 | laws | 1 | 0 | -1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-dreams | 3 | reuse | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-dreams | 3 | seconds | 208.2 | 211.5 | 3.2 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-library | 0 | by_kind.curve | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-library | 0 | by_kind.drawing | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-library | 0 | by_kind.formula | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-library | 0 | experiments | 24 | 26 | 2 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-library | 0 | laws | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-library | 0 | reuse | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-library | 0 | seconds | 225.0 | 234.2 | 9.2 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-proposer | 0 | by_kind.curve | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-proposer | 0 | by_kind.drawing | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-proposer | 0 | by_kind.formula | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-proposer | 0 | experiments | 24 | 32 | 8 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-proposer | 0 | laws | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-proposer | 0 | reuse | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-proposer | 0 | seconds | 237.6 | 203.0 | -34.6 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-proposer | 1 | by_kind.curve | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-proposer | 1 | by_kind.drawing | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-proposer | 1 | by_kind.formula | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-proposer | 1 | experiments | 9 | 3 | -6 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-proposer | 1 | laws | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-proposer | 1 | reuse | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-proposer | 1 | seconds | 204.5 | 223.3 | 18.8 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-proposer | 2 | by_kind.curve | 0 | 1 | 1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-proposer | 2 | by_kind.drawing | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-proposer | 2 | by_kind.formula | 0 | 1 | 1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-proposer | 2 | experiments | 2 | 7 | 5 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-proposer | 2 | laws | 0 | 2 | 2 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-proposer | 2 | reuse | 0 | 1 | 1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-proposer | 2 | seconds | 234.6 | 324.1 | 89.5 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-proposer | 3 | by_kind.curve | 1 | 0 | -1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-proposer | 3 | by_kind.drawing | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-proposer | 3 | by_kind.formula | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-proposer | 3 | experiments | 11 | 0 | -11 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-proposer | 3 | laws | 1 | 0 | -1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-proposer | 3 | reuse | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | discovery | no-proposer | 3 | seconds | 207.0 | 315.3 | 108.3 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | full | 0 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | full | 0 | fraction | 1.00 | 1.00 | 0.00 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | full | 0 | median item wall seconds | 1.3 | 1.1 | -0.2 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | full | 0 | rows | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | full | 0 | solved | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | full | 1 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | full | 1 | fraction | 0.88 | 1.00 | 0.12 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | full | 1 | median item wall seconds | 1.5 | 1.2 | -0.4 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | full | 1 | rows | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | full | 1 | solved | 7 | 8 | 1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | full | 2 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | full | 2 | fraction | 1.00 | 1.00 | 0.00 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | full | 2 | median item wall seconds | 0.5 | 0.7 | 0.1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | full | 2 | rows | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | full | 2 | solved | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | full | 3 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | full | 3 | fraction | 1.00 | 1.00 | 0.00 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | full | 3 | median item wall seconds | 0.7 | 0.6 | -0.0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | full | 3 | rows | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | full | 3 | solved | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-dreams | 0 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-dreams | 0 | fraction | 1.00 | 1.00 | 0.00 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-dreams | 0 | median item wall seconds | 1.3 | 2.4 | 1.1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-dreams | 0 | rows | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-dreams | 0 | solved | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-dreams | 1 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-dreams | 1 | fraction | 1.00 | 1.00 | 0.00 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-dreams | 1 | median item wall seconds | 0.6 | 0.8 | 0.2 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-dreams | 1 | rows | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-dreams | 1 | solved | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-dreams | 2 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-dreams | 2 | fraction | 1.00 | 1.00 | 0.00 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-dreams | 2 | median item wall seconds | 0.6 | 0.8 | 0.2 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-dreams | 2 | rows | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-dreams | 2 | solved | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-dreams | 3 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-dreams | 3 | fraction | 1.00 | 1.00 | 0.00 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-dreams | 3 | median item wall seconds | 1.0 | 0.8 | -0.2 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-dreams | 3 | rows | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-dreams | 3 | solved | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-library | 0 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-library | 0 | rows | 8 | 0 | -8 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-library | 1 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-library | 1 | rows | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-library | 2 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-library | 2 | rows | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-library | 3 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-library | 3 | rows | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-proposer | 0 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-proposer | 0 | fraction | 1.00 | 0.88 | -0.12 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-proposer | 0 | median item wall seconds | 1.5 | 2.9 | 1.5 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-proposer | 0 | rows | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-proposer | 0 | solved | 8 | 7 | -1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-proposer | 1 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-proposer | 1 | fraction | 0.50 | 0.38 | -0.12 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-proposer | 1 | median item wall seconds | 9.8 | 13.1 | 3.3 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-proposer | 1 | rows | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-proposer | 1 | solved | 4 | 3 | -1 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-proposer | 2 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-proposer | 2 | fraction | 0.75 | 1.00 | 0.25 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-proposer | 2 | median item wall seconds | 0.8 | 0.9 | 0.2 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-proposer | 2 | rows | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-proposer | 2 | solved | 6 | 8 | 2 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-proposer | 3 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-proposer | 3 | fraction | 0.62 | 0.88 | 0.25 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-proposer | 3 | median item wall seconds | 0.8 | 1.1 | 0.3 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-proposer | 3 | rows | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | retention | no-proposer | 3 | solved | 5 | 7 | 2 | MISSING | noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | full | 0 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | full | 0 | fraction | 0.65 | 0.81 | 0.17 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | full | 0 | median item wall seconds | 6.9 | 1.9 | -5.0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | full | 0 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | full | 0 | solved | 31 | 39 | 8 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | full | 1 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | full | 1 | fraction | 0.96 | 1.00 | 0.04 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | full | 1 | median item wall seconds | 3.7 | 2.0 | -1.8 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | full | 1 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | full | 1 | solved | 46 | 48 | 2 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | full | 2 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | full | 2 | fraction | 0.79 | 0.98 | 0.19 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | full | 2 | median item wall seconds | 5.4 | 0.8 | -4.5 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | full | 2 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | full | 2 | solved | 38 | 47 | 9 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | full | 3 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | full | 3 | fraction | 0.69 | 0.96 | 0.27 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | full | 3 | median item wall seconds | 4.2 | 1.5 | -2.7 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | full | 3 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | full | 3 | solved | 33 | 46 | 13 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | no-dreams | 0 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | no-dreams | 0 | fraction | 0.58 | 0.75 | 0.17 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | no-dreams | 0 | median item wall seconds | 7.1 | 2.9 | -4.1 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | no-dreams | 0 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | no-dreams | 0 | solved | 28 | 36 | 8 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | no-dreams | 1 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | no-dreams | 1 | fraction | 0.85 | 0.98 | 0.12 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | no-dreams | 1 | median item wall seconds | 5.0 | 1.4 | -3.6 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | no-dreams | 1 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | no-dreams | 1 | solved | 41 | 47 | 6 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | no-dreams | 2 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | no-dreams | 2 | fraction | 0.52 | 0.96 | 0.44 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | no-dreams | 2 | median item wall seconds | 7.0 | 1.0 | -6.0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | no-dreams | 2 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | no-dreams | 2 | solved | 25 | 46 | 21 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | no-dreams | 3 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | no-dreams | 3 | rows | 0 | 48 | 48 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | no-library | 0 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | no-library | 0 | rows | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | no-library | 1 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | no-library | 1 | rows | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | no-library | 2 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | no-library | 2 | rows | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | no-library | 3 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | no-library | 3 | rows | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | no-proposer | 0 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | no-proposer | 0 | fraction | 0.62 | 0.62 | 0.00 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | no-proposer | 0 | median item wall seconds | 7.6 | 4.4 | -3.2 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | no-proposer | 0 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | no-proposer | 0 | solved | 30 | 30 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | no-proposer | 1 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | no-proposer | 1 | fraction | 0.42 | 0.19 | -0.23 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | no-proposer | 1 | median item wall seconds | 11.9 | 15.9 | 4.0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | no-proposer | 1 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | no-proposer | 1 | solved | 20 | 9 | -11 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | no-proposer | 2 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | no-proposer | 2 | fraction | 0.83 | 0.58 | -0.25 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | no-proposer | 2 | median item wall seconds | 5.7 | 1.2 | -4.4 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | no-proposer | 2 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | no-proposer | 2 | solved | 40 | 28 | -12 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | no-proposer | 3 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | no-proposer | 3 | fraction | 0.77 | 0.85 | 0.08 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | no-proposer | 3 | median item wall seconds | 6.2 | 1.2 | -5.0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | no-proposer | 3 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | assessment | no-proposer | 3 | solved | 37 | 41 | 4 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | full | 0 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | full | 0 | g | 0.65 | 0.81 | 0.17 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | full | 0 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | full | 0 | solved | 31 | 39 | 8 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | full | 1 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | full | 1 | g | 0.96 | 1.00 | 0.04 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | full | 1 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | full | 1 | solved | 46 | 48 | 2 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | full | 2 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | full | 2 | g | 0.79 | 0.98 | 0.19 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | full | 2 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | full | 2 | solved | 38 | 47 | 9 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | full | 3 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | full | 3 | g | 0.69 | 0.96 | 0.27 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | full | 3 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | full | 3 | solved | 33 | 46 | 13 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-dreams | 0 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-dreams | 0 | g | 0.58 | 0.75 | 0.17 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-dreams | 0 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-dreams | 0 | solved | 28 | 36 | 8 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-dreams | 1 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-dreams | 1 | g | 0.85 | 0.98 | 0.12 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-dreams | 1 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-dreams | 1 | solved | 41 | 47 | 6 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-dreams | 2 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-dreams | 2 | g | 0.52 | 0.96 | 0.44 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-dreams | 2 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-dreams | 2 | solved | 25 | 46 | 21 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-dreams | 3 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-dreams | 3 | g | 0.00 | 0.96 | 0.96 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-dreams | 3 | rows | 0 | 48 | 48 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-dreams | 3 | solved | 0 | 46 | 46 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-library | 0 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-library | 0 | g | 0.00 | 0.00 | 0.00 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-library | 0 | rows | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-library | 0 | solved | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-library | 1 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-library | 1 | g | 0.00 | 0.00 | 0.00 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-library | 1 | rows | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-library | 1 | solved | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-library | 2 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-library | 2 | g | 0.00 | 0.00 | 0.00 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-library | 2 | rows | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-library | 2 | solved | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-library | 3 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-library | 3 | g | 0.00 | 0.00 | 0.00 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-library | 3 | rows | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-library | 3 | solved | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-proposer | 0 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-proposer | 0 | g | 0.62 | 0.62 | 0.00 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-proposer | 0 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-proposer | 0 | solved | 30 | 30 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-proposer | 1 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-proposer | 1 | g | 0.42 | 0.19 | -0.23 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-proposer | 1 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-proposer | 1 | solved | 20 | 9 | -11 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-proposer | 2 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-proposer | 2 | g | 0.83 | 0.58 | -0.25 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-proposer | 2 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-proposer | 2 | solved | 40 | 28 | -12 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-proposer | 3 | N | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-proposer | 3 | g | 0.77 | 0.85 | 0.08 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-proposer | 3 | rows | 48 | 48 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | curve | no-proposer | 3 | solved | 37 | 41 | 4 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | full | 0 | by_kind.curve | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | full | 0 | by_kind.drawing | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | full | 0 | by_kind.formula | 2 | 0 | -2 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | full | 0 | experiments | 41 | 30 | -11 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | full | 0 | laws | 2 | 0 | -2 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | full | 0 | reuse | 2 | 0 | -2 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | full | 0 | seconds | 222.0 | 202.6 | -19.4 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | full | 1 | by_kind.curve | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | full | 1 | by_kind.drawing | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | full | 1 | by_kind.formula | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | full | 1 | experiments | 2 | 7 | 5 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | full | 1 | laws | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | full | 1 | reuse | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | full | 1 | seconds | 294.1 | 223.3 | -70.9 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | full | 2 | by_kind.curve | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | full | 2 | by_kind.drawing | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | full | 2 | by_kind.formula | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | full | 2 | experiments | 3 | 8 | 5 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | full | 2 | laws | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | full | 2 | reuse | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | full | 2 | seconds | 246.1 | 202.9 | -43.2 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | full | 3 | by_kind.curve | 0 | 1 | 1 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | full | 3 | by_kind.drawing | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | full | 3 | by_kind.formula | 0 | 1 | 1 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | full | 3 | experiments | 2 | 4 | 2 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | full | 3 | laws | 0 | 2 | 2 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | full | 3 | reuse | 0 | 1 | 1 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | full | 3 | seconds | 245.2 | 205.6 | -39.7 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-dreams | 0 | by_kind.curve | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-dreams | 0 | by_kind.drawing | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-dreams | 0 | by_kind.formula | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-dreams | 0 | experiments | 24 | 26 | 2 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-dreams | 0 | laws | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-dreams | 0 | reuse | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-dreams | 0 | seconds | 204.0 | 204.5 | 0.5 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-dreams | 1 | by_kind.curve | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-dreams | 1 | by_kind.drawing | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-dreams | 1 | by_kind.formula | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-dreams | 1 | experiments | 7 | 8 | 1 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-dreams | 1 | laws | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-dreams | 1 | reuse | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-dreams | 1 | seconds | 225.8 | 221.4 | -4.4 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-dreams | 2 | by_kind.curve | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-dreams | 2 | by_kind.drawing | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-dreams | 2 | by_kind.formula | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-dreams | 2 | experiments | 3 | 2 | -1 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-dreams | 2 | laws | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-dreams | 2 | reuse | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-dreams | 2 | seconds | 203.6 | 210.6 | 7.0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-dreams | 3 | by_kind.curve | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-dreams | 3 | by_kind.drawing | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-dreams | 3 | by_kind.formula | 1 | 0 | -1 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-dreams | 3 | experiments | 15 | 2 | -13 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-dreams | 3 | laws | 1 | 0 | -1 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-dreams | 3 | reuse | 1 | 0 | -1 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-dreams | 3 | seconds | 282.5 | 211.5 | -71.1 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-proposer | 0 | by_kind.curve | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-proposer | 0 | by_kind.drawing | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-proposer | 0 | by_kind.formula | 2 | 0 | -2 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-proposer | 0 | experiments | 41 | 32 | -9 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-proposer | 0 | laws | 2 | 0 | -2 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-proposer | 0 | reuse | 2 | 0 | -2 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-proposer | 0 | seconds | 221.6 | 203.0 | -18.7 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-proposer | 1 | by_kind.curve | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-proposer | 1 | by_kind.drawing | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-proposer | 1 | by_kind.formula | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-proposer | 1 | experiments | 0 | 3 | 3 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-proposer | 1 | laws | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-proposer | 1 | reuse | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-proposer | 1 | seconds | 438.4 | 223.3 | -215.0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-proposer | 2 | by_kind.curve | 0 | 1 | 1 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-proposer | 2 | by_kind.drawing | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-proposer | 2 | by_kind.formula | 0 | 1 | 1 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-proposer | 2 | experiments | 2 | 7 | 5 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-proposer | 2 | laws | 0 | 2 | 2 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-proposer | 2 | reuse | 0 | 1 | 1 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-proposer | 2 | seconds | 281.0 | 324.1 | 43.1 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-proposer | 3 | by_kind.curve | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-proposer | 3 | by_kind.drawing | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-proposer | 3 | by_kind.formula | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-proposer | 3 | experiments | 16 | 0 | -16 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-proposer | 3 | laws | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-proposer | 3 | reuse | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | discovery | no-proposer | 3 | seconds | 213.3 | 315.3 | 101.9 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | full | 0 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | full | 0 | fraction | 1.00 | 1.00 | 0.00 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | full | 0 | median item wall seconds | 1.4 | 1.1 | -0.4 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | full | 0 | rows | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | full | 0 | solved | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | full | 1 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | full | 1 | fraction | 1.00 | 1.00 | 0.00 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | full | 1 | median item wall seconds | 0.6 | 1.2 | 0.5 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | full | 1 | rows | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | full | 1 | solved | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | full | 2 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | full | 2 | fraction | 1.00 | 1.00 | 0.00 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | full | 2 | median item wall seconds | 1.4 | 0.7 | -0.7 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | full | 2 | rows | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | full | 2 | solved | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | full | 3 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | full | 3 | fraction | 1.00 | 1.00 | 0.00 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | full | 3 | median item wall seconds | 0.7 | 0.6 | -0.0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | full | 3 | rows | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | full | 3 | solved | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | no-dreams | 0 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | no-dreams | 0 | fraction | 0.88 | 1.00 | 0.12 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | no-dreams | 0 | median item wall seconds | 4.8 | 2.4 | -2.4 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | no-dreams | 0 | rows | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | no-dreams | 0 | solved | 7 | 8 | 1 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | no-dreams | 1 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | no-dreams | 1 | fraction | 1.00 | 1.00 | 0.00 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | no-dreams | 1 | median item wall seconds | 0.8 | 0.8 | 0.0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | no-dreams | 1 | rows | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | no-dreams | 1 | solved | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | no-dreams | 2 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | no-dreams | 2 | fraction | 0.88 | 1.00 | 0.12 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | no-dreams | 2 | median item wall seconds | 0.8 | 0.8 | -0.0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | no-dreams | 2 | rows | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | no-dreams | 2 | solved | 7 | 8 | 1 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | no-dreams | 3 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | no-dreams | 3 | rows | 0 | 8 | 8 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | no-library | 0 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | no-library | 0 | rows | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | no-library | 1 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | no-library | 1 | rows | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | no-library | 2 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | no-library | 2 | rows | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | no-library | 3 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | no-library | 3 | rows | 0 | 0 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | no-proposer | 0 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | no-proposer | 0 | fraction | 0.62 | 0.88 | 0.25 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | no-proposer | 0 | median item wall seconds | 7.2 | 2.9 | -4.2 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | no-proposer | 0 | rows | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | no-proposer | 0 | solved | 5 | 7 | 2 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | no-proposer | 1 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | no-proposer | 1 | fraction | 0.62 | 0.38 | -0.25 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | no-proposer | 1 | median item wall seconds | 8.3 | 13.1 | 4.8 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | no-proposer | 1 | rows | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | no-proposer | 1 | solved | 5 | 3 | -2 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | no-proposer | 2 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | no-proposer | 2 | fraction | 0.88 | 1.00 | 0.12 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | no-proposer | 2 | median item wall seconds | 4.9 | 0.9 | -4.0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | no-proposer | 2 | rows | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | no-proposer | 2 | solved | 7 | 8 | 1 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | no-proposer | 3 | N | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | no-proposer | 3 | fraction | 0.62 | 0.88 | 0.25 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | no-proposer | 3 | median item wall seconds | 9.3 | 1.1 | -8.2 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | no-proposer | 3 | rows | 8 | 8 | 0 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | retention | no-proposer | 3 | solved | 5 | 7 | 2 | MISSING | noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |

Frozen suites: ["c809fde39db5ec5ecd6085986294c1dd3c53636c039058b511e90481e5081b9f", null]. Cases are comparable only on equal frozen suites. Smaller absolute differences are within noise; no replicate evidence means noise MISSING. Comparisons additionally match saved seed, device, allowances and evaluation sizes.

| left | right | section | arm | generation | metric | left value | right value | right - left | maximum replicate spread | interpretation | false credit |
|---|---|---|---|---|---|---|---|---|---|---|---|
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | full | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | full | 0 | fraction | 0.75 | 0.58 | -0.17 | 0.21 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | full | 0 | median item wall seconds | 4.5 | 8.5 | 4.1 | 4.3 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | full | 0 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | full | 0 | solved | 36 | 28 | -8 | 10 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | full | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | full | 1 | fraction | 0.81 | 0.83 | 0.02 | 0.21 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | full | 1 | median item wall seconds | 4.0 | 4.0 | -0.0 | 4.3 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | full | 1 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | full | 1 | solved | 39 | 40 | 1 | 10 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | full | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | full | 2 | fraction | 0.81 | 0.79 | -0.02 | 0.21 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | full | 2 | median item wall seconds | 1.2 | 3.7 | 2.4 | 4.3 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | full | 2 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | full | 2 | solved | 39 | 38 | -1 | 10 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | full | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | full | 3 | fraction | 0.85 | 0.71 | -0.15 | 0.21 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | full | 3 | median item wall seconds | 3.7 | 4.6 | 0.8 | 4.3 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | full | 3 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | full | 3 | solved | 41 | 34 | -7 | 10 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-dreams | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-dreams | 0 | fraction | 0.79 | 0.56 | -0.23 | 0.27 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-dreams | 0 | median item wall seconds | 4.4 | 9.0 | 4.6 | 4.9 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-dreams | 0 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-dreams | 0 | solved | 38 | 27 | -11 | 13 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-dreams | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-dreams | 1 | fraction | 0.81 | 0.77 | -0.04 | 0.27 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-dreams | 1 | median item wall seconds | 0.9 | 3.9 | 3.0 | 4.9 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-dreams | 1 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-dreams | 1 | solved | 39 | 37 | -2 | 13 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-dreams | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-dreams | 2 | fraction | 0.83 | 0.88 | 0.04 | 0.27 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-dreams | 2 | median item wall seconds | 0.9 | 4.1 | 3.3 | 4.9 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-dreams | 2 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-dreams | 2 | solved | 40 | 42 | 2 | 13 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-dreams | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-dreams | 3 | fraction | 0.83 | 0.71 | -0.12 | 0.27 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-dreams | 3 | median item wall seconds | 2.2 | 4.9 | 2.7 | 4.9 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-dreams | 3 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-dreams | 3 | solved | 40 | 34 | -6 | 13 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-library | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-library | 0 | fraction | 0.21 | 0.23 | 0.02 | 0.02 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-library | 0 | median item wall seconds | 10.5 | 11.2 | 0.7 | 0.1 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-library | 0 | rows | 48 | 48 | 0 | 48 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-library | 0 | solved | 10 | 11 | 1 | 1 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-library | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-library | 1 | fraction | 0.31 | 0.17 | -0.15 | 0.02 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-library | 1 | median item wall seconds | 10.6 | 11.1 | 0.5 | 0.1 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-library | 1 | rows | 48 | 48 | 0 | 48 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-library | 1 | solved | 15 | 8 | -7 | 1 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-library | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-library | 2 | fraction | 0.15 | 0.12 | -0.02 | 0.02 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-library | 2 | median item wall seconds | 10.6 | 11.0 | 0.4 | 0.1 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-library | 2 | rows | 48 | 48 | 0 | 48 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-library | 2 | solved | 7 | 6 | -1 | 1 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-library | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-library | 3 | fraction | 0.21 | 0.29 | 0.08 | 0.02 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-library | 3 | median item wall seconds | 10.6 | 11.0 | 0.4 | 0.1 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-library | 3 | rows | 48 | 48 | 0 | 48 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-library | 3 | solved | 10 | 14 | 4 | 1 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-proposer | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-proposer | 0 | fraction | 0.77 | 0.23 | -0.54 | 0.42 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-proposer | 0 | median item wall seconds | 5.9 | 15.2 | 9.3 | 7.9 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-proposer | 0 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-proposer | 0 | solved | 37 | 11 | -26 | 20 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-proposer | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-proposer | 1 | fraction | 0.54 | 0.12 | -0.42 | 0.42 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-proposer | 1 | median item wall seconds | 9.4 | 13.7 | 4.3 | 7.9 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-proposer | 1 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-proposer | 1 | solved | 26 | 6 | -20 | 20 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-proposer | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-proposer | 2 | fraction | 0.67 | 0.54 | -0.12 | 0.42 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-proposer | 2 | median item wall seconds | 6.7 | 7.2 | 0.5 | 7.9 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-proposer | 2 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-proposer | 2 | solved | 32 | 26 | -6 | 20 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-proposer | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-proposer | 3 | fraction | 0.35 | 0.46 | 0.10 | 0.42 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-proposer | 3 | median item wall seconds | 11.4 | 11.3 | -0.1 | 7.9 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-proposer | 3 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | assessment | no-proposer | 3 | solved | 17 | 22 | 5 | 20 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | full | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | full | 0 | g | 0.75 | 0.58 | -0.17 | 0.21 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | full | 0 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | full | 0 | solved | 36 | 28 | -8 | 10 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | full | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | full | 1 | g | 0.81 | 0.83 | 0.02 | 0.21 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | full | 1 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | full | 1 | solved | 39 | 40 | 1 | 10 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | full | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | full | 2 | g | 0.81 | 0.79 | -0.02 | 0.21 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | full | 2 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | full | 2 | solved | 39 | 38 | -1 | 10 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | full | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | full | 3 | g | 0.85 | 0.71 | -0.15 | 0.21 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | full | 3 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | full | 3 | solved | 41 | 34 | -7 | 10 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-dreams | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-dreams | 0 | g | 0.79 | 0.56 | -0.23 | 0.27 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-dreams | 0 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-dreams | 0 | solved | 38 | 27 | -11 | 13 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-dreams | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-dreams | 1 | g | 0.81 | 0.77 | -0.04 | 0.27 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-dreams | 1 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-dreams | 1 | solved | 39 | 37 | -2 | 13 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-dreams | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-dreams | 2 | g | 0.83 | 0.88 | 0.04 | 0.27 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-dreams | 2 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-dreams | 2 | solved | 40 | 42 | 2 | 13 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-dreams | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-dreams | 3 | g | 0.83 | 0.71 | -0.12 | 0.27 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-dreams | 3 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-dreams | 3 | solved | 40 | 34 | -6 | 13 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-library | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-library | 0 | g | 0.21 | 0.23 | 0.02 | 0.31 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-library | 0 | rows | 48 | 48 | 0 | 48 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-library | 0 | solved | 10 | 11 | 1 | 15 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-library | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-library | 1 | g | 0.31 | 0.17 | -0.15 | 0.31 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-library | 1 | rows | 48 | 48 | 0 | 48 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-library | 1 | solved | 15 | 8 | -7 | 15 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-library | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-library | 2 | g | 0.15 | 0.12 | -0.02 | 0.31 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-library | 2 | rows | 48 | 48 | 0 | 48 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-library | 2 | solved | 7 | 6 | -1 | 15 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-library | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-library | 3 | g | 0.21 | 0.29 | 0.08 | 0.31 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-library | 3 | rows | 48 | 48 | 0 | 48 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-library | 3 | solved | 10 | 14 | 4 | 15 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-proposer | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-proposer | 0 | g | 0.77 | 0.23 | -0.54 | 0.42 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-proposer | 0 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-proposer | 0 | solved | 37 | 11 | -26 | 20 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-proposer | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-proposer | 1 | g | 0.54 | 0.12 | -0.42 | 0.42 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-proposer | 1 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-proposer | 1 | solved | 26 | 6 | -20 | 20 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-proposer | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-proposer | 2 | g | 0.67 | 0.54 | -0.12 | 0.42 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-proposer | 2 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-proposer | 2 | solved | 32 | 26 | -6 | 20 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-proposer | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-proposer | 3 | g | 0.35 | 0.46 | 0.10 | 0.42 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-proposer | 3 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | curve | no-proposer | 3 | solved | 17 | 22 | 5 | 20 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | full | 0 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | full | 0 | fraction | 0.88 | 0.38 | -0.50 | 0.25 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | full | 0 | median item wall seconds | 2.4 | 11.2 | 8.8 | 2.8 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | full | 0 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | full | 0 | solved | 7 | 3 | -4 | 2 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | full | 1 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | full | 1 | fraction | 0.88 | 0.88 | 0.00 | 0.25 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | full | 1 | median item wall seconds | 3.4 | 2.7 | -0.7 | 2.8 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | full | 1 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | full | 1 | solved | 7 | 7 | 0 | 2 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | full | 2 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | full | 2 | fraction | 0.88 | 0.88 | 0.00 | 0.25 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | full | 2 | median item wall seconds | 1.0 | 3.1 | 2.1 | 2.8 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | full | 2 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | full | 2 | solved | 7 | 7 | 0 | 2 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | full | 3 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | full | 3 | fraction | 0.75 | 0.88 | 0.12 | 0.25 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | full | 3 | median item wall seconds | 2.9 | 4.4 | 1.5 | 2.8 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | full | 3 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | full | 3 | solved | 6 | 7 | 1 | 2 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-dreams | 0 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-dreams | 0 | fraction | 0.88 | 0.38 | -0.50 | 0.12 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-dreams | 0 | median item wall seconds | 1.2 | 10.8 | 9.5 | 4.5 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-dreams | 0 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-dreams | 0 | solved | 7 | 3 | -4 | 1 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-dreams | 1 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-dreams | 1 | fraction | 0.75 | 0.88 | 0.12 | 0.12 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-dreams | 1 | median item wall seconds | 0.8 | 2.8 | 1.9 | 4.5 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-dreams | 1 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-dreams | 1 | solved | 6 | 7 | 1 | 1 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-dreams | 2 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-dreams | 2 | fraction | 0.88 | 0.88 | 0.00 | 0.12 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-dreams | 2 | median item wall seconds | 0.6 | 4.1 | 3.5 | 4.5 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-dreams | 2 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-dreams | 2 | solved | 7 | 7 | 0 | 1 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-dreams | 3 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-dreams | 3 | fraction | 0.88 | 0.88 | 0.00 | 0.12 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-dreams | 3 | median item wall seconds | 0.5 | 4.1 | 3.5 | 4.5 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-dreams | 3 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-dreams | 3 | solved | 7 | 7 | 0 | 1 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-library | 0 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-library | 0 | fraction | 0.75 | 0.50 | -0.25 | MISSING | noise MISSING | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-library | 0 | median item wall seconds | 4.0 | 9.8 | 5.7 | MISSING | noise MISSING | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-library | 0 | rows | 8 | 8 | 0 | 8 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-library | 0 | solved | 6 | 4 | -2 | MISSING | noise MISSING | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-library | 1 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-library | 1 | fraction | 0.88 | 0.50 | -0.38 | MISSING | noise MISSING | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-library | 1 | median item wall seconds | 5.5 | 9.6 | 4.1 | MISSING | noise MISSING | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-library | 1 | rows | 8 | 8 | 0 | 8 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-library | 1 | solved | 7 | 4 | -3 | MISSING | noise MISSING | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-library | 2 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-library | 2 | fraction | 0.75 | 0.50 | -0.25 | MISSING | noise MISSING | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-library | 2 | median item wall seconds | 6.4 | 9.9 | 3.5 | MISSING | noise MISSING | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-library | 2 | rows | 8 | 8 | 0 | 8 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-library | 2 | solved | 6 | 4 | -2 | MISSING | noise MISSING | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-library | 3 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-library | 3 | fraction | 0.62 | 0.38 | -0.25 | MISSING | noise MISSING | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-library | 3 | median item wall seconds | 5.0 | 11.3 | 6.2 | MISSING | noise MISSING | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-library | 3 | rows | 8 | 8 | 0 | 8 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-library | 3 | solved | 5 | 3 | -2 | MISSING | noise MISSING | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-proposer | 0 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-proposer | 0 | fraction | 0.88 | 0.75 | -0.12 | 0.38 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-proposer | 0 | median item wall seconds | 2.0 | 6.3 | 4.3 | 5.9 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-proposer | 0 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-proposer | 0 | solved | 7 | 6 | -1 | 3 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-proposer | 1 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-proposer | 1 | fraction | 0.50 | 0.25 | -0.25 | 0.38 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-proposer | 1 | median item wall seconds | 10.1 | 14.6 | 4.5 | 5.9 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-proposer | 1 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-proposer | 1 | solved | 4 | 2 | -2 | 3 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-proposer | 2 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-proposer | 2 | fraction | 0.88 | 0.38 | -0.50 | 0.38 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-proposer | 2 | median item wall seconds | 0.6 | 12.6 | 12.0 | 5.9 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-proposer | 2 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-proposer | 2 | solved | 7 | 3 | -4 | 3 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-proposer | 3 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-proposer | 3 | fraction | 0.38 | 0.38 | 0.00 | 0.38 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-proposer | 3 | median item wall seconds | 11.5 | 12.0 | 0.5 | 5.9 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-proposer | 3 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | retention | no-proposer | 3 | solved | 3 | 3 | 0 | 3 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | full | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | full | 0 | fraction | 0.75 | 0.54 | -0.21 | 0.21 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | full | 0 | median item wall seconds | 4.5 | 9.4 | 5.0 | 4.3 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | full | 0 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | full | 0 | solved | 36 | 26 | -10 | 10 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | full | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | full | 1 | fraction | 0.81 | 0.69 | -0.12 | 0.21 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | full | 1 | median item wall seconds | 4.0 | 4.3 | 0.2 | 4.3 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | full | 1 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | full | 1 | solved | 39 | 33 | -6 | 10 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | full | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | full | 2 | fraction | 0.81 | 0.79 | -0.02 | 0.21 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | full | 2 | median item wall seconds | 1.2 | 5.0 | 3.8 | 4.3 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | full | 2 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | full | 2 | solved | 39 | 38 | -1 | 10 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | full | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | full | 3 | fraction | 0.85 | 0.75 | -0.10 | 0.21 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | full | 3 | median item wall seconds | 3.7 | 3.4 | -0.3 | 4.3 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | full | 3 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | full | 3 | solved | 41 | 36 | -5 | 10 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | no-dreams | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | no-dreams | 0 | fraction | 0.79 | 0.56 | -0.23 | 0.27 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | no-dreams | 0 | median item wall seconds | 4.4 | 9.1 | 4.7 | 4.9 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | no-dreams | 0 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | no-dreams | 0 | solved | 38 | 27 | -11 | 13 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | no-dreams | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | no-dreams | 1 | fraction | 0.81 | 0.52 | -0.29 | 0.27 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | no-dreams | 1 | median item wall seconds | 0.9 | 9.5 | 8.6 | 4.9 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | no-dreams | 1 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | no-dreams | 1 | solved | 39 | 25 | -14 | 13 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | no-dreams | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | no-dreams | 2 | fraction | 0.83 | 0.73 | -0.10 | 0.27 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | no-dreams | 2 | median item wall seconds | 0.9 | 5.3 | 4.4 | 4.9 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | no-dreams | 2 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | no-dreams | 2 | solved | 40 | 35 | -5 | 13 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | no-dreams | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | no-dreams | 3 | rows | 48 | 0 | -48 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | no-library | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | no-library | 0 | rows | 48 | 0 | -48 | 48 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | no-library | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | no-library | 1 | rows | 48 | 0 | -48 | 48 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | no-library | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | no-library | 2 | rows | 48 | 0 | -48 | 48 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | no-library | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | no-library | 3 | rows | 48 | 0 | -48 | 48 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | no-proposer | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | no-proposer | 0 | fraction | 0.77 | 0.08 | -0.69 | 0.42 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | no-proposer | 0 | median item wall seconds | 5.9 | 14.2 | 8.3 | 7.9 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | no-proposer | 0 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | no-proposer | 0 | solved | 37 | 4 | -33 | 20 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | no-proposer | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | no-proposer | 1 | fraction | 0.54 | 0.04 | -0.50 | 0.42 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | no-proposer | 1 | median item wall seconds | 9.4 | 13.8 | 4.4 | 7.9 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | no-proposer | 1 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | no-proposer | 1 | solved | 26 | 2 | -24 | 20 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | no-proposer | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | no-proposer | 2 | fraction | 0.67 | 0.50 | -0.17 | 0.42 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | no-proposer | 2 | median item wall seconds | 6.7 | 9.9 | 3.2 | 7.9 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | no-proposer | 2 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | no-proposer | 2 | solved | 32 | 24 | -8 | 20 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | no-proposer | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | no-proposer | 3 | fraction | 0.35 | 0.40 | 0.04 | 0.42 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | no-proposer | 3 | median item wall seconds | 11.4 | 12.1 | 0.6 | 7.9 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | no-proposer | 3 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | assessment | no-proposer | 3 | solved | 17 | 19 | 2 | 20 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | full | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | full | 0 | g | 0.75 | 0.54 | -0.21 | 0.21 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | full | 0 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | full | 0 | solved | 36 | 26 | -10 | 10 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | full | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | full | 1 | g | 0.81 | 0.69 | -0.12 | 0.21 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | full | 1 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | full | 1 | solved | 39 | 33 | -6 | 10 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | full | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | full | 2 | g | 0.81 | 0.79 | -0.02 | 0.21 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | full | 2 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | full | 2 | solved | 39 | 38 | -1 | 10 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | full | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | full | 3 | g | 0.85 | 0.75 | -0.10 | 0.21 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | full | 3 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | full | 3 | solved | 41 | 36 | -5 | 10 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-dreams | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-dreams | 0 | g | 0.79 | 0.56 | -0.23 | 0.27 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-dreams | 0 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-dreams | 0 | solved | 38 | 27 | -11 | 13 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-dreams | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-dreams | 1 | g | 0.81 | 0.52 | -0.29 | 0.27 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-dreams | 1 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-dreams | 1 | solved | 39 | 25 | -14 | 13 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-dreams | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-dreams | 2 | g | 0.83 | 0.73 | -0.10 | 0.27 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-dreams | 2 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-dreams | 2 | solved | 40 | 35 | -5 | 13 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-dreams | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-dreams | 3 | g | 0.83 | 0.00 | -0.83 | 0.27 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-dreams | 3 | rows | 48 | 0 | -48 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-dreams | 3 | solved | 40 | 0 | -40 | 13 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-library | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-library | 0 | g | 0.21 | 0.00 | -0.21 | 0.31 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-library | 0 | rows | 48 | 0 | -48 | 48 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-library | 0 | solved | 10 | 0 | -10 | 15 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-library | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-library | 1 | g | 0.31 | 0.00 | -0.31 | 0.31 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-library | 1 | rows | 48 | 0 | -48 | 48 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-library | 1 | solved | 15 | 0 | -15 | 15 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-library | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-library | 2 | g | 0.15 | 0.00 | -0.15 | 0.31 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-library | 2 | rows | 48 | 0 | -48 | 48 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-library | 2 | solved | 7 | 0 | -7 | 15 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-library | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-library | 3 | g | 0.21 | 0.00 | -0.21 | 0.31 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-library | 3 | rows | 48 | 0 | -48 | 48 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-library | 3 | solved | 10 | 0 | -10 | 15 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-proposer | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-proposer | 0 | g | 0.77 | 0.08 | -0.69 | 0.42 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-proposer | 0 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-proposer | 0 | solved | 37 | 4 | -33 | 20 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-proposer | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-proposer | 1 | g | 0.54 | 0.04 | -0.50 | 0.42 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-proposer | 1 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-proposer | 1 | solved | 26 | 2 | -24 | 20 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-proposer | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-proposer | 2 | g | 0.67 | 0.50 | -0.17 | 0.42 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-proposer | 2 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-proposer | 2 | solved | 32 | 24 | -8 | 20 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-proposer | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-proposer | 3 | g | 0.35 | 0.40 | 0.04 | 0.42 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-proposer | 3 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | curve | no-proposer | 3 | solved | 17 | 19 | 2 | 20 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | full | 0 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | full | 0 | fraction | 0.88 | 0.88 | 0.00 | 0.25 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | full | 0 | median item wall seconds | 2.4 | 9.1 | 6.7 | 2.8 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | full | 0 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | full | 0 | solved | 7 | 7 | 0 | 2 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | full | 1 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | full | 1 | fraction | 0.88 | 0.62 | -0.25 | 0.25 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | full | 1 | median item wall seconds | 3.4 | 4.2 | 0.9 | 2.8 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | full | 1 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | full | 1 | solved | 7 | 5 | -2 | 2 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | full | 2 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | full | 2 | fraction | 0.88 | 0.88 | 0.00 | 0.25 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | full | 2 | median item wall seconds | 1.0 | 3.6 | 2.6 | 2.8 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | full | 2 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | full | 2 | solved | 7 | 7 | 0 | 2 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | full | 3 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | full | 3 | fraction | 0.75 | 0.88 | 0.12 | 0.25 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | full | 3 | median item wall seconds | 2.9 | 3.4 | 0.5 | 2.8 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | full | 3 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | full | 3 | solved | 6 | 7 | 1 | 2 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | no-dreams | 0 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | no-dreams | 0 | fraction | 0.88 | 0.88 | 0.00 | 0.12 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | no-dreams | 0 | median item wall seconds | 1.2 | 6.7 | 5.5 | 4.5 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | no-dreams | 0 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | no-dreams | 0 | solved | 7 | 7 | 0 | 1 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | no-dreams | 1 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | no-dreams | 1 | fraction | 0.75 | 0.62 | -0.12 | 0.12 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | no-dreams | 1 | median item wall seconds | 0.8 | 5.8 | 5.0 | 4.5 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | no-dreams | 1 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | no-dreams | 1 | solved | 6 | 5 | -1 | 1 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | no-dreams | 2 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | no-dreams | 2 | fraction | 0.88 | 0.88 | 0.00 | 0.12 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | no-dreams | 2 | median item wall seconds | 0.6 | 3.0 | 2.4 | 4.5 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | no-dreams | 2 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | no-dreams | 2 | solved | 7 | 7 | 0 | 1 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | no-dreams | 3 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | no-dreams | 3 | rows | 8 | 0 | -8 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | no-library | 0 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | no-library | 0 | rows | 8 | 0 | -8 | 8 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | no-library | 1 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | no-library | 1 | rows | 8 | 0 | -8 | 8 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | no-library | 2 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | no-library | 2 | rows | 8 | 0 | -8 | 8 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | no-library | 3 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | no-library | 3 | rows | 8 | 0 | -8 | 8 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | no-proposer | 0 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | no-proposer | 0 | fraction | 0.88 | 0.25 | -0.62 | 0.38 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | no-proposer | 0 | median item wall seconds | 2.0 | 13.0 | 11.0 | 5.9 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | no-proposer | 0 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | no-proposer | 0 | solved | 7 | 2 | -5 | 3 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | no-proposer | 1 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | no-proposer | 1 | fraction | 0.50 | 0.00 | -0.50 | 0.38 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | no-proposer | 1 | median item wall seconds | 10.1 | 13.3 | 3.2 | 5.9 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | no-proposer | 1 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | no-proposer | 1 | solved | 4 | 0 | -4 | 3 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | no-proposer | 2 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | no-proposer | 2 | fraction | 0.88 | 0.88 | 0.00 | 0.38 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | no-proposer | 2 | median item wall seconds | 0.6 | 5.0 | 4.3 | 5.9 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | no-proposer | 2 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | no-proposer | 2 | solved | 7 | 7 | 0 | 3 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | no-proposer | 3 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | no-proposer | 3 | fraction | 0.38 | 0.38 | 0.00 | 0.38 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | no-proposer | 3 | median item wall seconds | 11.5 | 11.8 | 0.2 | 5.9 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | no-proposer | 3 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | retention | no-proposer | 3 | solved | 3 | 3 | 0 | 3 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | full | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | full | 0 | fraction | 0.75 | 0.54 | -0.21 | 0.21 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | full | 0 | median item wall seconds | 4.5 | 8.8 | 4.3 | 4.3 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | full | 0 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | full | 0 | solved | 36 | 26 | -10 | 10 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | full | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | full | 1 | fraction | 0.81 | 1.00 | 0.19 | 0.21 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | full | 1 | median item wall seconds | 4.0 | 0.8 | -3.2 | 4.3 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | full | 1 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | full | 1 | solved | 39 | 48 | 9 | 10 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | full | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | full | 2 | fraction | 0.81 | 0.81 | 0.00 | 0.21 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | full | 2 | median item wall seconds | 1.2 | 0.9 | -0.4 | 4.3 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | full | 2 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | full | 2 | solved | 39 | 39 | 0 | 10 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | full | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | full | 3 | fraction | 0.85 | 0.98 | 0.12 | 0.21 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | full | 3 | median item wall seconds | 3.7 | 2.4 | -1.3 | 4.3 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | full | 3 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | full | 3 | solved | 41 | 47 | 6 | 10 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 0 | fraction | 0.79 | 0.52 | -0.27 | 0.27 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 0 | median item wall seconds | 4.4 | 9.4 | 4.9 | 4.9 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 0 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 0 | solved | 38 | 25 | -13 | 13 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 1 | fraction | 0.81 | 0.96 | 0.15 | 0.27 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 1 | median item wall seconds | 0.9 | 1.3 | 0.4 | 4.9 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 1 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 1 | solved | 39 | 46 | 7 | 13 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 2 | fraction | 0.83 | 0.94 | 0.10 | 0.27 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 2 | median item wall seconds | 0.9 | 1.4 | 0.5 | 4.9 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 2 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 2 | solved | 40 | 45 | 5 | 13 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 3 | fraction | 0.83 | 0.94 | 0.10 | 0.27 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 3 | median item wall seconds | 2.2 | 3.3 | 1.1 | 4.9 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 3 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 3 | solved | 40 | 45 | 5 | 13 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-library | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-library | 0 | fraction | 0.21 | 0.23 | 0.02 | 0.02 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-library | 0 | median item wall seconds | 10.5 | 10.6 | 0.1 | 0.1 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-library | 0 | rows | 48 | 27 | -21 | 48 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-library | 0 | solved | 10 | 11 | 1 | 1 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-library | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-library | 1 | rows | 48 | 0 | -48 | 48 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-library | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-library | 2 | rows | 48 | 0 | -48 | 48 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-library | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-library | 3 | rows | 48 | 0 | -48 | 48 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 0 | fraction | 0.77 | 0.42 | -0.35 | 0.42 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 0 | median item wall seconds | 5.9 | 13.8 | 7.9 | 7.9 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 0 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 0 | solved | 37 | 20 | -17 | 20 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 1 | fraction | 0.54 | 0.12 | -0.42 | 0.42 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 1 | median item wall seconds | 9.4 | 14.3 | 4.9 | 7.9 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 1 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 1 | solved | 26 | 6 | -20 | 20 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 2 | fraction | 0.67 | 0.50 | -0.17 | 0.42 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 2 | median item wall seconds | 6.7 | 9.9 | 3.2 | 7.9 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 2 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 2 | solved | 32 | 24 | -8 | 20 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 3 | fraction | 0.35 | 0.42 | 0.06 | 0.42 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 3 | median item wall seconds | 11.4 | 12.0 | 0.6 | 7.9 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 3 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 3 | solved | 17 | 20 | 3 | 20 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | full | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | full | 0 | g | 0.75 | 0.54 | -0.21 | 0.21 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | full | 0 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | full | 0 | solved | 36 | 26 | -10 | 10 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | full | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | full | 1 | g | 0.81 | 1.00 | 0.19 | 0.21 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | full | 1 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | full | 1 | solved | 39 | 48 | 9 | 10 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | full | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | full | 2 | g | 0.81 | 0.81 | 0.00 | 0.21 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | full | 2 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | full | 2 | solved | 39 | 39 | 0 | 10 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | full | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | full | 3 | g | 0.85 | 0.98 | 0.12 | 0.21 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | full | 3 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | full | 3 | solved | 41 | 47 | 6 | 10 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 0 | g | 0.79 | 0.52 | -0.27 | 0.27 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 0 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 0 | solved | 38 | 25 | -13 | 13 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 1 | g | 0.81 | 0.96 | 0.15 | 0.27 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 1 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 1 | solved | 39 | 46 | 7 | 13 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 2 | g | 0.83 | 0.94 | 0.10 | 0.27 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 2 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 2 | solved | 40 | 45 | 5 | 13 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 3 | g | 0.83 | 0.94 | 0.10 | 0.27 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 3 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 3 | solved | 40 | 45 | 5 | 13 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 0 | g | 0.21 | 0.23 | 0.02 | 0.31 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 0 | rows | 48 | 27 | -21 | 48 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 0 | solved | 10 | 11 | 1 | 15 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 1 | g | 0.31 | 0.00 | -0.31 | 0.31 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 1 | rows | 48 | 0 | -48 | 48 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 1 | solved | 15 | 0 | -15 | 15 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 2 | g | 0.15 | 0.00 | -0.15 | 0.31 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 2 | rows | 48 | 0 | -48 | 48 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 2 | solved | 7 | 0 | -7 | 15 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 3 | g | 0.21 | 0.00 | -0.21 | 0.31 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 3 | rows | 48 | 0 | -48 | 48 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 3 | solved | 10 | 0 | -10 | 15 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 0 | g | 0.77 | 0.42 | -0.35 | 0.42 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 0 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 0 | solved | 37 | 20 | -17 | 20 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 1 | g | 0.54 | 0.12 | -0.42 | 0.42 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 1 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 1 | solved | 26 | 6 | -20 | 20 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 2 | g | 0.67 | 0.50 | -0.17 | 0.42 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 2 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 2 | solved | 32 | 24 | -8 | 20 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 3 | g | 0.35 | 0.42 | 0.06 | 0.42 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 3 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 3 | solved | 17 | 20 | 3 | 20 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | full | 0 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | full | 0 | fraction | 0.88 | 0.75 | -0.12 | 0.25 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | full | 0 | median item wall seconds | 2.4 | 3.6 | 1.2 | 2.8 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | full | 0 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | full | 0 | solved | 7 | 6 | -1 | 2 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | full | 1 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | full | 1 | fraction | 0.88 | 1.00 | 0.12 | 0.25 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | full | 1 | median item wall seconds | 3.4 | 0.6 | -2.8 | 2.8 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | full | 1 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | full | 1 | solved | 7 | 8 | 1 | 2 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | full | 2 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | full | 2 | fraction | 0.88 | 1.00 | 0.12 | 0.25 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | full | 2 | median item wall seconds | 1.0 | 0.6 | -0.4 | 2.8 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | full | 2 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | full | 2 | solved | 7 | 8 | 1 | 2 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | full | 3 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | full | 3 | fraction | 0.75 | 1.00 | 0.25 | 0.25 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | full | 3 | median item wall seconds | 2.9 | 2.1 | -0.9 | 2.8 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | full | 3 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | full | 3 | solved | 6 | 8 | 2 | 2 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 0 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 0 | fraction | 0.88 | 0.75 | -0.12 | 0.12 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 0 | median item wall seconds | 1.2 | 5.8 | 4.5 | 4.5 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 0 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 0 | solved | 7 | 6 | -1 | 1 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 1 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 1 | fraction | 0.75 | 0.75 | 0.00 | 0.12 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 1 | median item wall seconds | 0.8 | 2.2 | 1.4 | 4.5 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 1 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 1 | solved | 6 | 6 | 0 | 1 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 2 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 2 | fraction | 0.88 | 1.00 | 0.12 | 0.12 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 2 | median item wall seconds | 0.6 | 1.5 | 1.0 | 4.5 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 2 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 2 | solved | 7 | 8 | 1 | 1 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 3 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 3 | fraction | 0.88 | 1.00 | 0.12 | 0.12 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 3 | median item wall seconds | 0.5 | 2.2 | 1.7 | 4.5 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 3 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 3 | solved | 7 | 8 | 1 | 1 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-library | 0 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-library | 0 | rows | 8 | 0 | -8 | 8 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-library | 1 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-library | 1 | rows | 8 | 0 | -8 | 8 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-library | 2 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-library | 2 | rows | 8 | 0 | -8 | 8 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-library | 3 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-library | 3 | rows | 8 | 0 | -8 | 8 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 0 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 0 | fraction | 0.88 | 0.50 | -0.38 | 0.38 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 0 | median item wall seconds | 2.0 | 7.9 | 5.9 | 5.9 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 0 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 0 | solved | 7 | 4 | -3 | 3 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 1 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 1 | fraction | 0.50 | 0.25 | -0.25 | 0.38 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 1 | median item wall seconds | 10.1 | 11.8 | 1.8 | 5.9 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 1 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 1 | solved | 4 | 2 | -2 | 3 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 2 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 2 | fraction | 0.88 | 0.62 | -0.25 | 0.38 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 2 | median item wall seconds | 0.6 | 1.2 | 0.6 | 5.9 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 2 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 2 | solved | 7 | 5 | -2 | 3 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 3 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 3 | fraction | 0.38 | 0.50 | 0.12 | 0.38 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 3 | median item wall seconds | 11.5 | 9.7 | -1.8 | 5.9 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 3 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 3 | solved | 3 | 4 | 1 | 3 | within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | full | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | full | 0 | fraction | 0.58 | 0.54 | -0.04 | 0.21 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | full | 0 | median item wall seconds | 8.5 | 9.4 | 0.9 | 4.3 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | full | 0 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | full | 0 | solved | 28 | 26 | -2 | 10 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | full | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | full | 1 | fraction | 0.83 | 0.69 | -0.15 | 0.21 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | full | 1 | median item wall seconds | 4.0 | 4.3 | 0.3 | 4.3 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | full | 1 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | full | 1 | solved | 40 | 33 | -7 | 10 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | full | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | full | 2 | fraction | 0.79 | 0.79 | 0.00 | 0.21 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | full | 2 | median item wall seconds | 3.7 | 5.0 | 1.4 | 4.3 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | full | 2 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | full | 2 | solved | 38 | 38 | 0 | 10 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | full | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | full | 3 | fraction | 0.71 | 0.75 | 0.04 | 0.21 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | full | 3 | median item wall seconds | 4.6 | 3.4 | -1.1 | 4.3 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | full | 3 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | full | 3 | solved | 34 | 36 | 2 | 10 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | no-dreams | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | no-dreams | 0 | fraction | 0.56 | 0.56 | 0.00 | 0.27 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | no-dreams | 0 | median item wall seconds | 9.0 | 9.1 | 0.1 | 4.9 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | no-dreams | 0 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | no-dreams | 0 | solved | 27 | 27 | 0 | 13 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | no-dreams | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | no-dreams | 1 | fraction | 0.77 | 0.52 | -0.25 | 0.27 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | no-dreams | 1 | median item wall seconds | 3.9 | 9.5 | 5.5 | 4.9 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | no-dreams | 1 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | no-dreams | 1 | solved | 37 | 25 | -12 | 13 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | no-dreams | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | no-dreams | 2 | fraction | 0.88 | 0.73 | -0.15 | 0.27 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | no-dreams | 2 | median item wall seconds | 4.1 | 5.3 | 1.1 | 4.9 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | no-dreams | 2 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | no-dreams | 2 | solved | 42 | 35 | -7 | 13 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | no-dreams | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | no-dreams | 3 | rows | 48 | 0 | -48 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | no-library | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | no-library | 0 | rows | 48 | 0 | -48 | 48 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | no-library | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | no-library | 1 | rows | 48 | 0 | -48 | 48 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | no-library | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | no-library | 2 | rows | 48 | 0 | -48 | 48 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | no-library | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | no-library | 3 | rows | 48 | 0 | -48 | 48 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | no-proposer | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | no-proposer | 0 | fraction | 0.23 | 0.08 | -0.15 | 0.42 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | no-proposer | 0 | median item wall seconds | 15.2 | 14.2 | -1.0 | 7.9 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | no-proposer | 0 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | no-proposer | 0 | solved | 11 | 4 | -7 | 20 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | no-proposer | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | no-proposer | 1 | fraction | 0.12 | 0.04 | -0.08 | 0.42 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | no-proposer | 1 | median item wall seconds | 13.7 | 13.8 | 0.1 | 7.9 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | no-proposer | 1 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | no-proposer | 1 | solved | 6 | 2 | -4 | 20 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | no-proposer | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | no-proposer | 2 | fraction | 0.54 | 0.50 | -0.04 | 0.42 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | no-proposer | 2 | median item wall seconds | 7.2 | 9.9 | 2.7 | 7.9 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | no-proposer | 2 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | no-proposer | 2 | solved | 26 | 24 | -2 | 20 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | no-proposer | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | no-proposer | 3 | fraction | 0.46 | 0.40 | -0.06 | 0.42 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | no-proposer | 3 | median item wall seconds | 11.3 | 12.1 | 0.8 | 7.9 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | no-proposer | 3 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | assessment | no-proposer | 3 | solved | 22 | 19 | -3 | 20 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | full | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | full | 0 | g | 0.58 | 0.54 | -0.04 | 0.21 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | full | 0 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | full | 0 | solved | 28 | 26 | -2 | 10 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | full | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | full | 1 | g | 0.83 | 0.69 | -0.15 | 0.21 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | full | 1 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | full | 1 | solved | 40 | 33 | -7 | 10 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | full | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | full | 2 | g | 0.79 | 0.79 | 0.00 | 0.21 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | full | 2 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | full | 2 | solved | 38 | 38 | 0 | 10 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | full | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | full | 3 | g | 0.71 | 0.75 | 0.04 | 0.21 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | full | 3 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | full | 3 | solved | 34 | 36 | 2 | 10 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-dreams | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-dreams | 0 | g | 0.56 | 0.56 | 0.00 | 0.27 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-dreams | 0 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-dreams | 0 | solved | 27 | 27 | 0 | 13 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-dreams | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-dreams | 1 | g | 0.77 | 0.52 | -0.25 | 0.27 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-dreams | 1 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-dreams | 1 | solved | 37 | 25 | -12 | 13 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-dreams | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-dreams | 2 | g | 0.88 | 0.73 | -0.15 | 0.27 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-dreams | 2 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-dreams | 2 | solved | 42 | 35 | -7 | 13 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-dreams | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-dreams | 3 | g | 0.71 | 0.00 | -0.71 | 0.27 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-dreams | 3 | rows | 48 | 0 | -48 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-dreams | 3 | solved | 34 | 0 | -34 | 13 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-library | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-library | 0 | g | 0.23 | 0.00 | -0.23 | 0.31 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-library | 0 | rows | 48 | 0 | -48 | 48 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-library | 0 | solved | 11 | 0 | -11 | 15 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-library | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-library | 1 | g | 0.17 | 0.00 | -0.17 | 0.31 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-library | 1 | rows | 48 | 0 | -48 | 48 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-library | 1 | solved | 8 | 0 | -8 | 15 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-library | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-library | 2 | g | 0.12 | 0.00 | -0.12 | 0.31 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-library | 2 | rows | 48 | 0 | -48 | 48 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-library | 2 | solved | 6 | 0 | -6 | 15 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-library | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-library | 3 | g | 0.29 | 0.00 | -0.29 | 0.31 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-library | 3 | rows | 48 | 0 | -48 | 48 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-library | 3 | solved | 14 | 0 | -14 | 15 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-proposer | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-proposer | 0 | g | 0.23 | 0.08 | -0.15 | 0.42 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-proposer | 0 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-proposer | 0 | solved | 11 | 4 | -7 | 20 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-proposer | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-proposer | 1 | g | 0.12 | 0.04 | -0.08 | 0.42 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-proposer | 1 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-proposer | 1 | solved | 6 | 2 | -4 | 20 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-proposer | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-proposer | 2 | g | 0.54 | 0.50 | -0.04 | 0.42 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-proposer | 2 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-proposer | 2 | solved | 26 | 24 | -2 | 20 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-proposer | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-proposer | 3 | g | 0.46 | 0.40 | -0.06 | 0.42 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-proposer | 3 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | curve | no-proposer | 3 | solved | 22 | 19 | -3 | 20 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | full | 0 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | full | 0 | fraction | 0.38 | 0.88 | 0.50 | 0.25 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | full | 0 | median item wall seconds | 11.2 | 9.1 | -2.1 | 2.8 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | full | 0 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | full | 0 | solved | 3 | 7 | 4 | 2 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | full | 1 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | full | 1 | fraction | 0.88 | 0.62 | -0.25 | 0.25 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | full | 1 | median item wall seconds | 2.7 | 4.2 | 1.5 | 2.8 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | full | 1 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | full | 1 | solved | 7 | 5 | -2 | 2 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | full | 2 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | full | 2 | fraction | 0.88 | 0.88 | 0.00 | 0.25 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | full | 2 | median item wall seconds | 3.1 | 3.6 | 0.5 | 2.8 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | full | 2 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | full | 2 | solved | 7 | 7 | 0 | 2 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | full | 3 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | full | 3 | fraction | 0.88 | 0.88 | 0.00 | 0.25 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | full | 3 | median item wall seconds | 4.4 | 3.4 | -1.0 | 2.8 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | full | 3 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | full | 3 | solved | 7 | 7 | 0 | 2 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | no-dreams | 0 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | no-dreams | 0 | fraction | 0.38 | 0.88 | 0.50 | 0.12 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | no-dreams | 0 | median item wall seconds | 10.8 | 6.7 | -4.1 | 4.5 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | no-dreams | 0 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | no-dreams | 0 | solved | 3 | 7 | 4 | 1 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | no-dreams | 1 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | no-dreams | 1 | fraction | 0.88 | 0.62 | -0.25 | 0.12 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | no-dreams | 1 | median item wall seconds | 2.8 | 5.8 | 3.0 | 4.5 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | no-dreams | 1 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | no-dreams | 1 | solved | 7 | 5 | -2 | 1 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | no-dreams | 2 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | no-dreams | 2 | fraction | 0.88 | 0.88 | 0.00 | 0.12 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | no-dreams | 2 | median item wall seconds | 4.1 | 3.0 | -1.1 | 4.5 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | no-dreams | 2 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | no-dreams | 2 | solved | 7 | 7 | 0 | 1 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | no-dreams | 3 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | no-dreams | 3 | rows | 8 | 0 | -8 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | no-library | 0 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | no-library | 0 | rows | 8 | 0 | -8 | 8 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | no-library | 1 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | no-library | 1 | rows | 8 | 0 | -8 | 8 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | no-library | 2 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | no-library | 2 | rows | 8 | 0 | -8 | 8 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | no-library | 3 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | no-library | 3 | rows | 8 | 0 | -8 | 8 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | no-proposer | 0 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | no-proposer | 0 | fraction | 0.75 | 0.25 | -0.50 | 0.38 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | no-proposer | 0 | median item wall seconds | 6.3 | 13.0 | 6.7 | 5.9 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | no-proposer | 0 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | no-proposer | 0 | solved | 6 | 2 | -4 | 3 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | no-proposer | 1 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | no-proposer | 1 | fraction | 0.25 | 0.00 | -0.25 | 0.38 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | no-proposer | 1 | median item wall seconds | 14.6 | 13.3 | -1.3 | 5.9 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | no-proposer | 1 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | no-proposer | 1 | solved | 2 | 0 | -2 | 3 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | no-proposer | 2 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | no-proposer | 2 | fraction | 0.38 | 0.88 | 0.50 | 0.38 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | no-proposer | 2 | median item wall seconds | 12.6 | 5.0 | -7.6 | 5.9 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | no-proposer | 2 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | no-proposer | 2 | solved | 3 | 7 | 4 | 3 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | no-proposer | 3 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | no-proposer | 3 | fraction | 0.38 | 0.38 | 0.00 | 0.38 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | no-proposer | 3 | median item wall seconds | 12.0 | 11.8 | -0.2 | 5.9 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | no-proposer | 3 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | retention | no-proposer | 3 | solved | 3 | 3 | 0 | 3 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | full | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | full | 0 | fraction | 0.58 | 0.54 | -0.04 | 0.21 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | full | 0 | median item wall seconds | 8.5 | 8.8 | 0.2 | 4.3 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | full | 0 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | full | 0 | solved | 28 | 26 | -2 | 10 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | full | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | full | 1 | fraction | 0.83 | 1.00 | 0.17 | 0.21 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | full | 1 | median item wall seconds | 4.0 | 0.8 | -3.2 | 4.3 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | full | 1 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | full | 1 | solved | 40 | 48 | 8 | 10 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | full | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | full | 2 | fraction | 0.79 | 0.81 | 0.02 | 0.21 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | full | 2 | median item wall seconds | 3.7 | 0.9 | -2.8 | 4.3 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | full | 2 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | full | 2 | solved | 38 | 39 | 1 | 10 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | full | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | full | 3 | fraction | 0.71 | 0.98 | 0.27 | 0.21 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | full | 3 | median item wall seconds | 4.6 | 2.4 | -2.1 | 4.3 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | full | 3 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | full | 3 | solved | 34 | 47 | 13 | 10 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 0 | fraction | 0.56 | 0.52 | -0.04 | 0.27 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 0 | median item wall seconds | 9.0 | 9.4 | 0.3 | 4.9 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 0 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 0 | solved | 27 | 25 | -2 | 13 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 1 | fraction | 0.77 | 0.96 | 0.19 | 0.27 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 1 | median item wall seconds | 3.9 | 1.3 | -2.6 | 4.9 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 1 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 1 | solved | 37 | 46 | 9 | 13 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 2 | fraction | 0.88 | 0.94 | 0.06 | 0.27 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 2 | median item wall seconds | 4.1 | 1.4 | -2.7 | 4.9 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 2 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 2 | solved | 42 | 45 | 3 | 13 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 3 | fraction | 0.71 | 0.94 | 0.23 | 0.27 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 3 | median item wall seconds | 4.9 | 3.3 | -1.6 | 4.9 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 3 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 3 | solved | 34 | 45 | 11 | 13 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-library | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-library | 0 | fraction | 0.23 | 0.23 | 0.00 | 0.02 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-library | 0 | median item wall seconds | 11.2 | 10.6 | -0.6 | 0.1 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-library | 0 | rows | 48 | 27 | -21 | 48 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-library | 0 | solved | 11 | 11 | 0 | 1 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-library | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-library | 1 | rows | 48 | 0 | -48 | 48 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-library | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-library | 2 | rows | 48 | 0 | -48 | 48 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-library | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-library | 3 | rows | 48 | 0 | -48 | 48 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 0 | fraction | 0.23 | 0.42 | 0.19 | 0.42 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 0 | median item wall seconds | 15.2 | 13.8 | -1.4 | 7.9 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 0 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 0 | solved | 11 | 20 | 9 | 20 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 1 | fraction | 0.12 | 0.12 | 0.00 | 0.42 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 1 | median item wall seconds | 13.7 | 14.3 | 0.5 | 7.9 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 1 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 1 | solved | 6 | 6 | 0 | 20 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 2 | fraction | 0.54 | 0.50 | -0.04 | 0.42 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 2 | median item wall seconds | 7.2 | 9.9 | 2.7 | 7.9 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 2 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 2 | solved | 26 | 24 | -2 | 20 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 3 | fraction | 0.46 | 0.42 | -0.04 | 0.42 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 3 | median item wall seconds | 11.3 | 12.0 | 0.7 | 7.9 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 3 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 3 | solved | 22 | 20 | -2 | 20 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | full | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | full | 0 | g | 0.58 | 0.54 | -0.04 | 0.21 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | full | 0 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | full | 0 | solved | 28 | 26 | -2 | 10 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | full | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | full | 1 | g | 0.83 | 1.00 | 0.17 | 0.21 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | full | 1 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | full | 1 | solved | 40 | 48 | 8 | 10 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | full | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | full | 2 | g | 0.79 | 0.81 | 0.02 | 0.21 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | full | 2 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | full | 2 | solved | 38 | 39 | 1 | 10 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | full | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | full | 3 | g | 0.71 | 0.98 | 0.27 | 0.21 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | full | 3 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | full | 3 | solved | 34 | 47 | 13 | 10 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 0 | g | 0.56 | 0.52 | -0.04 | 0.27 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 0 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 0 | solved | 27 | 25 | -2 | 13 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 1 | g | 0.77 | 0.96 | 0.19 | 0.27 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 1 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 1 | solved | 37 | 46 | 9 | 13 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 2 | g | 0.88 | 0.94 | 0.06 | 0.27 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 2 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 2 | solved | 42 | 45 | 3 | 13 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 3 | g | 0.71 | 0.94 | 0.23 | 0.27 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 3 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 3 | solved | 34 | 45 | 11 | 13 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 0 | g | 0.23 | 0.23 | 0.00 | 0.31 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 0 | rows | 48 | 27 | -21 | 48 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 0 | solved | 11 | 11 | 0 | 15 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 1 | g | 0.17 | 0.00 | -0.17 | 0.31 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 1 | rows | 48 | 0 | -48 | 48 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 1 | solved | 8 | 0 | -8 | 15 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 2 | g | 0.12 | 0.00 | -0.12 | 0.31 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 2 | rows | 48 | 0 | -48 | 48 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 2 | solved | 6 | 0 | -6 | 15 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 3 | g | 0.29 | 0.00 | -0.29 | 0.31 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 3 | rows | 48 | 0 | -48 | 48 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 3 | solved | 14 | 0 | -14 | 15 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 0 | g | 0.23 | 0.42 | 0.19 | 0.42 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 0 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 0 | solved | 11 | 20 | 9 | 20 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 1 | g | 0.12 | 0.12 | 0.00 | 0.42 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 1 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 1 | solved | 6 | 6 | 0 | 20 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 2 | g | 0.54 | 0.50 | -0.04 | 0.42 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 2 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 2 | solved | 26 | 24 | -2 | 20 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 3 | g | 0.46 | 0.42 | -0.04 | 0.42 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 3 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 3 | solved | 22 | 20 | -2 | 20 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | full | 0 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | full | 0 | fraction | 0.38 | 0.75 | 0.38 | 0.25 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | full | 0 | median item wall seconds | 11.2 | 3.6 | -7.6 | 2.8 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | full | 0 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | full | 0 | solved | 3 | 6 | 3 | 2 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | full | 1 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | full | 1 | fraction | 0.88 | 1.00 | 0.12 | 0.25 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | full | 1 | median item wall seconds | 2.7 | 0.6 | -2.2 | 2.8 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | full | 1 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | full | 1 | solved | 7 | 8 | 1 | 2 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | full | 2 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | full | 2 | fraction | 0.88 | 1.00 | 0.12 | 0.25 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | full | 2 | median item wall seconds | 3.1 | 0.6 | -2.5 | 2.8 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | full | 2 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | full | 2 | solved | 7 | 8 | 1 | 2 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | full | 3 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | full | 3 | fraction | 0.88 | 1.00 | 0.12 | 0.25 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | full | 3 | median item wall seconds | 4.4 | 2.1 | -2.4 | 2.8 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | full | 3 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | full | 3 | solved | 7 | 8 | 1 | 2 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 0 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 0 | fraction | 0.38 | 0.75 | 0.38 | 0.12 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 0 | median item wall seconds | 10.8 | 5.8 | -5.0 | 4.5 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 0 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 0 | solved | 3 | 6 | 3 | 1 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 1 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 1 | fraction | 0.88 | 0.75 | -0.12 | 0.12 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 1 | median item wall seconds | 2.8 | 2.2 | -0.5 | 4.5 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 1 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 1 | solved | 7 | 6 | -1 | 1 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 2 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 2 | fraction | 0.88 | 1.00 | 0.12 | 0.12 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 2 | median item wall seconds | 4.1 | 1.5 | -2.5 | 4.5 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 2 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 2 | solved | 7 | 8 | 1 | 1 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 3 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 3 | fraction | 0.88 | 1.00 | 0.12 | 0.12 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 3 | median item wall seconds | 4.1 | 2.2 | -1.8 | 4.5 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 3 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 3 | solved | 7 | 8 | 1 | 1 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-library | 0 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-library | 0 | rows | 8 | 0 | -8 | 8 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-library | 1 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-library | 1 | rows | 8 | 0 | -8 | 8 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-library | 2 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-library | 2 | rows | 8 | 0 | -8 | 8 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-library | 3 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-library | 3 | rows | 8 | 0 | -8 | 8 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 0 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 0 | fraction | 0.75 | 0.50 | -0.25 | 0.38 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 0 | median item wall seconds | 6.3 | 7.9 | 1.6 | 5.9 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 0 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 0 | solved | 6 | 4 | -2 | 3 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 1 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 1 | fraction | 0.25 | 0.25 | 0.00 | 0.38 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 1 | median item wall seconds | 14.6 | 11.8 | -2.8 | 5.9 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 1 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 1 | solved | 2 | 2 | 0 | 3 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 2 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 2 | fraction | 0.38 | 0.62 | 0.25 | 0.38 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 2 | median item wall seconds | 12.6 | 1.2 | -11.4 | 5.9 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 2 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 2 | solved | 3 | 5 | 2 | 3 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 3 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 3 | fraction | 0.38 | 0.50 | 0.12 | 0.38 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 3 | median item wall seconds | 12.0 | 9.7 | -2.3 | 5.9 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 3 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 3 | solved | 3 | 4 | 1 | 3 | within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | full | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | full | 0 | fraction | 0.54 | 0.54 | 0.00 | 0.21 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | full | 0 | median item wall seconds | 9.4 | 8.8 | -0.6 | 4.3 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | full | 0 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | full | 0 | solved | 26 | 26 | 0 | 10 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | full | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | full | 1 | fraction | 0.69 | 1.00 | 0.31 | 0.21 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | full | 1 | median item wall seconds | 4.3 | 0.8 | -3.5 | 4.3 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | full | 1 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | full | 1 | solved | 33 | 48 | 15 | 10 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | full | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | full | 2 | fraction | 0.79 | 0.81 | 0.02 | 0.21 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | full | 2 | median item wall seconds | 5.0 | 0.9 | -4.2 | 4.3 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | full | 2 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | full | 2 | solved | 38 | 39 | 1 | 10 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | full | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | full | 3 | fraction | 0.75 | 0.98 | 0.23 | 0.21 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | full | 3 | median item wall seconds | 3.4 | 2.4 | -1.0 | 4.3 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | full | 3 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | full | 3 | solved | 36 | 47 | 11 | 10 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 0 | fraction | 0.56 | 0.52 | -0.04 | 0.27 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 0 | median item wall seconds | 9.1 | 9.4 | 0.3 | 4.9 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 0 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 0 | solved | 27 | 25 | -2 | 13 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 1 | fraction | 0.52 | 0.96 | 0.44 | 0.27 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 1 | median item wall seconds | 9.5 | 1.3 | -8.2 | 4.9 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 1 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 1 | solved | 25 | 46 | 21 | 13 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 2 | fraction | 0.73 | 0.94 | 0.21 | 0.27 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 2 | median item wall seconds | 5.3 | 1.4 | -3.8 | 4.9 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 2 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 2 | solved | 35 | 45 | 10 | 13 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | no-dreams | 3 | rows | 0 | 48 | 48 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | no-library | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | no-library | 0 | rows | 0 | 27 | 27 | 48 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | no-library | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | no-library | 1 | rows | 0 | 0 | 0 | 48 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | no-library | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | no-library | 2 | rows | 0 | 0 | 0 | 48 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | no-library | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | no-library | 3 | rows | 0 | 0 | 0 | 48 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 0 | fraction | 0.08 | 0.42 | 0.33 | 0.42 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 0 | median item wall seconds | 14.2 | 13.8 | -0.4 | 7.9 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 0 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 0 | solved | 4 | 20 | 16 | 20 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 1 | fraction | 0.04 | 0.12 | 0.08 | 0.42 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 1 | median item wall seconds | 13.8 | 14.3 | 0.4 | 7.9 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 1 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 1 | solved | 2 | 6 | 4 | 20 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 2 | fraction | 0.50 | 0.50 | 0.00 | 0.42 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 2 | median item wall seconds | 9.9 | 9.9 | -0.0 | 7.9 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 2 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 2 | solved | 24 | 24 | 0 | 20 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 3 | fraction | 0.40 | 0.42 | 0.02 | 0.42 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 3 | median item wall seconds | 12.1 | 12.0 | -0.1 | 7.9 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 3 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | assessment | no-proposer | 3 | solved | 19 | 20 | 1 | 20 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | full | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | full | 0 | g | 0.54 | 0.54 | 0.00 | 0.21 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | full | 0 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | full | 0 | solved | 26 | 26 | 0 | 10 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | full | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | full | 1 | g | 0.69 | 1.00 | 0.31 | 0.21 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | full | 1 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | full | 1 | solved | 33 | 48 | 15 | 10 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | full | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | full | 2 | g | 0.79 | 0.81 | 0.02 | 0.21 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | full | 2 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | full | 2 | solved | 38 | 39 | 1 | 10 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | full | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | full | 3 | g | 0.75 | 0.98 | 0.23 | 0.21 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | full | 3 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | full | 3 | solved | 36 | 47 | 11 | 10 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 0 | g | 0.56 | 0.52 | -0.04 | 0.27 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 0 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 0 | solved | 27 | 25 | -2 | 13 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 1 | g | 0.52 | 0.96 | 0.44 | 0.27 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 1 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 1 | solved | 25 | 46 | 21 | 13 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 2 | g | 0.73 | 0.94 | 0.21 | 0.27 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 2 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 2 | solved | 35 | 45 | 10 | 13 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 3 | g | 0.00 | 0.94 | 0.94 | 0.27 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 3 | rows | 0 | 48 | 48 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-dreams | 3 | solved | 0 | 45 | 45 | 13 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 0 | g | 0.00 | 0.23 | 0.23 | 0.31 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 0 | rows | 0 | 27 | 27 | 48 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 0 | solved | 0 | 11 | 11 | 15 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 1 | g | 0.00 | 0.00 | 0.00 | 0.31 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 1 | rows | 0 | 0 | 0 | 48 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 1 | solved | 0 | 0 | 0 | 15 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 2 | g | 0.00 | 0.00 | 0.00 | 0.31 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 2 | rows | 0 | 0 | 0 | 48 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 2 | solved | 0 | 0 | 0 | 15 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 3 | g | 0.00 | 0.00 | 0.00 | 0.31 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 3 | rows | 0 | 0 | 0 | 48 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-library | 3 | solved | 0 | 0 | 0 | 15 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 0 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 0 | g | 0.08 | 0.42 | 0.33 | 0.42 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 0 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 0 | solved | 4 | 20 | 16 | 20 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 1 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 1 | g | 0.04 | 0.12 | 0.08 | 0.42 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 1 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 1 | solved | 2 | 6 | 4 | 20 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 2 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 2 | g | 0.50 | 0.50 | 0.00 | 0.42 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 2 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 2 | solved | 24 | 24 | 0 | 20 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 3 | N | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 3 | g | 0.40 | 0.42 | 0.02 | 0.42 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 3 | rows | 48 | 48 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | curve | no-proposer | 3 | solved | 19 | 20 | 1 | 20 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | full | 0 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | full | 0 | fraction | 0.88 | 0.75 | -0.12 | 0.25 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | full | 0 | median item wall seconds | 9.1 | 3.6 | -5.5 | 2.8 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | full | 0 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | full | 0 | solved | 7 | 6 | -1 | 2 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | full | 1 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | full | 1 | fraction | 0.62 | 1.00 | 0.38 | 0.25 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | full | 1 | median item wall seconds | 4.2 | 0.6 | -3.7 | 2.8 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | full | 1 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | full | 1 | solved | 5 | 8 | 3 | 2 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | full | 2 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | full | 2 | fraction | 0.88 | 1.00 | 0.12 | 0.25 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | full | 2 | median item wall seconds | 3.6 | 0.6 | -3.0 | 2.8 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | full | 2 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | full | 2 | solved | 7 | 8 | 1 | 2 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | full | 3 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | full | 3 | fraction | 0.88 | 1.00 | 0.12 | 0.25 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | full | 3 | median item wall seconds | 3.4 | 2.1 | -1.3 | 2.8 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | full | 3 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | full | 3 | solved | 7 | 8 | 1 | 2 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 0 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 0 | fraction | 0.88 | 0.75 | -0.12 | 0.12 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 0 | median item wall seconds | 6.7 | 5.8 | -0.9 | 4.5 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 0 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 0 | solved | 7 | 6 | -1 | 1 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 1 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 1 | fraction | 0.62 | 0.75 | 0.12 | 0.12 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 1 | median item wall seconds | 5.8 | 2.2 | -3.6 | 4.5 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 1 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 1 | solved | 5 | 6 | 1 | 1 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 2 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 2 | fraction | 0.88 | 1.00 | 0.12 | 0.12 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 2 | median item wall seconds | 3.0 | 1.5 | -1.5 | 4.5 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 2 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 2 | solved | 7 | 8 | 1 | 1 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 3 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | no-dreams | 3 | rows | 0 | 8 | 8 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | no-library | 0 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | no-library | 0 | rows | 0 | 0 | 0 | 8 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | no-library | 1 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | no-library | 1 | rows | 0 | 0 | 0 | 8 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | no-library | 2 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | no-library | 2 | rows | 0 | 0 | 0 | 8 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | no-library | 3 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | no-library | 3 | rows | 0 | 0 | 0 | 8 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 0 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 0 | fraction | 0.25 | 0.50 | 0.25 | 0.38 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 0 | median item wall seconds | 13.0 | 7.9 | -5.1 | 5.9 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 0 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 0 | solved | 2 | 4 | 2 | 3 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 1 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 1 | fraction | 0.00 | 0.25 | 0.25 | 0.38 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 1 | median item wall seconds | 13.3 | 11.8 | -1.4 | 5.9 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 1 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 1 | solved | 0 | 2 | 2 | 3 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 2 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 2 | fraction | 0.88 | 0.62 | -0.25 | 0.38 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 2 | median item wall seconds | 5.0 | 1.2 | -3.7 | 5.9 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 2 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 2 | solved | 7 | 5 | -2 | 3 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 3 | N | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 3 | fraction | 0.38 | 0.50 | 0.12 | 0.38 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 3 | median item wall seconds | 11.8 | 9.7 | -2.0 | 5.9 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 3 | rows | 8 | 8 | 0 | 0 | at or above measured spread | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | retention | no-proposer | 3 | solved | 3 | 4 | 1 | 3 | within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
<!-- generated:end differences -->

<!-- generated:begin sources -->
| saved path | status | sha256 of bytes read | false credit |
|---|---|---|---|
| sera-runs/u8-u9-vmc-9036ca3/u-discovery-off/g_curve.json | read | 86e3f3bb51a1d28b502744967c875f57935aa60701546b313fbb1accbbe72228 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0; u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| sera-runs/u8-u9-vmc-9036ca3/u-discovery-off/protocol.json | read | 9498bfa73fb6eef3a3ecf0d47118f25f8efa8463e401fb5d556c679c00cfabd8 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0; u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| sera-runs/u8-u9-vmc-9036ca3/u-discovery-off/state.json | read | 61f05439833f4219026ab4ea7f194d3f80505d3f56b27648c4e95915ab52fa17 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0; u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| sera-runs/u8-u9-vmc-9036ca3/u-full/g_curve.json | read | c5ee2ed00cef5c5fda0a45a40ec2fcc0d39ad7669a60566c7bf81ebb5eab671f | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0; u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| sera-runs/u8-u9-vmc-9036ca3/u-full/protocol.json | read | 81a221eb73b6c86b0f7a72f126473164322a140c0f5211b2ef50dda339bc447a | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0; u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| sera-runs/u8-u9-vmc-9036ca3/u-full/state.json | read | d1277f1c73674024a0dabb7d1a25415080870955a9966da64dbe67f11d46f657 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0; u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| sera-runs/u8-u9-vmc-9036ca3/u-mem-choice/g_curve.json | read | e419973fdf0375eaafec12b8072003982b768d258d970469a681761d12411ef6 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0; u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| sera-runs/u8-u9-vmc-9036ca3/u-mem-choice/protocol.json | read | 30d48e529b4bd287b785e4e3f9618c331971b4d0c01fb2616ac06ab02d4f5522 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0; u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| sera-runs/u8-u9-vmc-9036ca3/u-mem-choice/state.json | read | e5680fc4013b55244b5a6e1cdc8528384fe53a4adca0d148902e3b1753cb49e6 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0; u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| sera-runs/u8-u9-vmc-9036ca3/u-no-memory/g_curve.json | read | 1feda25c8b3d0b948d48e2b735fea7459f61ad27e9d320bceb5cdc2ab666eb30 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0; u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| sera-runs/u8-u9-vmc-9036ca3/u-no-memory/protocol.json | read | 99718ff75d528cb0a70919f48b2069deb8c18e86505e9dc0f9896702e1253e25 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0; u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| sera-runs/u8-u9-vmc-9036ca3/u-no-memory/state.json | read | 67d1880944548e6ce5cfdd6f6b792162402dfbd032c33032c2d1743779f72c83 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0; u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| sera-runs/u9-discovery-vmc/u-discovery-no-unify/g_curve.json | read | 224c356ecf26704a3be332f508fb137f56dd983f43dda77d87b0152dd1f2f1ad | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0; u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| sera-runs/u9-discovery-vmc/u-discovery-no-unify/protocol.json | read | 135ebf42cd1943cb2bd1dd84430e563a6aa427ba080baf41c61e006bdac8223e | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0; u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| sera-runs/u9-discovery-vmc/u-discovery-no-unify/state.json | read | bb25f1397e924faa37abe4c1f234ec4ce1d38cf1f0a74f937903f7b07b7718d3 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0; u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| sera-runs/u9-discovery-vmc/u-discovery-random/g_curve.json | read | 3c6ec8b2894f2bc40cd804c59c94e0ba91dcad8cdcf5be44684d4a322f5b15e9 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0; u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| sera-runs/u9-discovery-vmc/u-discovery-random/protocol.json | read | be2b5524c55bc6d650c22b1672c8d155ab6fa93e07b0d1d7bb2b04ea2fa18871 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0; u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| sera-runs/u9-discovery-vmc/u-discovery-random/state.json | read | a523c18d7ca8a3dd73eadd20732ffff82030a54bc28494e0ba87c17042b606ba | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0; u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| sera-runs/u9-discovery-vmc/u-discovery/g_curve.json | read | 05be015352ab4101a473423fe7d8747f404ee002f046efd4d6193a23c64ae06e | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0; u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| sera-runs/u9-discovery-vmc/u-discovery/protocol.json | read | e296659102ddeb2164b349075003d11001b2ea9c86e198ab42bdc49798213fc3 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0; u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
| sera-runs/u9-discovery-vmc/u-discovery/state.json | read | 6b620440ba095702449732894a0dc9798faaab24763662fbdeb129b03f8e0b05 | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0; u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |
<!-- generated:end sources -->
