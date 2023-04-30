``gold-miner``: analyzes unknown traffic
-----------------------------------------------

The ``gold-miner`` tool is the core of the package that takes a
training profile created using both gold-miner-trainer_ and
gold-miner-trainer-aggregator_ and uses it to try and predict an
unknown traffic source.

.. _gold-miner-trainer: goldminertrainer.html
.. _gold-miner-trainer-aggregator: goldminertraineraggregator.html

Selecting a sub-algorithm to use
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``gold-miner`` supports four different (sub-)algorithms for identifying
traffic:

-  comparison
-  comparison-wide
-  linear
-  lms

See the `T&E algorithm documentation <tande>`__ for further details on
selecting the best algorithm for your use case.

Interpreting Tab-Separated Value Output
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The output of this utility by default is a
`FSDB <https://pyfsdb.readthedocs.io/en/latest/doc.html>`__ formatted
dataset containing (see below for turning on json output instead):

1. a packet timestamp
2. an identifier (5-tuple, 3-tuple or IPSec specific)
3. a token being searched for (eg: “mail”)
4. a confidence value 0-1
5. the packet counts seen per identifier so far

JSON output
~~~~~~~~~~~

The ``gold-miner`` tool can also output a stream json records if that’s
easier to parse. Run ``gold-miner`` with ``-j`` to enable this feature.

Command Line Arguments
^^^^^^^^^^^^^^^^^^^^^^

.. sphinx_argparse_cli::
   :module: apropos.goldminer.tools.goldminer
   :func: parse_args
   :hook:
   :prog: introduction
