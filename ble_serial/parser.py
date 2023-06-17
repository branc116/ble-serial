from enum import Enum
from typing import Dict, Optional, Tuple, Union
import struct

# 7*(0x00, 0xFF), 0x00, 0xXXXXXX = Controll message.
# 0bAABB,CCDD,EEFF,GGHH,IIJJ,KKLL = stream descripton
# 0bAA = 0b00 -> No more data
# 0bAA = 0b01 -> First element has 2 byte
# 0bAA = 0b10 -> Fist two elements have 2 bytes
# 0bAA = 0b11 -> Fist element has 4 bytes
# 0bBB = 0bST -> First (two) element(s) type
# 0bST = 0b00 -> First (two) element(s) type is unsigned int LE
# 0bST = 0b10 -> First (two) element(s) type is signed int LE
# 0bST = 0b01 -> First (two) element(s) type is unsigned float LE
# 0bST = 0b11 -> First (two) element(s) type is signed float LE
# AAAA = Number of values.
class stream_element(Enum):
    NODATA  = 0
    USHORT  = 4
    SSHORT  = 6
    USHORT2 = 8
    SSHORT2 = 10
    ULONG   = 12
    SLONG   = 14
    SFLOAT   = 15

s_elemets_to_format = {
    stream_element.NODATA: "",
    stream_element.USHORT: "H",
    stream_element.SSHORT: "h",
    stream_element.USHORT2: "HH",
    stream_element.SSHORT2: "hh",
    stream_element.ULONG: "I",
    stream_element.SLONG: "i",
    stream_element.SFLOAT: "f"
}

def is_controll_message(bs: bytes):
    for i in range(17):
        if bs[i] != 0xFF * (i % 2):
            return False
    return True

def get_stream_elements(cm: bytes):
    ret = []
    for i in cm[17:]:
        aabb = (i & 0xF0) >> 4
        ccdd = (i & 0x0F)
        print(aabb, ccdd)
        if aabb == 0:
            return ret
        elif ccdd == 0:
            ret += [stream_element(aabb)]
            return ret
        else:
            ret += [stream_element(aabb), stream_element(ccdd)]
    return ret

class State:
    def __init__(self):
        self.q: list[bytes]
        self.stream_elements: list[stream_element] = []
        self.data = []
        self.struct_format = ""
    def add_data(self, bs: bytes):
        if is_controll_message(bs):
            self.stream_elements = get_stream_elements(bs)
            self.struct_format = "<" + "".join([ s_elemets_to_format[se] for se in self.stream_elements ])
            self.struct_size = struct.calcsize(self.struct_format)
            print(self.stream_elements, self.struct_format)
        elif self.struct_format != "":
            es = struct.unpack(self.struct_format, bs[:self.struct_size])
            self.data += [ e for e in enumerate(es) ]
    def pop_data(self):
        if len(self.data) > 0:
            return self.data.pop(0)
        return None

class DBParser:
    def __init__(self):
        self.qs: Dict[int, State] = {}
    def add_data(self, handle_id: int, bs: bytes):
        if not handle_id in self.qs:
            self.qs[handle_id] = State()
        self.qs[handle_id].add_data(bs)
    def pop_data(self) -> Optional[Tuple[int, Union[int, float]]]:
        for i in self.qs:
            d = self.qs[i].pop_data()
            if d != None:
                index, value = d
                return (100*i + index, value)
        return None

if __name__ == "__main__":
    p = DBParser()
    p.add_data(1, bytes.fromhex("1232" * 20))
    p.add_data(1, bytes.fromhex("00FF" * 8 + "00" + "FF" * 2))
    p.add_data(1, bytes.fromhex("1232" * 20))
    p.add_data(1, bytes.fromhex("3212" * 20))
    r = p.pop_data()
    while r != None:
        print(r)
        r = p.pop_data()

