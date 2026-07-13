# Contributing

This project follows **GitFlow**. Full flow, diagrams, and command
sequences: [`docs/release-process.md`](docs/release-process.md).

## Quick reference for branch types

| Prefix | Purpose | Branched from | Merges into |
|---|---|---|---|
| `feature/` | new feature or task | `develop` | `develop` |
| `release/` | pre-release stabilization, version bump | `develop` | `main` **and** `develop` |
| `hotfix/` | urgent fix to the released version | `main` | `main` **and** `develop` |

Permanent branches:

- **`main`** — released state only; never commit directly; every commit on
  it is a tagged release or hotfix merge.
- **`develop`** — integration branch; day-to-day default. Small doc-only
  changes may be committed here directly; everything else arrives via
  `feature/*` branches merged with `--no-ff`.

## Rules

- Branch names: `<type>/<short-kebab-case-description>`
  (e.g. `feature/persistent-storage`, `hotfix/1.0.1`).
- All merges into `main` and `develop` use `--no-ff`.
- Before any merge into `develop` or `main`:
  `python -m unittest discover -s tests` and `python -m memdb demo`
  must pass.
- Released tags (`vX.Y.Z`) are immutable — never moved, deleted, or reused.
- Sanity check that the back-merge wasn't forgotten (must print nothing):
  `git log --oneline origin/develop..origin/main`
