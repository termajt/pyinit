import os
import platform
import re
import subprocess
import sys
from pathlib import Path
from typing import IO, Union

from pyinit import constants


def _eprint(msg: str, *args, file=sys.stderr, **kwargs):
    msg = msg % args
    print(f"ERROR: {msg}", file=file, **kwargs)


def _iprint(msg: str, *args, file=sys.stdout, **kwargs):
    msg = msg % args
    print(f"INFO: {msg}", file=file, **kwargs)


system = platform.system()
if system == "Windows":

    def _which(cmd):
        return subprocess.getoutput(f"where {cmd}")

elif system == "Linux":

    def _which(cmd):
        return subprocess.getoutput(f"which {cmd}")

else:
    raise NotImplementedError(f"script not implemented for {system}")


def _usage(prog: str, header_only: bool = False, file: IO = sys.stdout):
    print(f"Usage: {prog} [OPTIONS...] <project-name> <target-dir>", file=file)
    if header_only:
        return
    print(file=file)
    print("POSITIONALS:", file=file)
    print("    <project-name>    the name of the project", file=file)
    print(
        "    <target-dir>      the directory in which to create the project (default='.')",
        file=file,
    )
    print(file=file)
    print("OPTIONS:", file=file)
    print(
        "    -h/--help           shows this help message and exit with 0 code",
        file=file,
    )
    print(
        "    -d/--description    the project description, will be added to setup.py in the final project",
        file=file,
    )
    print(
        "    -a/--author         the project author, will be added to setup.py in the final project",
        file=file,
    )


def _prompt(prompt: str) -> bool:
    data = input(f"{prompt} y/N{os.linesep}")
    data = data.strip()
    while not data in ("Y", "y", "n", "N"):
        _eprint("Invalid input '%s', please provide y/n", data)
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


def _resolve_git() -> Union[str, None]:
    git_execs = _which("git")
    if not isinstance(git_execs, str):
        git_execs = git_execs.decode()
    git_execs = git_execs.splitlines()
    return git_execs[0] if len(git_execs) > 0 else None


def _init_git(project_path: Path):
    git_exec = _resolve_git()
    if git_exec is None:
        _iprint("No usable git found, skipping...")
        return
    _iprint("Initializing git repository...")
    code = subprocess.call(
        f'"{git_exec}" init .',
        cwd=str(project_path),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if code != 0:
        _eprint("Failed to initialize git repo at: %s, code: %d", project_path, code)
        return
    _iprint("Writing .gitignore...")
    with open(Path(project_path, ".gitignore"), "w") as fs:
        fs.write(constants.GITIGNORE)
    _iprint(
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
        _eprint("Failed to perform initial commit, code: %d", code)


def _install_local_environment(
    project_path: Path,
    project_name: str,
    project_description: str,
    project_author: str,
):
    _iprint("Creating setup.py...")
    with open(Path(project_path, "setup.py"), "w") as fs:
        fs.write(
            constants.SETUP_PY_FMT.format(
                project_name, project_description, project_author
            )
        )
    _iprint("Creating python source directory...")
    python_dir_name = re.sub(r"[^\w]+", "_", project_name)
    python_dir = Path(project_path, python_dir_name)
    python_dir.mkdir(parents=True)
    with open(Path(python_dir, "__init__.py"), "w") as fs:
        # Just pass, we only want to create an empty file.
        pass
    _iprint("Installing local environment...")
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
        _eprint("Could not install local environment, code: %d", code)
        return False
    return True


def main(prog: Union[str, None] = None):
    program, *args = sys.argv
    if prog is None:
        program = Path(program).name
    else:
        program = prog
    if len(args) < 1:
        _usage(program, header_only=True, file=sys.stderr)
        _eprint("No project name specified")
        exit(1)
    project_name = None
    target_dir = None
    project_description = ""
    project_author = ""
    while args:
        arg, *args = args
        if arg in ("-h", "--help"):
            _usage(program)
            exit(0)
        elif arg in ("-d", "--description"):
            arg, *args = args
            project_description = arg.replace('"', '\\"')
        elif arg in ("-a", "--author"):
            arg, *args = args
            project_author = arg.replace('"', '\\"')
        elif project_name is None:
            project_name = arg
        elif target_dir is None:
            target_dir = arg
        else:
            _usage(program, header_only=True, file=sys.stderr)
            _eprint("unknown subcommand '%s'", arg)
            exit(1)
    assert project_name is not None, "project_name is None?!"
    if target_dir is None:
        target_dir = Path.cwd()
    elif not isinstance(target_dir, Path):
        target_dir = Path(target_dir)
    final_path = Path(target_dir, project_name)
    if final_path.is_dir():
        is_empty = True
        for _ in final_path.iterdir():
            is_empty = False
            break
        if not is_empty:
            _iprint("Directory %s already exists and is not empty", final_path)
            if _prompt("Clean directory and continue?"):
                _clean_dir(final_path, final_path)
    else:
        final_path.mkdir(parents=True)
    _iprint("Creating project: %s", final_path)
    if not _install_local_environment(
        final_path, project_name, project_description, project_author
    ):
        _eprint("Failed to create python project!")
        exit(1)
    _init_git(final_path)
    _iprint("Project %s is now created!", project_name)
