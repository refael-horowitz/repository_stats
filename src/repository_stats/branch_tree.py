import logging
from functools import partial
from pathlib import Path
from typing import List

from attr import define, field
from attr.validators import deep_iterable, instance_of
from github.Commit import Commit
from github.Repository import Repository
from more_itertools import first, last, pairwise
from pydot import Dot, Node, Edge

from repository_stats.commit_utils import get_diverge_commit, get_merge_commit, get_in_between_commits


DOT_SUFFIX = '.dot'
_LOGGER = logging.getLogger(__name__)


def _create_node(branch: str, commit: Commit) -> Node:
    return Node(str(commit.sha), label=f'commit {commit.sha}\n{branch}', shape="circle")


@define(frozen=True, kw_only=True, slots=True)
class BranchTree:
    """  Represents a commit tree of a feature branch.

    :ivar str feature_branch: The feature branch to analyze its commits tree.
    :ivar str main_branch: The main branch of the feature branch from which it has diverged.
    :ivar List[Commit] feature_branch_commits: The commits of the feature branch by chronological order.
    :ivar List[Commit] main_branch_commits: The commits of the main branch by chronological order.
    :ivar Commit diverges_commit: The commit that the feature branch has diverged from.
    :ivar Commit merged_commit: The commit in the main branch the feature branch has merged to.
    """
    feature_branch: str = field(validator=instance_of(str))
    main_branch: str = field(validator=instance_of(str))
    feature_branch_commits: List[Commit] = field(
        factory=list,
        validator=deep_iterable(member_validator=instance_of(Commit), iterable_validator=instance_of(list))
    )
    main_branch_commits: List[Commit] = field(
        factory=list,
        validator=deep_iterable(member_validator=instance_of(Commit), iterable_validator=instance_of(list))
    )

    def build_graph(self) -> Dot:
        """ Builds a dot graph of the feature branch.

        :returns: A dot graph of the feature branch along the main branch.
        :rtype: Dot
        """
        _LOGGER.debug(f'Building a dot graph of the feature branch ({self.feature_branch})')
        graph = Dot(graph_type='digraph', rankdir='LR')
        list(map(graph.add_node, self.branch_nodes))
        list(map(graph.add_edge, self.branch_edges))
        _LOGGER.debug(
            f'The dot graph content:\n {graph.to_string()}'
        )
        return graph

    @property
    def feature_branch_nodes(self) -> List[Node]:
        """ Returns the unique nodes (from the unique commits) of the feature branch."""
        nodes = list(map(partial(_create_node, self.feature_branch), self.feature_branch_commits))
        _LOGGER.debug(f'Feature branch nodes: {repr(nodes)}.')
        return nodes

    @property
    def feature_branch_edges(self) -> List[Edge]:
        """ The nodes edges of the feature branch commit tree."""
        edges = [Edge(n1, n2) for n1, n2 in pairwise(self.feature_branch_nodes)]
        _LOGGER.debug(f'Feature branch edges: {repr(edges)}.')
        return edges

    @property
    def main_branch_nodes(self) -> List[Node]:
        """ The nodes of the main branch commit tree. """
        nodes = list(map(partial(_create_node, self.main_branch), self.main_branch_commits))
        _LOGGER.debug(f'Main branch nodes: {repr(nodes)}')
        return nodes

    @property
    def main_branch_edges(self) -> List[Edge]:
        """ The edges of the main branch commit tree."""
        edges = [Edge(n1, n2) for n1, n2 in pairwise(self.main_branch_nodes)]
        _LOGGER.debug(f'Main branch edges: {repr(edges)}.')
        return edges

    @property
    def branch_edges(self) -> List[Edge]:
        """ The edges of the feature and main branches commits tree."""
        _LOGGER.info(f'Creating the branch graph edges.')
        feature_nodes = self.feature_branch_nodes
        main_nodes = self.main_branch_nodes
        all_edges = [
            Edge(first(main_nodes), first(feature_nodes)),
            Edge(last(feature_nodes), last(main_nodes)),
            *self.feature_branch_edges,
            *self.main_branch_edges
        ]
        _LOGGER.debug(f'All edges:\n{repr(all_edges)}')
        return all_edges

    @property
    def branch_nodes(self) -> List[Node]:
        """ The nodes of the feature and main branches commits tree. """
        _LOGGER.info(f'Creating the branch graph nodes.')
        return self.feature_branch_nodes + self.main_branch_nodes

    def write_graph(self, output_file: Path) -> None:
        """ Writes a dot graph of the feature branch.

        :param output_file: The output file to write the dot graph.
        """
        try:
            if output_file.suffix != DOT_SUFFIX:
                output_file = output_file.with_suffix(DOT_SUFFIX)
            _LOGGER.info(f'Writing branch graph to {output_file}.')
            self.build_graph().write(output_file)
        except Exception:
            _LOGGER.exception('Error while writing the branch graph.')

    @classmethod
    def from_github_branch(cls, repo: Repository, feature_branch: str, pr_num: int, ) -> 'BranchTree':
        """ Generates a `BranchTree` from a GitHub feature branch.

        :param Repository repo: The repository object.
        :param str feature_branch: The feature branch to analyze its commits tree.
        :param int pr_num: The pull request nuber of the branch.
        :returns: A `BranchTree` instance.
        :rtype: BranchTree
        """
        try:
            pull_request = repo.get_pull(pr_num)
            if not pull_request.is_merged():
                raise ValueError(
                    f'Pull request #{pull_request.number} for branch {pull_request.head.ref} is not merged yet.'
                )
            if pull_request.head.ref != feature_branch:
                raise ValueError(f'The branch {feature_branch} does not match pull request number {pr_num}.')
            diverge_commit = get_diverge_commit(repo, pull_request)
            merge_commit = get_merge_commit(repo, pull_request)
            main_branch_commits = get_in_between_commits(repo, diverge_commit, merge_commit)
            return cls(
                feature_branch=feature_branch,
                main_branch=pull_request.base.ref,
                feature_branch_commits=[c for c in pull_request.get_commits()],
                main_branch_commits=[diverge_commit, *main_branch_commits, merge_commit]
            )
        except Exception:
            _LOGGER.exception(f'Error while retrieving the branch tree.')
