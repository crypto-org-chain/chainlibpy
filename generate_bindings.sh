#!/bin/bash
CORE_PATH=defi-wallet-core-rs/common
UDL_PATH=$CORE_PATH/src/common.udl
CONFIG_PATH=$CORE_PATH/uniffi.toml
OUTPUT_PATH=chainlibpy/generated/

uniffi-bindgen generate $UDL_PATH --config $CONFIG_PATH --language python --out-dir $OUTPUT_PATH