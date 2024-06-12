from setuptools import setup, find_packages


# read the contents of your README file
from os import path

THIS_DIRECTORY = path.abspath(path.dirname(__file__))
with open(path.join(THIS_DIRECTORY, "README.md")) as f:
    LONG_DESC = f.read()

setup(
    name="codal-tsetmc",
    version="1.4.5",
    description="Data Downloader for stock market and financial statement",
    url="http://github.com/mohsenebrahimyir/codal-tsetmc",
    author="Mohsen Ebrahimi",
    author_email="mohsenebrahimy.ir@gmail.com",
    license="MIT",
    long_description=LONG_DESC,
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=[
        "codal_tsetmc",
        "codal_tsetmc.download",
        "codal_tsetmc.models",
        "codal_tsetmc.config",
        "codal_tsetmc.tools",
    ],
    install_requires=[
        "wheel",
        "pandas",
        "sqlalchemy",
        "psycopg2",
        "requests",
        "jdatetime",
        "nest-asyncio"
    ],
    zip_safe=False,
    python_requires=">=3.8",
    scripts=["bin/ct-get", "bin/ct-get.bat"],
    include_package_data=True,
)
