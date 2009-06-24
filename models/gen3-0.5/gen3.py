#!BPY
# """
# Name: 'Gen3'
# Blender: 237
# Group: 'Misc'
# Tooltip: 'Generate tree models'
# """

__author__  = 'Sergey Prokhorchuk (Stager)'
__url__     = ('blender','elysiun')
__version__ = '0.5'
__bpydoc__  = """\
Description: Generate tree models, using model described by Jason Weber and
Joseph Pen in 'Creation and Rendering of Realistic Trees'
Usage: Run script, setup parameters and click on 'Generate' button
Notes: This version is an early pre-release and does not support all
parameters and possibilities.
"""

# --------------------------------------------------------------------------
# Gen3 by Sergey Prokhorchuk (Stager)
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

import sys
import math
#import random
#import time
import Blender
import Blender.Window

from gt.gtmath      import *
from gt.gtparams    import *
from gt.gttree      import *
from gt.gtgenerator import *
from gt.gtgui       import *

MaxBranchLevels = 4

NumberEditWidth  = 120
NumberEditHeight = 16

MeshDetail = [ 8,4,3,3,3]

class GTLeafMeshData:
    def __init__(self):
        self.verts   = []
        self.uvs     = []
        self.faces   = []
        self.faceuvs = []

    def GenFaceUVsFromVertUVs(self):
        for face in self.faces:
            uvs = []
            for v in face:
                uvs.append(self.uvs[v])
            self.faceuvs.append(uvs)

class GTLeafMeshDataCircle(GTLeafMeshData):
    def __init__(self,resolution):
        GTLeafMeshData.__init__(self)

        if resolution < 3:
            resolution = 3

        angle_step = 2.0 * math.pi / resolution

        self.verts.append((0.5,0.0,0.5))
        self.uvs.append((0.5,0.5))

        for i in xrange(resolution):
            x = math.cos(angle_step * i)
            z = math.sin(angle_step * i)

            self.verts.append((x * 0.5,0.0,0.5 + z * 0.5))
            self.uvs.append((x,z))

            self.faces.append([0,i + 1,(i + 1) % resolution + 1])

        self.GenFaceUVsFromVertUVs()

class GTLeafMeshDataRect(GTLeafMeshData):
    def __init__(self):
        GTLeafMeshData.__init__(self)

        self.verts.append((-0.5,0.0,0.0))
        self.verts.append(( 0.5,0.0,0.0))
        self.verts.append(( 0.5,0.0,1.0))
        self.verts.append((-0.5,0.0,1.0))

        self.uvs.append((0.0,0.0))
        self.uvs.append((1.0,0.0))
        self.uvs.append((1.0,1.0))
        self.uvs.append((0.0,1.0))

        self.faces.append([0,1,2,3])

        self.GenFaceUVsFromVertUVs()

class GTLeafMeshDataHexagon(GTLeafMeshData):
    def __init__(self):
        GTLeafMeshData.__init__(self)

        self.verts.append(( 0.0,0.0,1.0))
        self.verts.append((-0.5,0.0,0.75))
        self.verts.append((-0.5,0.0,0.25))
        self.verts.append(( 0.0,0.0,0.0))
        self.verts.append(( 0.5,0.0,0.25))
        self.verts.append(( 0.5,0.0,0.75))

        self.uvs.append((1.0 ,0.5))
        self.uvs.append((0.75,0.0))
        self.uvs.append((0.25,0.0))
        self.uvs.append((0.0,0.5))
        self.uvs.append((0.25,1.0))
        self.uvs.append((0.75,1.0))

        self.faces.append([0,1,5])
        self.faces.append([1,2,4,5])
        self.faces.append([2,3,4])

        self.GenFaceUVsFromVertUVs()

class GTLeafMeshDataUser(GTLeafMeshData):
    def __init__(self,nmesh):
        GTLeafMeshData.__init__(self)

        for v in nmesh.verts:
            self.verts.append((v.co.x,v.co.y,v.co.z))
            self.uvs.append((v.uvco.x,v.uvco.y))

        for f in nmesh.faces:
            fv = []
            for v in f.v:
                fv.append(v.index)

            self.faces.append(fv)

            if len(f.uv) > 0:
                fuv = []
                for uv in f.uv:
                    fuv.append(uv)
                self.faceuvs.append(fuv)

def StrHasPrefix(value,prefix):
    if len(value) >= len(prefix):
        if value[:len(prefix)] == prefix:
            return 1

    return 0

def GetMeshesNamesByPrefix(prefix):
    names   = []
    objects = Blender.Object.Get()

    for obj in objects:
        if obj.getType() == 'Mesh':
            if StrHasPrefix(obj.getName(),prefix):
                names.append(obj.getName())

    return names

