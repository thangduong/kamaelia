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
#

import Axon
from Axon.Ipc import producerFinished, shutdownMicroprocess

class TwoWaySplitter(Axon.Component.component):
    Outboxes = { "outbox"  : "",
                 "outbox2" : "",
                 "signal"  : "",
                 "signal2" : "",
               }
    

    def main(self):
        done=False
        while not done:

            while self.dataReady("inbox"):
                data = self.recv("inbox")
                self.send(data, "outbox")
                self.send(data, "outbox2")

            while self.dataReady("control"):
                data = self.recv("control")
                self.send(data, "signal")
                self.send(data, "signal2")
                if isinstance(data, (producerFinished, shutdownMicroprocess)):
                    return

            self.pause()
            yield 1
