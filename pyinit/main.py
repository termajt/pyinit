import os
import re
import subprocess
import sys
from pathlib import Path
from typing import IO, Union

from pyinit import constants


def eprint(msg: str, *args, file=sys.stderr, **kwargs):
    msg = msg % args
    print(f"ERROR: {msg}", file=file, **kwargs)


def iprint(msg: str, *args, file=sys.stdout, **kwargs):
    msg = msg % args
    print(f"INFO: {msg}", file=file, **kwargs)


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


def _resolve_git() -> Union[str, None]:
    git_execs = subprocess.getoutput("which git")
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
        f"'{git_exec}' init .",
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
    iprint("Adding files and makes an initial commit with message:")
    iprint(constants.INITIAL_COMMIT_MSG)
    code = subprocess.call(
        f"'{git_exec}' add . && '{git_exec}' commit -m {constants.INITIAL_COMMIT_MSG}",
        cwd=str(project_path),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if code != 0:
        eprint("Failed to perform initial commit, code: %d", code)


def _resolve_python() -> Union[str, None]:
    python_execs = subprocess.getoutput("which python")
    if not isinstance(python_execs, str):
        python_execs = python_execs.decode()
    python_execs = python_execs.splitlines()
    return python_execs[0] if len(python_execs) > 0 else None


def main(prog: Union[str, None] = None):
    program, *args = sys.argv
    if prog is None:
        program = Path(program).name
    else:
        program = prog
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
            eprint("unknown subcommand '%s'", arg)
            exit(1)
    assert project_name is not None, "project_name is None?!"
    python_exec = _resolve_python()
    if python_exec is None:
        eprint("No python to use was found, how did you use this script?!")
        exit(1)
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
            iprint("Directory %s already exists and is not empty", final_path)
            if _prompt("Clean directory and continue?"):
                _clean_dir(final_path, final_path)
    else:
        final_path.mkdir(parents=True)
    iprint("Creating project: %s", final_path)
    iprint("Creating setup.py...")
    with open(Path(final_path, "setup.py"), "w") as fs:
        fs.write(
            constants.SETUP_PY_FMT.format(
                project_name, project_description, project_author
            )
        )
    iprint("Creating python source directory...")
    python_dir_name = re.sub(r"[^\w]+", "_", project_name)
    python_dir = Path(final_path, python_dir_name)
    python_dir.mkdir(parents=True)
    with open(Path(python_dir, "__init__.py"), "w") as fs:
        # Just pass, we only want to create an empty file.
        pass
    iprint("Installing local environment...")
    code = subprocess.call(
        f"'{python_exec}' -m venv .venv && . .venv/bin/activate && pip install -e .",
        cwd=str(final_path),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if code != 0:
        eprint("Could not install local environment, code: %d", code)
        exit(1)
    _init_git(final_path)
    iprint("Project %s is now created!", project_name)
