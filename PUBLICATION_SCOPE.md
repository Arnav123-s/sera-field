# Publication scope

This release preserves the assessed releases from public base `8511d5f`, refreshes SERA Field records
and adds a reviewed current-file snapshot of the SERA discovery lab.

- Learned-field source revision: `7c39634b7cc193dfa50c894ec1e69e42993a3f73`.
- Discovery-lab source revision: `04fd415caf790f1476e138809e32e905f7e31392`.
- Unified-lab source revision: `120fdc46d629923b7c60d010854da297a01a4ed1`.
- Publication date: 2026-10-02.

Included: implementation, tests, prospective protocols, architecture and usage
guides, compact results, costs, and assessed inference checkpoints already in
the public repository. The lab adds selected text run artifacts under 1 MiB per
file. Active, incomplete, and planned studies are labeled accordingly.

Excluded: private Git history, raw source attachments and human corpora, full
training and optimizer/RNG archives, binary lab Fields, environment files,
credentials, development instructions, session records, and preparation tooling.
All original research repositories and complete local evidence remain preserved.

Publication adaptations: development attribution and private machine paths are
removed from prose; the lab README uses portable setup commands; the editable
lab package includes both `sera` and `ccops5`. Previously declared report-path
and validation-name renames are retained. Scientific results are not recomputed
or promoted by this publication.

[PUBLICATION_MANIFEST.json](PUBLICATION_MANIFEST.json) records SHA-256 identities
of Git blob bytes for every published file except the manifest itself.

This update adds the unified implementation and compact incomplete-pilot evidence.
It preserves older experiment tracks and assessed checkpoints. The unified design
omits local coordination and operational handoffs; current status is documented separately.
The vendored Field manifest retains upstream and pre-publication identities and
records published-file hashes after prose and line-ending adaptations.
