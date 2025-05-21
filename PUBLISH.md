# Publishing update to Pypi

    python3 -m venv venv
    source venv/bin/activate

    pip install --upgrade pip setuptools wheel build
    python -m build
    pip install twine
    twine upload dist/*

    # For TestPyPI:
    twine upload --repository testpypi dist/*