#!/usr/bin/env python2.3
# -*- coding: utf-8 -*-
#
#      TODO: Thread shutdown
#      TODO: How to allow the thread to start new components?
#            (ie we only yield 1, not a newComponent or any value from the
#            thread.)
#      TODO: Number of minor issues fixed - thread shutdown is an issue though!
#            Added simple trace statements into the code.
#
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

import threading
import Queue
import time
import Axon.Component
from Axon.AxonExceptions import noSpaceInBox
from Axon.Ipc import newComponent

class threadedcomponent(Axon.Component.component,threading.Thread):
   """This component is intended to allow blocking calls to be made from within
      a component by running them inside a thread in the component.
   """

   def __init__(self,queuelengths=10):
      super(threadedcomponent, self).__init__()
      threading.Thread.__init__(self)

      self.queuelengths = queuelengths
      self.inqueues = dict()
      self.outqueues = dict()
      for box in self.inboxes.iterkeys():
         self.inqueues[box] = Queue.Queue(self.queuelengths)
      for box in self.outboxes.iterkeys():
         self.outqueues[box] = Queue.Queue(self.queuelengths)

      self.outbuffer = dict()

      self.threadtoaxonqueue = Queue.Queue()
      self.axontothreadqueue = Queue.Queue()

      self.setDaemon(True) # means the thread is stopped if the main thread stops.
   
   def run(self):
      """STUB - Override this to do the work that will block.  Access the in and out
         queues that pass on to the in and out boxes.  You should read from all
         inqueues
      """
      while 1:
         for box in self.inqueues.iterkeys():
            print "ba",
            while not self.inqueues[box].empty():
               print "dada:", self.inqueues[box].get(),
         print "doing"
         if not self.axontothreadqueue.empty():
            mesg = self.axontothreadqueue.get()
            if mesg == "StopThread":
               self.threadtoaxonqueue.put("ThreadStopped")
               break
         time.sleep(1)
   
   def main(self):
      """Do not overide this unless you reimplement the pass through of the boxes to the threads.
      """
      self.start()
      while 1:
 
         for box in self.outboxes:
            if self.outbuffer.has_key(box):
               try:
                  self.send(self.outbuffer[box], box)
               except noSpaceInBox:
                  continue # Skip to next box, since outbox full
               del self.outbuffer[box]

            while(not self.outqueues[box].empty()):
               sending = self.outqueues[box].get()
               try:
                  self.send(sending,box)
               except noSpaceInBox:
                  self.outbuffer[box] = sending
                  break
   
         if not self.threadtoaxonqueue.empty():
         # Check for messages from internal thread.  It could loop through them but that 
         # would change the meaning of the continue statement from skipping the inbox
         #reading.
            m = self.threadtoaxonqueue.get()
            if isinstance(m, newComponent):
            # If new components have been created and need to be added to the run queue
            # It might be best that more of the work of adding children is done here to avoid
            # race conditions.
               yield m # yield for the scheduler to add to list of running components.
            elif m == "ThreadStopped":
            # See if thread has finished in which case the component should finish up and die
            # as soon as all the output from the thread is passed on and no longer pending
               residualdata = False
               for box in self.outboxes:
                  # This checks that there is no pending data that hasn't been put in an outbox
                  # before allowing the component to die.
                  if self.outbuffer.has_key(box) or not self.outqueues[box].empty():
                     residualdata = True
                     break
               if not residualdata:
                  return # The thread has finished, all data has been sent and the component
                             # can be removed from the run queue.
               yield 1
               continue # This means we do not pass in more data destined for the dead thread
   
         for box in self.inboxes:
            if(self.dataReady(box)):
               if(not self.inqueues[box].full()): # LBYL, but no race hazard
                  self.inqueues[box].put(self.recv(box))

         yield 1

if __name__ == '__main__':
     print "starting"
     tc = threadedcomponent()
     axonthread = tc.main()
     axonthread.next()
     axonthread.next()
     axonthread.next()
     time.sleep(2)
     tc._deliver("hello","inbox")
     axonthread.next()
     axonthread.next()
     axonthread.next()
     time.sleep(3)
     tc._deliver("world","inbox")
     axonthread.next()
     axonthread.next()
     axonthread.next()
     time.sleep(2)
     axonthread.next()
     axonthread.next()
     axonthread.next()
     tc._deliver("foo","inbox")
     axonthread.next()
     axonthread.next()
     axonthread.next()
     time.sleep(2)
     axonthread.next()
     axonthread.next()
     axonthread.next()
     tc.axontothreadqueue.put("StopThread")
 
