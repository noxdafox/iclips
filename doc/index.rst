.. iCLIPS documentation master file, created by
   sphinx-quickstart on Wed Dec 27 14:39:12 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

iCLIPS Documentation
====================

.. only:: html

   :Release: |release|
   :Date: |today|

iCLIPS provides an interactive shell for the 'C' Language Integrated Production System (`CLIPS <http://www.clipsrules.net/>`_).

.. image:: ../example.png

Features:

* A `Jupyter <http://jupyter.org/>`_ kernel to work with CLIPS code in Jupyter
  notebooks and other interactive frontends.

* Input history.

* Tab completion.

* Syntax highlighting via `Pygments <http://pygments.org/>`_.

* Parenthesis matching.

* Possibility to integrate Python code bringing into CLIPS the Python libraries and eco-system via `CLIPSPy <https://github.com/noxdafox/clipspy>`_.


Embedding Python code
---------------------

Via the ``%% define-python-function`` magic command it is possible to integrate Python code within the CLIPS environment.

.. code:: python

    In [1]: %% define-python-function
    DefPyFunction mode: return twice to define the inserted function within CLIPS.

    In [2]: import re
          : import requests
          :
          : def active_content(url):
          :     """Return TRUE if the website at the given URL contains active content."""
          :     try:
          :         response = requests.get(url)
          :         response.raise_for_status()
          :     except Exception:
          :         return clips.Symbol('ERROR')
          :
          :     if re.search(r'</script>', response.content.decode()):
          :         return True
          :     else:
          :         return False
          :
          :

    In [3]: (active_content "http://www.example.com")
    FALSE
    In [4]: (active_content "http://www.clipsrules.net")
    TRUE

The `define-python-function` defines the first top level function found within the entered code. For more complex definitions see the `python` magic command.

Executing Python code
---------------------

The ``%% python`` magic command allows to execute Python code within the console. The code will be executed after two consecutive new lines.

The `CLIPSPy Environment <https://clipspy.readthedocs.io/en/latest/clips.html#clips.environment.Environment>`_ used within the console is accessible via the `CLIPS` global variable.

In the following example, the conflict resolution strategy of the inference engine is changed via the programmatic API.

.. code:: python

    In [1]: %% python
    Python mode: return twice to execute the inserted code.

    In [2]: CLIPS.strategy = clips.Strategy.COMPLEXITY
          :
          :

    In [3]: (get-strategy)
    complexity

An object method is defined within the CLIPSPy Environment.

.. code:: python

    In [1]: %% python
    Python mode: return twice to execute the inserted code.

    In [2]: class Foo:
          :     bar = 0
          :
          :     def baz(self, value):
          :         self.bar += value
          :
          :         return self.bar
          :
          : foo = Foo()
          :
          : CLIPS.define_function(foo.baz)
          :
          :

    In [3]: (baz 1)
    1
    In [4]: (baz 1)
    2
    In [5]: (baz 1)
    3

.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
