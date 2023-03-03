import setuptools
from pathlib import Path

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    # package info
    name="pykneer",
    version="0.0.6.3",
    author="Serena Bonaretti",
    author_email="serena.bonaretti.research@gmail.edu",
    description="pyKNEEr: An image analysis workflow for open and reproducible research on femoral knee cartilage",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://sbonaretti.github.io/pyKNEEr/",
    license="GNU General Public License v3 (GPLv3)",
    # including requirements (dependencies)
    install_requires=[
        l.strip() for l in
        Path('requirements.txt').read_text('utf-8').splitlines()
    ],
    # including parameterFolder and Elastix package
    packages=setuptools.find_packages(),
    package_data={'pykneer': ['parameterFiles/*.txt', 'elastix/Darwin/', 'elastix/Linux/','elastix/Windows/']
    },
    include_package_data=True,
    # including tests
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    # python version, license, and OS
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)
