# ivan-pinatti-labs

Personal, non commercial repositories: side projects, infrastructure experiments,
and self hosted tooling. This organization exists mainly to get access to
features a personal GitHub account does not have, most importantly a merge
queue.

## Support

[![GitHub Sponsor](https://img.shields.io/badge/Sponsor-%E2%9D%A4-fe8e86?logo=github&style=for-the-badge)](https://github.com/sponsors/ivan-pinatti)
[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ffdd00?logo=buy-me-a-coffee&logoColor=black&style=for-the-badge)](https://www.buymeacoffee.com/ivan.pinatti)
[![PayPal](https://img.shields.io/badge/PayPal-Donate-003087?logo=paypal&style=for-the-badge)](https://www.paypal.com/paypalme/ivanrpinatti)

Crypto donations are also welcome: see
[docs/crypto/addresses.md](https://github.com/ivan-pinatti-labs/.github/blob/main/docs/crypto/addresses.md)
for the full list of addresses and QR codes.

## How pull requests merge here

Every repository in this organization follows the same pipeline: a human
authored pull request needs a CodeRabbit review before it can merge, no
exceptions; a bot authored dependency bump can merge on its own once it
passes the integration suite and a path check that keeps it to version pins
and lockfiles. Both routes go through the same merge queue and the same
required checks, so `main` only ever gains a commit that already passed the
suite on the exact code being merged. See each repository's
`docs/MERGE_PIPELINE.md` for the details.
