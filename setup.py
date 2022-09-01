from setuptools import setup, find_packages


# read the contents of your README file
from os import path

THISDIRECTORY = path.abspath(path.dirname(__file__))
with open(path.join(THISDIRECTORY, "README.md")) as f:
    LONGDESC = f.read()

setup(
    name="codal-tsetmc",
    version="1.0.2",
    description="Data Downloader for stock market and finantial statement",
    url="http://github.com/mohsenebrahimyir/codal-tsetmc",
    author="Mohsen Ebrahimi",
    author_email="mohsenebrahimy.ir@gmail.com",
    license="MIT",
    long_description=LONGDESC,
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=[
        "codal_tsetmc",
        "codal_tsetmc.download",
        "codal_tsetmc.models",
        "codal_tsetmc.config",
    ],
    install_requires=[
        "wheel", "pandas", "sqlalchemy",
        "requests", "jdatetime", "tehran_stocks"
    ],
    zip_safe=False,
    python_requires=">=3.8",
    scripts=["bin/ct-get", "bin/ct-get.bat"],
    include_package_data=True,
)
