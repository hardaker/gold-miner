``gold-miner``: analyzes unknown traffic
-----------------------------------------------

The ``gold-miner`` tool is the core of the package that takes a
training profile created using both gold-miner-trainer_ and
gold-miner-trainer-aggregator_ and uses it to try and predict an
unknown traffic source.

.. _gold-miner-trainer: goldminertrainer.html
.. _gold-miner-trainer-aggregator: goldminertraineraggregator.html

Command Line Arguments
^^^^^^^^^^^^^^^^^^^^^^

.. sphinx_argparse_cli::
   :module: apropos.goldminer.tools.goldminer
   :func: parse_args
   :hook:
   :prog: introduction
