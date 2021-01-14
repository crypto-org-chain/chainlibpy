import pathlib

from setuptools import find_packages, setup

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")


# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name="chainlibpy",
    version="1.0.0",
    description="Tools for Crypto.com wallet management and offline transaction signing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/crypto-com/chainlibpy",
    author="Linfeng.Yuan",
    author_email="linfeng@crypto.com",
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="CRO, blockchain, signature, crypto.com",
    packages=find_packages(),
    python_requires=">=3.6, <4",
    install_requires=[
        "ecdsa>=0.14.0, <0.17.0",
        "bech32~=1.1.0",
        "mnemonic>=0.19, <0.20",
        "hdwallets~=0.1.0",
    ],
    extras_require={
        "test": ["pytest", "pytest-cov", "pytest-randomly"],
    },
    project_urls={
        "Bug Reports": "https://github.com/crypto-com/chainlibpy/issues",
        "Funding": "https://donate.pypi.org",
        "Say Thanks!": "https://github.com/hukkinj1/cosmospy",
        "Source": "https://github.com/crypto-com/chainlibpy",
    },
)
