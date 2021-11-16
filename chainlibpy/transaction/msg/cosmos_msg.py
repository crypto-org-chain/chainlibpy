from chainlibpy.types.cosmos.types.v1beta1.msg import Msg
from chainlibpy.amino import message

class CosmosMsg:
    def to_raw_msg(self) -> Msg:
        '''
        Returns the raw Msg representation of any implementation of Message
        '''
        pass

    def to_raw_amino_msg(self) -> message.Msg:
        '''
        Returns the raw legacy amino Msg representation of any implementation of Message
        '''
        pass