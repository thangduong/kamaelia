#!/usr/bin/python
#
# Mock source for DJ 2
#

import Axon
from Axon.ThreadedComponent import threadedcomponent
from Kamaelia.Util.ConsoleEcho import consoleEchoer
from Kamaelia.Util.PipelineComponent import pipeline
from Kamaelia.Internet.TCPClient import TCPClient
from Kamaelia.ReadFileAdaptor import ReadFileAdaptor
from Kamaelia.File.Writing import SimpleFileWriter
from Kamaelia.SingleServer import SingleServer

import sys
if len(sys.argv) > 1:
   dj2port = int(sys.argv[1])
else:
   dj2port = 1702

class ConsoleReader(threadedcomponent):
   def main(self):
      while 1:
         line = raw_input("DJ1-> ")
         line = line + "\n"
         self.send(line,"outbox")

class message_source(Axon.Component.component):
    def main(self):
        while 1:
            self.send("hello", "outbox")
            yield 1

pipeline(
     ReadFileAdaptor("audio.2.raw", readmode="bitrate", bitrate =1536000),
     TCPClient("127.0.0.1", dj2port),
).run()

if 0:
    pipeline(
         ConsoleReader(),
         TCPClient("127.0.0.1", dj2port),
    ).run()