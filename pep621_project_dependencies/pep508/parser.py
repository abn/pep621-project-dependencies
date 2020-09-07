from pathlib import Path
from typing import Any, Dict

from lark import Lark, Token, Transformer


GRAMMAR_MARKER = Path(__file__).parent / "grammars" / "markers.lark"
PARSER_MARKER = Lark.open(GRAMMAR_MARKER, parser="lalr")

GRAMMAR_PEP508 = Path(__file__).parent / "grammars" / "pep508.lark"


class PEP508Transformer(Transformer):
    def version_specification(self, tokens):  # noqa
        return {"version": ", ".join(map(lambda t: t.value, tokens))}

    def revision(self, tokens):  # noqa
        return tokens[0].value

    def vcs_reference(self, tokens):  # noqa
        return {
            "vcs": tokens[0].value,
            "url": tokens[1].value,
            "revision": tokens[2] if len(tokens) > 2 else None,
        }

    def fragments(self, tokens):  # noqa
        value = {"fragments": []}
        for token in tokens:
            if "=" in token.value:
                algorithm, checksum = token.value.split("=", 1)
                if algorithm in {"md5", "sha1", "sha224", "sha256", "sha384", "sha512"}:
                    value["hash"] = token.value
                    continue
            value["fragments"].append(token.value)
        return value

    def hash(self, tokens):  # noqa
        return f"{tokens[0].value}={tokens[1].value}"

    def url_reference(self, tokens):  # noqa
        # TODO: Handle additional fragments?
        return {
            "url": tokens[0].value,
            "hash": tokens[1].get("hash") if len(tokens) > 1 else None,
        }

    def direct_reference(self, tokens):  # noqa
        return tokens[0]

    def markers__item(self, tokens):  # noqa
        return tokens[0], tokens[1], tokens[2]

    def marker_spec(self, tree):  # noqa
        value = {}
        markers = []

        ignore_next_bool = False
        for token in tree[0].children:
            if isinstance(token, Token) and token.type == "markers__BOOL_OP":
                if ignore_next_bool:
                    ignore_next_bool = False
                markers.append(token.value)
                continue

            if isinstance(token, tuple):
                name, op, string = token
                if name == "extra":
                    if not markers:
                        ignore_next_bool = True
                    elif markers[-1] in {"and", "or"}:
                        _ = markers.pop(-1)
                    value["in-optional"] = (
                        string.strip().replace("'", "", 1).replace("'", "", -1)
                    )
                else:
                    markers.append(f"{name} {op} {string}")

        value["markers"] = " ".join(markers)
        return value

    def extras(self, tokens):  # noqa
        return {"extras": [token.value for token in tokens]}

    def start(self, tokens) -> Dict[str, Any]:  # noqa
        data = {"name": tokens[0].value}
        for token in tokens[1:]:
            data.update(token)
        return data


PARSER_PEP508 = Lark.open(
    GRAMMAR_PEP508, parser="lalr", transformer=PEP508Transformer()
)


class PEP508Parser:
    @classmethod
    def parse(cls, text: str) -> Dict[str, Any]:
        return PARSER_PEP508.parse(text)  # noqa
