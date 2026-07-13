# Branching & Release Process (GitFlow)

This project follows **GitFlow**. Versions use **Semantic Versioning**
(`MAJOR.MINOR.PATCH`: breaking change / new feature / bug fix) and are
documented in `CHANGELOG.md` ([Keep a Changelog](https://keepachangelog.com)
format).

> History note: v1.0.0 was released trunk-based (tag directly on `main`).
> GitFlow was adopted immediately after, starting development toward the
> next version.

## The five branch types

| Branch | Lives | Created from | Merges into | Purpose |
|---|---|---|---|---|
| `main` | forever | — | — | released state only; every commit on it is a release or hotfix merge, tagged |
| `develop` | forever | `main` (once) | — | integration branch; latest development state |
| `feature/<name>` | days | `develop` | `develop` | one feature or task |
| `release/<x.y.z>` | days | `develop` | `main` + `develop` | stabilization & version bump for a release |
| `hotfix/<x.y.z>` | days | `main` | `main` + `develop` | urgent fix to the released version |

```
main      ──●─────────────────────────●─────────────  (tags: v1.0.0, v1.1.0)
             \                       / \
              \      release/1.1.0 ●───●  (bump+changelog; merge to both)
               \                  /     \
develop   ──────●──●─────●──●────●───────●──●───────
                    \   /   \   /
feature/a  ──────────●─●     \ /
feature/b  ───────────────────●
```

All merges into `main` and `develop` use `--no-ff` (no fast-forward), so
the branch structure stays visible in history as merge commits.

## Feature flow (day-to-day work)

```bash
git checkout develop
git pull origin develop
git checkout -b feature/persistent-storage     # branch from develop

# ... work, commit, repeat ...
python -m unittest discover -s tests           # green before finishing

git checkout develop
git pull origin develop                        # develop may have moved
git merge --no-ff feature/persistent-storage -m "Merge feature/persistent-storage into develop"
git push origin develop
git branch -d feature/persistent-storage       # delete merged branch
git push origin --delete feature/persistent-storage   # if it was pushed
```

Small, low-risk changes (docs typos and the like) may be committed
directly on `develop`. Never commit directly on `main`.

## Release flow

```bash
# 1. cut the release branch from develop
git checkout develop && git pull origin develop
git checkout -b release/1.1.0

# 2. on the release branch only: version bump + changelog (+ last-minute fixes)
#    - pyproject.toml -> version = "1.1.0"
#    - CHANGELOG.md   -> ## [1.1.0] - YYYY-MM-DD section
python -m unittest discover -s tests
git commit -am "Prepare release 1.1.0"

# 3. merge to main and tag the merge commit
git checkout main && git pull origin main
git merge --no-ff release/1.1.0 -m "Release 1.1.0"
git tag -a v1.1.0 -m "v1.1.0 - <summary>"
git push origin main v1.1.0

# 4. merge back to develop (brings the version bump + any release fixes)
git checkout develop
git merge --no-ff release/1.1.0 -m "Merge release/1.1.0 back into develop"
git push origin develop

# 5. delete the release branch
git branch -d release/1.1.0

# 6. GitHub Release on top of the tag
gh release create v1.1.0 --title "v1.1.0" --notes-file CHANGELOG.md
```

## Hotfix flow (urgent fix to the released version)

```bash
git checkout -b hotfix/1.0.1 main              # from main, NOT develop
# ... fix + test ...
#    - pyproject.toml -> "1.0.1", CHANGELOG.md -> ## [1.0.1]
git commit -am "Fix <bug> (1.0.1)"

git checkout main
git merge --no-ff hotfix/1.0.1 -m "Hotfix 1.0.1"
git tag -a v1.0.1 -m "v1.0.1 - <fix summary>"
git push origin main v1.0.1

git checkout develop                            # the fix must reach develop too,
git merge --no-ff hotfix/1.0.1 -m "Merge hotfix/1.0.1 into develop"   # or v1.1.0 re-breaks it
git push origin develop
git branch -d hotfix/1.0.1
```

## Rules

- **Released tags are immutable** — never move, delete, or reuse a pushed
  tag. A fix after `v1.0.0` is `v1.0.1`.
- **`main` receives only `--no-ff` merges from `release/*` and `hotfix/*`
  branches.** No direct commits.
- **Every merge to `main` gets a tag**; `pyproject.toml`'s version always
  matches the latest tag on `main`.
- **Release/hotfix branches merge into BOTH `main` and `develop`** — the
  back-merge is the step people forget, and forgetting it means the next
  release silently reverts the fix.
- Environment note: automated sessions (Claude) cannot push tags (403) or
  create GitHub Releases — those two steps are always run by the owner
  from their machine, exactly as written above.
