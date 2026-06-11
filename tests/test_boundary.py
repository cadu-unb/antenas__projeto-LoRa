"""AST-based boundary check: Bloco 1 must not import GIS, network, or UI libs."""

import ast
import pathlib

BLOCO1_ROOTS = [
    pathlib.Path("src/lora_antenna/propagation"),
    pathlib.Path("src/lora_antenna/core"),
    pathlib.Path("src/lora_antenna/antenna"),
]

FORBIDDEN_PREFIXES = (
    "lora_antenna.gis",
    "lora_antenna.network",
    "streamlit",
    "folium",
    "shapely",
    "requests",
)


def _module_is_forbidden(module_name: str) -> bool:
    return any(
        module_name == prefix or module_name.startswith(prefix + ".")
        for prefix in FORBIDDEN_PREFIXES
    )


def test_no_forbidden_imports_in_bloco1():
    violations: list[str] = []

    for root_dir in BLOCO1_ROOTS:
        for py_file in root_dir.rglob("*.py"):
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(py_file))

            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    if _module_is_forbidden(module):
                        violations.append(
                            f"{py_file}:{node.lineno}: from {module} import ..."
                        )
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        if _module_is_forbidden(alias.name):
                            violations.append(
                                f"{py_file}:{node.lineno}: import {alias.name}"
                            )

    assert not violations, (
        "Forbidden imports found in Bloco 1:\n" + "\n".join(violations)
    )
