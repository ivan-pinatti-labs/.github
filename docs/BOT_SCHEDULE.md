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
| Monday | pre-commit-checklists-demo | 07:00 | Dependabot, pip (`requirements.txt`) |
| Wednesday | pre-commit-checklists-demo | 08:00 | Dependabot, pre-commit hooks |
| Wednesday | pre-commit-checklists-demo | 08:30 | Dependabot, GitHub Actions |
| Thursday | docker-torrent-box-with-vpn | 06:00 | Dependabot, pre-commit hooks |
| Thursday | docker-torrent-box-with-vpn | 06:30 | Dependabot, GitHub Actions |
| Friday | docker-torrent-box-with-vpn | 06:00 | Dependabot, pip (`tests/requirements.txt`) |
| Saturday | github-template | 06:00 | Dependabot, pre-commit hooks |
| Saturday | github-template | 06:30 | Dependabot, GitHub Actions |
| Daily | every repository | before 07:00 | Renovate, every surface it manages |

Every row is a Dependabot slot except the last. Renovate is daily everywhere,
`docker-torrent-box-with-vpn` included as of its migration, so it takes no day
of its own; see "Renovate runs daily everywhere" below.

A row missing from this table is how a collision gets through, so add one for
every ecosystem a repository schedules, not just the ones that felt worth
recording. `pre-commit-checklists-demo`'s Monday pip slot was absent here, and
`docker-torrent-box-with-vpn` was then given Monday 07:00 on the strength of
this table looking free, which put two repositories in the same hour again
after two earlier collisions had just been fixed.

Renovate is deliberately the one row that is not spread across days, in every
repository without exception. See "Renovate runs daily everywhere" below for
why the daily default does not compete for the quota this table exists to
protect.

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

`docker-torrent-box-with-vpn` has since migrated into this organization, and
its weekday spread did not survive the move. Its Renovate groups are now on
the daily default like every other repository, and its Dependabot took the
Thursday and Friday slots that spread had been holding. See "The exception
that was considered and dropped" below for the argument for keeping it and
why the merge queue it gained on migrating is what answered it.

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

Nothing is reserved any more. Thursday, Friday and Sunday were held for
`docker-torrent-box-with-vpn`'s Renovate weekday spread; that spread is gone
now that Renovate runs daily everywhere, and the repository's Dependabot took
Thursday and Friday instead. Sunday and Wednesday afternoon onward are the
emptiest parts of the week today.

A newly added repository should take a free hour, checked against every row
of the table above rather than against a day at a glance, since the unit that
matters is the hour and several days already carry two repositories at
different hours.

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

## The exception that was considered and dropped

`docker-torrent-box-with-vpn` used to stagger seven or more grouped image
stacks (the arr suite, the observability stack, library and reading tools,
lint and scanner tooling, container runtime tooling, and the ungrouped
default) across Thursday through Sunday. Recorded here because the argument
for keeping it was a real one and will be made again.

That staggering was volume control, not a cooling window. Its `main` is
`strict`, so every merge invalidates every other open pull request's checks,
and opening a week's worth of grouped bumps on one day compounded into
repeated rebases and reruns of an integration suite that takes upward of
twelve minutes.

Two things settled it against keeping the exception.

**The merge queue is what actually solves that problem.** A queue is
precisely the mechanism for "every merge invalidates the other open pull
requests": it builds and merges entries against its own commit rather than
making each pull request chase `main`. That repository moved into this
organization specifically so it could have one, and it now does. The
staggering was standing in for a queue that did not exist yet.

**The window it bought was never free.** `.github/renovate.json5`'s own
comment had already written this down and not acted on it: the spread cost up
to seven days on top of `minimumReleaseAge`'s seven, and it existed to give a
person one sitting a week to work through the batch, which nobody does any
more. A weekly window stacked on the seven day floor rather than overlapping
it, so a release missing its day by a day waited a full extra week and the
real floor was 14 days.

Volume is still bounded there, by `prConcurrentLimit` and `prHourlyLimit`
rather than by the calendar. Those are the levers to reach for if it becomes
a problem again. Reinstating a weekday spread would bring the 14 day floor
back with it, so it should be the last thing tried, not the first.
