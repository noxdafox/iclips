iCLIPS
======

Jupyter Kernel for CLIPS_

:Source: https://github.com/noxdafox/iclips
:Documentation: https://iclips.readthedocs.io
:Download: https://pypi.python.org/pypi/iclips

|docs badge|

.. |docs badge| image:: https://readthedocs.org/projects/iclips/badge/?version=latest
   :target: http://iclips.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://iclips.readthedocs.io/en/latest/_images/example.png

Installation
------------

.. code:: bash

    $ pip install iclips

Usage
-----

.. code:: bash

    $ jupyter console --kernel clips

.. _CLIPS: http://www.clipsrules.net/

Docker Container
----------------

The container ships a Jupyter Notebook with CLIPS support.

.. code:: bash

    $ docker build -t iclips .

    # Run Jupyter Console
    $ docker run -it iclips jupyter console --kernel clips

    # Run Jupyter Notebook
    $ docker run -it -p 8888:8888 iclips
