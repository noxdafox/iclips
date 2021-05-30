import os
import fileinput

from setuptools import find_packages, setup


CWD = os.path.dirname(__file__)


def package_version():
    module_path = os.path.join(CWD, 'iclips', '__init__.py')
    for line in fileinput.input(module_path):
        if line.startswith('__version__'):
            return line.split('=')[-1].strip().replace('\'', '')


setup(
    name='iCLIPS',
    version=package_version(),
    author='Matteo Cafasso',
    author_email='noxdafox@gmail.com',
    description=('CLIPS Jupyter console'),
    long_description=open(os.path.join(CWD, 'README.rst')).read(),
    license='GPL',
    keywords='clips expert-system jupyter',
    install_requires=[
        'regex',
        'clipspy >= 1.0.0',
        'jupyter-console'
    ],
    data_files=[
        (os.path.join('share/jupyter/kernels/clips'), ['kernel.json']),
        (os.path.join('share/jupyter/kernels/clips'), ['kernel.js']),
        (os.path.join('share/jupyter/kernels/clips'), ['kernel.css'])
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
