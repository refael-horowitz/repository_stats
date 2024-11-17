# Repository Stats

Here is a link to my GitHub `CTFD/CTFD` forked repository:
https://github.com/refael-horowitz/CTFd

## Installation

In order to install the `repository_stats` package:

1. Install [Python 3.10](https://www.python.org/downloads/release/python-3100/)
   Make sure Python version 3 is set as default.
2. Recommended: Activate new virtual environment (venv).
3. Install `repository_stats` as a package (installing the `requirements.txt` is not sufficient):
   * Install in edit mode (code at can be edited):
     ```shell
     $ pip install -e .
     ```
4. Check Installation (without the need to update `PYTHONPATH`) by: 
   * Import methods from `repository_stats/src/repository_stats`:
     ```python
     from repository_stats import *
     ```

## Invoking the main function

Default environment variables can be found in the root directory `.env` file.
E.g:
```shell
FEATURE_BRANCH=improve-none-password-behavior
PR_NUM=2660
REPOSITORY_NAME=CTFd/CTFd
```
`FEATURE_BRANCH` - represents the merge feature branch.
`PR_NUM` - Represents the pull request number in which the feature branch (`FEATURE_BRANCH`) was merged.
`REPOSITORY_NAME` - The repository name.

### Run locally from command line

Define environment variables for `FEATURE_BRANCH`, `PR_NUM` and `REPOSITORY_NAME`.
E.g:
```shell
FEATURE_BRANCH=l10n_master PR_NUM=2660 REPOSITORY_NAME=CTFd/CTFd python3 -m repository_stats --github-token=YOUR_TOKEN --debug-mode --log-to-file
```

### Run docker compose

```shell
docker compose up --build
```

The docker compose will use the environment variables in `.env`.

## Outputs

This will start the main function, and perform the assignment requirements.

A summary of the chosen repository will be printed to the terminal (stdout).
A `.dot` file will be created and saved in the repository root directory.
If logging to a file was chosen, a logging file will be created and saved in the
project root directory.

In order to convert the `.dot` file to an image, run the following in the terminal:
```shell
dot -Tpng src/repository_stats/OUTPUT_DOT_GRAPH > OUTPUT_DOT_GRAPH.png
```
Make sure to change the `.dot` file suffix to `.png`.
