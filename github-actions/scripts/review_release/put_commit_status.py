"""
Sets a commit status for a target commit on an app repo
"""

import argparse
import logging
import os
import sys

from github import Github

DEFAULT_COMMIT_STATUS = "App Release"


def parse_args():
    help_str = " ".join(line.strip() for line in __doc__.splitlines())
    argparser = argparse.ArgumentParser(description=help_str)
    argparser.add_argument("app_repo", type=str, help="Repo name including the owner")
    argparser.add_argument("commit_sha", type=str, help="Hash of the commit to put the status for")
    argparser.add_argument(
        "-s",
        "--state",
        required=True,
        type=str,
        choices=["pending", "success", "failure"],
        help="State to assign the commit status",
    )
    argparser.add_argument(
        "-n", "--name", type=str, help="Name of the commit status", default=DEFAULT_COMMIT_STATUS
    )
    argparser.add_argument("-d", "--description", type=str, help="Optional status description")
    argparser.add_argument(
        "-t", "--target_url", type=str, help="Optional url to include in the commit status"
    )

    return argparser.parse_args()


def main(args):
    github = Github(login_or_token=os.environ["GITHUB_TOKEN"])
    repo = github.get_repo(args.app_repo)
    commit = repo.get_commit(args.commit_sha)

    status = commit.create_status(
        context=args.name,
        state=args.state,
        description=args.description,
        target_url=args.target_url,
    )
    logging.info("Created commit status: %s", status.url)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    sys.exit(main(parse_args()))
