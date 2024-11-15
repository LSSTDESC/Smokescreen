Installation
============

Regular Installation
--------------------

.. note::
    If you have both `Firecrown <https://github.com/LSSTDESC/firecrown>`_ and `pyccl <https://github.com/LSSTDESC/CCL>`_ installed in your environment, you can skip the installation of the dependencies in the ``environment.yml`` file and simply install ``Smokescreen`` using ``pip``:

    .. code-block:: bash

       python -m pip install smokescreen

If you do not have *Firecrown* and *pyccl* installed, you can install the dependencies using conda:

.. code-block:: bash

   conda install -c conda-forge lsstdesc-smokescreen


Developer Installation
-----------------------
If you want to install the package in development mode (or from source to get the latest version), Follow these instructions below.

Creating a new environment:
~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can create a new conda environment with the required packages using the `environment.yml` file:

.. code-block:: bash

   conda env create -f environment.yml

This will create a new environment called `desc_smokescreen` with the required packages. You can activate the environment with:

.. code-block:: bash

   conda activate desc_smokescreen

Using an existing environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to install the `Smokescreen` package in an existing environment, you can install it using:

.. code-block:: bash

   conda activate myenv
   conda env update --name myenv --file environment.yml --prune

After installing the dependencies from `environment.yml`, you can install the `Smokescreen` package using:

Normal Usage Installation
~~~~~~~~~~~~~~~~~~~~~~~~~

After installing the dependencies from ``environment.yml``, you can install the ``Smokescreen`` package using:

.. code-block:: bash

   python -m pip install [-e] .

The `-e` flag is optional and installs the package in editable mode (useful for development).

Testing the installation
------------------------

You can test the developer installation by running the unit tests from the Smokescreen directory:

.. code-block:: bash

   pytest .