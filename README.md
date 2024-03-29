# nestle-text

Nestle-Text is a lightweight, human-friendly format for encoding a directory tree structure and its contents.
Its cozy TOML-based syntax aids reading, writing, and editing 
small text-based projects with complex or evolving file structures.  Nestle-Text is handy when...
- prototyping or stubbing out new projects;
- sharing project templates;
- performing refactors that move and rename lots of files; or even 
- postponing decisions on project structure until a clear organizing principle emerges.

Nestle-Text files typically use the extension `.nestle.toml`.

## Installation
To install nestle-text from git, you can run

```sh
pip install git+https://github.com/zagaran/nestle-text.git
```

## Usage
To use Nestle-Text, you can use the following command line tools:

- `nestle`: Converts a directory structure to a Nestle-Text file in TOML format.
- `unnestle`: Converts a Nestle-Text file in TOML format to a directory structure.

Both tools take two arguments: the path to the input directory or file, and the path to the output file or directory. If the directory is not specified, the TOML filename will be used as the root directory name.

For example, if you have a Nestle-Text file called `project.nestle.toml` in the current working directory, you can convert it to a directory structure with:

    unnestle project.nestle.toml

This will create a directory called `project` in the current working directory, containing the directory structure and files described in the Nestle-Text file.

Similarly, if you have a directory called `my_project` in the current working directory, you can convert it to a Nestle-Text file called `my_project.nestle.toml` with:

    nestle my_project

This will create a file called `my_project.nestle.toml` in the current working directory, containing the Nestle-Text representation of the directory structure and files.


## Example

Here is an example of a directory structure described in Nestle-Text format:

```
# The root directory name is specified by the argument to unnestle,
# so it doesn't appear in this file

# Use double brackets to declare a directory
[[src]]

# and dot notation to declare a subdirectory.
[[src.utils]]

# Use single brackets to declare a file. You will need to
# use quotes if, as is typical, the filename contains a '.'
# Here we define a top level file LICENSE.txt
["LICENSE.txt"]
# File contents are given inline using the "content" key
content = "This text will be placed inside LICENSE.txt"

["README.md"]
# Larger files can be included by providing a system path
source = "files/readme-template-version-2.md"

[".gitignore"]
# Pull a standard gitignore from github
url = "https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore"

[[src.core]]
# It can be nice to give a comment when introducing a new file or directory.

[src.core."core.py"]
# The entire functionality of the project is included in the following simple python file
content = """
def hello_world():
    return "Hello world!"
"""

# Nesting directories is easy
[[src.utils.datetimes]]
[src.utils.datetimes."timezone_helpers.py"]
content = """
# TODO: write some useful functions for timezones, should be easy
"""

# Non-text files can only be included using the "source" key
[[assets]]
[[assets.gifs]]
[assets.gifs."not_bad.gif"]
source = "files/personal-animated-gif-collection/not_bad-small.gif"
```

For example, to generate a nestle-text file describing this git repo, you can run

    nestle . --git-only

which will regenerate the file `nestle-text.nestle.toml`.

## Tests
To test the `nestle` command, move to the `tests/nestle` directory and run:

    nestle root_directory

To test the `unnestle` command, move to the `tests/unnestle` directory and run:

    unnestle example.nestle.toml

## Future directions
- Allow the specification of file permissions in addition to content
- Somehow support syntax highlighting when editing nestle.toml files
- Automatically sync a directory and its nestle.toml file when either one is edited