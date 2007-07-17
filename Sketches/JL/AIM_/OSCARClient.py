#! /usr/bin/env python

import md5
import struct
#from oscarutil import *
import pickle
from Axon.Component import component
from Axon.Ipc import shutdownMicroprocess

FLAP_HEADER_LEN = 6
class OSCARProtocol(component):
    Inboxes = {"inbox" : "receives messages, usually from TCP",
               "control" : "shutdown handling",
               "talk" : "(channel, FLAP payload)",
               }

    Outboxes = {"outbox" : "sends messages to AIM, usually via TCP",
                "signal" : "shutdown handling", 
                "heard" : "(channel, FLAP payload)",
                }
    
    def __init__(self):
        super(OSCARProtocol, self).__init__()
        self.seqnum = 0
        self.done = False

    def main(self):
        while not self.done:
            yield 1
            self.checkBoxes()

    def checkBoxes(self):
        for box in self.Inboxes:
            if self.dataReady(box):
                cmd = "self.handle%s()" % box
                exec(cmd)

    def handleinbox(self):
        data = self.recv("inbox")
        head = '!cBHH'
        while data:
            a, chan, seqnum, datalen = struct.unpack(head, data[:FLAP_HEADER_LEN])
            assert len(data) >= 6+datalen
            flapbody = data[FLAP_HEADER_LEN:FLAP_HEADER_LEN+datalen]
            self.send((chan, flapbody), "heard")  
            data = data[FLAP_HEADER_LEN+datalen:]

    def handlecontrol(self):
        data = self.recv("control")
        self.done = True
        self.send(shutdownMicroprocess(), "signal")

    def handletalk(self):
        chan, data = self.recv("talk")
        self.sendFLAP(data, chan)

    #most of method definition from Twisted's oscar.py
    def sendFLAP(self,data,channel = 0x02):
        header="!cBHH"
        self.seqnum=(self.seqnum+1)%0x10000
        seqnum=self.seqnum
        head=struct.pack(header,'*', channel,
                         seqnum, len(data))
        self.send(head+str(data))


from Kamaelia.Chassis.Graphline import Graphline
from Kamaelia.Internet.TCPClient import TCPClient

def OSCARClient(server, port):
    return Graphline(oscar = OSCARProtocol(),
                     tcp = TCPClient(server, port),
                     linkages = {
                         ("oscar", "outbox") : ("tcp", "inbox"),
                         ("tcp", "outbox") : ("oscar", "inbox"),

                         ("oscar", "signal") : ("tcp", "control"),

                         ("self", "inbox") : ("oscar", "talk"),
                         ("oscar", "heard") : ("self", "outbox"),
                         ("self", "control") : ("oscar", "control"),
                         ("tcp", "signal") : ("self", "signal"),
                         }
                     )
    

if __name__ == '__main__':
    from Kamaelia.Util.Console import ConsoleEchoer
    from Kamaelia.Util.PureTransformer import PureTransformer
    
    proto = OSCARProtocol()
    flap = '*\x03\x00\x01\x00\x08flapbody' * 5
    proto._deliver(flap, "inbox")
    
    Graphline(proto = proto,
              echo = ConsoleEchoer(),
              linkages = {("proto", "heard") : ("echo", "inbox"),
                          }
              ).run()
