# Bot schedule and dependency freshness policy

CodeRabbit's review quota on the plan these repositories use is shared across
the whole GitHub App installation, not handed out per repository. If two
repositories' dependency bots opened pull requests at the same hour, their
review requests would queue behind each other and both would look stuck for
no visible reason. This document records when each repository's bots are
actually scheduled to run, and reserves the slots nothing uses yet, so a new
repository can be given a time that does not collide with an existing one.

It also records the two settings that decide how *fresh* a dependency is
allowed to be when it merges, in "Cooling windows" below, because those
interact with the schedule directly and were twice re-derived incorrectly
from the table above them before being written down here.

Nothing here is enforced by code. It is a plan for picking a schedule when a
repository is set up or migrated in, checked by hand against this table.
Times are America/Toronto, matching every `schedule:` block below.

## Slots in use

| Day (ET) | Repository | Hour | Ecosystem |
| --- | --- | --- | --- |
| Monday | rsync-crypt | 06:00 | Dependabot, pre-commit hooks |
| Monday | rsync-crypt | 06:30 | Dependabot, GitHub Actions |
| Tuesday | .github | 06:00 | Dependabot, pre-commit hooks |
| Tuesday | .github | 06:30 | Dependabot, GitHub Actions |
| Wednesday | pre-commit-checklists | 06:00 | Dependabot, pre-commit hooks |
| Wednesday | pre-commit-checklists | 06:30 | Dependabot, GitHub Actions |
| Wednesday | pre-commit-checklists-demo | 08:00 | Dependabot, pre-commit hooks |
| Wednesday | pre-commit-checklists-demo | 08:30 | Dependabot, GitHub Actions |
| Saturday | github-template | 06:00 | Dependabot, pre-commit hooks |
| Saturday | github-template | 06:30 | Dependabot, GitHub Actions |
| Daily | every repository | before 07:00 | Renovate, asdf tool versions (and `.env.example` in rsync-crypt) |

Renovate is deliberately the one row that is not spread across days. See
"Renovate runs daily everywhere" below for why that does not compete for the
quota this table exists to protect.

The library and its demo share Wednesday at different hours rather than
taking a day each. They are a library and its own consumer, so a bump that
affects one usually affects the other, and having both land in one morning
keeps that pairing visible. Two hours apart is enough separation: the unit
this table protects is the hour, not the day. The demo is at 08:00 rather
than a fourth weekday because Thursday, Friday and Sunday are spoken for by
`docker-torrent-box-with-vpn`'s existing internal spread when it migrates in
(see below), and taking one of them now would force that spread to be
rearranged later.

`docker-torrent-box-with-vpn` is not in this organization yet (see the
migration plan). Once it moves here, it keeps its own existing weekday
spread (pre-commit and GitHub Actions on Monday/Tuesday, the arr suite on
Thursday, observability and library tooling on Friday, lint and scanner
tooling and CI runtime tooling on Sunday) rather than being folded into a
single day: that spread was built to keep the pull request volume from
its seven or more grouped images manageable within one repository, which is
a different problem from the one this document solves. What this document
still needs to check at that point is whether any of those hours collide
with rsync-crypt's Monday morning window above, since Monday is the one day
both repositories currently touch.

## Reserved

| Day (ET) | Repository | Notes |
| --- | --- | --- |
| Thursday | (held for `docker-torrent-box-with-vpn`) | Part of that repository's existing internal spread |
| Friday | (held for `docker-torrent-box-with-vpn`) | Part of that repository's existing internal spread |
| Sunday | (held for `docker-torrent-box-with-vpn`) | Part of that repository's existing internal spread |

No unheld spare day is left. A repository added before
`docker-torrent-box-with-vpn` migrates should take a free hour on an
existing day, the way `pre-commit-checklists-demo` took Wednesday 08:00,
rather than claiming one of the three days above and forcing that
repository's spread to be rearranged on arrival.

## Cooling windows

How old a release has to be before either bot will offer it. This is the
part of the setup that actually defends against a compromised upstream
release, so it is recorded here rather than left to be re-derived from each
repository's config.

| Bot | Setting | Value | Where |
| --- | --- | --- | --- |
| Renovate | `minimumReleaseAge` | 7 days | `.github/renovate.json5` |
| Renovate | `internalChecksFilter` | `strict` | `.github/renovate.json5` |
| Renovate | `vulnerabilityAlerts.minimumReleaseAge` | `null` | `.github/renovate.json5` |
| Dependabot | `cooldown.default-days` | 7 | `.github/dependabot.yml`, on every ecosystem |

Why a window at all: `scripts/assert-pin-only-diff.py` publishes the
`Pin Only` status that lets a dependency bump merge unattended, and it is
explicit in its own docstring that it can tell a line that changed
structurally from one that changed only its version, but it cannot tell a
version that exists from a version that is safe. A freshly compromised
upstream release has no advisory yet for any scanner to match, so age is the
only thing standing between that release and an unattended merge. Seven days
is the window in which most compromised releases are found and yanked.

`vulnerabilityAlerts.minimumReleaseAge: null` is the deliberate exception: a
fix for a known vulnerability is not made safer by aging. Dependabot's
`cooldown` needs no equivalent carve-out because it applies to version
updates only and never to Dependabot security updates.

Both bots carry the same seven days on purpose. Dependabot's two ecosystems
are GitHub Actions and pre-commit hooks, and both execute arbitrary code, in
CI holding a token and on a developer's machine respectively, so they are
the larger attack surface here rather than the smaller one. Until this was
written down, every repository in this organization had a Renovate window
and no Dependabot window at all, which left the more dangerous of the two
surfaces as the uncovered one.

`cooldown` accepts `semver-major-days`, `semver-minor-days` and
`semver-patch-days` as well, and they are deliberately not used: GitHub
supports those keys only on a specific list of ecosystems that includes
neither `github-actions` nor `pre-commit`, so setting them here would be
configuration that silently does nothing.

## Renovate runs daily everywhere

Renovate is scheduled `before 7am` every day in every repository, and is not
given a weekday the way Dependabot is. Two separate reasons, both of which
have been re-derived wrongly at least once:

**A weekly Renovate would stack on top of the seven day window rather than
overlap it.** A release that misses its weekly slot by a day waits a full
extra week for the next one, so the oldest a package could sit before
merging becomes up to 14 days even though 7 was the intended floor. Checking
daily keeps the schedule's own period short enough that it cannot add more
than a day on top of that floor.

**Renovate does not compete for the quota this document protects.** A
pin-only bump resolves `Review Verified` straight to `success` through
`coderabbit-review-verdict.py`'s bot lane, with CodeRabbit never asked for
an opinion at all, so a Renovate pull request normally consumes no review
slot. The day-spreading in the table above is therefore a Dependabot
concern. Only a Renovate bump whose diff fails `Pin Only` falls through to
being graded like a human pull request, and that is rare enough not to plan
a schedule around.

So: give a new repository a Dependabot day out of the table, and leave its
Renovate on the daily default.
