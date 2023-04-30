Automated test and evaluation
=============================

**IMPORTANT: this page describes the `gold-mine-tande` tool that is
part of the ``gold-miner-ui`` python package, which is distributed
separately from the ``gold-miner`` python package**

The ``gold-miner-tande`` tool is designed to take a series of labeled
pcap files listed in a YAML configuration file and:

1. take one listed set of PCAP files as a training set and use it to
   create a gold-miner training profile
2. take a second list of labeled files to evaluate the effectiveness
   of traffic detection using the profile and the ``gold-miner`` tool
3. output an html (and markdown) report that shows the results of these
   training and testing phases

*Note: ``gold-miner-tande`` tool requires ``pandoc`` to be installed
on the system.*

*Example output:* see the Example_ section below, and the `example
report`_ page.

YAML configuration overview
---------------------------

The ``gold-miner-tande`` tool is driven by a YAML configuration file
that is divided into parts:

1. a general configuration section
2. a *train* section
3. a *test* section

The YAML configuration structure looks like the following
example block. Each configuration section is further discussed below.

.. code:: yaml

   ---

   # number of (hyper)cores to use
   processes: 32

   # where to store the output results/images
   output_directory: where-output-should-go

   # a temporary directory to store filtered pcaps in
   tmp_dir: directory-to-store-temporary-files

   # details about the pcaps to use for training
   train:
     files:
       # ...

   # details about the pcaps to use for testing
   test:
     files:
       # ...

Training
--------

The *train* section should contain a list of pcap files to use for
training, along with their appropriate labels. These files **must not
contain multiple types of data** (i.e., multiple labels).

Note that both the ``train``\ ing and ``test``\ ing section entries can take a
``filter`` token that will apply a standard PCAP filter for selecting or
removing certain elements from supplied packet traces. Do note that
these ``filter`` sections will create secondary (filtered) PCAPs inside
the temporary directory that is specified by the ``tmp_dir`` directive.

The results of the training will produce a *training-profile.fsdb*
file in the output directory.

.. code:: yaml

   train:
     files:
       - file: /path/to/something.pcap
         label: something
       - file: /path/to/other.pcap
         label: other
       - file: /path/to/toomuch.pcap
         label: filtered
         filter: not icmp and not arp

Testing
-------

The ``test`` sections works similar to the ``train`` section,
containing a list of PCAP ``file``\ s and associated ``label``\ s, to
use for determining when the ``gold-miner`` classifier gets a label
prediction of unknown traffic correct or incorrect.

.. code:: yaml

   test:
     files:
       - file: /path/to/something2.pcap
         label: something
       - file: /path/to/other2.pcap
         label: other
       - file: /path/to/toomuch2.pcap
         label: filtered
         filter: not icmp and not arp

Optional attributes
-------------------

The YAML configuration tokens can include additional directives that
affect the processing of the ``gold-miner-tande`` run. Be sure to read
the 'Inheritance and Overrides'_ section below, which discusses how to
apply these at different levels of the configuration hierarchy.

packet_count N
~~~~~~~~~~~~~~

This will limit the number of packets to read in a **train* and/or *test*
file

.. code:: yaml

   packet_count: 10000

skip_packets N
^^^^^^^^^^^^^^

This will cause the ``gold-miner-tande`` to skip the first N packets of
the pcap before processing it for the given section (*train* or *test*).

.. code:: yaml

   packet_count: 10000


Inheritance and Overrides
-------------------------

A number of the directives that affect processing of individual
entries can be placed at the top level in the YAML file, underneath
just the ``test`` or ``train`` sections, or next to each file
itself. Lower level directives will override upper level directives.

As an example, consider the case where you want to read 10000 packets
from every pcap in the ``train`` section, 20000 in the ``test`` section,
except for one file in particular that isn’t that long. And for the
``test`` files you actually want to read from the same files as
training, but skip the packets that were used for training itself.

The resulting YAML might look like:

.. code:: yaml

   # by default, read only 20,000 packets
   packet_count: 20000
   train:
     # for training, read 10,000 though
     packet_count: 10000
     files:
     - file: one.pcap
       label: one
     - file: two.pcap
       label: two
       # over-ride the 10,000 packet count to just 500
       packet_count: 500
   test:
     # for testing, skip the first 10,000
     # (and evaluate the remaining 20,000)
     skip_packets: 10000
     files:
     - file: one.pcap
       label: one
     - file: two.pcap
       label: two
       # over-ride the 10,000 packet and skip counts to just 500
       packet_count: 500
       skip_packets: 500

Algorithm selection
---------------------

There are actually 4 (sub)algorithms that the ``gold-miner`` suite
supports. The algorithm to use can be specified with a top level
``algorithm`` directive:

-  comparison
-  comparison-wide
-  linear
-  lms

There is additionally a special algorithm that ``gold-miner-tande``
supports called ``all``, which will run the train/test suite repeatedly
– once for each algorithm and generate a resulting comparison summary.

See the `gold-miner algorithm documentation <tools/goldminer.html>`__
for further details on selecting the best algorithm for your use case.

Output
------

The output of the ``gold-miner-tande`` tool produces an entire
directory of files in the directory specified by the
`output_directory` token. An ``index.html`` file is built at the top
of the directory to allow easy browsing and understanding of all of
the results.

Example
-------

An `example report`_ shows what the results look like for a simple
test case that involved testing client and server traffic from three
different traffic types over an IPsec tunnel.  The `example
configuration`_ shows the YAML configuration file given to the
`gold-mine-tande` application.

.. _example report: tande-example/index.html
.. _example configuration: tande-example/tande.yml
