``gold-miner-trainer``: profiles a single PCAP training file
------------------------------------------------------------

The ``gold-miner-trainer`` tool takes a PCAP file as an input
and produces a profile for the single dataset.  The PCAP file being
passed into it **must** be of a single traffic type to be profiled.
It can take an optional *tcpdump* filter string to limit the traffic
that is taken as training data (such as in the example below where
*"esp and src 10.0.0.1"* limits the traffic to just IPsec traffic from
a particular source).

Example invocation:
^^^^^^^^^^^^^^^^^^^

::

   gold-miner-trainer -f "esp and src 10.0.0.1" -T -o web_traffic.fsdb web_traffic.pcap


Next Steps
^^^^^^^^^^

Once a number of training sets have been created, use the
gold-miner-trainer-aggregator_ tool to compile them all into a single
profile that can be passed to the gold-miner_ tool to attempt detection
of unknown traffic types.

.. _gold-miner-trainer-aggregator: goldminertraineraggregator.html
.. _gold-miner: goldminer.html

Command Line Arguments
^^^^^^^^^^^^^^^^^^^^^^

.. sphinx_argparse_cli::
   :module: apropos.goldminer.tools.trainer
   :func: parse_args
   :hook:
   :prog: introduction
