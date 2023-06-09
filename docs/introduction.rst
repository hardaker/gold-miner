About
================

The ``gold-miner`` tool suite applies a simple statistical analysis of
labeled traffic samples to produce a profile which can then be used to
fingerprint an unknown traffic sample with a goal of rapidly identifying
its contents without requiring deep packet inspection. Specifically,
``gold-miner`` is designed to prioritize calculation speed over higher
levels of accuracy that more complex analysis techniques may produce.

To get started with gold-miner, we suggest reading the `Gold Mine
Workflow <workflow>`__ document that describes in greater detail how to
use the tools, and the `Gold Mine Test and Evaluation Tool <tande>`__
describes a tool that takes a *YAML* configuration file to analyze a set
of traffic samples and produce a detailed report about how well the
``gold-miner`` tool properly identifies those samples (which includes
generated
`ROC <https://en.wikipedia.org/wiki/Receiver_operating_characteristic>`__
curves).

Installation
=====================

You can install ``gold-miner`` from pypi or from a ``git clone`` of
the repository_:

.. _repository: https://github.com/hardaker/gold-miner

Installing from pypi
--------------------

You can install gold-miner using pip:

::

   pip install --user --upgrade gold-miner

*Optionally* install the UI tools that provide a number of additional
tools (that in turn require pulling in a larger number of python
prerequisite packages):

::

   pip install --user --upgrade gold-miner-ui

Installing from the source tree
-------------------------------

Clone the repository:

::

   git clone https://github.com/hardaker/gold-miner.git

Start with installing the requirements:

::

   pip3 install --user --upgrade -r requirements.txt

Start with installing the package itself:

::

   python3 setup.py install --user --force


*optionally repeat this process for the gold-miner-ui_ package*

.. _gold-miner-ui: https://github.com/hardaker/gold-miner-ui
