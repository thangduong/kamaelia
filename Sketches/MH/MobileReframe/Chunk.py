#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2010 British Broadcasting Corporation and Kamaelia Contributors(1)
#
# (1) Kamaelia Contributors are listed in the AUTHORS file and at
#     http://www.kamaelia.org/AUTHORS - please extend this file,
#     not this notice.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# -------------------------------------------------------------------------
"""\
===========================================
Breaks data into the specified sized chunks
===========================================

Send data, such as binary strings to this component and it will break it down
to roughly constant sized chunks.

The chunk size is determined by you specifying the data rate of the incoming
data and the desired chunk rate.



Example Usage
-------------

Chunking 48KHz 16bit stereo audio into 25 chunks per second (one chunk for each
frame of a corresponding piece of 25fps video)::

    bps = bytesPerSample = 2*2

    Pipeline( AudioSource(),
              Chunk(datarate=48000*bps, quantasize=bps, chunkrate=25),
              ...
            )



Behaviour
---------

At initialisation, specify:
    
  * the rate of the incoming data (eg. bytes/second)
  * the required rate of outgoing chunks of data
  * the minimum quanta size (see below)

Send slicable data items, such as strings containing binary data to the "inbox"
inbox. The same data is sent out of the "outbox" outbox, rechunked to meet the
required chunk rate.

The outgoing chunk sizes are dynamically varied to match the required chunk rate
as accurately as possible. The quantasize parameter dictates the minimum unit by
which the chunksize will be varied.

For example, for 16bit stereo audio data, there are 4 bytes per sample, so
a quantasize of 4 should be specified, to make sure samples remain whole.

If a producerFinished or shutdownMicroprocess message is received on the
"control" inbox. It is immediately sent on out of the "signal" outbox and the
component then immediately terminates.

"""

from Axon.Component import component
from Axon.Ipc import producerFinished, shutdownMicroprocess


class Chunk(component):
    """\
    Chunk(datarate,quantasize,chunkrate) -> new Chunk component.
    
    Alters the chunksize of incoming data to match a desired chunkrate.
    
    Keyword arguments::
    
    - datarate    -- rate of the incoming data
    - quantasize  -- minimum granularity with which the data can be split
    - chunkrate   -- desired chunk rate
    """
    
    Inboxes = { "inbox" : "Data items",
                "control" : "Shutdown signalling"
              }
              
    Outboxes = { "outbox" : "Rechunked data items",
                 "signal" : "Shutdown signalling",
               }
                    
    def __init__(self,datarate,quantasize,chunkrate):
        """x.__init__(...) initializes x; see x.__class__.__doc__ for signature"""
        super(Chunk,self).__init__()
        self.datarate  = datarate
        self.quanta    = quantasize
        self.chunkrate = chunkrate
        
    def main(self):
        """Main loop"""
        
        quantaPerChunk = float(self.datarate)/self.chunkrate/self.quanta
        
        nextChunk = quantaPerChunk
        
        buffer = ""
        while 1:
            while self.dataReady("inbox"):
                newdata=self.recv("inbox")
                buffer += newdata
                
                while len(buffer) >= (int(nextChunk)*self.quanta):
                    amount = (int(nextChunk)*self.quanta)
                    toSend = buffer[:amount]
                    buffer = buffer[amount:]
                    nextChunk = nextChunk - int(nextChunk) + quantaPerChunk
                    self.send(toSend,"outbox")
        
            while  self.dataReady("control"):
                msg = self.recv("control")
                self.send(msg,"signal")
                if isinstance(msg,(producerFinished,shutdownMicroprocess)):
                    return
                
            self.pause()
            yield 1

__kamaelia_components__ = ( Chunk, )