def GetNMeshByName(name):
    objects = Blender.Object.Get()

    for obj in objects:
        if obj.getType() == 'Mesh':
            if obj.getName() == name:
                return obj.getData()

def GetMeshDetail(Level):
    try:
        return MeshDetail[Level]
    except:
        return MeshDetail[-1]

class GTTreeMeshes:
    def __init__(self):
        self.meshes = []

    def GetMesh(self,level):
        if level >= len(self.meshes):
            count = level - len(self.meshes) + 1

            for i in xrange(count):
                self.meshes.append(None)

        if self.meshes[level] is None:
            self.meshes[level] = Blender.NMesh.GetRaw()

        return self.meshes[level]

    def PutMeshes(self):
        self.objs = []

        for mesh in self.meshes:
            if mesh is not None:
                mesh.update(1)
                self.objs.append(Blender.NMesh.PutRaw(mesh))

        if len(self.objs) > 0:
            self.objs[0].makeParent(self.objs[1:])

        for obj in self.objs:
            obj.select(1)

class GTNumberEdit(ControlNumberEdit):
    def __init__(self,name,x,y,inititial,min,max,tooltip='',tags=''):
        ControlNumberEdit.__init__(self,name,x,y,NumberEditWidth,NumberEditHeight,inititial,min,max,tooltip,tags)

class GTPosCounter:
    def __init__(self,start,step):
        self.value = start - step
        self.step  = step

    def Get(self):
        self.value = self.value + self.step

        return self.value

def CreateCircleVerts(mesh,height,radius,detalization,transform,v):
    result = []

    angle = 2.0 * math.pi / detalization

    for i in xrange(detalization):
        x = radius * math.sin(angle * i)
        y = radius * math.cos(angle * i)

        vect = GTMultMatrix4x4Vec4(transform,GTVector4(x,y,height,1.0))

        vert = Blender.NMesh.Vert(vect.x,vect.y,vect.z)

        u = float(i) / detalization

        vert.uvco.x = u
        vert.uvco.y = v

        result.append(len(mesh.verts))

        mesh.verts.append(vert)
    return result

def CreateCylinderFromCircles(mesh,c1_verts,c2_verts):
    detalization = len(c1_verts)

    for i in xrange(detalization):
        face = Blender.NMesh.Face()

        face.v.append(mesh.verts[c1_verts[i]])
        face.v.append(mesh.verts[c1_verts[(i + 1) % detalization]])
        face.v.append(mesh.verts[c2_verts[(i + 1) % detalization]])
        face.v.append(mesh.verts[c2_verts[i]])

        face.uv.append((mesh.verts[c1_verts[i]].uvco.x,mesh.verts[c1_verts[i]].uvco.y))
        face.uv.append((mesh.verts[c1_verts[(i + 1) % detalization]].uvco.x,mesh.verts[c1_verts[(i + 1) % detalization]].uvco.y))
        face.uv.append((mesh.verts[c2_verts[(i + 1) % detalization]].uvco.x,mesh.verts[c2_verts[(i + 1) % detalization]].uvco.y))
        face.uv.append((mesh.verts[c2_verts[i]].uvco.x,mesh.verts[c2_verts[i]].uvco.y))

        mesh.faces.append(face)

def GetSegRadiusBottom(Stem,SegIndex):
    segment = Stem.segments[SegIndex]

    if segment.parent is None:
        return Stem.radius
    else:
        return Stem.segments[segment.parent].radius

def GetSegRadiusTop(Stem,SegIndex):
    return Stem.segments[SegIndex].radius

def UpdateProgressBar(factor,msg):
    pass
#    Blender.Window.DrawProgressBar(factor,msg)
#    Blender.Draw.Draw()

def GenCylinderChunk(mesh,TreeData,Stem,SegIndex,ParentVerts,v,m):
    v = v + Stem.segments[SegIndex].length

    SelfVerts = CreateCircleVerts(mesh,Stem.segments[SegIndex].length,GetSegRadiusTop(Stem,SegIndex),len(ParentVerts),m,v)

    CreateCylinderFromCircles(mesh,ParentVerts,SelfVerts)

    for ChildIndex in Stem.segments[SegIndex].children:
        GenCylinderChunk(mesh,TreeData,Stem,ChildIndex,SelfVerts,v,GTMultMatrix4x4(m,Stem.segments[ChildIndex].transform))

