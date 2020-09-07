from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, TypeVar

from pep621_project_dependencies.exceptions import DependencySpecificationError


def required_default_factory(message: Optional[str] = None):
    raise DependencySpecificationError(
        message or f"Required field for dependency undefined"
    )


def required_field(message: Optional[str] = None):
    return lambda: required_default_factory(message)


@dataclass
class Dependency:
    name: str
    extras: Optional[List[str]] = field(default=None)
    markers: Optional[str] = field(default=None)
    in_optional: Optional[str] = field(default=None, repr=False)

    def __post_init__(self):
        self.validate()

    def validate(self):
        pass

    def _pep508_string(self) -> str:  # noqa
        return ""

    def to_pep508(self) -> str:
        pep508 = f"{self.name}"

        if self.extras:
            pep508 += f"[{','.join(self.extras)}]"

        _reference = f"{self._pep508_string().strip()}"
        if _reference:
            pep508 += f" {_reference}"

        markers = self.markers or ""
        if self.in_optional:
            if self.in_optional:
                markers = f"{markers} and " if markers else ""
                markers = f"{markers}extra == '{self.in_optional}'"

        if markers:
            pep508 += f" ; {markers}"

        return pep508

    def to_specification(self) -> Dict[str, Any]:
        return {
            k: v
            for k, v in asdict(self).items()
            if k not in {"name", "in_optional"} and v
        }


DependencyType = TypeVar("DependencyType", bound=Dependency)


@dataclass
class VersionedDependency(Dependency):
    version: str = field(default_factory=str)

    def _pep508_string(self) -> str:  # noqa
        if self.version:
            return f"({self.version})"
        return ""

    def validate(self):
        self.version = self.version.strip() if self.version is not None else ""

        if self.version == "*":
            self.version = ""

        if self.version and self.version[0].isnumeric():
            self.version = f"=={self.version}"


@dataclass
class DirectDependency(Dependency):
    url: str = required_field("A url must me specified for a direct dependency")
    vcs: Optional[str] = field(default=None)
    hash: Optional[str] = field(default=None)
    revision: Optional[str] = field(default=None)

    def _pep508_string(self) -> str:  # noqa
        pep508 = "@ "

        if self.vcs:
            pep508 += f"{self.vcs}+"

        pep508 += self.url

        if self.revision:
            pep508 += f"@{self.revision}"

        if self.hash:
            pep508 += f"#{self.hash}"

        return pep508

    @property
    def is_vcs(self) -> bool:
        return self.vcs is not None

    @property
    def hash_algorithm(self) -> Optional[str]:
        if self.hash:
            return self.hash.split("=", 1)[0]

    def validate(self):
        if self.is_vcs:
            if self.vcs not in {"git", "hg", "svn", "bz"}:
                # Maybe this should be a warning
                raise DependencySpecificationError(
                    f"Invalid vcs ({self.vcs}) specified for direct dependency ({self.name})"
                )

            if self.hash:
                raise DependencySpecificationError(
                    f"A hash cannot be specified for a vcs direct dependency ({self.name})"
                )

        if not self.is_vcs:
            if self.revision is not None:
                raise DependencySpecificationError(
                    f"Invalid direct dependency ({self.name}) specified, only vcs dependencies can request a revision"
                )

        if self.hash and "=" not in self.hash:
            raise DependencySpecificationError(
                f"Invalid hash ({self.hash}) specified for direct dependency ({self.name}), "
                "expected value of the form <hash-algorithm>=<expected-hash>"
            )
