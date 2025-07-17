from setuptools import setup, find_packages

# read the contents of your README file
from os import path

THIS_DIRECTORY = path.abspath(path.dirname(__file__))
with open(path.join(THIS_DIRECTORY, "README.md"), encoding="utf-8") as f:
    LONG_DESC = f.read()

setup(
    name="codal-tsetmc",
    version="3.0.5",
    description="Data Downloader for Codal and Tehran stock market",
    url="http://github.com/mohsenebrahimyir/codal-tsetmc",
    author="Mohsen Ebrahimi",
    author_email="mohsenebrahimy.ir@gmail.com",
    license="MIT",
    long_description=LONG_DESC,
    long_description_content_type="text/markdown",
    keywords="stock, tsetmc, codal, iran, finance, crawler",
    package_dir={"": "src"},
    packages=find_packages(
        where="src",
        include=["codal_tsetmc*"],
    ),
    install_requires=[
        "pandas>=2.2",
        "sqlalchemy>=2.0",
        "requests>=2.25",
        "jdatetime>=5.0",
        "nest-asyncio>=1.6",
        "aiohttp>=3.10",
        "beautifulsoup4>=4.11",
        "html5lib>=1.1",
        "lxml>=5.3",
        "PyYAML>=6.0",
        "python-dotenv>=1.0",
        "python-decouple>=3.8",
    ],
    zip_safe=False,
    python_requires=">=3.12",
    scripts=["bin/ct-get", "bin/ct-get.bat"],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