def GenLeaf(mesh,TreeParam,LeafMeshData,m):
    LeafQualitySQRt = math.sqrt(TreeParam.LeafQuality)
    LeafLength  = TreeParam.LeafScale / LeafQualitySQRt
    LeafWidth   = TreeParam.LeafScale * TreeParam.LeafScaleX / LeafQualitySQRt

    BaseVertIndex = len(mesh.verts)

    for vi in xrange(len(LeafMeshData.verts)):
        x,y,z = LeafMeshData.verts[vi]
        u,v   = LeafMeshData.uvs[vi]
        vect = GTMultMatrix4x4Vec4(m,GTVector4(x * LeafWidth,y * LeafLength,z * LeafLength,1.0))
        vert = Blender.NMesh.Vert(vect.x,vect.y,vect.z)
        vert.uvco.x = u
        vert.uvco.y = v

        mesh.verts.append(vert)

    for fi in xrange(len(LeafMeshData.faces)):
        face = Blender.NMesh.Face()

        for vi in xrange(len(LeafMeshData.faces[fi])):
            face.v.append(mesh.verts[BaseVertIndex + LeafMeshData.faces[fi][vi]])
            if len(LeafMeshData.faceuvs) > 0:
                face.uv.append(LeafMeshData.faceuvs[fi][vi])

        mesh.faces.append(face)

def GetStemLevel(TreeData,Stem):
    Level    = 0
    CurrStem = Stem

    while CurrStem.parent_stem is not None:
        Level    = Level + 1
        CurrStem = TreeData.stems[CurrStem.parent_stem]

    return Level

def GenerationRun(TreeParam,Seed,Details,LeafMeshData):
    GTMathRNGSeed(Seed)

    Meshes = GTTreeMeshes()

#    start_time = time.time()

    TreeData = GenTree(TreeParam,UpdateProgressBar)

#    genstruct_time = time.time()

    for Stem in TreeData.stems:
        StemLevel = GetStemLevel(TreeData,Stem)
        mesh = Meshes.GetMesh(StemLevel)

#        if len(Stem.segments) > 0:
        if (StemLevel < TreeParam.Levels) or (TreeParam.Leaves == 0):
            Detail = GetMeshDetail(StemLevel)

            m = GTTreeSegmentToWorldMatrix(TreeData,Stem,0)

            SelfVerts = CreateCircleVerts(mesh,0.0,GetSegRadiusBottom(Stem,0),Detail,m,0.0)

            GenCylinderChunk(mesh,TreeData,Stem,0,SelfVerts,0.0,GTTreeSegmentToWorldMatrix(TreeData,Stem,0))
        else:
            GenLeaf(mesh,TreeParam,LeafMeshData,GTTreeLeafToWorldMatrix(TreeData,Stem))

#    finish_time = time.time()

    Meshes.PutMeshes()

    Blender.Redraw()

#    print 'Structure generation time: %.04f sec' % (genstruct_time - start_time)
#    print 'Meshes    generation time: %.04f sec' % (finish_time - genstruct_time)
#    print 'Total     generation time: %.04f sec' % (finish_time - start_time)

def AppendBranchParams(TreeParam,MaxCount):
    Count = MaxCount - len(TreeParam.Branches)

    if Count > 0:
        for Index in xrange(MaxCount):
            TreeParam.Branches.append(GTTreeBranchParam())

def QuoteTag(tag):
    return '@' + tag + '@'

def QuoteBranchTag(tag,index):
    return QuoteTag(tag + str(index))

