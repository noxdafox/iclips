import os

from setuptools import setup, find_packages


setup(
    name="ICLIPS",
    version="0.0.1",
    author="Matteo Cafasso",
    author_email="noxdafox@gmail.com",
    description=("CLIPS Jupyter console"),
    license="GPL",
    keywords="clips expert-system jupyter",
    install_requires=["jupyter-console"],
    data_files=[
        (os.path.join('share', 'jupyter', 'kernels', 'clips'), 'kernel.json')
    ],
    packages=find_packages(exclude=["test"]),
    entry_points={
        'pygments.lexers': [
            'clips=iclips.clips_pygments:CLIPSLexer'
        ]
    }
)
