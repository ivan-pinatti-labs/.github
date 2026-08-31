#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Ivan Pinatti
"""Decide the `Review Verified` status from a pull request's own state.

Read a small JSON object on stdin (assembled by
`.github/workflows/coderabbit-gate.yml` from the GitHub API, never from an
event payload) and print `state=<success|pending|failure>` and
`description=<text>` on stdout, in the shape `>> "$GITHUB_OUTPUT"` expects.

Ported from rsync-crypt's script of the same name, itself ported from
docker-torrent-box-with-vpn's fix for its own #114: `CodeRabbit` reports
`success` on three outcomes that are not the same thing. `Review completed`
means a review happened. `Review rate limited` means the quota was exhausted
and nothing read the diff. A skipped draft means CodeRabbit never looked
because it was told not to. Branch protection cannot tell these apart,
because the legacy commit status API it reads has no fifth state for "green
but not for the reason you think." `Review Verified` exists to be the
context that can tell them apart, so it is required instead of `CodeRabbit`
and grades every one of those outcomes as `failure` rather than inheriting
their `success`.

Trimmed relative to rsync-crypt's copy: this repository has no `Pin Only`
context and no dependency-bot fast lane around a review. rsync-crypt grades a
clean pin-only dependency bump `success` with no CodeRabbit review at all,
because it has a `Pin Only` context to gate that lane on; this repository
does not, so a dependency bot pull request here is graded exactly like a
human one, on the same two lanes below.

Two lanes, decided in this order:

1. A draft is `pending`, not `failure`.
CodeRabbit has not reviewed it because it was told not to (`drafts: false` in
.coderabbit.yaml), which is a deliberate wait rather than a decline, and a
required context that reads red for a pull request's entire draft phase
teaches nothing. Pending blocks the merge exactly as hard as failure does, so
nothing merges early either way.

2. Everything else is `success` only when the latest `CodeRabbit` status
description is exactly `Review completed`. Absent, `Review queued`, or
`Review in progress` is `pending`: a review that has been asked for and not
yet returned, or is actively running, has not declined anything, and reading
it as a failure would turn every ordinary review's opening minutes into a red
required check for no reason. Anything else, including `Review rate
limited`, any `Review skipped: ...` description reaching this lane (a
non-draft pull request is never a draft by the time this runs, since lane 1
already caught that), an error state, or a description this has never seen
before, is `failure`. No exceptions there: this is the lane where an
unreviewed merge would happen, and a status this script does not recognize
is exactly the shape a future change to CodeRabbit's wording would take, so
only the two known in-flight strings above move to `pending`; nothing else
gets the benefit of the doubt.

Because there is no bot fast lane, a dependency bot pull request here needs
an actual `Review completed` before it can merge, same as a human one. See
`coderabbit-review-queue.yml` for what makes CodeRabbit actually review a
bot's pull request in the first place; it never does so on its own.
"""

import json
import sys

# CodeRabbit's own in-flight states, observed live on real pull requests.
# Neither is a decline: a review that is queued or actively running has not
# read the diff and returned an answer yet, which is exactly what `pending`
# is for.
IN_FLIGHT_DESCRIPTIONS = frozenset({"Review queued", "Review in progress"})


def decide(data: dict) -> tuple[str, str]:
    """Return (state, description) for `Review Verified`."""
    if data.get("is_draft"):
        return "pending", "waiting for ready for review"

    description = data.get("coderabbit_description", "")
    # `in IN_FLIGHT_DESCRIPTIONS` raises TypeError for an unhashable value (a
    # list or an object survives JSON decoding as one), which main() does not
    # catch, so a malformed payload would crash this script instead of
    # reaching its own fail-closed return below.
    #
    # coderabbit-gate.yml cannot produce a non-string here, since it builds
    # the payload with jq `--arg`, which always yields a JSON string, over a
    # value already coerced with `// ""`. This is defence in depth for that
    # caller, not a bug it can hit. It is load bearing for any other caller,
    # including a test that feeds this script stdin directly.
    if not isinstance(description, str):
        return "failure", "coderabbit_description was not a string"
    if description == "":
        return "pending", "waiting for a CodeRabbit review"
    if description == "Review completed":
        return "success", 'CodeRabbit reports "Review completed"'
    if description in IN_FLIGHT_DESCRIPTIONS:
        return "pending", f'CodeRabbit reports "{description}"'
    return "failure", f'CodeRabbit reports "{description}", which is not a review'


def main() -> int:
    raw = sys.stdin.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"REFUSED: stdin was not valid JSON: {exc}", file=sys.stderr)
        return 1

    if not isinstance(data, dict):
        print("REFUSED: stdin JSON was not an object.", file=sys.stderr)
        return 1

    state, description = decide(data)
    # Both values are written to GITHUB_OUTPUT as `key=value` lines by the
    # caller, where a newline would let the rest of the value be parsed as a
    # further output: an unsanitised description could set `state=success` on
    # the very check meant to withhold it. The description embeds CodeRabbit's
    # own text, so it is flattened here rather than trusted to be one line.
    description = " ".join(description.split())
    print(f"state={state}")
    print(f"description={description}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
