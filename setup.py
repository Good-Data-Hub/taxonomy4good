# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

# The directory containing this file
HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# This call to setup() does all the work
setup(
    name="taxonomy4good",
    version="1.1.0",
    description="Sustainability lexicon providing both listed and non-listed taxonomies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://taxonomy4good.readthedocs.io/",
    author="Hloni Dichabe, Emily Luskind, Zwelakhe Gile, Luvo Gila, Myles Francis, Haroune Aaffoute, Anis Bouhamadouche",
    author_email="gooddatahub@gmail.com, hlonidichabe@gmail.com, luskinde@gmail.com, zwelakhegila@gmail.com, "
                 "luvogila@gmail.com, mxfrancis43@gmail.com, hrna2011@gmail.com,anis.bouhamadouche@outlook.com",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Legal Industry",
        "Intended Audience :: Other Audience",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent"
    ],
    packages=["taxonomy4good", "images"],
    include_package_data=True,
    package_data={'taxonomy4good': ['taxonomies/*.xlsx'], 'images': ['*.svg', '*.png']},
    install_requires=["numpy", "pandas", "xlrd==1.2.0"]
)