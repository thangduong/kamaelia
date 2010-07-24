#!/usr/bin/python
# -*- coding: utf-8 -*-

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

# To use pygame alpha
import sys ;
sys.path.insert(0, "/home/zathras/Documents/pygame-1.9.0rc1/build/lib.linux-i686-2.5")

import time
import pygame
import pygame.camera
from Axon.ThreadedComponent import threadedcomponent
from Axon.Component import component
from Kamaelia.Chassis.Pipeline import Pipeline

from Kamaelia.File.Writing import SimpleFileWriter
from Kamaelia.Codec.Dirac import DiracEncoder
from Kamaelia.Video.PixFormatConversion import ToYUV420_planar
from Kamaelia.Util.PureTransformer import PureTransformer
from Kamaelia.Internet.TCPClient import TCPClient

pygame.init()
pygame.camera.init()

class VideoCaptureSource(threadedcomponent):
  capturesize = (352, 288)
  delay = 0
  fps = -1
  device = "/dev/video0"

  def __init__(self, **argd):
    super(VideoCaptureSource, self).__init__(**argd)
    self.camera = pygame.camera.Camera(self.device,
                                       self.capturesize)
    self.camera.start()
    if self.fps != -1:
      self.delay = 1.0/self.fps
    self.snapshot = None

  def capture_one(self):
    self.snapshot = None
    self.snapshot = self.camera.get_image()

  def main(self):
    while 1:
      self.capture_one()
      self.send(self.snapshot, "outbox")
      time.sleep(self.delay)

from Kamaelia.Internet.TCPClient import TCPClient
from Record import AlsaRecorder
Pipeline(
    AlsaRecorder(),
    TCPClient("127.0.0.1", 1501),
).activate()

Pipeline(
   VideoCaptureSource(),
   PureTransformer(lambda F : \
             {"rgb" : pygame.image.tostring(F, "RGB"),
                      "size" : (352, 288),
                      "pixformat" : "RGB_interleaved",
             }),
    ToYUV420_planar(),
    DiracEncoder(preset="CIF",  encParams={"num_L1":0}),
    TCPClient("127.0.0.1", 1500),
).run()


