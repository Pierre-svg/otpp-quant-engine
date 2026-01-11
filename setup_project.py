import os

# The professional structure we designed for OTPP
structure = [
    "config/",
    "data/raw/",
    "qsr_system/",
    "qsr_system/data/",
    "qsr_system/strategies/",
    "qsr_system/execution/",
    "qsr_system/analytics/",
    "tests/",
    "notebooks/",
    ".github/workflows/"
]

files = {
    "README.md": "# OTPP Quant Engine\n\nA modular systematic trading system.",
    "requirements.txt": "pandas\nnumpy\npytest",
    ".gitignore": "__pycache__/\n*.pyc\nvenv/\n.env\n.DS_Store\ndata/",
    "main.py": "# Entry point for the trading engine\n\nif __name__ == '__main__':\n    print('System Initialized')",
    "config/settings.py": "# Global configurations\nRISK_LIMIT = 0.02",
    "qsr_system/__init__.py": "",
    "qsr_system/strategies/base.py": "from abc import ABC, abstractmethod\n\nclass Strategy(ABC):\n    @abstractmethod\n    def generate_signal(self, data):\n        pass",
    "tests/test_strategies.py": "import pytest\n\ndef test_sanity():\n    assert True"
}

# 1. Create Directories
for folder in structure:
    os.makedirs(folder, exist_ok=True)

# 2. Create Files
for filepath, content in files.items():
    with open(filepath, "w") as f:
        f.write(content)

# 3. Create empty __init__.py files (makes folders 'packages')
init_folders = [
    "qsr_system/data/", "qsr_system/strategies/", 
    "qsr_system/execution/", "qsr_system/analytics/"
]
for folder in init_folders:
    with open(os.path.join(folder, "__init__.py"), "w") as f:
        pass

print("✅ Success! Your Quant Engineering folder structure is ready.")