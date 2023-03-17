import os
import argparse
import toml
from binaryornot.check import is_binary
import subprocess


from toml.encoder import _dump_str, TomlEncoder, unicode


def _dump_str_prefer_multiline(v):
    multilines = v.split('\n')
    if len(multilines) > 1:
        return unicode('"""\n' + v.replace('"""', '\\"""').strip() + '\n"""')
    else:
        return _dump_str(v)


class MultilinePreferringTomlEncoder(TomlEncoder):
    def __init__(self, _dict=dict, preserve=False):
        super(MultilinePreferringTomlEncoder, self).__init__(_dict=dict, preserve=preserve)
        self.dump_funcs[str] = _dump_str_prefer_multiline


class UndisplayableFileException(Exception):
    pass


def get_parent_directories(path):
    """
    Returns a list of all parent directories of a given path.
    """
    parent_dirs = []
    while True:
        path = os.path.dirname(path)
        if not path:
            break
        parent_dirs.append(path)
    return parent_dirs


def get_git_root_directory():
    output = subprocess.check_output(["git", "rev-parse", "--show-toplevel"]).decode().strip()
    return output

def get_git_working_tree_paths():
    output = subprocess.check_output(["git", "ls-files", "--full-name"]).decode()
    file_paths = output.split("\n")[:-1]  # exclude the last empty string
    paths = set(file_paths + [parent for file_path in file_paths for parent in get_parent_directories(file_path)])
    return paths


def path_to_data(path, max_lines=30, paths=None):
    data = {}
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        if paths and os.path.abspath(file_path) not in paths:
            continue
        if os.path.isdir(file_path):
            data[filename] = [path_to_data(file_path, max_lines=max_lines, paths=paths)]
        else:
            try:
                with open(file_path, "r") as f:
                    content = f.read()
                if is_binary(file_path) or content.count("\n") > max_lines:
                    raise UndisplayableFileException()
                else:
                    file_data = {"content": content}
            except (UnicodeDecodeError, UndisplayableFileException):
                file_data = {"source": file_path}
            data[filename] = file_data
    return data


def main():
    parser = argparse.ArgumentParser(description='Build a .nestle.toml file from a directory tree')
    parser.add_argument('root', type=str, help='path to the root directory')
    parser.add_argument('--max-lines', type=int, default=30, help='maximum number of lines for text files')
    parser.add_argument('--output', type=str, default=None, help='output file name')
    parser.add_argument('--git-only', default=False, action='store_true', help='restrict attention to files tracked by git')
    args = parser.parse_args()

    root = args.root
    max_lines = args.max_lines
    git_only = args.git_only
    paths = None
    if git_only:
        git_root = get_git_root_directory()
        file_paths = [os.path.abspath(os.path.join(git_root, git_path)) for git_path in get_git_working_tree_paths()]
        paths = set(file_paths + [os.path.abspath(os.path.dirname(path)) for path in file_paths])
    output = args.output

    if not os.path.isdir(root):
        print(f"{root} is not a directory")
        exit(1)

    if not output:
        output = os.path.basename(os.path.abspath(root)) + '.nestle.toml'

    nestle_toml = path_to_data(root, max_lines=max_lines, paths=paths)
    with open(output, 'w') as f:
        toml.dump(nestle_toml, f, encoder=MultilinePreferringTomlEncoder())
    print(f"Wrote file at {output}")


if __name__ == '__main__':
    main()
