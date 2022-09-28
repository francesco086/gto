import inspect
import logging
from contextlib import contextmanager
from functools import wraps
from tempfile import TemporaryDirectory
from typing import Callable, Dict

from git import Repo

from gto.constants import remote_git_repo_regex


def git_clone_remote_repo(push_tags: bool = False):
    def execute_f_on_cloned_repo(f: Callable):
        @wraps(f)
        def wrapped_f(*args, **kwargs):
            kwargs = _turn_args_into_kwargs(f, args, kwargs)

            if isinstance(kwargs["repo"], str) and is_url_of_remote_repo(
                repo=kwargs["repo"]
            ):
                try:
                    with cloned_git_repo(repo=kwargs["repo"]) as tmp_dir:
                        kwargs["repo"] = tmp_dir
                        result = f(**kwargs)
                        if push_tags:
                            git_push_tags(path=tmp_dir)
                except (NotADirectoryError, PermissionError) as e:
                    raise e.__class__(
                        "Are you using windows with python < 3.9? "
                        "This may be the reason of this error: https://bugs.python.org/issue42796. "
                        "Consider upgrading python."
                    ) from e
            else:
                result = f(**kwargs)

            return result

        return wrapped_f

    return execute_f_on_cloned_repo


def is_url_of_remote_repo(repo: str) -> bool:
    if remote_git_repo_regex.fullmatch(repo) is not None:
        logging.debug("%s recognized as remote git repo", repo)
        return True

    logging.debug("%s NOT recognized as remote git repo", repo)
    return False


@contextmanager
def cloned_git_repo(repo: str):
    tmp_dir = TemporaryDirectory()
    logging.debug("create temporary directory %s", tmp_dir)
    git_clone(repo=repo, dir=tmp_dir.name)
    yield tmp_dir.name
    logging.debug("delete temporary directory %s", tmp_dir)
    tmp_dir.cleanup()


def git_clone(repo: str, dir: str) -> None:
    logging.debug("clone %s in directory %s", repo, dir)
    Repo.clone_from(url=repo, to_path=dir)


def git_push_tags(path: str, remote_name: str = "origin") -> None:
    repo = Repo(path=path)
    remote = repo.remote(name=remote_name)
    remote.push("--tags")


def _turn_args_into_kwargs(
    f: Callable, args: tuple, kwargs: Dict[str, object]
) -> Dict[str, object]:
    kwargs_complement = {
        k: args[i]
        for i, k in enumerate(inspect.getfullargspec(f).args)
        if i < len(args)
    }
    kwargs.update(kwargs_complement)
    return kwargs
