# CI-Scripts

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
          repository: 'jonathangreen/ci-scripts'
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
 