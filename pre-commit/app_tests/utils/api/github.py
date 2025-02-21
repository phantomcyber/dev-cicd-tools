import base64
import http
import itertools
import os
import shutil
from enum import Enum
from contextlib import contextmanager
from urllib.parse import quote_plus

import git
from requests import HTTPError

from utils import memoize
from utils.api import ApiSession
from utils.phantom_constants import APP_QA_OVERLORD, GITHUB_APP_REPO_BRANCH


class StrEnum(str, Enum):
    pass


class GitHubOrganization(StrEnum):
    CONNECTORS = "splunk-soar-connectors"
    GENERAL = "phantomcyber"


DEFAULT_AUTHOR = {"name": "root", "email": "root@splunksoar"}

# Pipeline job triggers are skipped for commits made by this author
ADMIN_AUTHOR = {"name": "splunk-soar-connectors-admin", "email": "admin@splunksoar"}


class GitHubApi:
    """
    Our internal GitHub utils class.
    """

    def __init__(self, token=None, owner_repo=None):
        self.session = ApiSession("https://api.github.com")

        self._github_repo_owner = owner_repo if owner_repo else GitHubOrganization.CONNECTORS
        self.base_repo_path = f"/repos/{self._github_repo_owner}/"
        self._token = token
        if self._token:
            self.session.headers.update({"Authorization": f"Token {self._token}"})

    def _repo_sub_path(self, sub_path):
        return os.path.join(self.base_repo_path, sub_path)

    def get_file_contents(
        self, file_path, repo_name, branch=GITHUB_APP_REPO_BRANCH, repo_owner=None
    ):
        """
        Return the text of the file specified by file_path in the repo given
        """
        params = {"ref": branch}
        file_path = quote_plus(file_path)

        if not repo_owner:
            repo_owner = self._github_repo_owner

        resp = self.session.get(
            f"/repos/{repo_owner}/{repo_name}/contents/{file_path}",
            params=params,
            headers={"Accept": "application/vnd.github.v3.raw"},
        )
        return resp.content.decode()

    def list_directory_contents(
        self, repo_name, path=None, branch=GITHUB_APP_REPO_BRANCH, recursive=True, repo_owner=None
    ):
        """
        Takes relative repo directory path and returns the files in that directory.
        """
        return list(self.iter_files(repo_name, path, branch, recursive, repo_owner))

    def iter_files(
        self, repo_name, path=None, branch=GITHUB_APP_REPO_BRANCH, recursive=True, repo_owner=None
    ):
        """
        Generator version of list_directory_contents that returns one result at a time.
        Useful for searching for files in large directories by not always running through every page in the REST response
        """
        if not repo_owner:
            repo_owner = self._github_repo_owner
        paths_to_visit = []
        if path:
            path = path.rstrip("/")
            paths_to_visit.append(f"/repos/{repo_owner}/{repo_name}/contents/{path}?ref={branch}")
        else:
            paths_to_visit.append(f"/repos/{repo_owner}/{repo_name}/contents?ref={branch}")

        while paths_to_visit:
            for obj in self._iter_data(paths_to_visit.pop()):
                if obj["type"] == "dir" and recursive:
                    paths_to_visit.append(obj["url"])
                elif path is None:
                    yield obj["path"]
                else:
                    yield obj["path"].replace(path, "", 1).lstrip("/")

    def get_tree(self, repo_name, branch=GITHUB_APP_REPO_BRANCH):
        """
        Fetches the Git tree for a given commit. Used to list contents for repositories
        containing over 1000 files. Note that the trees API does not supported filtering
        contents by path like the contents API does.
        """
        commit = self.get_single_commit(repo_name, branch)["commit"]
        paths_to_get = [(commit["tree"]["url"], "")]

        while paths_to_get:
            url, parent_dir = paths_to_get.pop()
            resp = self.session.get(url).json()
            for obj in resp["tree"]:
                if obj["type"] == "tree":
                    paths_to_get.append((obj["url"], os.path.join(parent_dir, obj["path"])))
                else:
                    yield os.path.join(parent_dir, obj["path"])

    def add_labels(self, repo_name, issue_number, labels, org=GitHubOrganization.CONNECTORS):
        return self.session.post(
            f"/repos/{org}/{repo_name}/issues/{issue_number}/labels", json={"labels": labels}
        ).json()

    def iter_issue_labels(self, repo_name, issue_number, org=GitHubOrganization.CONNECTORS):
        yield from self._iter_data(f"/repos/{org}/{repo_name}/issues/{issue_number}/labels")

    def get_repo_permissions(self, repo, user, org=GitHubOrganization.CONNECTORS):
        """
        Returns the given user's permissions on the specified repo
        """
        return self.session.get(f"/repos/{org}/{repo}/collaborators/{user}/permission").json()

    def check_org_membership(self, user, group_name=GitHubOrganization.CONNECTORS):
        """
        Checks if the given user in the specified org

        https://docs.github.com/en/rest/reference/orgs#check-organization-membership-for-a-user
        """
        try:
            resp = self.session.get(f"/orgs/{group_name}/members/{user}")
            return resp.status_code == http.HTTPStatus.NO_CONTENT
        except HTTPError as ex:
            if ex.response.status_code == http.HTTPStatus.NOT_FOUND:
                return False
            raise ex

    def iter_org_members(self, group_name=GitHubOrganization.CONNECTORS):
        yield from self._iter_data(f"/orgs/{group_name}/members")

    def _iter_data(self, url, **kwargs):
        while url is not None:
            resp = self.session.get(url, params=kwargs.pop("params", None), **kwargs)
            page = resp.json()
            if isinstance(page, list):
                yield from page
            else:
                yield page

            try:
                url = resp.links["next"]["url"]
            except KeyError:
                url = None

    def iter_branches(self, repo_name):
        yield from self._iter_data(f"/repos/{self._github_repo_owner}/{repo_name}/branches")

    def iter_repos(self, group_name=GitHubOrganization.CONNECTORS):
        yield from self._iter_data(f"/orgs/{group_name}/repos", params={"per_page": 50})

    def iter_annotated_tags(self, repo_name):
        """
        Generator to fetch annotated tags for the given repo descending from most recent

        When the repo doesn't contain any tags, the API returns 404 instead of an empty list,
        so we have to test for this condition
        """
        tags_itr = self._iter_data(self._repo_sub_path(f"{repo_name}/git/refs/tags"))

        try:
            first_tag = next(tags_itr)
        except HTTPError as ex:
            if ex.response.status_code == 404:
                return
            raise ex

        for tag in itertools.chain([first_tag], tags_itr):
            if tag["object"]["type"] == "tag":
                yield self.session.get(
                    self._repo_sub_path("{}/git/tags/{}".format(repo_name, tag["object"]["sha"]))
                ).json()

    def get_latest_version_tag(self, repo_name, version_message):
        """
        Fetches the most recent tag with an annotation matching the given version_message
        """
        for tag in self.iter_annotated_tags(repo_name):
            if tag["message"] == version_message:
                return tag["tag"]

        return None

    def create_tag(self, repo_name, branch, tag, message):
        """
        Creates an annotated tag with the following steps

        1. Create the tag object
        2. Create the tag reference using the SHA of the tag object

        Subsequent requests to create a tag object with the same name will override
        the previous object, so retries are possible after failing on step 2
        """
        latest_commit = self.get_single_commit(repo_name, branch)
        create_tag_obj_req = {
            "tag": tag,
            "message": message,
            "object": latest_commit["sha"],
            "type": "commit",
            "tagger": DEFAULT_AUTHOR,
        }
        tag_obj = self.session.post(
            self._repo_sub_path(f"{repo_name}/git/tags"), json=create_tag_obj_req
        ).json()
        create_ref_req = {"ref": f"refs/tags/{tag}", "sha": tag_obj["sha"]}
        return self.session.post(
            self._repo_sub_path(f"{repo_name}/git/refs"), json=create_ref_req
        ).json()

    def create_release(self, repo_name, branch_name, release_name, body):
        """
        Creates a release for the given app_repo along with its associated tag
        using the latest commit from branch_name

        https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository
        """
        req_body = {
            "name": release_name,
            "tag_name": release_name,
            "target_commitish": branch_name,
            "body": body,
        }
        return self.session.post(
            f"/repos/{self._github_repo_owner}/{repo_name}/releases", json=req_body
        ).json()

    def iter_releases(self, repo_name):
        yield from self._iter_data(f"/repos/{self._github_repo_owner}/{repo_name}/releases")

    def iter_commits(self, repo_name, branch_name, org=GitHubOrganization.CONNECTORS):
        yield from self._iter_data(f"/repos/{org}/{repo_name}/commits?sha={branch_name}")

    def get_single_commit(self, repo_name, ref, file_path=None):
        """
        Fetches a commit by a Git reference, where ref can be the SHA of a commit
        or the name of a branch or tag
        """
        params = {}
        if file_path:
            params["file_path"] = file_path

        resp = self.session.get(
            f"/repos/{self._github_repo_owner}/{repo_name}/commits/{ref}",
            params=params,
            headers={"Accept": "application/vnd.github+json"},
        )
        return resp.json()

    def commit_file(self, repo_name, branch, repo_path, content_unencoded, commit_msg, author=None):
        """
        Commits the contents of a file to the specified path in the repository,
        will override an existing path in the repo
        """
        try:
            # If the file already exists, we need to provide its hash to override it
            query_resp = self.session.get(
                self._repo_sub_path(f"{repo_name}/contents/{repo_path}?ref={branch}")
            )
            prev_sha = query_resp.json()["sha"]
        except HTTPError as ex:
            if ex.response.status_code != 404:
                raise ex
            prev_sha = None

        req_json = {
            "content": base64.b64encode(content_unencoded.encode()).decode(),
            "branch": branch,
            "message": commit_msg,
            "committer": author or DEFAULT_AUTHOR,
        }
        if prev_sha:
            req_json["sha"] = prev_sha

        return self.session.put(
            self._repo_sub_path(f"{repo_name}/contents/{repo_path}"), json=req_json
        ).json()

    def update_file(self, repo_name, branch, filepath, new_contents, commit_msg, author=None):
        """
        Alias for commit_file
        """
        return self.commit_file(
            repo_name=repo_name,
            branch=branch,
            repo_path=filepath,
            content_unencoded=new_contents,
            commit_msg=commit_msg,
            author=author,
        )

    @contextmanager
    def work_on_protected_branch(self, repo_name, *args):
        """
        The @contextmanager decorator exists to preserve backwards compatibility with how
        build_app.py uses @class GitLabApi, where branch protection is temporarily disabled to push changes.

        This implementation checks if the configured API key is scoped to an admin
        user allowed to push to protected branches.
        """
        allowed = False
        for repo in self._iter_data("/user/repos", params={"per_page": 100}):
            if (
                repo["name"] == repo_name
                and repo["permissions"]["admin"]
                and repo["permissions"]["push"]
            ):
                allowed = True
                yield
                break

        if not allowed:
            raise ValueError("Configured API key is not scoped to an admin")

    @memoize(ignore_self=True)
    def _get_clone_url(self, repo_name):
        """
        Given a repo name, return its ssh clone link. Also, minimize requests by memoizing results
        """
        repo_name = repo_name.lower()
        try:
            resp = self.session.get(f"/repos/{self._github_repo_owner}/{repo_name}")
            return resp.json()["clone_url"]
        except Exception:
            raise ValueError(f"Could not find repo url for {repo_name}!") from None

    @memoize(ignore_self=True)
    def _get_user_id(self, username):
        try:
            users = self.session.get(f"/users/{username}").json()
            assert len(users) == 1
            return users[0]["id"]
        except Exception as e:
            raise ValueError(f"Could not find user {username} due to this error: {e}") from None

    def validate_username(self, username):
        try:
            self._get_user_id(username)
            return True
        except ValueError:
            return False

    @staticmethod
    def _setup_dirpath(dir_path):
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
        os.makedirs(dir_path)

    def _clone(self, repo_name, local_repo_dir, branch=GITHUB_APP_REPO_BRANCH):
        if self._token:
            clone_url = "{}/{}".format(
                f"https://{self._token}@github.com/{self._github_repo_owner}", repo_name
            )
        else:
            clone_url = f"https://github.com/{self._github_repo_owner}/{repo_name}"
        self._setup_dirpath(local_repo_dir)
        branch_name = branch or GITHUB_APP_REPO_BRANCH
        print(
            "clone_url: {}, local_repo_dir: {}, branch: {}".format(
                clone_url.replace(f"{self._token}@", ""), local_repo_dir, branch_name
            )
        )
        repo = git.Repo.clone_from(clone_url, to_path=local_repo_dir, branch=branch)

        for submodule in repo.submodules:
            submodule.update(init=True)

        return local_repo_dir

    @contextmanager
    def clone_and_manage(self, repo_name, local_repo_dir, branch=GITHUB_APP_REPO_BRANCH):
        """
        This is method calls the _clone method with required parameters depending the mode of the testing.
        It yields the repo directory to wrapper function.
        """
        try:
            yield self._clone(repo_name, local_repo_dir, branch=branch)
        finally:
            if os.path.exists(local_repo_dir):
                shutil.rmtree(local_repo_dir)

    @contextmanager
    def clone_and_manage_app_repo(
        self, repo_name, local_repo_dir="/tmp", branch=GITHUB_APP_REPO_BRANCH
    ):
        """
        This is a wrapper function to call the clone_and_manage method with required parameters depending the mode of the testing.
        """
        local_repo_dir = os.path.join(local_repo_dir, repo_name)

        with self.clone_and_manage(repo_name, local_repo_dir, branch=branch) as repo_dir:
            if not repo_dir:
                raise ValueError(f"Error while cloning the repo {repo_name}!")
            yield repo_dir

    def create_merge_request(
        self, from_branch, to_branch, title, repo_name=None, description="", assignee=None, **kwargs
    ):
        post_data = {"head": from_branch, "base": to_branch, "title": title, "body": description}

        # Pass along any extra kwargs or overrides
        post_data.update(kwargs)
        resp = self.session.post(
            f"/repos/{self._github_repo_owner}/{repo_name}/pulls", json=post_data
        )
        return resp.json()["url"]

    def create_app_merge_request(
        self,
        from_branch,
        to_branch,
        title,
        repo_name,
        description,
        assignee=APP_QA_OVERLORD,
        **kwargs,
    ):
        return self.create_merge_request(
            from_branch, to_branch, title, repo_name, description, assignee=assignee, **kwargs
        )

    def create_issue_comment(self, repo_name, issue_number, comment_str):
        """
        Creates a comment on a issue or PR given by issue_number

        https://docs.github.com/en/rest/reference/issues#create-an-issue-comment
        """
        req_json = {"body": comment_str}
        return self.session.post(
            self._repo_sub_path(f"{repo_name}/issues/{issue_number}/comments"), json=req_json
        ).json()

    def get_pull_request(self, repo_name, pr_number):
        """
        Fetches a pull request for the given repo

        https://docs.github.com/en/rest/reference/pulls#get-a-pull-request
        """
        return self.session.get(self._repo_sub_path(f"{repo_name}/pulls/{pr_number}")).json()

    def put_commit_status(
        self, repo_name, commit_sha, status, description=None, target_url=None, context="default"
    ):
        """
        Creates or overwrites a commit status uniquely identified by :param: context

        https://docs.github.com/en/rest/reference/repos#create-a-commit-status
        """
        req_body = {"state": status, "context": context}
        if description:
            req_body["description"] = description
        if target_url:
            req_body["target_url"] = target_url

        return self.session.post(
            self._repo_sub_path(f"{repo_name}/statuses/{commit_sha}"), json=req_body
        ).json()

    def get_branch(self, repo_name, branch_name):
        """
        Fetches details for a given branch of a repo, returns None if
        the branch doesn't exist.
        """
        try:
            return self.session.get(
                self._repo_sub_path(f"{repo_name}/branches/{branch_name}")
            ).json()
        except HTTPError as ex:
            if ex.response.status_code == http.HTTPStatus.NOT_FOUND:
                return None
            raise ex

    def list_matching_refs(self, repo_name, ref):
        """
        Searches for references matching the supplied :param: ref
        """
        return self.session.get(self._repo_sub_path(f"{repo_name}/git/matching-refs/{ref}")).json()

    def search(self, topic, query_string):
        """
        Wrapper around the search API

        https://docs.github.com/en/rest/search#about-the-search-api
        """
        results = []
        page = 1
        per_page = 100
        while True:
            url = f"/search/{topic}?q={query_string}&per_page={per_page}&page={page}"
            resp = self.session.get(url).json()
            results.extend(resp["items"])
            if len(results) >= resp["total_count"]:
                break
            page += 1

        return results
