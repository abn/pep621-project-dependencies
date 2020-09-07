from typing import Any, Dict, Optional, Union

from pep621_project_dependencies.dependency.types import (
    DependencyType,
    DirectDependency,
    VersionedDependency,
)
from pep621_project_dependencies.exceptions import DependencySpecificationError
from pep621_project_dependencies.pep508.parser import PEP508Parser


def make_dependency_from_specification(
    name: str,
    specification: Union[str, Dict[str, Any]],
    in_optional: Optional[str] = None,
) -> DependencyType:
    try:
        dependency = None

        if not specification or isinstance(specification, str):
            dependency = VersionedDependency(name=name, version=specification or "")

        if isinstance(specification, dict):
            if "version" in specification:
                dependency = VersionedDependency(name=name, **specification)
            elif "url" in specification:
                dependency = DirectDependency(name=name, **specification)
            elif "direct" in specification:
                # this is done here to handle draft examples
                dependency = DirectDependency(name=name, **specification.get("direct"))

        if dependency is not None:
            dependency.in_optional = in_optional
            return dependency
    except TypeError as e:
        raise DependencySpecificationError(f"Invalid dependency specification: {e}")

    raise DependencySpecificationError(
        f"Unable to detect valid dependency from {specification}"
    )


def make_dependency_from_pep508(text: str) -> DependencyType:
    data = PEP508Parser.parse(text)
    name = data.pop("name")
    in_optional = data.pop("in-optional", None)
    return make_dependency_from_specification(name, data, in_optional)
