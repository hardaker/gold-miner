``gold-miner``: analyzes unknown traffic
-----------------------------------------------

The ``gold-miner`` tool is the core of the package that takes a
training profile created using both gold-miner-trainer_ and
gold-miner-trainer-aggregator_ and uses it to try and predict an
unknown traffic source.

.. _gold-miner-trainer: goldminertrainer.html
.. _gold-miner-trainer-aggregator: goldminertraineraggregator.html

Example Invocation
^^^^^^^^^^^^^^^^^^^^

The following example command line processes a PCAP file containing
unknown data (*unknown.pcap*) using a training-profile created from
the gold-miner-trainer_ gold-miner-trainer-aggregator_ tools.  It
specifically looks for the `mail` label.  Note that multiple labels
can be passed to the `-g` flag in order to compare various values to
determine what the *best guess* might be.

::

   gold-miner -r unknown.pcap -p training-profile.fsdb -g mail

Example Output
^^^^^^^^^^^^^^^^

The output includes a bunch of columns in a tab-separated file (called
an FSDB_ file).  Example output may look like:

Interpreting Tab-Separated Value Output
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The output of this utility by default is a FSDB_ formatted dataset
containing (see below for turning on json output instead):


.. _FSDB: https://fsdb.readthedocs.io/

::

   #fsdb -F t timestamp:d identifier token confidence total:l
   1612276702.252115	(50, '10.0.3.2', '10.0.6.2')	email-client	0.019922011881270296	1
   1612276702.252115	(50, '10.0.3.2', '10.0.6.2')	email-server	0.09949107222576414	1
   1612276702.252115	(50, '10.0.3.2', '10.0.6.2')	https-client	0.1108216386959876	1
   1612276702.252115	(50, '10.0.3.2', '10.0.6.2')	https-server	0.0	1
   1612276702.252115	(50, '10.0.3.2', '10.0.6.2')	ftp-client	0.0	1
   1612276702.252115	(50, '10.0.3.2', '10.0.6.2')	ftp-server	0.0	1
   ...
   1612276796.641313	(50, '10.0.3.2', '10.0.6.2')	email-client	0.7168803043442527	1400
   1612276796.641313	(50, '10.0.3.2', '10.0.6.2')	email-server	0.21853768852005073	1400
   1612276796.641313	(50, '10.0.3.2', '10.0.6.2')	https-client	0.09337264365783604	1400
   1612276796.641313	(50, '10.0.3.2', '10.0.6.2')	https-server	0.3331007977800903	1400
   1612276796.641313	(50, '10.0.3.2', '10.0.6.2')	ftp-client	0.06126245747562031	1400
   1612276796.641313	(50, '10.0.3.2', '10.0.6.2')	ftp-server	0.16666655917372097	1400

The columns in question contain:

1. a packet timestamp
2. an identifier (5-tuple, 3-tuple or IPSec specific)
3. a token being searched for (eg: “mail”)
4. a confidence value 0-1
5. the packet counts seen per identifier so far

Example Graph
^^^^^^^^^^^^^^^^

The `multi-key-graph` tool that comes with the `multikeygraph` python
package can be used to graph the results:

::

   multi-key-graph -k token -c confidence -o graph.png gold-mine-output.fsdb

.. image:: ../tande-example/tande-example/b1f1fc5a469f926f506c1a1520b0f613f4ac2df146f4fba7b4e365bbbece6d15.test.0.png

This example graph shows that after a number of packets the
`email-client` label becomes the most likely prediction among the
options being graphed.

Selecting a sub-algorithm to use
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``gold-miner`` supports four different (sub-)algorithms for identifying
traffic:

-  comparison
-  comparison-wide
-  linear
-  lms

The following algorithms are available for use:

algorithm: comparison
^^^^^^^^^^^^^^^^^^^^^^

This is the default, and works best with entirely labeled traffic with
no unknown traffic expected. It works by comparing an unknown flow
against all known profiles to differentiate among the different types in
the training profile. Thus, it will not work when applied to a traffic
sample with an unprofiled traffic flow within it.

algorithm: linear
^^^^^^^^^^^^^^^^^^^^

The ``linear`` algorithm calculates the difference from a given flow vs
the training profile, regardless of what the other training flows use.
This may succeed at times when the ``comparison`` algorithm doesn’t,
especially in cases of unknown traffic being mixed in with the traffic
being prioritized.

algorithm: lms
^^^^^^^^^^^^^^^^^^^^^

The ``lms`` algorithm is similar to the ``linear`` algorithm, but uses
the common square of the difference instead of a linear distance. These
two algorithms usually perform closely together in performance but one
may be better than another.

algorithm: comparison-wide
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This is rarely the right algorithm to use, but is left in for the
moment. It may go away in the future.

JSON output
^^^^^^^^^^^

The ``gold-miner`` tool can also output a stream JSON records if that’s
easier to parse. Run ``gold-miner`` with ``-j`` to enable this
feature, or ``-J`` to output a flattened JSON output.

Command Line Arguments
^^^^^^^^^^^^^^^^^^^^^^

.. sphinx_argparse_cli::
   :module: apropos.goldminer.tools.goldminer
   :func: parse_args
   :hook:
   :prog: introduction