def TransferParamsFromWindow(ws,TreeParam):
    AppendBranchParams(TreeParam,MaxBranchLevels)

    TreeParam.LeafQuality = ws.GetTaggedValue(QuoteTag('LEAFQUALITY'))
    TreeParam.LeafScaleX = ws.GetTaggedValue(QuoteTag('LEAFSCALEX'))
    TreeParam.LeafScale  = ws.GetTaggedValue(QuoteTag('LEAFSCALE'))
    TreeParam.Leaves     = ws.GetTaggedValue(QuoteTag('LEAVES'))
    TreeParam.RatioPower = ws.GetTaggedValue(QuoteTag('RATIOPOWER'))
    TreeParam.Ratio      = ws.GetTaggedValue(QuoteTag('RATIO'))
    TreeParam.Levels     = ws.GetTaggedValue(QuoteTag('LEVELS'))
    TreeParam.ZScaleV    = ws.GetTaggedValue(QuoteTag('ZSCALEV'))
    TreeParam.ZScale     = ws.GetTaggedValue(QuoteTag('ZSCALE'))
    TreeParam.ScaleV     = ws.GetTaggedValue(QuoteTag('SCALEV'))
    TreeParam.Scale      = ws.GetTaggedValue(QuoteTag('SCALE'))
    TreeParam.BaseSize   = ws.GetTaggedValue(QuoteTag('BASESIZE'))
    TreeParam.Shape      = ws.GetTaggedValue(QuoteTag('SHAPE'))

    for BranchIndex in xrange(MaxBranchLevels):
        BranchParam = TreeParam.Branches[BranchIndex]

        if BranchIndex > 0:
            BranchParam.Branches   = ws.GetTaggedValue(QuoteBranchTag('BRANCHES',BranchIndex))
            BranchParam.RotateV    = math.radians(ws.GetTaggedValue(QuoteBranchTag('RotateV',BranchIndex)))
            BranchParam.Rotate     = math.radians(ws.GetTaggedValue(QuoteBranchTag('Rotate',BranchIndex)))
            BranchParam.DownAngleV = math.radians(ws.GetTaggedValue(QuoteBranchTag('DownAngleV',BranchIndex)))
            BranchParam.DownAngle  = math.radians(ws.GetTaggedValue(QuoteBranchTag('DownAngle',BranchIndex)))
        else:
            BranchParam.Branches   = 0
            BranchParam.RotateV    = 0.0
            BranchParam.Rotate     = 0.0
            BranchParam.DownAngleV = 0.0
            BranchParam.DownAngle  = 0.0

        BranchParam.CurveV    = math.radians(ws.GetTaggedValue(QuoteBranchTag('CurveV',BranchIndex)))
        BranchParam.CurveBack = math.radians(ws.GetTaggedValue(QuoteBranchTag('CurveBack',BranchIndex)))
        BranchParam.Curve     = math.radians(ws.GetTaggedValue(QuoteBranchTag('Curve',BranchIndex)))

        BranchParam.CurveRes  = ws.GetTaggedValue(QuoteBranchTag('CurveRes',BranchIndex))

        BranchParam.SplitAngleV = math.radians(ws.GetTaggedValue(QuoteBranchTag('SplitAngleV',BranchIndex)))
        BranchParam.SplitAngle  = math.radians(ws.GetTaggedValue(QuoteBranchTag('SplitAngle',BranchIndex)))

        BranchParam.SegSplits = ws.GetTaggedValue(QuoteBranchTag('SegSplits',BranchIndex))

        if BranchIndex > 0:
            BranchParam.BaseSplits = 0
        else:
            BranchParam.BaseSplits = ws.GetTaggedValue(QuoteBranchTag('BaseSplits',BranchIndex))

        BranchParam.Taper   = ws.GetTaggedValue(QuoteBranchTag('Taper',BranchIndex))
        BranchParam.LengthV = ws.GetTaggedValue(QuoteBranchTag('LengthV',BranchIndex))
        BranchParam.Length  = ws.GetTaggedValue(QuoteBranchTag('Length',BranchIndex))

        if BranchIndex == 0:
            BranchParam.ScaleV = ws.GetTaggedValue(QuoteBranchTag('ScaleV',BranchIndex))
            BranchParam.Scale  = ws.GetTaggedValue(QuoteBranchTag('Scale',BranchIndex))

def NewSeedButtonClick():
    new_seed = GTMathRNGRandInt(1,0xFFFF)

    ws.SetTaggedValue(QuoteTag('Seed'),new_seed)

    Blender.Window.Redraw()

LeafMeshList = []

def RefreshLeafShapeListButtonClick():
    global LeafMeshList
    LeafShapeList = ws.GetControlByTag(QuoteTag('LEAFSHAPE'))
    LeafShapeList.ClearList()

    LeafShapeList.AppendItem('Circle',0,1)
    LeafShapeList.AppendItem('Quad',1)
    LeafShapeList.AppendItem('Hexagon',2)

    LeafShapeId = 3

    LeafMeshList = []

    for name in GetMeshesNamesByPrefix('Leaf'):
        LeafMeshList.append(name)
        LeafShapeList.AppendItem(name,LeafShapeId)

        LeafShapeId = LeafShapeId + 1

