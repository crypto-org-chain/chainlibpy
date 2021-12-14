# Changelog

This log documents all public API breaking backwards incompatible changes.

*Dec 7, 2021*

## 2.1.0

[#28](https://github.com/crypto-org-chain/chainlibpy/pull/21) Migrate to gRPC which supports `chain-main` using `Cosmos SDK` version v0.43/0.44

## 2.0.0

- Added
  - `timeout_height` argument in transaction
  - amino types including `Coin`, `StdFee`, `StdSignDoc` and many transaction messages
- simplified the transaction arguments
- require Python >= 3.7

## 1.0.0

- Added
  - Code for address generation and transaction signing
