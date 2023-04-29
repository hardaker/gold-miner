``gold-miner-trainer-aggregator``: builds a complete training profile
---------------------------------------------------------------------

The ``gold-miner-trainer-aggregator`` tool takes a number of
single-file profiles created by ``gold-miner-trainer``, along with
labels for them, and combines them into a single profile that can be
later fed to ``gold-miner``.

Command Line Arguments
^^^^^^^^^^^^^^^^^^^^^^

.. sphinx_argparse_cli::
   :module: apropos.goldminer.tools.aggregator
   :func: parse_args
   :hook:
   :prog: introduction
