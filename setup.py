import setuptools 

with open("README.md", "rb") as fh:
    long_description = fh.read()


setuptools.setup(
    name="vix",
    version="1.00",
    author="Ruitao Wang",
    author_email="wang.ruitao@outlook.com",
    description="Vix Calculation ",
    # long_description=long_description,
    # long_description_content_type="text/markdown",
    # packages=setuptools.find_packages(
    #     exclude=["*.git", "__pycache__/", ".vscode/"]
    # ),
    python_requires=">=3",
    install_requires=[
        "numpy",
        "pandas",
        "sqlalchemy",
        "scipy"
    ]
)