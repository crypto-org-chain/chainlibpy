# Changelog

This log documents all public API breaking backwards incompatible changes.

## 2.2.0 - 17/May/2022

[#26](https://github.com/crypto-org-chain/chainlibpy/issues/26) [#27](https://github.com/crypto-org-chain/chainlibpy/issues/27) [#28](https://github.com/crypto-org-chain/chainlibpy/issues/28) Refactor protobuf message to class to add more functionalities and hide protobuf complexity

[#32](https://github.com/crypto-org-chain/chainlibpy/issues/32) Add test environment

Require Python >= 3.8

[#25](https://github.com/crypto-org-chain/chainlibpy/issues/25) Add mainnet and testnet-croeseid-4 network configurations

[#24](https://github.com/crypto-org-chain/chainlibpy/pull/24) Fix unable to use secure gRPC channel to interact with chain

## 2.1.0 - 7/Dec/2021

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
