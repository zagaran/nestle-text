import os
import argparse
import toml
from binaryornot.check import is_binary


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


def path_to_data(path, max_lines=30):
    data = {}
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        if os.path.isdir(file_path):
            data[filename] = [path_to_data(file_path)]
        else:
            if is_binary(file_path):
                file_data = {"source": file_path}
            else:
                with open(file_path, "r") as f:
                    content = f.read()
                if content.count("\n") > max_lines:
                    file_data = {"source": file_path}
                else:
                    file_data = {"content": content}
            data[filename] = file_data
    return data


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Build a .nestle.toml file from a directory tree')
    parser.add_argument('root', type=str, help='path to the root directory')
    parser.add_argument('--max-lines', type=int, default=30, help='maximum number of lines for text files')
    parser.add_argument('--output', type=str, default=None, help='output file name')
    args = parser.parse_args()

    root = args.root
    max_lines = args.max_lines
    output = args.output

    if not os.path.isdir(root):
        print(f"{root} is not a directory")
        exit(1)

    if not output:
        output = os.path.basename(os.path.normpath(root)) + '.nestle.toml'

    nestle_toml = path_to_data(root, max_lines)
    with open(output, 'w') as f:
        toml.dump(nestle_toml, f, encoder=MultilinePreferringTomlEncoder())
    print(f"{output} successfully generated")
