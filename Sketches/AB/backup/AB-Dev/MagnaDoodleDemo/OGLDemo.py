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

from Kamaelia.Chassis.Graphline import Graphline

from Kamaelia.UI.OpenGL.OpenGLDisplay import OpenGLDisplay
from Kamaelia.UI.OpenGL.PygameWrapper import PygameWrapper
from Kamaelia.UI.OpenGL.MatchedTranslationInteractor import MatchedTranslationInteractor

from Kamaelia.Util.Console import ConsoleReader

from Kamaelia.UI.Pygame.MagnaDoodle import MagnaDoodle
from Kamaelia.UI.Pygame.Display import PygameDisplay
from Kamaelia.UI.Pygame.Ticker import Ticker

from Kamaelia.Apps.Whiteboard.TagFiltering import TagAndFilterWrapper, FilterAndTagWrapper
from Kamaelia.Apps.Whiteboard.TagFiltering import TagAndFilterWrapperKeepingTag, FilterAndTagWrapperKeepingTag
from Kamaelia.Apps.Whiteboard.Tokenisation import tokenlists_to_lines, lines_to_tokenlists
from Kamaelia.Apps.Whiteboard.Canvas import Canvas
from Kamaelia.Apps.Whiteboard.Painter import Painter
from Kamaelia.Apps.Whiteboard.SingleShot import OneShot
from Kamaelia.Apps.Whiteboard.CheckpointSequencer import CheckpointSequencer
from Kamaelia.Apps.Whiteboard.Entuple import Entuple
from Kamaelia.Apps.Whiteboard.Routers import Router, TwoWaySplitter, ConditionalSplitter
from Kamaelia.Apps.Whiteboard.Palette import buildPalette, colours
from Kamaelia.Apps.Whiteboard.Options import parseOptions
from Kamaelia.Apps.Whiteboard.UI import PagingControls, LocalPagingControls, Eraser, ClearPage, SaveDeck, LoadDeck, ClearScribbles
from Kamaelia.Apps.Whiteboard.CommandConsole import CommandConsole
from Kamaelia.Apps.Whiteboard.SmartBoard import SmartBoard
from Kamaelia.Apps.Whiteboard.Webcam import Webcam

#from Webcam import Webcam
from Webcam import VideoCaptureSource

#from BlankCanvas import BlankCanvas


if __name__=="__main__":
    width = 1024
    height = 768
    top = 0
    left = 0
    colours_order = [ "black", "red", "orange", "yellow", "green", "turquoise", "blue", "purple", "darkgrey", "lightgrey" ]
    ogl_display = OpenGLDisplay(title="Kamaelia Whiteboard",width=width,height=height,background_colour=(255,255,255))
    ogl_display.activate()
    OpenGLDisplay.setDisplayService(ogl_display)
    
    ogl_display = OpenGLDisplay.getDisplayService()
    PygameDisplay.setDisplayService(ogl_display[0])
    
    if (0):
        #PygameDisplay.setDisplayService(ogl_display)
        CANVAS = Canvas( position=(left,top+32),size=(1200,(900-(32+15))),notepad="Test" ).activate() #(replace width with 'width' and height with 'height-(32+15)'
        PAINTER = Painter().activate()
        CANVAS_WRAPPER = PygameWrapper(wrap=CANVAS, position=(0,0,-10), rotation=(0,0,0)).activate() 
        ERASER  = Eraser(left,top).activate()
        PALETTE = buildPalette( cols=colours, order=colours_order, topleft=(left+64,top), size=32 ).activate()
        CLEAR = ClearPage(left+(64*5)+32*len(colours),top).activate()
        #PALETTE_WRAPPER = PygameWrapper(wrap=PALETTE, position=(4,1,-10), rotation=(-20,15,3)).activate()
    
        #PAINTER_WRAPPER = PygameWrapper(wrap=PAINTER, position=(4,1,-10), rotation=(-20,15,3)).activate()
        CANVAS.link( (PAINTER,"outbox"), (CANVAS, "inbox") )
        PAINTER.link( (CANVAS,"eventsOut"), (PAINTER, "inbox") )
        PAINTER.link( (PALETTE,"outbox"), (PAINTER, "colour") )
        PAINTER.link( (ERASER, "outbox"), (PAINTER, "erase") )
        PAINTER.link( (CLEAR, "outbox"), (CANVAS, "inbox") )
        
    CANVAS = Canvas( position=(left,top+32),size=(1200,(900-(32+15))),notepad="Test" ).activate() #(replace width with 'width' and height with 'height-(32+15)'
    PAINTER = Painter().activate()
    ERASER  = Eraser(left,top).activate()
    PALETTE = buildPalette( cols=colours, order=colours_order, topleft=(left+64,top), size=32 ).activate()
    CLEAR = ClearPage(left+(64*5)+32*len(colours),top).activate()    
        
    MAIN = Graphline(CANVAS = CANVAS,PAINTER = PAINTER,ERASER = ERASER,PALETTE = PALETTE,CLEAR = CLEAR,
                    CANVAS_WRAPPER = PygameWrapper(wrap=CANVAS, position=(0,0,-10), rotation=(0,0,0)),
                    linkages = {
                        ("PAINTER","outbox") : ("CANVAS", "inbox"),
                        ("CANVAS","eventsOut") : ("PAINTER", "inbox"),
                        ("PALETTE","outbox") : ("PAINTER", "colour"),
                        ("ERASER", "outbox") : ("PAINTER", "erase"),
                        ("CLEAR", "outbox") : ("CANVAS", "inbox"),
                        },
                     ).activate()
              
    WEBCAM = VideoCaptureSource().activate()
    BLANKCANVAS = Canvas( position=(left,top+32),size=((63*3+2),140),notepad="Test",bgcolour=(200,200,200) ).activate()
    #BLANKCANVAS = BlankCanvas().activate()
    BLANKCANVAS.link( (WEBCAM, "outbox"), (BLANKCANVAS, "inbox") )
    WEBCAM_WRAPPER = PygameWrapper(wrap=BLANKCANVAS, position=(3.7,2.7,-9), rotation=(-1,-5,-5)).activate()
    
    #WEBCAMWRAPPER = PygameWrapper(wrap=WEBCAM, position=(0,0,-9), rotation=(0,0,0)).activate()
    #WEBCAM = Webcam().activate()            
    #WEBCAMWRAPPER = PygameWrapper(wrap=WEBCAM, position=(0,0,-9), rotation=(0,0,0)).activate()
    #PAINTER_WRAPPER = PygameWrapper(wrap=PAINTER, position=(4,1,-10), rotation=(-20,15,3)).activate()
    #TICKER = Ticker(size = (150, 150)).activate()
    #TICKER_WRAPPER = PygameWrapper(wrap=TICKER, position=(4, 1,-10), rotation=(-20,15,3)).activate()
    #MAGNADOODLE = MagnaDoodle(size=(200,200)).activate()
    #MAGNADOODLEWRAPPER = PygameWrapper(wrap=MAGNADOODLE, position=(3,-2,-8), rotation=(1,-1,0)).activate()
    i1 = MatchedTranslationInteractor(target=WEBCAM_WRAPPER).activate()
    #READER = ConsoleReader().activate()
    
    #READER.link( (READER,"outbox"), (TICKER, "inbox") )
    
    Axon.Scheduler.scheduler.run.runThreads()  