def CreateParamControls(ws,TreeParam):
    YPosCounter  = GTPosCounter(50,20)

    MaxY = 0

    X = 20

    ws.AppendControl(GTNumberEdit('LeafQuality',X,YPosCounter.Get(),TreeParam.LeafQuality,0.1,10.0,'Set leaf quality factor',QuoteTag('LEAFQUALITY')))
    ws.AppendControl(GTNumberEdit('LeafScaleX',X,YPosCounter.Get(),TreeParam.LeafScaleX,0.0,10.0,'Set leaf width scale',QuoteTag('LEAFSCALEX')))
    ws.AppendControl(GTNumberEdit('LeafScale',X,YPosCounter.Get(),TreeParam.LeafScale,0.0,10.0,'Set leaf scale',QuoteTag('LEAFSCALE')))

    LeafShapeList = ControlDropDownList('LeafShape',X,YPosCounter.Get(),NumberEditWidth,NumberEditHeight,'Set leaf shape',QuoteTag('LEAFSHAPE'))
    ws.AppendControl(LeafShapeList)

    RefreshLeafShapeListButtonClick()

    ws.AppendControl(ControlCommandButton('R',LeafShapeList.x + NumberEditWidth + 1,LeafShapeList.y,18,18,RefreshLeafShapeListButtonClick,'Refresh available leaf shapes list'))

    ws.AppendControl(GTNumberEdit('Leaves',X,YPosCounter.Get(),TreeParam.Leaves,0,1000,'Set leaves count',QuoteTag('LEAVES')))
    ws.AppendControl(GTNumberEdit('RatioPower',X,YPosCounter.Get(),TreeParam.RatioPower,0.0,100.0,'Set child branch radius power ratio',QuoteTag('RATIOPOWER')))
    ws.AppendControl(GTNumberEdit('Ratio',X,YPosCounter.Get(),TreeParam.Ratio,0.0,100.0,'Set trunk radius/length ratio',QuoteTag('RATIO')))
    ws.AppendControl(GTNumberEdit('Levels',X,YPosCounter.Get(),TreeParam.Levels,0,4,'Set branch level count',QuoteTag('LEVELS')))
    ws.AppendControl(GTNumberEdit('ZScaleV',X,YPosCounter.Get(),TreeParam.ZScaleV,0.0,1000.0,'Not used',QuoteTag('ZSCALEV')))
    ws.AppendControl(GTNumberEdit('ZScale',X,YPosCounter.Get(),TreeParam.ZScale,0.0,1000.0,'Not used',QuoteTag('ZSCALE')))
    ws.AppendControl(GTNumberEdit('ScaleV',X,YPosCounter.Get(),TreeParam.ScaleV,0.0,1000.0,'Set tree length scale variation',QuoteTag('SCALEV')))
    ws.AppendControl(GTNumberEdit('Scale',X,YPosCounter.Get(),TreeParam.Scale,0.0,1000.0,'Set tree length scale',QuoteTag('SCALE')))
    ws.AppendControl(GTNumberEdit('BaseSize',X,YPosCounter.Get(),TreeParam.BaseSize,0.0,0.99,'Set relative branchless area size',QuoteTag('BASESIZE')))

    ShapeList = ControlDropDownList('Shape',X,YPosCounter.Get(),NumberEditWidth,NumberEditHeight,'Set tree shape',QuoteTag('SHAPE'))

    ShapeList.AppendItem('Conical',0,1)
    ShapeList.AppendItem('Spherical',1)
    ShapeList.AppendItem('Hemispherical',2)
    ShapeList.AppendItem('Cylindrical',3)
    ShapeList.AppendItem('Tapered cylindrical',4)
    ShapeList.AppendItem('Flame',5)
    ShapeList.AppendItem('Inverse conical',6)
    ShapeList.AppendItem('Tend flame',7)

    ShapeList.SetValue(TreeParam.Shape)

    ws.AppendControl(ShapeList)

    X = X + NumberEditWidth + 20

    for BranchIndex in xrange(MaxBranchLevels):
        BranchParam = TreeParam.Branches[BranchIndex]

        YPosCounter  = GTPosCounter(50,20)

        if BranchIndex > 0:
            ws.AppendControl(GTNumberEdit('Branches',X,YPosCounter.Get(),BranchParam.Branches,0,10000,'Set max branch count',QuoteBranchTag('BRANCHES',BranchIndex)))
            ws.AppendControl(GTNumberEdit('RotateV',X,YPosCounter.Get(),math.degrees(BranchParam.RotateV),-360.0,360.0,'Set branch rotation angle step variation (about parent Z-axis)',QuoteBranchTag('RotateV',BranchIndex)))
            ws.AppendControl(GTNumberEdit('Rotate',X,YPosCounter.Get(),math.degrees(BranchParam.Rotate),-360.0,360.0,'Set branch rotation angle step (about parent Z-axis)',QuoteBranchTag('Rotate',BranchIndex)))
            ws.AppendControl(GTNumberEdit('DownAngleV',X,YPosCounter.Get(),math.degrees(BranchParam.DownAngleV),-360.0,360.0,'Set branch rotation angle step variation (about parent X-axis)',QuoteBranchTag('DownAngleV',BranchIndex)))
            ws.AppendControl(GTNumberEdit('DownAngle',X,YPosCounter.Get(),math.degrees(BranchParam.DownAngle),-360.0,360.0,'Set branch rotation angle step (about parent X-axis)',QuoteBranchTag('DownAngle',BranchIndex)))
        else:
            YPosCounter.Get()
            YPosCounter.Get()
            YPosCounter.Get()
            YPosCounter.Get()
            YPosCounter.Get()

        ws.AppendControl(GTNumberEdit('CurveV',X,YPosCounter.Get(),math.degrees(BranchParam.CurveV),-360.0,360.0,'Set segment rotation angle variation',QuoteBranchTag('CurveV',BranchIndex)))
        ws.AppendControl(GTNumberEdit('CurveBack',X,YPosCounter.Get(),math.degrees(BranchParam.CurveBack),-360.0,360.0,'Set segment rotation angle (for second half segments)',QuoteBranchTag('CurveBack',BranchIndex)))
        ws.AppendControl(GTNumberEdit('Curve',X,YPosCounter.Get(),math.degrees(BranchParam.Curve),-360.0,360.0,'Set segment rotation angle',QuoteBranchTag('Curve',BranchIndex)))
        ws.AppendControl(GTNumberEdit('CurveRes',X,YPosCounter.Get(),BranchParam.CurveRes,1,1000,'Set stem resolution (segment count)',QuoteBranchTag('CurveRes',BranchIndex)))
        ws.AppendControl(GTNumberEdit('SplitAngleV',X,YPosCounter.Get(),math.degrees(BranchParam.SplitAngleV),-360.0,360.0,'Set stem split angle variation',QuoteBranchTag('SplitAngleV',BranchIndex)))
        ws.AppendControl(GTNumberEdit('SplitAngle',X,YPosCounter.Get(),math.degrees(BranchParam.SplitAngle),-360.0,360.0,'Set stem split angle',QuoteBranchTag('SplitAngle',BranchIndex)))
        ws.AppendControl(GTNumberEdit('SegSplits',X,YPosCounter.Get(),BranchParam.SegSplits,0.0,100.0,'Stem split factor',QuoteBranchTag('SegSplits',BranchIndex)))

        if BranchIndex > 0:
            YPosCounter.Get()
        else:
            ws.AppendControl(GTNumberEdit('BaseSplits',X,YPosCounter.Get(),BranchParam.BaseSplits,0,100,'Trunk base split count',QuoteBranchTag('BaseSplits',BranchIndex)))

        ws.AppendControl(GTNumberEdit('Taper',X,YPosCounter.Get(),BranchParam.Taper,0.0,3.0,'Taper mode',QuoteBranchTag('Taper',BranchIndex)))
        ws.AppendControl(GTNumberEdit('LengthV',X,YPosCounter.Get(),BranchParam.LengthV,0.0,100.0,'Maximum branch relative length variation',QuoteBranchTag('LengthV',BranchIndex)))
        ws.AppendControl(GTNumberEdit('Length',X,YPosCounter.Get(),BranchParam.Length,0.0,100.0,'Maximum branch relative length',QuoteBranchTag('Length',BranchIndex)))

        if BranchIndex == 0:
            ws.AppendControl(GTNumberEdit('ScaleV',X,YPosCounter.Get(),BranchParam.ScaleV,0.0,100.0,'Trunk radius scale variation',QuoteBranchTag('ScaleV',BranchIndex)))
            ws.AppendControl(GTNumberEdit('Scale',X,YPosCounter.Get(),BranchParam.Scale,0.0,100.0,'Trunk radius scale',QuoteBranchTag('Scale',BranchIndex)))
        else:
            YPosCounter.Get()
            YPosCounter.Get()

        ws.AppendControl(GTNumberEdit('Detail',X,YPosCounter.Get(),MeshDetail[BranchIndex],3,256,'Cylinder faces',QuoteBranchTag('Detail',BranchIndex)))

        X = X + NumberEditWidth + 10

        MaxY = YPosCounter.Get()

    ws.AppendControl(GTNumberEdit('Seed',20,MaxY + 50,GTMathRNGRandInt(1,0xFFFF),1,0xFFFF,'Random number generator seed',QuoteTag('Seed')))
    ws.AppendControl(ControlCommandButton('New seed',20,MaxY + 25,100,20,NewSeedButtonClick,'Generate new seed'))

