
'Generated protocol buffer code.'
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from .....gogoproto import gogo_pb2 as gogoproto_dot_gogo__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='cosmos/crypto/multisig/v1beta1/multisig.proto', package='cosmos.crypto.multisig.v1beta1', syntax='proto3', serialized_options=b'Z)github.com/cosmos/cosmos-sdk/crypto/types', create_key=_descriptor._internal_create_key, serialized_pb=b'\n-cosmos/crypto/multisig/v1beta1/multisig.proto\x12\x1ecosmos.crypto.multisig.v1beta1\x1a\x14gogoproto/gogo.proto"*\n\x0eMultiSignature\x12\x12\n\nsignatures\x18\x01 \x03(\x0c:\x04\xd0\xa1\x1f\x01"A\n\x0fCompactBitArray\x12\x19\n\x11extra_bits_stored\x18\x01 \x01(\r\x12\r\n\x05elems\x18\x02 \x01(\x0c:\x04\x98\xa0\x1f\x00B+Z)github.com/cosmos/cosmos-sdk/crypto/typesb\x06proto3', dependencies=[gogoproto_dot_gogo__pb2.DESCRIPTOR])
_MULTISIGNATURE = _descriptor.Descriptor(name='MultiSignature', full_name='cosmos.crypto.multisig.v1beta1.MultiSignature', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='signatures', full_name='cosmos.crypto.multisig.v1beta1.MultiSignature.signatures', index=0, number=1, type=12, cpp_type=9, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=b'\xd0\xa1\x1f\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=103, serialized_end=145)
_COMPACTBITARRAY = _descriptor.Descriptor(name='CompactBitArray', full_name='cosmos.crypto.multisig.v1beta1.CompactBitArray', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='extra_bits_stored', full_name='cosmos.crypto.multisig.v1beta1.CompactBitArray.extra_bits_stored', index=0, number=1, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='elems', full_name='cosmos.crypto.multisig.v1beta1.CompactBitArray.elems', index=1, number=2, type=12, cpp_type=9, label=1, has_default_value=False, default_value=b'', message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=b'\x98\xa0\x1f\x00', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=147, serialized_end=212)
DESCRIPTOR.message_types_by_name['MultiSignature'] = _MULTISIGNATURE
DESCRIPTOR.message_types_by_name['CompactBitArray'] = _COMPACTBITARRAY
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
MultiSignature = _reflection.GeneratedProtocolMessageType('MultiSignature', (_message.Message,), {'DESCRIPTOR': _MULTISIGNATURE, '__module__': 'cosmos.crypto.multisig.v1beta1.multisig_pb2'})
_sym_db.RegisterMessage(MultiSignature)
CompactBitArray = _reflection.GeneratedProtocolMessageType('CompactBitArray', (_message.Message,), {'DESCRIPTOR': _COMPACTBITARRAY, '__module__': 'cosmos.crypto.multisig.v1beta1.multisig_pb2'})
_sym_db.RegisterMessage(CompactBitArray)
DESCRIPTOR._options = None
_MULTISIGNATURE._options = None
_COMPACTBITARRAY._options = None
