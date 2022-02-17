#!/bin/bash

# Directory
OUTPUT="./chainlibpy/generated"

TEMP_DOWNLOAD_DIR="./temp_download"
COSMOS_REPO_ZIP="./temp_download/cosmos_sdk_tmp.zip"
COSMOS_SDK_DIR="./temp_download/cosmos-sdk"
COSMOS_PROTO_DIR="./temp_download/cosmos-sdk/proto"

# Download reference
COSMOS_REF=${COSMOS_REF:-"master"}
COSMOS_SUFFIX=${COSMOS_REF}
[[ $COSMOS_SUFFIX =~ ^v[0-9]+\.[0-9]+\.[0-9]+(-.+)?$ ]] && COSMOS_SUFFIX=${COSMOS_SUFFIX#v}

# Setup download and output directories
rm -rf $OUTPUT
mkdir -p $OUTPUT $TEMP_DOWNLOAD_DIR

# Add .proto files here to generate respective gRPC code
PROTO_FILES="
$COSMOS_SDK_DIR/proto/cosmos/auth/v1beta1/auth.proto
$COSMOS_SDK_DIR/proto/cosmos/auth/v1beta1/query.proto
$COSMOS_SDK_DIR/proto/cosmos/bank/v1beta1/bank.proto
$COSMOS_SDK_DIR/proto/cosmos/bank/v1beta1/query.proto
$COSMOS_SDK_DIR/proto/cosmos/bank/v1beta1/tx.proto
$COSMOS_SDK_DIR/proto/cosmos/base/abci/v1beta1/abci.proto
$COSMOS_SDK_DIR/proto/cosmos/base/query/v1beta1/pagination.proto
$COSMOS_SDK_DIR/proto/cosmos/base/v1beta1/coin.proto
$COSMOS_SDK_DIR/proto/cosmos/crypto/secp256k1/keys.proto
$COSMOS_SDK_DIR/proto/cosmos/crypto/multisig/v1beta1/multisig.proto
$COSMOS_SDK_DIR/proto/cosmos/tx/signing/v1beta1/signing.proto
$COSMOS_SDK_DIR/proto/cosmos/tx/v1beta1/service.proto
$COSMOS_SDK_DIR/proto/cosmos/tx/v1beta1/tx.proto
$COSMOS_SDK_DIR/third_party/proto/cosmos_proto/cosmos.proto
$COSMOS_SDK_DIR/third_party/proto/gogoproto/gogo.proto
$COSMOS_SDK_DIR/third_party/proto/google/api/annotations.proto
$COSMOS_SDK_DIR/third_party/proto/google/api/http.proto
$COSMOS_SDK_DIR/third_party/proto/tendermint/abci/types.proto
$COSMOS_SDK_DIR/third_party/proto/tendermint/crypto/keys.proto
$COSMOS_SDK_DIR/third_party/proto/tendermint/crypto/proof.proto
$COSMOS_SDK_DIR/third_party/proto/tendermint/types/params.proto
$COSMOS_SDK_DIR/third_party/proto/tendermint/types/types.proto
$COSMOS_SDK_DIR/third_party/proto/tendermint/types/validator.proto
$COSMOS_SDK_DIR/third_party/proto/tendermint/version/types.proto
"

curl -sL -o "$COSMOS_REPO_ZIP" "https://github.com/cosmos/cosmos-sdk/archive/$COSMOS_REF.zip"
unzip "$COSMOS_REPO_ZIP" "*.proto" -d "$TEMP_DOWNLOAD_DIR"
mv "$COSMOS_SDK_DIR-$COSMOS_SUFFIX" "$COSMOS_SDK_DIR"

python -m grpc.tools.protoc --proto_path=$COSMOS_SDK_DIR/proto --proto_path=$COSMOS_SDK_DIR/third_party/proto --python_out=$OUTPUT --grpc_python_out=$OUTPUT $PROTO_FILES

# use relative imports in generated modules https://github.com/protocolbuffers/protobuf/issues/1491
protol \
  --create-package \
  --in-place \
  --python-out $OUTPUT \
  protoc \
  --proto-path=$COSMOS_SDK_DIR/proto \
  --proto-path=$COSMOS_SDK_DIR/third_party/proto $PROTO_FILES
