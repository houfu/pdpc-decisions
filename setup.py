#  MIT License Copyright (c) 2020. Houfu Ang

from setuptools import setup

setup(
    name='pdpc-decisions',
    version='1.0c1',
    description='Tools to extract and compile enforcement '
                'decisions from the Singapore Personal Data Protection Commission',
    author='Ang Houfu  ',
    author_email='houfu@outlook.sg',
    url='https://github.com/houfu/pdpc-decisions/',
    packages=['pdpc_decisions'],
    install_requires=['Click', 'selenium', 'beautifulsoup4', 'pdfminer.six', 'html5lib',
                      'requests']
)