def SetParamControls(ws,TreeParam):
    ws.SetTaggedValue(QuoteTag('LEAFQUALITY'),TreeParam.LeafQuality)
    ws.SetTaggedValue(QuoteTag('LEAFSCALEX'),TreeParam.LeafScaleX)
    ws.SetTaggedValue(QuoteTag('LEAFSHAPE'),TreeParam.LeafShape)
    ws.SetTaggedValue(QuoteTag('LEAFSCALE'),TreeParam.LeafScale)
    ws.SetTaggedValue(QuoteTag('LEAVES'),TreeParam.Leaves)
    ws.SetTaggedValue(QuoteTag('RATIOPOWER'),TreeParam.RatioPower)
    ws.SetTaggedValue(QuoteTag('RATIO'),TreeParam.Ratio)
    ws.SetTaggedValue(QuoteTag('LEVELS'),TreeParam.Levels)
    ws.SetTaggedValue(QuoteTag('ZSCALEV'),TreeParam.ZScaleV)
    ws.SetTaggedValue(QuoteTag('ZSCALE'),TreeParam.ZScale)
    ws.SetTaggedValue(QuoteTag('SCALEV'),TreeParam.ScaleV)
    ws.SetTaggedValue(QuoteTag('SCALE'),TreeParam.Scale)
    ws.SetTaggedValue(QuoteTag('BASESIZE'),TreeParam.BaseSize)

    ws.SetTaggedValue(QuoteTag('SHAPE'),TreeParam.Shape)

    for BranchIndex in xrange(MaxBranchLevels):
        BranchParam = TreeParam.Branches[BranchIndex]

        if BranchIndex > 0:
            ws.SetTaggedValue(QuoteBranchTag('BRANCHES',BranchIndex),BranchParam.Branches)
            ws.SetTaggedValue(QuoteBranchTag('RotateV',BranchIndex),math.degrees(BranchParam.RotateV))
            ws.SetTaggedValue(QuoteBranchTag('Rotate',BranchIndex),math.degrees(BranchParam.Rotate))
            ws.SetTaggedValue(QuoteBranchTag('DownAngleV',BranchIndex),math.degrees(BranchParam.DownAngleV))
            ws.SetTaggedValue(QuoteBranchTag('DownAngle',BranchIndex),math.degrees(BranchParam.DownAngle))

        ws.SetTaggedValue(QuoteBranchTag('CurveV',BranchIndex),math.degrees(BranchParam.CurveV))
        ws.SetTaggedValue(QuoteBranchTag('CurveBack',BranchIndex),math.degrees(BranchParam.CurveBack))
        ws.SetTaggedValue(QuoteBranchTag('Curve',BranchIndex),math.degrees(BranchParam.Curve))
        ws.SetTaggedValue(QuoteBranchTag('CurveRes',BranchIndex),BranchParam.CurveRes)
        ws.SetTaggedValue(QuoteBranchTag('SplitAngleV',BranchIndex),math.degrees(BranchParam.SplitAngleV))
        ws.SetTaggedValue(QuoteBranchTag('SplitAngle',BranchIndex),math.degrees(BranchParam.SplitAngle))
        ws.SetTaggedValue(QuoteBranchTag('SegSplits',BranchIndex),BranchParam.SegSplits)

        if BranchIndex == 0:
            ws.SetTaggedValue(QuoteBranchTag('BaseSplits',BranchIndex),BranchParam.BaseSplits)

        ws.SetTaggedValue(QuoteBranchTag('Taper',BranchIndex),BranchParam.Taper)
        ws.SetTaggedValue(QuoteBranchTag('LengthV',BranchIndex),BranchParam.LengthV)
        ws.SetTaggedValue(QuoteBranchTag('Length',BranchIndex),BranchParam.Length)

        if BranchIndex == 0:
            ws.SetTaggedValue(QuoteBranchTag('ScaleV',BranchIndex),BranchParam.ScaleV)
            ws.SetTaggedValue(QuoteBranchTag('Scale',BranchIndex),BranchParam.Scale)

