# Contributing

This repository is maintained by Studio Sanka members. We are not accepting pull requests or outside contributions at this time.

Found a bug, or have a question or idea? Please open an issue: https://github.com/studiosanka/lerobot-sixeyes/issues. We read everything, though we cannot promise a reply to every message.

Licence: Apache-2.0 (see `LICENSE`).

## For maintainers

- Run the tests before committing: `python -m unittest discover -s tests`.
- Keep the stand-in in `tests/stubs/` in line with LeRobot's `Robot` and `Teleoperator` (see `docs/appendix/appendix-lerobot-contract.md`); the real-LeRobot CI job is the check.
- Keep the README to one screen and technical detail in `docs/appendix/`.
