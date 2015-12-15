from distutils.core import setup

setup(
    name = 'uchicagoldrrecords',
    version = '1.0.0',
    author = "Brian Balsamo",
    author_email = "balsamo@uchicago.edu",
    packages = ['uchicagoldrrecords'],
    description = "A set of classes for creating new accession reocrds for the repository",
    keywords = ["uchicago","repository","file-level","processing"],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "Operating System :: Unix",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    install_requires = [])
