# Script to sync with upstream.
#
# Meant to be called via CI

import sys

import configargparse
from git import Repo
from git.exc import GitError

REMOTE_URL = "https://github.com/{}/{}.git"


class SyncException(Exception):
    def __init__(self, message):
        super().__init__(self)
        self.message = message


if __name__ == "__main__":
    config = configargparse.ArgParser()

    # Get our required arguments, they can be specified by environment variables
    config.add('--upstream-org', env_var='UPSTREAM_ORG', help='The upstream github organization', required=True)
    config.add('--upstream-repo', env_var='UPSTREAM_REPO', help='The upstream repository', required=True)
    config.add('--upstream-branch', env_var='UPSTREAM_BRANCH', help='The upstream branch', required=True)
    config.add('--origin-branch', env_var='ORIGIN_BRANCH', help='The downstream branch that will be pushed to the '
                                                                'origin remote', required=True)
    config.add('path', help='Path to local repository')
    options = config.parse_args()

    repo = Repo(options.path)

    # Fail if upstream remote is already defined
    if 'upstream' in repo.remotes:
        print('There is already an "upstream" remote. Exiting.')
        sys.exit(-1)

    try:
        # Fail if origin remote is not defined
        if 'origin' not in repo.remotes:
            raise SyncException('There is no "origin" remote to push to.')

        # Fetch the upstream remote
        upstream_url = REMOTE_URL.format(options.upstream_org, options.upstream_repo)
        print("Fetching upstream: {}.".format(upstream_url))
        upstream = repo.create_remote('upstream', upstream_url)
        fetch_info = upstream.fetch(prune=True)
        for info in fetch_info:
            if info.flags & info.ERROR:
                raise SyncException(info.note)

        # Fetch the origin remote
        origin = repo.remotes.origin
        print("Fetching origin: {}.".format(origin.url))
        fetch_info = origin.fetch(prune=True)
        for info in fetch_info:
            if info.flags & info.ERROR:
                raise SyncException(info.note)

        # Fail if the upstream branch does not exist
        if options.upstream_branch not in upstream.refs:
            raise SyncException('Upstream branch ({}) does not exist.'.format(options.upstream_branch))

        # Origin branch does not exist in local repo
        if options.origin_branch not in repo.heads:
            repo.create_head(options.origin_branch, upstream.refs[options.upstream_branch])

        if options.origin_branch in origin.refs:
            print("Origin branch ({}) exists on remote.".format(options.origin_branch))
            origin_commit = origin.refs[options.origin_branch].commit
            print("Origin commit:   {}".format(origin_commit))
        else:
            origin_commit = None
            print("Origin branch ({}) does not exist on remote, creating it.".format(options.origin_branch))

        upstream_commit = upstream.refs[options.upstream_branch].commit
        print("Upstream commit: {}".format(upstream_commit))

        if upstream_commit == origin_commit:
            print("Already up to date. Exiting without update.")
        else:
            repo.heads[options.origin_branch].reference = upstream.refs[options.upstream_branch].commit
            print("Pushing to origin ({})".format(repo.heads[options.origin_branch]))
            push_info = origin.push(repo.heads[options.origin_branch], force=True)
            for info in push_info:
                if info.flags & info.ERROR:
                    raise SyncException(push_info.summary)
            print("Updated!")

    except SyncException as e:
        error = "\n".join([e.message.strip(), "Exiting."])
        print(error)
        sys.exit(-1)

    except GitError as e:
        print("Git Error!")
        print(e)
        sys.exit(-2)

    finally:
        # clean up remotes
        if 'upstream' in repo.remotes:
            repo.delete_remote(repo.remotes.upstream)
