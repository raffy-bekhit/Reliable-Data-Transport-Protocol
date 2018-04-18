import struct


def calc_checksum(data):
    encoded_data = data.encode()

    i = 0
    checksum = 0
    while((i)<len(encoded_data)):

        short1=0
        short1 =encoded_data[i]

        if ((i + 1) < len(encoded_data)):
            short1+=(encoded_data[i+1]<<8)

        checksum +=short1

        if((checksum&0x10000)>0):
            checksum= (checksum+1) & 0xFFFF

        i+=2

    return (~checksum & 0xFFFF)


class ack:
    def __init__(self,checksum=0):
        self.checksum=checksum

class packet:

    def __init__(self,pkd_data=None,length=0,seqno=0,data=''):
        if pkd_data:
            var, data = self.unpack(pkd_data)
            self.checksum = var[0]
            self.length = var[1]
            self.seqno = var[2]
            self.data = data.decode()
        else:
            self.length = len(data.encode())+8
            self.seqno = seqno
            self.data = data
            self.checksum = calc_checksum(data)

    def unpack(self, data):
        size = struct.calcsize('HHI')
        return struct.unpack('HHI', data[:size]), data[size:]

    def pack(self):
        encoded_data = self.data.encode()
        str_len = len(encoded_data)
        #packet_length = self.length
        fmt ='HHI%ds' %str_len
        packed_packet = struct.pack(fmt, self.checksum ,self.length,self.seqno,encoded_data)
        return packed_packet