# Pyinit
Simple script to create python projects.

Creates a virtual environment using python venv module, package and setup.py for the project.

## Project structure
```
. <target-dir>
└── <project-name>
    ├── <package_name>
    |   └── __init__.py
    ├── setup.py 
    └── .gitignore
```

## Installation
```console
$ pip install .
```

## Usage
```console
$ pyinit <project-name> [<target-dir>]
$ pyinit -h
Usage: pyinit [OPTIONS...] <project-name> <target-dir>

POSITIONALS:
    <project-name>    the name of the project
    <target-dir>      the directory in which to create the project (default='.')

OPTIONS:
    -h/--help           shows this help message and exit with 0 code
    -d/--description    the project description, will be added to setup.py in the final project
    -a/--author         the project author, will be added to setup.py in the final project
    -n/--no-git         do not initialize git repository
    -v/--verbose        enable verbose output, shows all output of external commands aswell
```
