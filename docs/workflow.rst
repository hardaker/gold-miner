Using gold-miner
================

To use the ``gold-miner`` suite to attempt classification of unknown
traffic, the following steps should be done in turn:

1. Analyze a set of labeled training pcaps containing known, encrypted
   protocol traffic using gold-miner-trainer_
2. Combining those individual training results into a single, aggregated
   *training profile* by using gold-miner-trainer-aggregator_.
3. Use the gold-miner_ tools with the training profile to analyze
   unknown traffic in a PCAP or on an interface.

.. _gold-miner-trainer: tools/goldminertrainer.html
.. _gold-miner-trainer-aggregator: tools/goldminertraineraggregator.html
.. _gold-miner: tools/goldminer.html

The steps below describe this process at a higher level, and the
individual tools pages above provide greater detail about how each of
the tools work.

Note that all of these steps can be executed in automated fashion by
using the `Test and Evaluation Suite <tande>`_, which takes a a YAML
configuration file, creates a profile, analyzes the data for accuracy
and produces an HTML report. (an `example report`_ is available to see
what the output looks like). The `Test and Evaluation Suite <tande>`_
tool may be easier to start with instead of running each of these
steps by hand.

.. _example report: tande-example/index.html

Also see the `Additional Tools <tools>`__ document that describes
additional useful tools that are distributed with the ``gold-miner``
package.

Steps to Classify Unknown Traffic Samples
=========================================

The process for using the rapid classifier involves *Generating
individual training profiles* that measures a sample of labeled traffic
to build a profile of what each type of traffic looks like. The results
of each measurement needs to be *combined into a resulting single
profile of all traffic*. After these steps are completed, the resulting
training profile can be used to analyze an unknown traffic stream to see
how well it may match a known profile.

1. Generating individual training profiles
------------------------------------------

To generate individual training profiles based on each type of known,
labeled datasets use the ``gold-miner-trainer`` command. It can analyze
any number of pcaps and generate a starting statistical dataset to be
used in later steps. [Hint: Use an output filename that reflects the
type of data being analyzed.] Example usage:

::

   gold-miner-trainer -T -o web_traffic.fsdb web_traffic.pcap
   gold-miner-trainer -T -o mail_traffic.fsdb mail_traffic.pcap

In these examples, the ``web_traffic.pcap`` file is analyzed and a
``web_traffic.fsdb`` training profile file is produced. A similar
example is shown for (e)mail traffic.

For further information see the gold-miner-trainer_ tool documentation.

2. Combine individual training profiles together
------------------------------------------------

Once the multiple individual training sets are created, they must be
merged before giving them to ``gold-miner`` below. To merge them, use
``gold-miner-trainer-aggregator`` with label/file pairs to create an
aggregated ``training-profile.fsdb``:

::

   gold-miner-trainer-aggregator -o training-profile.fsdb \
   web web_traffic.fsdb \
   mail mail_traffic.fsdb

Note that the arguments to the script include a repeated set of pairs of
a generic word as a label (e.g. ``web``) and the individual training
profile for it (e.g. ``web_traffic.fsdb``).

For further information see the gold-miner-trainer-aggregator_ tool documentation.

3. Analyzing an unknown traffic source
--------------------------------------

Now that we have trained parameters, we can analyze an existing pcap
file or watch an interface for traffic of interest. The output will be a
string of FSDB (tab separated) data representing confidence values. We
assume we have a protocol of interest matching one of the profile names
in the training file (“mail” in the example below).

::

   gold-miner -r unknown.pcap -p training-profile.fsdb -g mail

This tools, by default, generates a tab-separated list of output data
that can be easily parsed.  A confidence value is given per traffic
type being detected that can be compared against other types to
determine what the traffic most likely might be.

For further information see the gold-miner_ tool documentation, which
also goes into greater detail about the output, describes the other
output format options, along with specifying other sub-algorithms to
select between.
