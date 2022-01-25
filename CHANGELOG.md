# Changelog

This log documents all public API breaking backwards incompatible changes.

## 2.2.0 - to be released

[#32](https://github.com/crypto-org-chain/chainlibpy/issues/32) Add test environment\
Require Python >= 3.8\
[#25](https://github.com/crypto-org-chain/chainlibpy/issues/25) Add mainnet and testnet-croeseid-4 network configurations\
[#24](https://github.com/crypto-org-chain/chainlibpy/pull/24) Fix unable to use secure gRPC channel to interact with chain

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
