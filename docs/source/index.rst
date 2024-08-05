.. Smokescreen documentation master file, created by
   sphinx-quickstart on Thu Aug  1 17:44:01 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

********************************************************************
**Smokescreen** -- DESC Library for concealing cosmological results
********************************************************************

.. image:: _static/Smokescreen_Banner.png
   :align: center

`Smokescreen <https://github.com/LSSTDESC/Smokescreen>`_ (currently under development) contains the modules for data concealment (blinding) at the following levels of the analysis:

* Data-vector measurements

* Posterior distribution [not yet developed]

* (TBC) Catalogues

.. attention::
    The term "blinding" is used in the context of data concealment for scientific analysis. We understand this is an outdated term and we are working to update it to a more appropriate term. If you have any suggestions, please let us know.

Smokescreen's  data-vector blinding methodis based on the `Muir et al. (2021) <https://arxiv.org/abs/1911.05929>`_ and was developed to be used as part of DESC measurements and inference pipelines such as `TXPipe <https://github.com/LSSTDESC/TXPipe>`_ .

.. toctree::
   :maxdepth: 2
   :caption: Contents

   installation
   usage
   reference


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