def GenerateButtonClick():
    TreeParam = GTTreeParam()

    TransferParamsFromWindow(ws,TreeParam)

    Seed = ws.GetTaggedValue(QuoteTag('Seed'))

    Details = []

    for Index in xrange(MaxBranchLevels):
        Details.append(ws.GetTaggedValue(QuoteBranchTag('Detail',Index)))

    # LeafMeshData

    LeafMeshId = ws.GetTaggedValue(QuoteTag('LEAFSHAPE'))

    if   LeafMeshId == 0:
        LeafMeshData = GTLeafMeshDataCircle(8)
    elif LeafMeshId == 1:
        LeafMeshData = GTLeafMeshDataRect()
    elif LeafMeshId == 2:
        LeafMeshData = GTLeafMeshDataHexagon()
    else:
        nmesh      = None
        LeafMeshId = LeafMeshId - 3

        if LeafMeshId < len(LeafMeshList):
            nmesh = GetNMeshByName(LeafMeshList[LeafMeshId])

        if nmesh is not None:
            LeafMeshData = GTLeafMeshDataUser(nmesh)
        else:
            Blender.Draw.PupMenu('ERROR%t|User-defined leaf mesh not found. aborting.' )
            return

    Blender.Window.WaitCursor(1)

    selection = Blender.Object.GetSelected()

    for obj in selection:
        obj.select(0)

