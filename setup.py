#  MIT License Copyright (c) 2020. Houfu Ang

from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='pdpc-decisions',
    version='1.1.1',
    description='Tools to extract and compile enforcement '
                'decisions from the Singapore Personal Data Protection Commission',
    author='Ang Houfu ',
    author_email='houfu@outlook.sg',
    url='https://github.com/houfu/pdpc-decisions/',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['pdpc_decisions'],
    install_requires=['Click', 'selenium', 'beautifulsoup4', 'pdfminer.six', 'html5lib',
                      'requests', 'spacy'],
    classifiers=[
        'Development Status :: 5 - Production/Stable'
    ],
    python_requires='>=3.7',
)
