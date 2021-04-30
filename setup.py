import os
import codecs
from setuptools import setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding="utf-8").read()


setup(
    name="pytest-relative-order",
    author="Starfish Storage Corporation",
    author_email="rkujawa@starfishstorage.com",
    maintainer="Radek Kujawa",
    maintainer_email="rkujawa@starfishstorage.com",
    license="MIT",
    url="https://github.com/StarfishStorage/pytest-relative-order",
    description='a pytest plugin that sorts tests using "before" and "after" markers',
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    py_modules=["pytest_relative_order"],
    python_requires=">=3.5",
    install_requires=["pytest>=3.5.0"],
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
    entry_points={"pytest11": ["relative_order = pytest_relative_order"]},
)
