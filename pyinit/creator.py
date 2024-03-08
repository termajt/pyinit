import os
import platform
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional as _Optional
from typing import Union as _U

from pyinit import constants
from pyinit.util import eprint, iprint

system = platform.system()
if system == "Windows":

    def _which(cmd):
        return subprocess.getoutput(f"where {cmd}")

elif system == "Linux":

    def _which(cmd):
        return subprocess.getoutput(f"which {cmd}")

else:
    raise NotImplementedError(f"script not implemented for {system}")


def _prompt(prompt: str) -> bool:
    data = input(f"{prompt} y/N{os.linesep}")
    data = data.strip()
    while not data in ("Y", "y", "n", "N"):
        eprint("Invalid input '%s', please provide y/n", data)
        data = input(f"{prompt} y/N{os.linesep}")
        data = data.strip()
    return data in ("Y", "y")


def _clean_dir(path: Path, start: Path):
    if path.is_dir():
        for it in path.iterdir():
            _clean_dir(it, start)
        if path != start:
            path.rmdir()
    elif path.is_file() or path.is_symlink():
        path.unlink()


def _resolve_git() -> _Optional[str]:
    git_execs = _which("git")
    if not isinstance(git_execs, str):
        git_execs = git_execs.decode()
    git_execs = git_execs.splitlines()
    return git_execs[0] if len(git_execs) > 0 else None


def _init_git(project_path: Path):
    git_exec = _resolve_git()
    if git_exec is None:
        iprint("No usable git found, skipping...")
        return
    iprint("Initializing git repository...")
    code = subprocess.call(
        f'"{git_exec}" init .',
        cwd=str(project_path),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if code != 0:
        eprint("Failed to initialize git repo at: %s, code: %d", project_path, code)
        return
    iprint("Writing .gitignore...")
    with open(Path(project_path, ".gitignore"), "w") as fs:
        fs.write(constants.GITIGNORE)
    iprint(
        "Adding files and makes an initial commit with message:\n    %s",
        constants.INITIAL_COMMIT_MSG,
    )
    code = subprocess.call(
        f'"{git_exec}" add . && "{git_exec}" commit -m {constants.INITIAL_COMMIT_MSG}',
        cwd=str(project_path),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if code != 0:
        eprint("Failed to perform initial commit, code: %d", code)


def _install_local_environment(
    project_path: Path,
    project_name: str,
    project_description: str,
    project_author: str,
) -> bool:
    iprint("Creating setup.py...")
    with open(Path(project_path, "setup.py"), "w") as fs:
        fs.write(
            constants.SETUP_PY_FMT.format(
                project_name, project_description, project_author
            )
        )
    iprint("Creating python source directory...")
    python_dir_name = re.sub(r"[^\w]+", "_", project_name)
    python_dir = Path(project_path, python_dir_name)
    python_dir.mkdir(parents=True)
    with open(Path(python_dir, "__init__.py"), "w") as _:
        # Just pass, we only want to create an empty file.
        pass
    iprint("Installing local environment...")
    activate_cmd = ". .venv/bin/activate"
    venv_cmd = f'"{sys.executable}" -m venv .venv'
    pip_cmd = "pip install -e ."
    if system == "Windows":
        activate_cmd = ".venv\\Scripts\\activate"
    cmd = f"{venv_cmd} && {activate_cmd} && {pip_cmd}"
    code = subprocess.call(
        cmd,
        cwd=str(project_path),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if code != 0:
        eprint("Could not install local environment, code: %d", code)
        return False
    return True


def create_python_project(
    project_name: str,
    target_dir: _Optional[_U[str, Path]] = ".",
    project_description: _Optional[str] = None,
    project_author: _Optional[str] = None,
    no_git: bool = False,
):
    """Create a new python project that resides in `target_dir`.

    :param project_name: The directory name of the project. Will also be used as `package_name` if `package_name` is `None`.
    :param target_dir: The target directory in which to create the project.
    :param project_description: The project description, this will be added to setup.py.
    :param project_author: The project author, this will be added to setup.py.
    :param no_git: if `True` no git initialization will be done for the created project.
    """
    if project_name is None:
        raise ValueError("project_name cannot be None")
    if target_dir is None:
        target_dir = Path.cwd()
    elif isinstance(target_dir, str):
        target_dir = Path(target_dir)
    elif not isinstance(target_dir, Path):
        raise TypeError("target_dir must be either pathlib.Path or str")
    if project_description is None:
        project_description = ""
    if project_author is None:
        project_author = ""
    final_path = Path(target_dir, project_name)
    if final_path.is_dir():
        is_empty = True
        for _ in final_path.iterdir():
            is_empty = False
            break
        if not is_empty:
            iprint("Directory %s already exists and is not empty", final_path)
            if _prompt("Clean directory and continue?"):
                _clean_dir(final_path, final_path)
    else:
        final_path.mkdir(parents=True)
    iprint("Creating project: %s", final_path)
    if not _install_local_environment(
        final_path, project_name, project_description, project_author
    ):
        eprint("Failed to create python project!")
        return False
    if not no_git:
        _init_git(final_path)
    iprint("Project %s is now created!", project_name)
    return True
