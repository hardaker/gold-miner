import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gold-miner",
    version="1.1",
    author="Wes Hardaker",
    author_email="opensource@hardakers.net",
    description="A encrypted tunnel identification research package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/isi-apropos/gold-miner",
    packages=setuptools.find_packages(),
    entry_points={
        "console_scripts": [
            "gold-miner = apropos.goldminer.tools.goldminer:main",
            "gold-miner-trainer = apropos.goldminer.tools.trainer:main",
            "gold-miner-trainer-aggregator = apropos.goldminer.tools.aggregator:main",
            "gold-miner-smelter = apropos.goldminer.tools.smelter:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "pyfsdb",
        "numpy",
        "dpkt",
        "rich",
        "pyaml",
    ],
    python_requires=">=3.6",
    test_suite="nose.collector",
    tests_require=["nose"],
)
