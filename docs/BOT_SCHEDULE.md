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
| Monday | docker-torrent-box-with-vpn | 07:00 | Dependabot, pre-commit hooks |
| Tuesday | docker-torrent-box-with-vpn | 07:00 | Dependabot, GitHub Actions |
| Wednesday | docker-torrent-box-with-vpn | 07:00 | Dependabot, pip (`tests/requirements.txt`) |
| Thursday | docker-torrent-box-with-vpn | before 07:00 | Renovate, the arr suite group |
| Friday | docker-torrent-box-with-vpn | before 07:00 | Renovate, the observability stack and library and reading tools groups |
| Saturday | docker-torrent-box-with-vpn | before 07:00 | Renovate, every ungrouped image (its root schedule, used as the default) |
| Sunday | docker-torrent-box-with-vpn | before 07:00 | Renovate, the lint and scanner tooling and container runtime tooling groups |
| Daily | every other repository | before 07:00 | Renovate, asdf tool versions (and `.env.example` in rsync-crypt) |

Renovate is deliberately the one row that is not spread across days for every
repository except `docker-torrent-box-with-vpn`. See "Renovate runs daily
everywhere" below for why the daily default does not compete for the quota
this table exists to protect, and "The one exception" below that section for
why `docker-torrent-box-with-vpn` keeps a weekday-staggered Renovate schedule
instead of the daily default the rest of the organization uses.

The library and its demo share Wednesday at different hours rather than
taking a day each. They are a library and its own consumer, so a bump that
affects one usually affects the other, and having both land in one morning
keeps that pairing visible. Two hours apart is enough separation: the unit
this table protects is the hour, not the day. The demo is at 08:00 rather
than a fourth weekday because Thursday, Friday and Sunday were already spoken
for by `docker-torrent-box-with-vpn`'s existing internal spread (it had not
migrated into this organization yet, but the spread it would arrive with was
already known), and taking one of them then would have forced that spread to
be rearranged on arrival.

`docker-torrent-box-with-vpn` has since migrated into this organization and
kept its own existing weekday spread (pre-commit and GitHub Actions on
Monday/Tuesday, pip on Wednesday, the arr suite on Thursday, observability
and library tooling on Friday, every ungrouped image on Saturday, and lint,
scanner and CI runtime tooling on Sunday) rather than being folded into a
single day, exactly as anticipated: that spread was built to keep the pull
request volume from its seven or more grouped image stacks manageable within
one repository, which is a different problem from the one this document
solves, and it is recorded in full in the table above.

Checking its hours against this table, as the previous revision of this
document said still needed doing, found two collisions rather than the one
that revision anticipated. Its original Monday 06:00 (Dependabot, pre-commit
hooks) matched rsync-crypt's Monday 06:00 exactly, which was the collision
this document already knew to check for. Its original Tuesday 06:30
(Dependabot, GitHub Actions) also matched this repository's own Tuesday
06:30 slot, a second collision the previous revision did not think to check,
since it framed Monday as "the one day both repositories currently touch"
without checking Tuesday against the table it was already sitting in.
`docker-torrent-box-with-vpn`'s hours moved in both cases, to 07:00, rather
than either existing repository's, since those slots were already on record
first; the table above reflects the moved hours, and its `dependabot.yml`
carries the reasoning inline as well. Its Wednesday pip slot and its
Renovate groups were new additions this table had not held a placeholder
for, and neither collided with anything already in the table.

## Reserved

Nothing is reserved any more. The three days held for
`docker-torrent-box-with-vpn`'s migration (Thursday, Friday and Sunday) are
now in the "Slots in use" table above along with the rest of its spread, and
every weekday now carries at least one repository's schedule.

No unheld spare day is left. A newly added repository should take a free
hour on an existing day, the way `pre-commit-checklists-demo` took Wednesday
08:00, rather than claiming a day that already carries another repository's
schedule and forcing one spread or the other to be rearranged.

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
Renovate on the daily default, unless it falls under the one exception below.

## The one exception: `docker-torrent-box-with-vpn`

`docker-torrent-box-with-vpn` keeps its own weekly, day-staggered Renovate
schedule (see the "Slots in use" table above) rather than the daily default
this section otherwise recommends, and that is deliberate rather than an
oversight to fix on sight.

The two reasons above are both about the seven day cooling window, and
neither applies to what this repository's schedule is actually solving.
Its `.github/renovate.json5` and `docs/DEPENDENCY_UPDATES.md` stagger seven
or more grouped image stacks (the arr suite, the observability stack,
library and reading tools, lint and scanner tooling, container runtime
tooling, and the ungrouped default) across Thursday through Sunday purely to
keep pull request volume manageable in one repository whose `main` is
`strict`: every merge invalidates every other open pull request's checks, so
opening a week's worth of grouped bumps on one day would compound into
repeated rebases and reruns of an integration suite that takes upward of
twelve minutes. Flattening that to the daily default would not shorten the
seven day window (each group already sits behind it independently, the same
as every other repository's Renovate); it would only undo the volume control
the staggering exists for.

The two reasons for a daily default hold everywhere else in the
organization because no other repository has this problem: none groups
enough images, or carries `main` `strict` with no merge queue yet, for
volume to be worth staggering around. If that changes for another
repository, its own documented reason would need to be at least as
specific as this one before repeating the exception; "we would rather
spread it out" alone is not what makes this repository different, the
grouped volume against a `strict`, queue-less `main` is.
