# Pyinit
Simple script to create python projects.

Creates a virtual environment using python venv module, package and setup.py for the project.

## Project structure
```
|-project-name
|-setup.py
|-.gitignore
|--project_name
|---__init__.py
```

## Usage
```console
$ python pyinit <project-name> [<target-dir>] [-a <author>] [-d <project-description>]
```
If installed with pip:
```console
$ python -m pyinit <project-name> [<target-dir>] [-a <author>] [-d <project-description>]
```

```console
$ python pyinit -h
Usage: pyinit [OPTIONS...] <project-name> <target-dir>

POSITIONALS:
    <project-name>    the name of the project
    <target-dir>      the directory in which to create the project (default='.')

OPTIONS:
    -h/--help           shows this help message and exit with 0 code
    -d/--description    the project description, will be added to setup.py in the final project
    -a/--author         the project author, will be added to setup.py in the final project
```

## Additonal
Add alias to .bashrc (or .bash_alias) after pip install:
```console
$ alias pyinit="python -m pyinit $@"
```
