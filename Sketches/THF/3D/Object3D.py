#!/usr/bin/env python
#
# (C) 2005 British Broadcasting Corporation and Kamaelia Contributors(1)
#     All Rights Reserved.
#
# You may only modify and redistribute this under the terms of any of the
# following licenses(2): Mozilla Public License, V1.1, GNU General
# Public License, V2.0, GNU Lesser General Public License, V2.1
#
# (1) Kamaelia Contributors are listed in the AUTHORS file and at
#     http://kamaelia.sourceforge.net/AUTHORS - please extend this file,
#     not this notice.
# (2) Reproduced in the COPYING file, and at:
#     http://kamaelia.sourceforge.net/COPYING
# Under section 3.5 of the MPL, we are using this text since we deem the MPL
# notice inappropriate for this file. As per MPL/GPL/LGPL removal of this
# notice is prohibited.
#
# Please contact us via: kamaelia-list-owner@lists.sourceforge.net
# to discuss alternative licensing.
# -------------------------------------------------------------------------
"""\
=====================
General 3D Object
=====================
TODO
"""


import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from Display3D import Display3D
import Axon

class Object3D(Axon.Component.component):
    Inboxes = {
       "inbox": "not used",
       "control": "ignored",
       "hit" : "We expect to recieve messages telling us that the cube is clicked",
    }
    
    Outboxes = {
        "outbox": "not used",
        "display_signal": "for communication with display3d",
    }
    
    def __init__(self, **argd):
        super(Object3D, self).__init__()
        # not sure about the needed data yet, just for testing
        self.angle = 0
        self.turndir = 0.3
        self.size = [2,2,2]
        self.pos = argd.get("pos",[0,0,-15])
        self.rot = [0,0,0]
        
        # similar to Pygame component registration
        self.disprequest = { "3DDISPLAYREQUEST" : True,
#                                          "callback" : (self,"callback"),
                                          "events" : (self, "inbox"),
                                          "size": self.size,
                                          "pos": self.pos, }

    def main(self):
        displayservice = Display3D.getDisplayService()
        self.link((self,"display_signal"), displayservice)
        self.send(self.disprequest, "display_signal");

        while 1:

#            for _ in self.waitBox("callback"): yield 1
#            self.display = self.recv("callback")

# There is no need for a callback yet
            
            yield 1

            # simple test action: change rotation dir
            while self.dataReady("hit"):
                self.turndir = -self.turndir
            
            self.angle += self.turndir %360;

# Later it might be a good idea to provide a set of drawing functions
# so the component developer does not need to know about opengl
# This way opengl could later easily be replaced by an other mechanism
# for drawing
# TOGRA

            # translation and rotation
            glPushMatrix()
            glTranslate(*self.pos)
            glRotate(self.angle, 1.0,1.0,1.0)

            # draw faces 
            glBegin(GL_QUADS)
            glColor3f(1.0,0.0,0.0)
            glVertex3f(1.0,1.0,1.0)
            glVertex3f(1.0,-1.0,1.0)
            glVertex3f(-1.0,-1.0,1.0)
            glVertex3f(-1.0,1.0,1.0)

            glColor3f(0.0,1.0,0.0)
            glVertex3f(1.0,1.0,-1.0)
            glVertex3f(1.0,-1.0,-1.0)
            glVertex3f(-1.0,-1.0,-1.0)
            glVertex3f(-1.0,1.0,-1.0)
            
            glColor3f(0.0,0.0,1.0)
            glVertex3f(1.0,1.0,1.0)
            glVertex3f(1.0,-1.0,1.0)
            glVertex3f(1.0,-1.0,-1.0)
            glVertex3f(1.0,1.0,-1.0)

            glColor3f(1.0,0.0,1.0)
            glVertex3f(-1.0,1.0,1.0)
            glVertex3f(-1.0,-1.0,1.0)
            glVertex3f(-1.0,-1.0,-1.0)
            glVertex3f(-1.0,1.0,-1.0)

            glColor3f(0.0,1.0,1.0)
            glVertex3f(1.0,1.0,1.0)
            glVertex3f(-1.0,1.0,1.0)
            glVertex3f(-1.0,1.0,-1.0)
            glVertex3f(1.0,1.0,-1.0)

            glColor3f(1.0,1.0,0.0)
            glVertex3f(1.0,-1.0,1.0)
            glVertex3f(-1.0,-1.0,1.0)
            glVertex3f(-1.0,-1.0,-1.0)
            glVertex3f(1.0,-1.0,-1.0)
            glEnd()

            glPopMatrix()
            glFlush()


if __name__=='__main__':
    from Kamaelia.Util.Graphline import Graphline
    pygame.init()
    obj = Object3D(pos=[0, 0,-12]).activate()
    obj = Object3D(pos=[0,4,-20]).activate()
    obj = Object3D(pos=[4,0,-22]).activate()
    obj = Object3D(pos=[0,-4,-18]).activate()
    obj = Object3D(pos=[-4, 0,-15]).activate()
    Axon.Scheduler.scheduler.run.runThreads()  
