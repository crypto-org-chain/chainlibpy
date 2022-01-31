from google.protobuf import any_pb2, message


def pack_to_any_message(msg: message.Message) -> any_pb2.Any:
    """Packs a protobuf Message type to protobuf Any type.

    Args:
        msg (message.Message): protobuf Message to be packed

    Returns:
        any_pb2.Any: to be used for `google.protobuf.Any` type
    """

    assert isinstance(msg, message.Message), "Wrong type"

    packed_any = any_pb2.Any()
    packed_any.Pack(msg, type_url_prefix="/")

    return packed_any
