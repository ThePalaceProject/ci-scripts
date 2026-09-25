# CI-Scripts

Shared CI helpers for the Palace Project repositories.

## images/minio

A mirror of the upstream MinIO server image, published to
`ghcr.io/thepalaceproject/palace-ci-minio` by
[`.github/workflows/build-minio-mirror.yml`](.github/workflows/build-minio-mirror.yml).

MinIO withdrew anonymous public access to its server image from both Docker Hub and quay.io, so
`FROM minio/minio` now fails with a 401 before any test suite starts. The mirror is assembled from
MinIO's official GitHub release binaries — the one channel still served anonymously — each pinned
by sha256. It is a bare passthrough: no credentials, no buckets, no entrypoint script, because the
repos that consume it each configure MinIO differently.

Consumers pin the exact release tag; the mirror deliberately publishes no `latest`:

```dockerfile
FROM ghcr.io/thepalaceproject/palace-ci-minio:RELEASE.2025-09-07T16-13-09Z
```

Used by `circulation`, `library-registry` and `virtual-library-card`. Only pushes to `main`
publish — pull requests and manual runs from a branch build and validate, then discard, so an
unmerged branch cannot overwrite the tag those repos depend on.

### Retirement

This mirror is a bridge, not a destination: the intent is to drop MinIO for a maintained
S3-compatible image, tracked by [PP-5245](https://ebce-lyrasis.atlassian.net/browse/PP-5245).

It should be short-lived for two reasons. We do not want to become a de-facto public distributor of
a frozen MinIO build. And GitHub does not allow self-service deletion of a public package once any
version passes 5,000 downloads — above that it becomes a Support request. With `pull=True` on every
tox-docker build, ephemeral CI runners and three repos pulling, that threshold arrives faster than
it sounds, so check the count before assuming deletion is still a one-liner:

```
gh api -X DELETE /orgs/ThePalaceProject/packages/container/palace-ci-minio
```

## sync.py

`sync.py` is a helper script used in our CI process to keep a branch on our repositories in sync with upstream.

### Usage

```
usage: sync.py [-h] --upstream-org UPSTREAM_ORG --upstream-repo UPSTREAM_REPO --upstream-branch UPSTREAM_BRANCH --origin-branch ORIGIN_BRANCH path

positional arguments:
  path                  Path to local repository

optional arguments:
  -h, --help            show this help message and exit
  --upstream-org UPSTREAM_ORG
                        The upstream github organization [env var: UPSTREAM_ORG]
  --upstream-repo UPSTREAM_REPO
                        The upstream repository [env var: UPSTREAM_REPO]
  --upstream-branch UPSTREAM_BRANCH
                        The upstream branch [env var: UPSTREAM_BRANCH]
  --origin-branch ORIGIN_BRANCH
                        The downstream branch that will be pushed to the origin remote [env var: ORIGIN_BRANCH]

 If an arg is specified in more than one place, then commandline values override environment variables which override defaults.
```

### Actions

Here is an example action that uses sync.py to keep a branch in sync with upstream.

```yaml
name: Sync branch with upstream
on:
  schedule:
    - cron:  '0 7 * * *'

  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest

    env:
      UPSTREAM_ORG: NYPL-Simplified
      UPSTREAM_REPO: circulation
      UPSTREAM_BRANCH: develop
      ORIGIN_BRANCH: nypl/develop

    steps:
    
      - name: Checkout repo to sync
        uses: actions/checkout@v2
        with:
          path: code

      - name: Checkout CI scripts
        uses: actions/checkout@v2
        with:
          repository: 'ThePalaceProject/ci-scripts'
          path: ci

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.8
          
      - name: Install Python Packages
        run: pip install -r ci/sync-requirements.txt

      - name: Sync with upstream
        run: python ci/sync.py code
```
 
