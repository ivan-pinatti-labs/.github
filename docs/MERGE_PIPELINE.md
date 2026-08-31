# The Merge Pipeline

<!-- cspell:words coderabbit coderabbitai -->

What happens between opening a pull request against this repository and it
landing on `main`. This is a much thinner version of rsync-crypt's document
of the same name: this repository has no app code, no build, no tests, and
no merge queue, so most of what makes that pipeline complex does not apply
here. Where the reasoning is identical it is only summarized, not restated;
see rsync-crypt's `docs/MERGE_PIPELINE.md` for the fuller version this one
was trimmed from.

## What actually gates a merge

Two required status checks, both from `main`'s branch protection:

| Context | What it actually proves | Who publishes it |
| --- | --- | --- |
| `Pre-commit` | The full pre-commit hook set passed over every file | `pull-request-validation.yml`, as a job |
| `Review Verified` | CodeRabbit's actual review outcome, not merely that it reported something | `coderabbit-gate.yml`, published directly onto the head SHA |

There is no `Tests` context (no app code to run tests against) and no
`Pin Only` context: unlike rsync-crypt, a dependency bump here is not
auto-approved or fast-tracked around review, so every pull request, bot
authored or not, is graded the same way in the table above. Branch
protection requires no PR approval and no linear-history-only queue trick:
Ivan is the only account with write access here, and merges by hand once
both contexts are green. There is no `merge_group` trigger anywhere in this
repository's workflows because there is no merge queue ruleset to feed one.

## A human pull request

Open it as a **draft** first. `Pre-commit` runs the full hook set over every
file, and CodeRabbit does not review a draft at all: `.coderabbit.yaml` sets
`drafts: false` on purpose, so a review is not spent on a diff the mechanical
linters have not finished cleaning up yet. Mark it ready once `Pre-commit` is
green; that is what starts CodeRabbit. Merge once `Review Verified` reads
`success` too.

## A dependency bot pull request

Dependabot (`.github/dependabot.yml`, `github-actions` and `pre-commit`
ecosystems) opens these unattended. CodeRabbit does not automatically review
a pull request it did not see a human open, so nothing would ever turn
`Review Verified` green on its own here. `coderabbit-review-queue.yml`'s
hourly nudge is what asks for the review CodeRabbit would otherwise never
give a bot's pull request; see rsync-crypt's `CLAUDE.md`, "Dependency-bot
pull requests are not reviewed automatically," for the mechanism and its
caveats. Once that review lands as `Review completed`, the pull request
merges the same way a human one does: by hand, once both contexts are green.

## `Review Verified`, and the bug it exists to fix

Ported unchanged in reasoning from rsync-crypt: a green `CodeRabbit` check
does not mean a review happened, because CodeRabbit posts through the legacy
commit status API, which has no state for "green, but not for the reason you
think." `scripts/coderabbit-review-verdict.py`, published as
`Review Verified` by `coderabbit-gate.yml`, reads the actual description
behind the `CodeRabbit` status rather than its color. A draft is `pending`;
`Review completed` is `success`; an in-flight review (`Review queued` or
`Review in progress`) is `pending`; anything else, including no status at
all, is `failure`. There is no bot lane here: rsync-crypt's version grades a
pin-only dependency bump `success` without a review at all, but that lane
exists only because rsync-crypt has a `Pin Only` context to gate it on; this
repository has none, so every pull request, bot authored or not, is graded
on the same three lanes above.

## Recovering a stuck `Review Verified`

`coderabbit-gate.yml`'s hourly schedule and its `workflow_dispatch` recovery
path work the same way as rsync-crypt's; see that repository's
`docs/MERGE_PIPELINE.md`, "Recovering a stuck `Review Verified`, honestly,"
for the caveats about GitHub deprioritizing scheduled runs on public
repositories.

## Release automation is not part of this gate

`.github/workflows/release-please.yml` runs on push to `main`, after a merge,
not as a pull request check. It is not a required status context and cannot
block or delay a merge.

---

See also: [profile/README.md](../profile/README.md)
