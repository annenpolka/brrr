# Reduced excerpt of _read_pyproject on failing_ref
# setuptools/tests/integration/test_pip_install_sdist.py

def _read_pyproject(archive):
    contents = (
        archive.get_content(member)
        for member in archive
        if os.path.basename(archive.get_name(member)) == "pyproject.toml"
    )
    return next(contents, "")
