"""Filtro de deploy para versionar somente a aplicação completa.

Mantém o código, a interface, a documentação técnica, scripts de apoio e testes.
Remove artefatos locais, relatórios de trabalho, prompts, caches e ambientes.
"""

DEFAULT_CONFIG: dict = {
    "ignored_dirs": [
        "__pycache__",
        ".git",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".uv-cache",
        ".venv",
        "venv",
        "env",
        "node_modules",
        ".vscode",
        ".idea",
        ".agents",
        ".claude",
        ".codex",
        ".plan",
        ".prompt",
        ".reports",
        "__docs",
        "__roteiro",
        "_path",
        "build",
        "dist",
        "htmlcov",
        "toolbox",
    ],
    "visible_dirs": [
        "backend",
        "frontend",
        "docs",
        "scripts",
        "tests",
    ],
    "ignored_extensions": [
        ".pyc",
        ".pyo",
        ".pyd",
        ".pdf",
        ".log",
        ".tmp",
        ".txt",
    ],
    "visible_extensions": [],
    "ignored_files": [
        "caminhos.txt",
        "tree_focada.txt",
        "programa.c",
    ],
    "visible_files": [
        ".gitignore",
        ".python-version",
        "Dockerfile",
        "docker-compose.yml",
        "pyproject.toml",
        "requirements.txt",
        "uv.lock",
        "README.md",
    ],
}
