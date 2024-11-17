import logging
from typing import List

from attr import define, field
from attr.validators import instance_of
from github import Repository, GithubException
from github.NamedUser import NamedUser
from more_itertools import first, last


_LOGGER = logging.getLogger(__name__)


@define(frozen=True, kw_only=True, slots=True)
class RepositorySummary:
    """ Represents a GitHub repository.

    :ivar str name: Name of the repository.
    :ivar List[str] releases: List of GitHub releases.
    :ivar int forks: Number of repository forks.
    :ivar int stars: Number of repository stars.
    :ivar int num_contributors: Number of repository contributors.
    :ivar List[str] sorted_contributors: List of ordered repository contributors
        by number of all pull requests (closed and open).
    """
    name: str | None = field(validator=instance_of(str), default=None)
    releases: List[str] = field(factory=list)
    forks: int | None = field(validator=instance_of(int), default=None)
    stars: int | None = field(validator=instance_of(int), default=None)
    num_contributors: int | None = field(validator=instance_of(int), default=None)
    sorted_contributors: List[str] = field(factory=list)

    def __str__(self) -> str:
        return (
            f"Repository ({self.name}) Summary: \n"
            f"  releases={repr(self.releases)},\n"
            f"  forks={self.forks},\n"
            f"  stars={self.stars},\n"
            f"  num_contributors={self.num_contributors},\n"
            f"  sorted_contributors={repr(self.sorted_contributors)}\n"
        )


def summarize_repository(repo: Repository, recent_releases: int = 3) -> RepositorySummary:
    """ Summarizes a GitHub repository in a certain format.

    :param Repository repo: A GitHub repository.
    :param int recent_releases: The number of recent releases to return.
    :returns: A `RepositorySummary` object.
    :rtype: RepositorySummary
    """
    _LOGGER.info(f'summarizing repository {repo.name}')
    contributors = get_contributors(repo)
    summary = RepositorySummary(
        name=repo.name,
        releases=latest_releases(repo, recent_releases),
        forks=repo.forks_count,
        stars=repo.stargazers_count,
        num_contributors=len(contributors),
        sorted_contributors=sort_contributors_by_prs(repo, contributors)
    )
    _LOGGER.info('repository summary has been completed.')
    _LOGGER.debug(str(summary))
    return summary


def get_contributors(repo: Repository) -> List[NamedUser]:
    """ Returns the list of contributors of the repository.

    :param Repository repo: The repository to get the contributors for.
    :returns: A list of contributors of the repository.
    :rtype: List[NamedUser]
    """
    try:
        contributors = [c for c in repo.get_contributors()]
        _LOGGER.debug(f'contributors of repository ({repo.name}): {[c.login for c in contributors]}')
        return contributors
    except GithubException as e:
        _LOGGER.exception(
            f'Unable to get contributors for repository {repo.name}.\nException: {e.message}'
        )


def latest_releases(repo: Repository, latest: int) -> List[str]:
    """ Returns the latest releases of the repository.

    :param Repository repo: The repository to get the latest releases for.
    :param int latest: The number of recent releases to return.
    :returns: A list of the latest repository releases tag names.
    :rtype: List[str]
    """
    try:
        releases = [r.tag_name for r in repo.get_releases()[:latest]]
        _LOGGER.debug(f'{latest} latest repository releases: {releases}')
        return releases
    except GithubException:
        _LOGGER.exception(f'Unable to get releases for repository {repo.name}.')


def sort_contributors_by_prs(repo: Repository, contributors: List[NamedUser]) -> List[str]:
    """ Sorts the list of contributors of the repository per amount of pull requests.

    The contributors are sorted based on the number of all pull requests, including the closed ones.

    :param Repository repo: The repository to get the contributors for.
    :param List[NamedUser] contributors: A list of repository contributors.
    :returns: A list of contributors of the repository.
    :rtype: List[str]
    """
    try:
        pull_requests = repo.get_pulls(state='all')
        contributions = {contributor: [
            pr for pr in pull_requests if pr.user.login == contributor.login
        ]
            for contributor in contributors}
        _LOGGER.debug(repr({k: [p.title for p in v] for k, v in contributions.items()}))
        return [first(c).login for c in sorted(contributions.items(), key=lambda item: len(last(item)), reverse=True)]
    except GithubException:
        _LOGGER.exception(f'Unable to get releases for repository {repo.name}.')
