# Additional Tools

## `gold-miner-auditor`: predicts what `gold-miner` may be good at identifying

*NOTE: this tool is part of the `gold-miner-ui` python package, which
is distributed separately from the `gold-miner` python package``

The `gold-miner` approach will work better at differentiating between
some protocols vs others.  `gold-miner-auditor`, when given a training
profile, attempts to predict which protocols will (hopefully) be
better predicted when compared with other traffic types.  To determine
this, use `gold-miner-auditor` to display, given a list of traffic
labels of interest.  The result will be a list of other protocols and
the similarity to them (with lower numbers being more similar and less
likely to be differentiated against, potentially producing false
positives).  Use the `-j` switch to output `JSON` formatted results.

Example:

    $ gold-miner-auditor -d mail -j training-profile.fsdb

    Similarity distance for mail from other types (lower is better):

      mail:       0.0
      web:        0.83
