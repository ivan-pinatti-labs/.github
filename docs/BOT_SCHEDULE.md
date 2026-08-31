# Bot schedule

CodeRabbit's review quota on the plan these repositories use is shared across
the whole GitHub App installation, not handed out per repository. If two
repositories' dependency bots opened pull requests at the same hour, their
review requests would queue behind each other and both would look stuck for
no visible reason. This document records when each repository's bots are
actually scheduled to run, and reserves the slots nothing uses yet, so a new
repository can be given a time that does not collide with an existing one.

Nothing here is enforced by code. It is a plan for picking a schedule when a
repository is set up or migrated in, checked by hand against this table.
Times are America/Toronto, matching every `schedule:` block below.

## Slots in use

| Day (ET) | Repository | Hour | Ecosystem |
| --- | --- | --- | --- |
| Monday | rsync-crypt | 06:00 | Dependabot, pre-commit hooks |
| Monday | rsync-crypt | 06:30 | Dependabot, GitHub Actions |
| Monday | rsync-crypt | before 07:00 | Renovate, asdf tool versions and the `.env.example` pin |
| Tuesday | .github | 06:00 | Dependabot, pre-commit hooks |
| Tuesday | .github | 06:30 | Dependabot, GitHub Actions |

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
| Wednesday | (spare) | |
| Saturday | (spare) | |

A repository added later that does not need its own internal weekday spread
gets one of the spare days above, at an hour that does not land in
rsync-crypt's Monday 06:00 to 07:00 window.
