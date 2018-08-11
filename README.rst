
========
entangle
========

This is the entangle application.


Minimum Requirements
====================

- Python 3.4


Optional Requirements
=====================

.. _pytest: http://pytest.org
.. _Sphinx: http://sphinx-doc.org

- `pytest`_ (for running the test suite)
- `Sphinx`_ (for generating documentation)


Basic Setup
===========

Install for the current user:

.. code-block:: console

    $ python setup.py install --user


Run the application:

.. code-block:: console

    $ python -m entangle --help


Run the test suite:

.. code-block:: console
   
    $ pytest test/


Build documentation:

.. code-block:: console

    $ sphinx-build -b html doc doc/_build/html


package:
python -m zipapp src -o entangle.pyz

run:
python -m entangle.pyz cmd2

python -m entangle -c ../etc/config.yml cmd2
python -m entangle -c ../etc/config.yml -s cmd2
python -m entangle -c ../etc/config.yml cmd3 -n PS_ETC_CW_BUDSTR
