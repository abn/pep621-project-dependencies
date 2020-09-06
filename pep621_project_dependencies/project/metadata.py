from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import toml

from pep621_project_dependencies.dependency import (
    DependencyType,
    make_dependency_from_pep508,
    make_dependency_from_specification,
)


class ProjectMetadata:
    def __init__(self, file: Optional[Union[str, Path]] = None) -> None:
        self._file = Path(file) if file else None

        if self._file:
            self._data = toml.load(self._file).get("project", {})
        else:
            self._data = {}

        self._dependencies: Optional[List[DependencyType]] = None
        self._optional_dependencies: Optional[Dict[str, List[DependencyType]]] = None

    @staticmethod
    def _dependency_from_specifications(
        data: Dict[str, Union[str, Dict[str, Any]]], in_optional: Optional[str] = None
    ) -> List[DependencyType]:
        dependencies = list()

        for (name, specifications) in data.items():
            if not isinstance(specifications, list):
                specifications = [specifications]

            for specification in specifications:
                dependencies.append(
                    make_dependency_from_specification(
                        name, specification, in_optional=in_optional
                    )
                )

        return dependencies

    @property
    def dependencies(self) -> List[DependencyType]:
        if self._dependencies is None:
            self._dependencies = self._dependency_from_specifications(
                self._data.get("dependencies", {})
            )
        return self._dependencies

    @property
    def optional_dependencies(self) -> Dict[str, List[DependencyType]]:
        if self._optional_dependencies is None:
            self._optional_dependencies = {}

            sections = self._data.get("optional-dependencies", {})
            for section in sections:
                self._optional_dependencies[
                    section
                ] = self._dependency_from_specifications(
                    sections.get(section, []), in_optional=section
                )

        return self._optional_dependencies

    @property
    def extras(self) -> List[str]:
        return list(self.optional_dependencies.keys())

    def add_pep508_dependency(self, specification: str):
        dependency = make_dependency_from_pep508(text=specification)
        self.add_dependency(dependency)

    def add_dependency(
        self,
        specification: Union[DependencyType, Dict[str, Any]],
        in_optional: Optional[str] = None,
    ):
        if isinstance(specification, dict):
            dependency = self._dependency_from_specifications(
                specification, in_optional
            )
        else:
            dependency = specification

        if dependency.in_optional:
            if dependency.in_optional not in self.optional_dependencies:
                self._optional_dependencies[dependency.in_optional] = []
            self._optional_dependencies[dependency.in_optional].append(dependency)
        else:
            _ = self.dependencies
            self._dependencies.append(dependency)

    def all_dependencies(self):
        for dependency in self.dependencies:
            yield dependency

        for dependencies in self.optional_dependencies.values():
            for dependency in dependencies:
                yield dependency

    def dumps(self) -> Dict[str, Any]:
        # TODO: replace with tomlkit for better inline array support
        decoder = toml.decoder.TomlDecoder()
        encoder = toml.encoder.TomlArraySeparatorEncoder(preserve=True)

        dependencies = {}
        optional_dependencies = {}

        for dependency in self.all_dependencies():
            specification = decoder.get_empty_inline_table()
            specification.update(dependency.to_specification())

            _dependencies = dependencies
            if dependency.in_optional:
                if dependency.in_optional not in optional_dependencies:
                    optional_dependencies[dependency.in_optional] = {}
                _dependencies = optional_dependencies[dependency.in_optional]

            if dependency.name in _dependencies:
                if not isinstance(_dependencies[dependency.name], list):
                    _dependencies[dependency.name] = [specification]
                _dependencies[dependency.name].append(specification)
            else:
                _dependencies[dependency.name] = specification

        data = deepcopy(self._data)
        project = data.get("project", {})
        project.update(
            {
                "dependencies": dependencies,
                "optional-dependencies": optional_dependencies,
            }
        )
        data["project"] = project

        return toml.dumps(data, encoder=encoder)
