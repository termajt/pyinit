import sys
from pathlib import Path
from typing import IO

from pyinit.creator import create_python_project
from pyinit.util import eprint


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
    print("    -n/--no-git         do not initialize git repository", file=file)


if __name__ == "__main__":
    _, *args = sys.argv  # strip __main__.py from argv
    program = "pyinit"
    if len(args) < 1:
        _usage(program, header_only=True, file=sys.stderr)
        eprint("No project name specified")
        exit(1)
    project_name = None
    target_dir = None
    project_description = ""
    project_author = ""
    no_git = False
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
        elif arg in ("-n", "--no-git"):
            no_git = True
        elif project_name is None:
            project_name = arg
        elif target_dir is None:
            target_dir = arg
        else:
            _usage(program, header_only=True, file=sys.stderr)
            eprint("unknown subcommand '%s'", arg)
            exit(1)
    assert project_name is not None, "project_name is None?!"
    if target_dir is None:
        target_dir = Path.cwd()
    elif not isinstance(target_dir, Path):
        target_dir = Path(target_dir)
    try:
        if create_python_project(
            project_name,
            target_dir=target_dir,
            project_description=project_description,
            project_author=project_author,
            no_git=no_git,
        ):
            exit(0)
    except:
        eprint("Brutally failed to create python project: %s", project_name)
    exit(1)
