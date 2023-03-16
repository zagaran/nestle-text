import os
import shutil
import requests
import toml
import argparse


def create_directory_tree(root_path, tree):
    for item, subtree in tree.items():
        if isinstance(subtree, dict):
            filepath = os.path.join(root_path, item)
            if 'source' in subtree:
                source_path = subtree['source']
                shutil.copy(source_path, filepath)
            elif 'content' in subtree:
                with open(filepath, 'w') as f:
                    f.write(subtree['content'])
            elif 'url' in subtree:
                url = subtree['url']
                response = requests.get(url)
                with open(filepath, 'wb') as f:
                    f.write(response.content)
            else:
                raise ValueError("File declaration must use one of the keys 'source', 'content', or 'url'")
        elif isinstance(subtree, list):
            subdirectory_path = os.path.join(root_path, item)
            os.makedirs(subdirectory_path, exist_ok=True)
            create_directory_tree(subdirectory_path, {k: v for d in subtree for k, v in d.items()})


def main():
    parser = argparse.ArgumentParser(description='Convert a Nestle-Text file to a directory tree.')
    parser.add_argument('filename', type=str, help='The .nestle.toml file to expand into a directory tree')
    parser.add_argument('--root', type=str, help='The name of the root directory to create. If not provided, the root directory will be named after the filename without the .nestle.toml extension.')
    parser.add_argument('--hard', action='store_true', help='Delete and replace the target directory')
    args = parser.parse_args()

    root_name = args.root
    expected_ending = ".nestle.toml"
    if not root_name and args.filename.endswith(expected_ending):
        root_name = args.filename[:-len(expected_ending)]

    if not root_name:
        raise ValueError("Specify a root directory or supply a nestle-text file with extension .nestle.toml")

    with open(args.filename) as f:
        data = toml.load(f)

    root_path = os.path.abspath(root_name)
    if args.hard:
        shutil.rmtree(root_path)
    elif os.path.exists(root_path):
        raise Exception("Root directory already exists.  Use the --hard flag to force an overwrite")

    create_directory_tree(root_path, data)


if __name__ == '__main__':
    main()
