``gold-miner-trainer``: profiles a single PCAP training file
------------------------------------------------------------

The ``gold-miner-trainer`` tool takes a PCAP file as an input
and produces a profile for the single dataset.  The PCAP file being
passed into it **must** be of a single traffic type to be profiled.

Command Line Arguments
^^^^^^^^^^^^^^^^^^^^^^

.. sphinx_argparse_cli::
   :module: apropos.goldminer.tools.trainer
   :func: parse_args
   :hook:
   :prog: introduction
