#!/usr/bin/python
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

import unittest
from Kamaelia.Sketch.SubtitleFilter import SubtitleFilter2

class TestSubtitleFilter(unittest.TestCase):
   def setUp(self):
      self.sf = SubtitleFilter2()
      
   def test_BasicStringPasses(self):
      """filter - A string containing no markup passes through unchanged."""
      teststring = "This is a normal string."
      out = self.sf.filter(teststring) + self.sf.filter("")
      self.failUnless(teststring == out,out)
      
   def test_MaintestAllAtOnce(self):
      """filter - A string containing <clear/> tags and repeated text is appropriately filtered."""
      output = self.sf.filter(themaintestinput) + self.sf.filter("")
      self.failUnless(themaintestoutput == output)
      
   def test_locateDifferences(self):
      """filter - A string containing <clear/> tags and repeated text is appropriately filtered also gives details of where they fail."""
      out = self.sf.filter(themaintestinput) + self.sf.filter("")
      for i in xrange(0,len(out)):
         if out[i] != themaintestoutput[i]:
            self.fail("Difference at character " + str(i) + " " + out[i] + "\n" + out[i-90:i+45] + "\n" + themaintestoutput[i-90:i+45])
     
   def test_bitbybit(self):
      """filter - Filters the same string as the other tests but by passing the string in as small sections."""
      out = ""
      pos = 0
      while pos <= len(themaintestinput):
         out = out + self.sf.filter(themaintestinput[pos:pos +20])
         pos = pos + 20
      out = out + self.sf.filter("")
      for i in xrange(0,len(out)):
         if out[i] != themaintestoutput[i]:
            self.fail("Difference at character " + str(i) + " " + out[i] + "\n" + out[i-90:i+45] + "\n" + themaintestoutput[i-90:i+45])
      self.failUnless(out == themaintestoutput)
      
def suite():
   return unittest.makeSuite(TestSubtitleFilter)

themaintestinput = """<font color="#FFFF00"/> careful decision whether it will<clear/><font color="#FFFF00"/> careful decision whether it will<font color="#FFFF00"/> enhance his career. He's not the<clear/><font color="#FFFF00"/> enhance his career. He's not the<font color="#FFFF00"/> best in England u Frank Lamp ard<clear/><font color="#FFFF00"/> best in England u Frank Lamp ard<font color="#FFFF00"/> won the player of the year. And<clear/><font color="#FFFF00"/> won the player of the year. And<font color="#FFFF00"/> both of them, we might bin the -<clear/><font color="#FFFF00"/> both of them, we might bin the -<font color="#FFFF00"/> win the World Cup!.<font color="#FFFFFF"/> Getting ahead<clear/><font color="#FFFF00"/> win the World Cup!.<font color="#FFFFFF"/> Getting ahead<font color="#FFFFFF"/> of yourself!<clear/><font color="#FFFFFF"/> of yourself!<font color="#FFFFFF"/> Shouldn't praise be given to both<clear/><font color="#FFFFFF"/> Shouldn't praise be given to both<font color="#FFFFFF"/> teams, without the diving and<clear/><font color="#FFFFFF"/> teams, without the diving and<font color="#FFFFFF"/> screaming at referees. And TS says<clear/><font color="#FFFFFF"/> screaming at referees. And TS says<font color="#FFFFFF"/> it was a great advert for English<clear/><font color="#FFFFFF"/> it was a great advert for English<font color="#FFFFFF"/> football.<font color="#FFFF00"/> I think it was a good<clear/><font color="#FFFFFF"/> football.<font color="#FFFF00"/> I think it was a good<font color="#FFFF00"/> point. The Milan team, the Italian<clear/><font color="#FFFF00"/> point. The Milan team, the Italian<font color="#FFFF00"/> side you might have thought they<clear/><font color="#FFFF00"/> side you might have thought they<font color="#FFFF00"/>would resort to unsavoury tactics-"""

themaintestoutput = """<font color="#FFFF00"/> careful decision whether it will<font color="#FFFF00"/> enhance his career. He's not the<font color="#FFFF00"/> best in England u Frank Lamp ard<font color="#FFFF00"/> won the player of the year. And<font color="#FFFF00"/> both of them, we might bin the -<font color="#FFFF00"/> win the World Cup!.<font color="#FFFFFF"/> Getting ahead<font color="#FFFFFF"/> of yourself!<font color="#FFFFFF"/> Shouldn't praise be given to both<font color="#FFFFFF"/> teams, without the diving and<font color="#FFFFFF"/> screaming at referees. And TS says<font color="#FFFFFF"/> it was a great advert for English<font color="#FFFFFF"/> football.<font color="#FFFF00"/> I think it was a good<font color="#FFFF00"/> point. The Milan team, the Italian<font color="#FFFF00"/> side you might have thought they<font color="#FFFF00"/>would resort to unsavoury tactics-"""

if __name__=='__main__':
   unittest.main()
