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
import stat
import os

def filesfrompath(path):
    dir = False
    try:
        dir = os.path.isdir(path)
    except OSError:
        return []
    
    files = []
    if dir:
        ps = [path+'/'+p for p in os.listdir(path) if p[0] != '.']
        for p in ps:
            files += filesfrompath(p)
    else: # assume is file
        if path[-3:] == '.py':
            files += [path]
    
    return files

def glom(file):
    if file[-3:] != '.py':
        return []
    
    f = open(file, 'r')
    lines = f.readlines()
    
    # remove any lines before first function def, e.g. docs
    while lines and len(lines[0]) < 3 and lines[0].lstrip()[0:4] != 'def ':
        lines.pop(0)
    
    i = 0
    fs = []
    while i < len(lines):
        l = lines[i]
        start = i
        indent = len(l) - len(l.lstrip())
        
        if l.lstrip()[0:4] == 'def ':
            i += 1
            while i < len(lines) and len(lines[i]) - len(lines[i].lstrip()) > indent:
                i+= 1
            fs += [lines[start:i]]
        i += 1
    
    return file, fs

def format(fftup):
    file, functions = fftup
    fs = {}
    for f in functions:
        defline = f[0]
        indent = len(defline) - len(defline.lstrip())
        
        f = [line[indent:] for line in f]
        name = file + ': ' + f[0].partition('(')[0].split(' ')[1]
        
        fs[name] = f
    
    return fs # fs['<filepath>: <functionname>'] = [lines of code]



def glomfrompath(path = ''):
    if not path: return []
        
    fs = {}
    for f in filesfrompath(path):
        fs.update(format(glom(f)))
    return fs

    