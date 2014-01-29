from pyasn1.type import univ
from pyasn1.codec.ber import decoder
from pyasn1.error import PyAsn1Error
from pysnmp.proto.error import ProtocolError

def decodeMessageVersion(wholeMsg):
    try:
        seq, wholeMsg = decoder.decode(
            wholeMsg, asn1Spec=univ.Sequence(), recursiveFlag=0
        )
        ver, wholeMsg = decoder.decode(
            wholeMsg, asn1Spec=Integer(), recursiveFlag=0
        )
        return ver
    except PyAsn1Error:
        raise ProtocolError('Invalid BER at SNMP version component')
