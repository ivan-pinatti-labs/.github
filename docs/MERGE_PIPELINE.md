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

Three status checks, from `main`'s branch protection:

| Context | What it actually proves | Who publishes it |
| --- | --- | --- |
| `Pre-commit` | The full pre-commit hook set passed over every file | `pull-request-validation.yml`, as a job |
| `Review Verified` | CodeRabbit's actual review outcome, not merely that it reported something | `coderabbit-gate.yml`, published directly onto the head SHA |
| `Pin Only` | A Renovate diff changes nothing but a pin, on the two surfaces `.github/pin-only.yml` allows; `success` with "not a dependency bot pull request" on everything else | `coderabbit-gate.yml`, published directly onto the head SHA |

`Pin Only` is required as of this change, and the ordering is worth stating
because it cannot be otherwise: a required context that nothing has ever
published blocks every pull request, including the one that adds it. So the
gate ships first, publishes `Pin Only` at least once, and branch protection
is updated straight after. If you are reading this while that second step is
still outstanding, `Pin Only` is publishing but advisory.

There is no `Tests` context (no app code to run tests against). `Pin Only`
is new, and it is what gives this repository the bot lane it spent its whole
life without: a Renovate diff that changes nothing but a `rev:` pin or a
`uses:` pin resolves `Review Verified` through it, with CodeRabbit never
asked. Everything else, bot authored or not, is still graded the same way in
the table above, and so is a Renovate diff that fails `Pin Only`. The
development container base image digest is deliberately outside that lane;
`.github/pin-only.yml` says why. Branch
protection requires no PR approval and no linear-history-only queue trick:
Ivan is the only account with write access here, and merges by hand once
the contexts are green. There is no `merge_group` trigger anywhere in this
repository's workflows because there is no merge queue ruleset to feed one.

## A human pull request

Open it as a **draft** first. `Pre-commit` runs the full hook set over every
file, and CodeRabbit does not review a draft at all: `.coderabbit.yaml` sets
`drafts: false` on purpose, so a review is not spent on a diff the mechanical
linters have not finished cleaning up yet. Mark it ready once `Pre-commit` is
green; that is what starts CodeRabbit. Merge once `Review Verified` reads
`success` too.

## A dependency bot pull request

Renovate (`.github/renovate.json5`, `github-actions`, `pre-commit` and
`dockerfile` managers) opens these unattended.

**A pin-only diff needs none of what follows.** A `rev:` or `uses:` bump on
the two surfaces `.github/pin-only.yml` allows passes `Pin Only`, which
resolves `Review Verified` to `success` through the shared check's bot lane,
and the pull request is ready to merge with CodeRabbit never asked.

The rest of this section is for the bumps that do not qualify: a base image
digest, which is outside the lane on purpose, and anything whose diff reaches
past a pin. CodeRabbit does not automatically
review a pull request it did not see a human open, so nothing turns
`Review Verified` green on its own for those. Somebody has to ask for the
review:

```shell
gh pr comment <n> --body '@coderabbitai review'
```

An hourly workflow used to post that comment. It was retired on 2026-09-21,
and this repository was then the one where that looked like the biggest loss,
because it had no bot fast lane at all: every dependency bot pull request
needed a real `Review completed` before it could merge. `Pin Only` has since
taken most of that traffic out of the review path entirely.

It was retired on cost rather than on capability. The nudge did work: it
posted with a personal access token, so the comment came from a human account
and CodeRabbit honoured it, answering within seconds.

What it cost was a repository-scoped credential that fails silently, and this
repository is the proof. `CODERABBIT_NUDGE_TOKEN` is an organization secret
whose visibility is set per repository. `.github` was never added to that
list, so the secret resolved empty here, and eight of the last ten scheduled
runs found the stuck pull request, tried to comment, and exited 4:

```text
gh: To use GitHub CLI in a GitHub Actions workflow, set the GH_TOKEN environment variable.
```

Nothing surfaced that outside the Actions tab. #18 has been sitting on exactly
the condition the nudge existed to clear, which is the sharpest possible
statement of the problem: the one repository with no bot fast lane, and so the
one that depended on the nudge most, is the one where the nudge could not
post.

The job also could not see the shared review quota it was firing into, so a
mistimed nudge spent a slot on nothing.

The pull requests it covered waited for a person either way, since a bot pull
request that needs a review is also one that gets no automatic approval. The
workflow saved that person one command, at the price of a credential to
maintain. Once the review lands as `Review completed`, the pull request merges
the same way a human one does.

## `Review Verified`, and the bug it exists to fix

Ported unchanged in reasoning from rsync-crypt: a green `CodeRabbit` check
does not mean a review happened, because CodeRabbit posts through the legacy
commit status API, which has no state for "green, but not for the reason you
think." The shared review verdict in ivan-pinatti-labs/gh-actions,
published as `Review Verified` by `coderabbit-gate.yml`, reads the actual
description behind the `CodeRabbit` status rather than its color. A draft is
`pending`; `Review completed` is `success`; an in-flight review
(`Review queued` or `Review in progress`) is `pending`; anything else,
including no status at all, is `failure`.

There is a bot lane here now. It grades a pin-only dependency bump `success`
without a review at all, and it works because this repository finally has a
`Pin Only` context for it to gate on: `.github/pin-only.yml`, read by the
same shared workflow. Until then every pull request, bot authored or not, was
graded on the three lanes above, which is why a routine Renovate bump here
had to spend a slot from the organization's shared OSS review quota.

## Recovering a stuck `Review Verified`

`coderabbit-gate.yml`'s hourly schedule and its `workflow_dispatch` recovery
path work the same way as rsync-crypt's; see that repository's
`docs/MERGE_PIPELINE.md`, "Recovering a stuck `Review Verified`, honestly,"
for the caveats about GitHub deprioritizing scheduled runs on public
repositories.

## Release automation is not part of this gate

`.github/workflows/new-tag-and-release.yml` runs on push to `main`, after a
merge, not as a pull request check. It is not a required status context and
cannot block or delay a merge.

It computes the next version from the Conventional Commit prefixes of the
commits since the previous tag, tags that commit and publishes a GitHub
release with generated notes. That is the same workflow every other
repository in the organization runs, which is why it replaced
release-please here: release-please kept a `CHANGELOG.md` and announced a
version by opening a release pull request, and a pull request in this
repository is graded like any other, so a release spent a review slot out of
the organization's shared CodeRabbit quota to say something the tag already
said.

A tag that already exists on `HEAD` is left alone, so a version created by
hand and this automation can coexist. The first tag here, `v1.0.0`, was
created that way: the repository had no tag at all when it moved off
release-please, and with an empty tag list the action starts at `v0.1.0`.

---

See also: [profile/README.md](../profile/README.md)
