# --------------------------------------------------------------------------
# gttree.py
# --------------------------------------------------------------------------
# ***** BEGIN GPL LICENSE BLOCK *****
#
# Copyright (C) 2006 Sergey Prokhorchuk
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# ***** END GPL LICENCE BLOCK *****
# --------------------------------------------------------------------------

# Tree structure definition module.

from gtmath import *

class GTSegment(object):
    __slots__ = [ 'parent','children','length','radius','transform' ]
    def __init__(self,parent,length):
        self.parent    = parent
        self.children  = []
        self.length    = length
        self.radius    = None
        self.transform = GTMatrix4x4()    # to parent space
        self.transform.SetIdentity()


class GTStem(object):
    __slots__ = [ 'segments','length','radius','parent_stem','parent_segment','parent_offset','transform']
    def __init__(self,length,radius):
        self.segments        = []
        self.length          = length
        self.radius          = radius
        self.parent_stem     = None
        self.parent_segment  = None
        self.parent_offset   = 0.0
        self.transform = GTMatrix4x4() # to parent space
        self.transform.SetIdentity()

class GTLeaf(object):
    __slots__ = [ 'parent_stem','parent_segment','parent_offset','transform']
    def __init__(self):
        self.parent_stem     = None
        self.parent_segment  = None
        self.parent_offset   = 0.0
        self.transform       = None

class GTTree:
    def __init__(self):
        self.stems = []


def GTTreeSegmentPointToWorldSpace(TreeData,Stem,SegIndex,x,y,z):
    v = GTVector4(x,y,z,1.0)

    while Stem is not None:
        while SegIndex is not None:
            v = GTMultMatrix4x4Vec4(Stem.segments[SegIndex].transform,v)

            SegIndex = Stem.segments[SegIndex].parent

        if Stem.parent_stem is None:
            Stem = None
        else:
            SegIndex = Stem.parent_segment
            Stem     = TreeData.stems[Stem.parent_stem]

    return GTVector4(v.x,v.y,v.z,v.w)

def GTTreeSegmentToWorldMatrix(TreeData,Stem,SegIndex):
    m = GTMatrix4x4()
    m.SetIdentity()

    while Stem is not None:
        while SegIndex is not None:
            m = GTMultMatrix4x4(Stem.segments[SegIndex].transform,m)

            SegIndex = Stem.segments[SegIndex].parent

        if Stem.parent_stem is None:
            Stem = None
        else:
            SegIndex = Stem.parent_segment
            Stem     = TreeData.stems[Stem.parent_stem]

    return m

def GTTreeLeafToWorldMatrix(TreeData,Stem):
    m = Stem.transform.Clone()

    SegIndex = Stem.parent_segment
    Stem     = TreeData.stems[Stem.parent_stem]

    while Stem is not None:
        while SegIndex is not None:
            m = GTMultMatrix4x4(Stem.segments[SegIndex].transform,m)

            SegIndex = Stem.segments[SegIndex].parent

        if Stem.parent_stem is None:
            Stem = None
        else:
            SegIndex = Stem.parent_segment
            Stem     = TreeData.stems[Stem.parent_stem]

    return m

