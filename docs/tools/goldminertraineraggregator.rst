``gold-miner-trainer-aggregator``: builds a complete training profile
---------------------------------------------------------------------

The ``gold-miner-trainer-aggregator`` tool takes a number of
single-file profiles created by ``gold-miner-trainer``, along with
labels for them, and combines them into a single profile that can be
later fed to ``gold-miner``.

Example Invocation
^^^^^^^^^^^^^^^^^^^^

This example invokes `gold-mine-trainer-aggregator` to combine two
profiles created from gold-mine-trainer_ that contains web traffic
and email traffic.  The output combined profile is stored in
`training-profile.fsdb`.

.. _gold-miner-trainer: goldminertrainer.html

::

   gold-miner-trainer-aggregator -o training-profile.fsdb \
   web web_traffic.fsdb \
   mail mail_traffic.fsdb


Next Steps
^^^^^^^^^^

Once an aggregate training profile has been constructed, the results
can be passed to the gold-miner_ tool to attempt detection
of unknown traffic types.

.. _gold-miner: goldminer.html


Command Line Arguments
^^^^^^^^^^^^^^^^^^^^^^

.. sphinx_argparse_cli::
   :module: apropos.goldminer.tools.aggregator
   :func: parse_args
   :hook:
   :prog: introduction