#    GenerationRun(TreeParam,Seed,Details,LeafMeshData)
#    Blender.Window.WaitCursor(0)

    try:
        GenerationRun(TreeParam,Seed,Details,LeafMeshData)
    except Exception,err:
        Blender.Window.WaitCursor(0)
        Blender.Draw.PupMenu('ERROR%t|Unexpected error (' + str(err) + '). aborting.' )
    else:
        Blender.Window.WaitCursor(0)

def BlackTupeloButtonClick():
    TreeParam = GetTreeParamBlackTupelo()

    SetParamControls(ws,TreeParam)

    AppendBranchParams(TreeParam,MaxBranchLevels)

    Blender.Window.Redraw()

def CABlackOakButtonClick():
    TreeParam = GetTreeParamCABlackOak()

    SetParamControls(ws,TreeParam)

    AppendBranchParams(TreeParam,MaxBranchLevels)

    Blender.Window.Redraw()

def QuakingAspenButtonClick():
    TreeParam = GetTreeParamQuakingAspen()

    SetParamControls(ws,TreeParam)

    AppendBranchParams(TreeParam,MaxBranchLevels)

    Blender.Window.Redraw()

def ImportFileNameCallback(ImportFileName):
    if ImportFileName is not None:
        try:
            source = open(ImportFileName,'rt')

            TreeParam = GTImportParamsArbaro(source)

            source.close()

            AppendBranchParams(TreeParam,MaxBranchLevels)

            SetParamControls(ws,TreeParam)

            Blender.Window.Redraw()
        except Exception,err:
            Blender.Draw.PupMenu('ERROR%t|Unable to import file (' + str(err) + ')')

def ImportButtonClick():
    Blender.Window.FileSelector(ImportFileNameCallback,'IMPORT FILE','')

CurrentFileName = ''

def LoadFileNameCallback(SourceFileName):
    global CurrentFileName
    if SourceFileName is not None:
        try:
            source = open(SourceFileName,'rt')

            TreeParam = GTImportParamsGen3(source)

            source.close()

            AppendBranchParams(TreeParam,MaxBranchLevels)

            SetParamControls(ws,TreeParam)

            CurrentFileName = SourceFileName

            Blender.Window.Redraw()
        except Exception,err:
            Blender.Draw.PupMenu('ERROR%t|Unable to load file (' + str(err) + ')')

def LoadButtonClick():
    global CurrentFileName
    Blender.Window.FileSelector(LoadFileNameCallback,'LOAD FILE',CurrentFileName)

def SaveFileNameCallback(TargetFileName):
    global CurrentFileName
    if TargetFileName is not None:
        try:
            target = open(TargetFileName,'wt')

            TreeParam = GTTreeParam()

            TransferParamsFromWindow(ws,TreeParam)

            GTExportParamsGen3(target,TreeParam)

            target.close()

            CurrentFileName = TargetFileName
        except Exception,err:
            Blender.Draw.PupMenu('ERROR%t|Unable to save file (' + str(err) + ')')

def SaveButtonClick():
    global CurrentFileName
    Blender.Window.FileSelector(SaveFileNameCallback,'SAVE FILE',CurrentFileName)

def Init():
    TreeParam = GetTreeParamQuakingAspen()

    AppendBranchParams(TreeParam,MaxBranchLevels)

    CreateParamControls(ws,TreeParam)

ws = Workspace()

Init()

ws.ReorderControlsByColumns()

ws.AppendControl(ControlCommandButton('Generate',20,25,100,20,GenerateButtonClick,'Start tree generation'))
ws.AppendControl(ControlCommandButton('Black Tupelo',125,25,100,20,BlackTupeloButtonClick,'Set Black Tupelo parameters'))
ws.AppendControl(ControlCommandButton('CA Black Oak',230,25,100,20,CABlackOakButtonClick,'Set CA Black Oak parameters'))
ws.AppendControl(ControlCommandButton('Quaking Aspen',335,25,100,20,QuakingAspenButtonClick,'Set Quaking Aspen parameters'))

if GTImportParamsArbaro is not None:
    ws.AppendControl(ControlCommandButton('Import',20,1,100,20,ImportButtonClick,'Import parameters from external file'))

ws.AppendControl(ControlCommandButton('Load',125,1,100,20,LoadButtonClick,'Load parameters'))
ws.AppendControl(ControlCommandButton('Save',230,1,100,20,SaveButtonClick,'Save parameters'))

ws.Run()

