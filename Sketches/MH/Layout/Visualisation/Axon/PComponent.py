#!/usr/bin/env python
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
# -------------------------------------------------------------------------

import pygame

from Visualisation.Graph import BaseParticle
from pygame.locals import *
_COMPONENT_RADIUS = 32

def abbreviate(string):
    """Abbreviates strings to capitals, word starts and numerics and underscores"""
    out = ""
    prev = ""
    for c in string:
        if c.isupper() or c.isdigit() or c == "_" or c == "." or (c.isalpha() and not prev.isalpha()):
            out += c.upper()
        prev = c
    return out

class PComponent(BaseParticle):
    def __init__(self, ID, position, name):
        super(PComponent,self).__init__(position=position, ID = ID )
        self.name = name
        self.ptype = "component"
        self.shortname = abbreviate(name)
        self.left = 0
        self.top = 0
        self.selected = False
        
        font = pygame.font.Font(None, 20)
        self.slabel   = font.render(self.shortname, True, (0,0,0))
        self.slabelxo = - self.slabel.get_width()/2
        self.slabelyo = - self.slabel.get_height()/2
        
        self.radius = _COMPONENT_RADIUS
        
        self.desclabel = font.render("Component "+self.shortname+" : "+self.name, True, (0,0,0), (255,255,255))
        
    def render(self, surface):
        x = int(self.pos[0] - self.left)
        y = int(self.pos[1] - self.top )
    
        yield 1
        for p in self.bondedTo:
            px = int(p.pos[0] - self.left)
            py = int(p.pos[1] - self.top )
            pygame.draw.line(surface, (192,192,192), (x,y), (px,py))
        
        yield 2
        colour = (192,192,192)
        if self.selected:
            colour = (160,160,255)
        pygame.draw.circle(surface, colour, (x,y), self.radius)
        surface.blit(self.slabel, ( x+self.slabelxo, y+self.slabelyo ) )
        if self.selected:
            yield 10
            surface.blit(self.desclabel, (72,16) )
                     
    def setOffset( self, (x,y) ):
        self.left = x
        self.top  = y

    def select( self ):
        """Tell this particle it is selected"""
        self.selected = True

    def deselect( self ):
        """Tell this particle it is selected"""
        self.selected = False
        
            
