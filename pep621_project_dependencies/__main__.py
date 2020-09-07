import argparse
import sys
from pathlib import Path

from pep621_project_dependencies.exceptions import DependencySpecificationError
from pep621_project_dependencies.project.metadata import ProjectMetadata

parser = argparse.ArgumentParser()
parser.add_argument(
    "--format", "-f", help="Target format (pep508,toml)", default="pep508"
)
parser.add_argument(
    "source", help="A toml file or PEP 508 string", default="pyproject.toml"
)


def main():
    args = parser.parse_args()
    if args.format == "pep508":
        if not Path(args.source).exists():
            print(f"Source file '{args.source}' does not exist")
        try:
            for dependency in ProjectMetadata(args.source).all_dependencies():
                print(dependency.to_pep508())
        except DependencySpecificationError as e:
            print(f"ERROR: {e}")
    elif args.format == "toml":
        metadata = ProjectMetadata()
        metadata.add_pep508_dependency(args.source)
        print(metadata.dumps())
    else:
        print("Invalid format specified")
        sys.exit(1)


if __name__ == "__main__":
    main()
