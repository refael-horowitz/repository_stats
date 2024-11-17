import argparse
import os
from pathlib import Path

from github import Github

from repository_stats.repository_summary import summarize_repository
from repository_stats.branch_tree import BranchTree
from repository_stats.logging_setup import setup_logging


_FEATURE_BRANCH = os.getenv('FEATURE_BRANCH')
_PR_NUMBER = os.getenv('PR_NUMBER')
_REPOSITORY_NAME = os.getenv('REPOSITORY_NAME')
_BRANCH_DOT_GRAPH = f'branch_{_FEATURE_BRANCH}_graph.dot'
_LOGGING_FILE = Path(__file__).parent.parent.parent / 'logging.yaml'


def _parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Parameters for running the repository stats.')
    parser.add_argument('--github-token', type=str, required=True)
    parser.add_argument('--debug-mode', action='store_true')
    parser.add_argument('--log-to-file', action='store_true')
    return parser.parse_args()


if __name__ == '__main__':
    args = _parse_arguments()
    setup_logging(_LOGGING_FILE, debug_mode=args.debug_mode, log_to_file=args.log_to_file)
    repo = Github(args.github_token).get_repo(_REPOSITORY_NAME)
    print(summarize_repository(repo))
    branch_tree = BranchTree.from_github_branch(repo, _FEATURE_BRANCH, int(_PR_NUMBER))
    branch_tree.write_graph(Path(_BRANCH_DOT_GRAPH))
