# One SERA for physics, code and words (G1)

Plan revision 4, R4-5. development review, 2026-09-26. Built on research RG (`(review notes, not published)`, reviewer medium with search;
its sources were opened in its session). Status: the shared language exists (`sera/general.py`, 9 tests), and so
does the G2 machinery (`sera/synth.py`, 3 tests: the loop finds and audits small list functions). The pre-registered
G2 experiment, words (G3) and the transfer test (G4) are next.

## 1. What "the same SERA" means, exactly

One mind, with one set of parts. Only three things differ by domain: what the world is, which primitives the
language offers, and how a claim is verified.

| Part | Shared | Per domain |
|---|---|---|
| **Hypothesis language** | typed programs: shared constructors (add, mul, neg, compare, and, or, not, if, map, filter, lambda) and one prefix code, `pi0(p) = 2^-L(p)`, Kraft ≤ 1 | the primitives: grammar terms of (x, v, t); list and integer operations; thing features |
| **Belief** | `b(p) ∝ p_F(p) m(p)`, the Field's floor `p_F = (1 − eta) p_mem + eta pi0` | `m(p)`: the evidence model (Gaussian evidence for physics; exact agreement for code; the caretaker's likelihood for words) |
| **Imagination** | one proposer over the language's symbols | – |
| **Memory** | memory v3 (`sera/memory.py`): tags, lessons, skills, knowledge; domains never mix | the context features |
| **Questions** | ask where the surviving hypotheses disagree most: Box–Hill for pushes, output-partition entropy for inputs | the available questions: pushes; inputs; rooms |
| **Verifier** | returns a certificate with scope and premises, or a refusal with its reason | the e-value judge; execution plus an audit; grounding e-values; Lean |

A physics law is `λ(x, v, t). Σ_j c_j φ_j(x, v, t)`. A list function is a program from a list to a value. The word
"iron" is a predicate over a thing. All three are programs in the one language, built from the same constructors.

## 2. The shared language (built: `sera/general.py`)

- **Programs** are trees: `(symbol, payload, children...)`. Every symbol has argument types, a result type and the
  domains it may appear in. The element variable `e` is allowed only inside a `lam_*` node.
- **Search prior.** The program is written in preorder. Each node is chosen from the symbols that fit its slot's type
  and domain, so `L(p) = Σ log2 |alphabet(slot)|`, plus payload tables. This is a branching process, so
  `Σ_p 2^-L(p) ≤ 1`, checked numerically to depth 4 for every type and domain. The prior guides search only.
- **Proof prices never change.** A physics claim keeps the judge's frozen D9 prior (`price_physics`). The judge,
  the checker and every certificate are untouched.
- **Physics adapter.** All 3,175 laws of the Field, plus the empty law (`zero`), round-trip exactly through
  `encode_law` and `decode_law`. Each has one canonical spelling. Evaluating a law program calls the judge's own
  term code, so its force is bit for bit the judge's.

## 3. Verifiers: what "sure" means in each domain

- **Physics:** the e-value judge (docs/SERA_EXPLAINED.md Part 3), under the premises P, M, N, U, S, F and Q.
- **Code: exact execution plus an anytime audit** (RG section 2.2, derived there).
  - Freeze the program `p`, the input distribution `D` and the prior before the audit. Draw fresh IID inputs with
    exact oracle outputs.
  - Under the null `H0(p): R_D(p) ≥ epsilon`, the quantity `E_{p,n} = 1{all n pass} / (1 − epsilon)^n` is a
    nonnegative supermartingale.
  - By Ville plus a union bound over programs weighted by `pi0`: `P(some program is ever accepted with error ≥
    epsilon) ≤ delta` when programs are accepted at `E_{p,n} ≥ 1 / (delta pi0(p))`.
  - That is "sure the error rate under D is below epsilon", never "correct everywhere". Exact correctness needs an
    exhaustive bounded domain or a proof.
  - Adaptive questions may find counterexamples, but they never count toward the audit.
- **Words:** a lexicon entry maps a word to a predicate. Its evidence comes from the caretaker's known utterance
  likelihood, and the same e-value construction applies. The claim holds within the playroom's grammar and reference
  distribution only, never for English at large.
- **Mathematics:** Lean proofs (the B6 track).

## 4. Next, each pre-registered before it runs (RG section 6)

- **G2 code pilot.**
  - **Tasks:** 12 task schemas over integers in [−8, 8], lists of length 0 to 6, and two-operator compositions.
    Each schema gets 10 development instances and 10 fresh ones.
  - **Loop:** the same dream → test → revise loop. Enumerate by code length, cache each program's output vector,
    ask the input that best splits the survivors, then run the audit above.
  - **Baseline:** the same grammar's size-ordered enumerator, with the same CPU, examples and question budget.
  - **Bars, on fresh instances:**
    - ≥ 1.5× programs solved per CPU-second (paired, lower 95% bound > 1);
    - held-out correctness ≥ baseline;
    - 0 accepted-but-wrong on 100 audit inputs each;
    - ≥ 50% of tasks accepted, so the safety bar cannot pass vacuously.
- **G3 words.** Playroom predicates for the material, size, shape and relative-mass words.
  - **Bars:** top-1 grounded mapping ≥ 90% for visible features and ≥ 75% for mass and room predicates; 0 checker-
    accepted false mappings; ≥ 50% certificate coverage.
- **G4 transfer, "the same entity" measured.** One shared proposer against three per-domain proposers of the same
  size. The three together have three times the weights, which is reported; a matched total size is also run.
  - **Bars:** paired by task, clustered by program skeleton, with Bonferroni simultaneous bounds. The lower bound
    must be ≥ 0 on every domain and > 0 on at least one, with no held-out decline beyond 2 points.
  - A shared model that does worse is reported as it is. Then the architecture changes, never the bar.

## 5. Honest limits

- A shared syntax can be cosmetic: a shared encoder may just memorize the domain tag. G4 is the test of that.
- A 30k-parameter proposer on a laptop will not be "good at language" the way a large model is. The claim here is one
  mechanism, and it is measured.
- No source RG opened tests one shared proposer against per-domain proposers of equal size on physics, code and
  language. G4's outcome is unknown.
