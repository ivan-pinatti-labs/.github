# .github

Organization-wide defaults and shared tooling for
[ivan-pinatti-labs](https://github.com/ivan-pinatti-labs).

GitHub treats a repository with this name specially, and two things here are
picked up automatically because of it:

- [profile/README.md](profile/README.md) renders on the organization's public
  page at <https://github.com/ivan-pinatti-labs>.
- Any community health file added here (`CONTRIBUTING.md`, `SECURITY.md`,
  issue templates, and so on) is inherited by every repository in the
  organization that does not ship its own. None are here today: each
  repository carries its own copies.

The rest is ordinary content that lives in one place because it applies in
more than one:

- [docs/MERGE_PIPELINE.md](docs/MERGE_PIPELINE.md) describes how a pull
  request gets from opened to merged in this repository. Every repository has
  its own copy for its own pipeline; this one is the thinnest, since there is
  no app code, no build, no test suite and no merge queue here.
- [docs/crypto/addresses.md](docs/crypto/addresses.md) holds the donation
  addresses and QR codes the profile page links to.
- [scripts/coderabbit-review-verdict.py](scripts/coderabbit-review-verdict.py)
  is the script behind the `Review Verified` status check that every
  repository's pipeline depends on.

## Dependency policy

Every repository in this organization runs both Renovate and Dependabot on
the same schedule with the same cooling window. This section is the reasoning
behind those two settings, kept because both have been re-derived incorrectly
more than once.

### Both bots run daily

Renovate is scheduled `before 7am` daily; Dependabot uses `interval: daily`.
Neither is given a weekday of its own.

**A weekly schedule stacks on top of the cooling window rather than
overlapping it.** A release that misses its weekly slot by a day waits a full
extra week, so the oldest a package can sit before merging becomes up to 14
days even though 7 was the intended floor. Checking daily keeps the schedule's
own period short enough that it cannot add more than a day to that floor.

**Neither bot competes for CodeRabbit's review quota.** A pin-only bump
resolves `Review Verified` straight to `success` through
[`coderabbit-review-verdict.py`](scripts/coderabbit-review-verdict.py)'s bot
lane, with CodeRabbit never asked for an opinion, so a bot pull request
normally consumes no review slot. This holds for Dependabot exactly as it does
for Renovate: both report `pin-only diff, nothing to review`. Only a bump whose
diff fails `Pin Only` falls through to being graded like a human pull request,
which is rare enough not to plan a schedule around.

That second point is why this repository no longer keeps a table of per-repository
bot days. One existed until 2026-09-02, spreading each repository's Dependabot
across a different weekday to keep their review requests from queueing behind
each other. It was protecting a quota Dependabot never spent, while charging
every repository up to seven extra days of staleness for the privilege. If a
future change makes bot pull requests consume review slots, the volume levers to
reach for are `prConcurrentLimit` and `prHourlyLimit` for Renovate and
`open-pull-requests-limit` for Dependabot, not the calendar.

### Both bots wait seven days

| Bot | Setting | Value | Where |
| --- | --- | --- | --- |
| Renovate | `minimumReleaseAge` | 7 days | `.github/renovate.json5` |
| Renovate | `internalChecksFilter` | `strict` | `.github/renovate.json5` |
| Renovate | `vulnerabilityAlerts.minimumReleaseAge` | `null` | `.github/renovate.json5` |
| Dependabot | `cooldown.default-days` | 7 | `.github/dependabot.yml`, every ecosystem |

**Why a window at all.** `assert-pin-only-diff.py` publishes the `Pin Only`
status that lets a dependency bump merge unattended, and it is explicit in its
own docstring that it can tell a line that changed structurally from one that
changed only its version, but it cannot tell a version that exists from a
version that is safe. A freshly compromised upstream release has no advisory
yet for any scanner to match, so age is the only thing standing between that
release and an unattended merge. Seven days is the window in which most
compromised releases are found and yanked.

**`vulnerabilityAlerts.minimumReleaseAge: null` is the deliberate exception.**
A fix for a known vulnerability is not made safer by aging. Dependabot's
`cooldown` needs no equivalent carve-out because it applies to version updates
only and never to Dependabot security updates.

**Both bots carry the same seven days on purpose.** Dependabot's ecosystems here
are GitHub Actions and pre-commit hooks, and both execute arbitrary code, in CI
holding a token and on a developer's machine respectively. They are the larger
attack surface, not the smaller one. Until this was written down, every
repository had a Renovate window and no Dependabot window at all, which left the
more dangerous of the two surfaces as the uncovered one.

**`cooldown`'s `semver-major-days`, `semver-minor-days` and `semver-patch-days`
are deliberately unused.** GitHub supports those keys only on a specific list of
ecosystems that includes neither `github-actions` nor `pre-commit`, so setting
them here would be configuration that silently does nothing.
