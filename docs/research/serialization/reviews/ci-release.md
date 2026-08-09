# SQ-0005 CI and release-boundary review

Status: **Experimental review record**

Disposition: **APPROVE FOR HOSTED RERUN**

Review date: 2026-08-09

Reviewer: `/root/sq0005_ci_release_backup`, acting as the independent CI,
reproducibility, dependency-gate, and release-boundary reviewer

## Decision

The focused checkout correction is approved for hosted rerun. The first hosted
run reached the final deterministic-regeneration step after every earlier
workflow gate passed, then failed because the default one-commit checkout did
not contain the reviewed baseline object. Setting `fetch-depth: 0` only on the
conformance checkout is necessary and sufficient for the current verifier.

This remains conditional. A successful rerun on the exact corrected head and a
successful post-merge run on `main` are required before merge/integration may
be described as green.

## Exact subjects

| Subject | Exact identity |
|---|---|
| Original implementation subject | `410465d773fc011ee01e38e6e76a79a60efe8837` |
| First hosted/final-state subject | `cc1021e33441b4bfba5c1459d644d2c5a6b79127` |
| Failed hosted run | `31320961923` |
| Failed conformance job | `93263761605` |
| Failed step | `Confirm static evidence and clean regeneration` |
| Corrected workflow SHA-256 | `3cb67d26721258413ff80150df453dca77f76ea77374fe6a5a92bd7494cd8536` |
| Retained failure record | `conformance/prototypes/results/failures/hosted-shallow-checkout-baseline-v1.json` |
| Retained failure SHA-256 | `c78fcfb1efa2741db07118c228a9a753f54edffa86ea47beb21970100019b6d2` |
| Required baseline | `8875d8f6fa8e3b45e706ea567d45448927a02efa` |

The focused manager change adds only `fetch-depth: 0` to the conformance
checkout, retains the minimized failure record, and rebinds the RFC workflow
hash. It does not change an implementation, fixture, semantic rule, action
revision, toolchain, lock, permission, or execution command.

## Hosted failure disposition

Official GitHub run metadata confirms:

- workflow `Serialization prototypes`, pull-request head `cc1021e...`;
- Python 3.12.13 job `93263761564`: success;
- Python 3.14.7 job `93263761592`: success;
- conformance job `93263761605`: failure only in its final step;
- source-audit verification passed;
- static evidence verification passed for 156 subjects and 203 negative
  fixtures;
- all 12 evidence-corruption tests passed; and
- evidence-manifest regeneration then failed because `git show` could not
  resolve baseline commit `8875d8f...` in the depth-one clone.

The retained record classifies this as
`reproducibility_environment_failure`, binds the run, job, head, command, exact
failure, cause, and remediation, and does not rewrite the failed observation
as success.

## Why complete history is required

The permanent evidence builder compares protected paths and RFC-0006 against
the exact reviewed base. It must read
`8875d8f...:rfcs/0006-canonical-logical-data-digest.md` from Git, not trust only
the current working-tree copy. A depth-one checkout contains the file but not
the historical commit object, so it cannot establish byte identity with the
reviewed baseline.

`8875d8f...` is an ancestor of the failed head. `fetch-depth: 0` makes the
needed commit and tree objects locally available, which is sufficient for all
existing `git show`/protected-diff operations. No submodule, LFS object,
additional action, write permission, persisted credential, or executable from
old history is needed. The Python-only jobs retain shallow checkouts because
they do not run baseline-dependent evidence regeneration.

## Least privilege and unchanged gates

The workflow still has only `contents: read`; checkout remains pinned to
`3d3c42e5aac5ba805825da76410c181273ba90b1` and keeps
`persist-credentials: false`. Setup Python remains commit-pinned. Timeouts,
concurrency, exact Python 3.12.13/3.14.7, exact Rust 1.97.1, clean Cargo home,
locked/offline Rust gates, Cargo.lock drift, differential/mutation/resource
tests, inventory/live-yanked checks, immutable advisory inputs, corruption
tests, clean regeneration, and runner metadata are unchanged.

Fetching read-only history increases downloaded Git objects but does not
expand repository permissions or execute historical content. Only scripts at
the checked-out reviewed head execute. Hosted `ubuntu-24.04` remains a mutable
observed runner, not a cross-platform or immutable-platform support claim.

The workflow has no upload, release, deployment, or write-token step. Its
license and advisory results remain exact-lock, point-in-time observations,
not distribution approval or a security guarantee.

## Review checks

```text
gh run view 31320961923 --job 93263761605 --log-failed
  PASS: exact run/head/jobs and shallow-baseline failure reproduced in logs

sha256sum .github/workflows/serialization-prototypes.yml
  PASS: 3cb67d26721258413ff80150df453dca77f76ea77374fe6a5a92bd7494cd8536

git merge-base --is-ancestor 8875d8f... cc1021e...
  PASS: baseline belongs to the reviewed ancestry

git diff --check
  PASS: focused manager change has no whitespace errors
```

## Conditions before merge

1. Commit the focused correction and rebind every final evidence/review hash
   affected by the workflow and retained failure record.
2. Rerun `Serialization prototypes` on that exact pull-request head. Both
   Python jobs and the complete conformance job, especially deterministic
   manifest regeneration and final clean diff, must succeed.
3. Retain run ID, head SHA, job IDs, timestamps, and observed runner-image
   metadata. Do not replace the retained failed-run record.
4. Any further workflow change invalidates this disposition and requires
   another focused review.
5. Require the same workflow to succeed on the exact merged `main` commit.

Subject to those conditions, the shallow-checkout failure is correctly
explained and the full-history conformance checkout is approved for rerun.
