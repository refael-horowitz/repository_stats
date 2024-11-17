import logging
from typing import List

from github import GithubException
from github.Commit import Commit
from github.PullRequest import PullRequest
from github.Repository import Repository


_LOGGER = logging.getLogger(__name__)


def get_diverge_commit(repo: Repository, pull_request: PullRequest) -> Commit:
    """ Get the base commit between a feature branch and the main branch.

    :param Repository repo: The repository object.
    :param PullRequest pull_request: The pull request of the branch.
    :returns: The base commit between a feature branch and the main branch.
    :rtype: Commit
    """
    try:
        _LOGGER.info(f'Getting diverge commit for {pull_request.head.ref} (#{pull_request.number})')
        commit = repo.compare(pull_request.base.sha, pull_request.head.sha).merge_base_commit
        _LOGGER.debug(f'Diverge commit of feature branch ({pull_request.head.ref}): {commit.sha}')
        return commit
    except GithubException:
        _LOGGER.exception(
            f'Could not find the base commit for branch: {pull_request.head.ref} (#{pull_request.number})'
        )


def get_merge_commit(repo: Repository, pull_request: PullRequest) -> Commit:
    """ Get the merge commit for a branch if it has been merged into the main branch.

    :param Repository repo: The repository object.
    :param PullRequest pull_request: The pull request of the branch.
    :returns: The merge commit for a branch if it has been merged into the main branch.
    :rtype: Commit
    """
    try:
        _LOGGER.info(f'Getting merge commit for branch: {pull_request.head.ref} (#{pull_request.number})')
        commit = pull_request.merge_commit_sha
        _LOGGER.debug(f'Merge commit for branch ({pull_request.head.ref}): {commit}')
        return repo.get_commit(commit)
    except GithubException:
        _LOGGER.exception(
            f'Failed to retrieve merge commit for branch: {pull_request.head.ref} (#{pull_request.number})'
        )


def get_in_between_commits(repo: Repository, base: Commit, head: Commit) -> List[Commit]:
    """ Return the commits between the `base` and `head` commits.

    :param Repository repo: The repository object.
    :param Commit base: The base commit to compare.
    :param Commit head: The head commit to compare.
    :returns: The commits between the base and head commits.
    :rtype: List[Commit]
    """
    try:
        commits = [c for c in repo.compare(base.sha, head.sha).commits if c.sha != head.sha]
        _LOGGER.debug(f'Commits between the base ({base.sha}) and head ({head.sha}) commits: {repr(commits)}')
        return commits
    except GithubException:
        _LOGGER.exception('Failed to retrieve commits between base and head.')
