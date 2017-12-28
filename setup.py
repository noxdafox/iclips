import os
import subprocess

from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def package_version():
    """Get the package version via Git Tag."""
    version_path = os.path.join(os.path.dirname(__file__), 'version.py')

    version = read_version(version_path)
    write_version(version_path, version)

    return version


def read_version(path):
    try:
        return subprocess.check_output(('git', 'describe')).rstrip().decode()
    except subprocess.CalledProcessError:
        with open(path) as version_file:
            version_string = version_file.read().split('=')[-1]
            return version_string.strip().replace('"', '')


def write_version(path, version):
    msg = '"""Versioning controlled via Git Tag, check setup.py"""'
    with open(path, 'w') as version_file:
        version_file.write(msg + os.linesep + os.linesep +
                           '__version__ = "{}"'.format(version) +
                           os.linesep)


setup(
    name='iCLIPS',
    version="{}".format(package_version()),
    author='Matteo Cafasso',
    author_email='noxdafox@gmail.com',
    description=('CLIPS Jupyter console'),
    long_description=read('README.rst'),
    license='GPL',
    keywords='clips expert-system jupyter',
    install_requires=[
        'clipspy',
        'jupyter-console'
    ],
    data_files=[
        (os.path.join('share/jupyter/kernels/clips'), ['kernel.json'])
    ],
    packages=find_packages(),
    entry_points={
        'pygments.lexers': [
            'clips=iclips.clips_pygments:CLIPSLexer'
        ]
    },
    url="https://github.com/noxdafox/iclips",
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: " +
        "GNU General Public License v3 or later (GPLv3+)"
    ]
)
