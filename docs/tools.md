# Additional Tools

## `gold-mine-auditor`: predicts what `gold-mine` may be good at identifying

*NOTE: this tool is part of the `gold-mine-ui` python package, which
is distributed separately from the `gold-mine` python package``

The `gold-mine` approach will work better at differentiating between
some protocols vs others.  `gold-mine-auditor`, when given a training
profile, attempts to predict which protocols will (hopefully) be
better predicted when compared with other traffic types.  To determine
this, use `gold-mine-auditor` to display, given a list of traffic
labels of interest.  The result will be a list of other protocols and
the similarity to them (with lower numbers being more similar and less
likely to be differentiated against, potentially producing false
positives).  Use the `-j` switch to output `JSON` formatted results.

Example:

    $ gold-mine-auditor -d mail -j training-profile.fsdb

    Similarity distance for mail from other types (lower is better):

      mail:       0.0
      web:        0.83
