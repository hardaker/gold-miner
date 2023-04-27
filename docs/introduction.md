# About gold-mine

The `gold-mine` tool suite applies a simple statistical analysis of
labeled traffic samples to produce a profile which can then be used to
fingerprint an unknown traffic sample with a goal of rapidly
identifying its contents without requiring deep packet inspection.
Specifically, `gold-mine` is designed to prioritize calculation speed
over higher levels of accuracy that more complex analysis techniques
may produce.

To get started with gold-mine, we suggest reading the
[Gold Mine Workflow](workflow)
document that describes in greater detail how to use
the tools, and the [Gold Mine Test and Evaluation Tool](tande)
describes a tool that takes a *YAML* configuration file to analyze a
set of traffic samples and produce a detailed report about how well
the `gold-mine` tool properly identifies those samples (which includes
generated
[ROC](https://en.wikipedia.org/wiki/Receiver_operating_characteristic)
curves).

# Installing gold-mine

## Installing the requirements

    pip3 install --user --upgrade -r requirements.txt

## Install the gold mine tools itself.

If you have release tar-ball, install it with pip:

    pip3 install --user --upgrade gold-mine-0.3.2.tar.gz

If you're installing from source, install it with the setup.py
manager:

    python3 setup.py install --user --force
