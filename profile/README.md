# ivan-pinatti-labs

Personal, non commercial repositories: side projects, infrastructure experiments,
and self hosted tooling. This organization exists mainly to get access to
features a personal GitHub account does not have, most importantly a merge
queue, without mixing that infrastructure into a business account.

## Repositories

- [rsync-crypt](https://github.com/ivan-pinatti-labs/rsync-crypt), encrypted
  backup over SSH with Docker, gocryptfs, and rsync.

## How pull requests merge here

Every repository in this organization follows the same pipeline: a human
authored pull request needs a CodeRabbit review before it can merge, no
exceptions; a bot authored dependency bump can merge on its own once it
passes the integration suite and a path check that keeps it to version pins
and lockfiles. Both routes go through the same merge queue and the same
required checks, so `main` only ever gains a commit that already passed the
suite on the exact code being merged. See each repository's
`docs/MERGE_PIPELINE.md` for the details.

[docs/BOT_SCHEDULE.md](https://github.com/ivan-pinatti-labs/.github/blob/main/docs/BOT_SCHEDULE.md)
records when each repository's dependency bots are scheduled to run.
