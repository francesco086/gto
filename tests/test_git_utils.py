from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Union
from unittest.mock import patch

import pytest
from git import Repo

import tests.resources
from gto.git_utils import cloned_git_repo, git_clone_remote_repo
from tests.skip_presets import (
    only_for_windows_py_lt_3_8,
    skip_for_windows_py_lt_3_9,
)


def test_git_clone_remote_repo_if_repo_gitpython_object_then_leave_it_unchanged(
    tmp_gitpython_repo: Repo,
):
    assert_f_called_with_repo_return_repo_itself(repo=tmp_gitpython_repo)


@pytest.mark.parametrize(
    "repo",
    (
        "/local/path",
        "local/path",
        ".",
        "meaningless_string",
    ),
)
def test_git_clone_remote_repo_if_repo_is_string_and_invalid_remote_url_then_leave_repo_as_it_is(
    repo: str,
):
    assert_f_called_with_repo_return_repo_itself(repo=repo)


@skip_for_windows_py_lt_3_9
@pytest.mark.parametrize(
    "repo",
    (
        tests.resources.SAMPLE_HTTP_REMOTE_REPO,
        tests.resources.SAMPLE_HTTP_REMOTE_REPO_WITHOUT_DOT_GIT_SUFFIX,
    ),
)
def test_git_clone_remote_repo_if_repo_is_string_and_valid_remote_url_then_clone_and_set_repo_to_its_local_path(
    repo,
):
    with patch("gto.git_utils.cloned_git_repo") as mock_cloned_git_repo:
        decorated_func(repo=repo, spam=0, jam=3)
        mock_cloned_git_repo.assert_called_once_with(repo=repo)


@only_for_windows_py_lt_3_8
def test_git_clone_remote_repo_if_windows_os_error_then_hint_the_cause():
    with pytest.raises(OSError) as e:
        decorated_func(repo=tests.resources.SAMPLE_HTTP_REMOTE_REPO, spam=0, jam=3)
    assert e.type in (NotADirectoryError, PermissionError)
    assert "windows" in str(e)
    assert "python" in str(e)
    assert "< 3.9" in str(e)


@skip_for_windows_py_lt_3_9
@pytest.mark.parametrize(
    "repo",
    (
        tests.resources.SAMPLE_HTTP_REMOTE_REPO,
        tests.resources.SAMPLE_HTTP_REMOTE_REPO_WITHOUT_DOT_GIT_SUFFIX,
    ),
)
def test_cloned_git_repo_if_valid_remote_then_clone(repo: str):
    with cloned_git_repo(repo=repo) as repo_dir:
        assert_dir_contain_git_repo(dir=repo_dir)


def test_cloned_git_repo_if_invalid_remote_then_raise_exception():
    with pytest.raises(Exception):
        with cloned_git_repo(repo="invalid_remote_url"):
            pass


@git_clone_remote_repo
def decorated_func(
    spam: int, repo: Union[Repo, str], jam: int
):  # pylint: disable=unused-argument
    return repo


def assert_f_called_with_repo_return_repo_itself(repo: Union[str, Repo]) -> None:
    assert decorated_func(0, repo, 3) is repo
    assert decorated_func(0, repo, jam=3) is repo
    assert decorated_func(0, jam=3, repo=repo) is repo
    assert decorated_func(spam=0, jam=3, repo=repo) is repo


def assert_dir_contain_git_repo(dir: str) -> None:
    assert (Path(dir) / ".git").is_dir()
    assert (Path(dir) / ".git/HEAD").is_file()


@pytest.fixture
def tmp_gitpython_repo() -> Repo:
    tmp_repo_dir = TemporaryDirectory()  # pylint: disable=consider-using-with
    yield Repo.init(path=tmp_repo_dir.name)
    tmp_repo_dir.cleanup()
