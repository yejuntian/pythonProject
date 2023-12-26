import argparse
import json
import glob
import re


def replace(mapping, dir):
    with open(mapping, "r") as f:
        d = json.loads(f.read())
    pattern = "|".join(map(re.escape, d.keys()))
    for file in glob.glob(f"{dir}/**/*.smali", recursive=True):
        with open(file, 'r') as f:
            content = f.read()
            content = re.sub(pattern, lambda m: d[m.group()], content)
        with open(file, "w") as f:
            f.write(content)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mappingPath")
    parser.add_argument("from_dir")
    args = parser.parse_args()
    mappingPath = args.mappingPath
    targetDir = args.from_dir
    replace(mappingPath, targetDir)


if __name__ == "__main__":
    main()
