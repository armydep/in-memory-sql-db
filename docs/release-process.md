# Release Process

How versions of this project are released, and the exact commands used.
Methodology: **trunk-based development** — all work happens on `main`,
which is kept releasable by the test suite; a release is an **annotated
tag** on `main`. Versions follow **Semantic Versioning**
(`MAJOR.MINOR.PATCH`: breaking change / new feature / bug fix).

## Release checklist

1. **Sync and verify** — `main` must be up to date and green:

   ```bash
   git fetch origin main
   git status                                # clean working tree
   python -m unittest discover -s tests      # all tests pass
   python -m memdb demo                      # smoke test the real flow
   ```

2. **Bump the package version** in `pyproject.toml` to the release version
   (it must match the tag — a v1.0.0 tag pointing at a package that calls
   itself 0.1.0 is the classic release mistake):

   ```toml
   version = "1.0.0"
   ```

3. **Update `CHANGELOG.md`** — add a `## [X.Y.Z] - YYYY-MM-DD` section
   describing what the release contains and its known limitations
   ([Keep a Changelog](https://keepachangelog.com) format).

4. **Commit and push the release state:**

   ```bash
   git add pyproject.toml CHANGELOG.md
   git commit -m "Release v1.0.0"
   git push origin main
   ```

5. **Create the annotated tag and push it** (tags are NOT pushed by
   default — `git push` pushes branches only):

   ```bash
   git tag -a v1.0.0 -m "v1.0.0 - CLI tool, minimal query set, no persistence"
   git push origin v1.0.0
   ```

6. **Create the GitHub Release** (manual step, from a machine with `gh`
   or via the GitHub web UI). It is a UI layer on top of the tag: rendered
   release notes, a "latest" badge, downloadable source archives.

   ```bash
   gh release create v1.0.0 --title "v1.0.0" --notes-file CHANGELOG.md
   # or: GitHub → Releases → "Draft a new release" → choose tag v1.0.0,
   #     paste the changelog section as the description
   ```

## Rules

- **Released tags are immutable.** Never move, delete, or reuse a tag that
  has been pushed. A fix after `v1.0.0` is `v1.0.1`, tagged separately.
- **Release branches are created lazily.** No `release/1.x` branch exists
  until the day a v1 hotfix is actually needed while `main` has moved on.
  The tag makes that possible at any time:

  ```bash
  git checkout -b release/1.x v1.0.0     # only when a hotfix is needed
  # fix, test, then:
  git tag -a v1.0.1 -m "v1.0.1 - <fix summary>"
  git push origin release/1.x v1.0.1
  ```

- `pyproject.toml` on `main` stays at the last released version between
  releases (no `.dev0` suffixes; this project does not publish to PyPI).

## Useful commands

```bash
git tag                        # list tags
git show v1.0.0                # inspect a tag (message + tagged commit)
git describe --tags            # "nearest tag + distance" for current commit
git checkout v1.0.0            # inspect the exact released state (detached HEAD)
```

## Releases so far

| Version | Date | Commit | Summary |
|---|---|---|---|
| v1.0.0 | 2026-07-13 | (tagged on main) | CLI tool, minimal query set, no persistence |
