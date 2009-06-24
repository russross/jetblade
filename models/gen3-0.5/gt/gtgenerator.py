# --------------------------------------------------------------------------
# gtgenerator.py
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

# Tree structure generator module.
# Implements (partialy) model described in:
# Jason Weber and Joseph Penn, "Creation and Rendering of Realistic Trees",
# Proceedings of ACM SIGGRAPH 1995: pp. 119-128.

import math
#import random

from gttree   import *
from gtparams import *
from gtmath   import *

# General parameters calculation block

def CalcShapeRatio(Shape,Ratio):
    if   Shape == 0: # conical
        return 0.2 + 0.8 * Ratio
    elif Shape == 1: # spherical
        return 0.2 + 0.8 * math.sin(math.pi * Ratio)
    elif Shape == 2: # hemispherical
        return 0.2 + 0.8 * math.sin(0.5 * math.pi * Ratio)
    elif Shape == 3: # cylindrical
        return 1.0
    elif Shape == 4: # tapered cylindrical
        return 0.5 + 0.5 * Ratio
    elif Shape == 5: # flame
        if Ratio <= 0.7:
            return Ratio / 0.7
        else:
            return (1.0 - Ratio) / 0.3
    elif Shape == 6: # inverse conical
        return 1.0 - 0.8 * Ratio
    elif Shape == 7: # tend flame
        if Ratio <= 0.7:
            return 0.5 + 0.5 * Ratio / 0.7
        else:
            return 0.5 + 0.5 * (1.0 - Ratio) / 0.3
    else:
        raise RuntimeException,"invalid or unsupported shape"

def CalcScaleTree(Scale,ScaleV):
    return Scale + GTMathRNGUniform(-ScaleV,ScaleV)

def CalcLengthBase(BaseSize,ScaleTree):
    return BaseSize * ScaleTree

def CalcLengthChildMax(LengthN,LengthVN):
    return LengthN + GTMathRNGUniform(-LengthVN,LengthVN)

def CalcLengthTrunk(Length0,LengthV0,ScaleTree):
    return (Length0 + GTMathRNGUniform(-LengthV0,LengthV0)) * ScaleTree

def CalcLengthTrunkBranch(LengthTrunk,Length1,LengthV1,OffsetChild,Shape,LengthBase):
    return LengthTrunk * CalcLengthChildMax(Length1,LengthV1) *\
           CalcShapeRatio(Shape,(LengthTrunk - OffsetChild) / (LengthTrunk - LengthBase))

def CalcLengthBranchOther(LengthParent,LengthN,LenghVN,OffsetChild):
    return CalcLengthChildMax(LengthN,LenghVN) * (LengthParent - 0.6 * OffsetChild)

def CalcRadiusTrunk(LengthTrunk,Ratio,Scale0):
    return LengthTrunk * Ratio * Scale0

def CalcRadiusBranch(RadiusParent,LengthBranch,LengthParent,RatioPower):
    #FIXME: Is RadiusParent equal to maximum parent radius or to parent radius at
    #       branch point?
    return RadiusParent * math.pow(LengthBranch / LengthParent,RatioPower)

def CalcRadiusByTaper(Taper,StemLength,StemRadius,NormZ):
    if   Taper < 0.0:
        raise RuntimeException,"taper value must be positive"
    elif Taper < 1.0:
        unit_taper = Taper
    elif Taper < 2.0:
        unit_taper = 2.0 - Taper
    elif Taper <= 3.0:
        unit_taper = 0.0
    else:
        raise RuntimeException,"taper value must <= 3.0"

    taperZ = StemRadius * (1.0 - unit_taper * NormZ)

    if Taper < 1.0:
        return taperZ
    else:
        z2 = (1.0 - NormZ) * StemLength

        if (Taper < 2.0) or (z2 < taperZ):
            depth = 1.0
        else:
            depth = Taper - 2.0

        if Taper < 2.0:
            z3 = z2
        else:
            z3 = math.fabs(z2 - 2.0 * taperZ * int(z2 / (2.0 * taperZ) + 0.5))

        if (Taper < 2.0) and (z3 >= taperZ):
            return taperZ
        else:
            return (1.0 - depth) * taperZ + depth * math.sqrt(taperZ * taperZ - (z3 - taperZ) * (z3 - taperZ))

# Tree geometry helpers

def CalcDeclinationAngle(TreeData,Stem,SegIndex):
    z = GTVector4(0.0,0.0,1.0,0.0)

    CurrSegIndex = SegIndex

    while Stem is not None:
        while CurrSegIndex is not None:
            z = GTMultMatrix4x4Vec4(Stem.segments[CurrSegIndex].transform,z)

            CurrSegIndex = Stem.segments[CurrSegIndex].parent

        if Stem.parent_stem is None:
            Stem = None
        else:
            CurrSegIndex = Stem.parent_segment
            Stem         = TreeData.stems[Stem.parent_stem]

    angle = math.acos(z.z)

    return angle

def WorldZToSegmentSpace(TreeData,Stem,SegIndex):
    m = GTMatrix4x4()
    m.SetIdentity()

    while Stem is not None:
        while SegIndex is not None:
            lm = Stem.segments[SegIndex].transform.GetRotationOnly().GetTranspose()

            m = GTMultMatrix4x4(m,lm)

            SegIndex = Stem.segments[SegIndex].parent

        if Stem.parent_stem is None:
            Stem = None
        else:
            SegIndex = Stem.parent_segment
            Stem     = TreeData.stems[Stem.parent_stem]

    lz = GTVector4(0.0,0.0,1.0,0.0)

    z = GTMultMatrix4x4Vec4(m,lz)

    return GTVector3(z.x,z.y,z.z)

class StemGenState:
    def __init__(self):
        self.SplitError = 0.0

def GenStemSegmentsChunk(TreeParam,TreeData,Stem,GenState,Level,SegIndex,SegCount,SegLength,SegGlobIndex):

    BranchParam = TreeParam.GetBranchParam(Level)

    while SegIndex < (SegCount - 1):
        if (Level == 0) and (SegIndex == 0):
            SplitCount = BranchParam.BaseSplits
        else:
            SplitCount = FloatRound(BranchParam.SegSplits + GenState.SplitError)
            GenState.SplitError = GenState.SplitError - (SplitCount - BranchParam.SegSplits)

        if SplitCount > 0:
            m_tr = GTMatrix4x4()
            m_tr.SetTranslation(0.0,0.0,SegLength)

            declination = CalcDeclinationAngle(TreeData,Stem,SegGlobIndex)

            SegIndex = SegIndex + 1

            world_z = WorldZToSegmentSpace(TreeData,Stem,SegGlobIndex)

            for SplitIndex in xrange(SplitCount + 1):
                AngleSplit = BranchParam.SplitAngle +\
                             GTMathRNGUniform(-BranchParam.SplitAngleV,BranchParam.SplitAngleV) - \
                             declination

                if AngleSplit < 0.0:
                    AngleSplit = 0.0

                m_rot = GTMatrix4x4()
                m_rot.SetRotationX(AngleSplit)

                temp_rnd = GTMathRNGUniform(0.0,1.0)

                WorldZAngle = 20.0 + 0.75 * (30.0 + math.fabs(declination - math.pi / 2.0)) * temp_rnd * temp_rnd

                if GTMathRNGUniform(0.0,1.0) >= 0.5:
                    WorldZAngle = -WorldZAngle

                w_rot = GTMatrix4x4()
                w_rot.SetRotation(world_z,WorldZAngle)

                m_rot = GTMultMatrix4x4(w_rot,m_rot)

                Stem.segments[SegGlobIndex].children.append(len(Stem.segments))

                segment = GTSegment(SegGlobIndex,SegLength)
                segment.radius    = CalcRadiusByTaper(BranchParam.Taper,Stem.length,Stem.radius,float(SegIndex + 1) / SegCount)
                segment.transform = GTMultMatrix4x4(m_tr,m_rot)

                Stem.segments.append(segment)

                GenStemSegmentsChunk(TreeParam,TreeData,Stem,GenState,Level,SegIndex,SegCount,SegLength,len(Stem.segments) - 1)
            return
        else:
            if FloatEqualToZero(BranchParam.CurveBack):
                RotXAngle = BranchParam.Curve / BranchParam.CurveRes
            else:
                if SegIndex < (SegCount / 2):
                    RotXAngle = BranchParam.Curve / (BranchParam.CurveRes / 2)
                else:
                    RotXAngle = BranchParam.CurveBack / (BranchParam.CurveRes / 2)

            #FIXME: Negative CurveV mode (helix stems) is not supported

            RotXAngle = RotXAngle + \
                         GTMathRNGUniform(-BranchParam.CurveV,BranchParam.CurveV) / \
                          BranchParam.CurveRes

            m_rot = GTMatrix4x4()
            m_rot.SetRotationX(RotXAngle)

            m_tr = GTMatrix4x4()
            m_tr.SetTranslation(0.0,0.0,SegLength)

            Stem.segments[SegGlobIndex].children.append(len(Stem.segments))

            segment           = GTSegment(SegGlobIndex,SegLength)
            segment.radius    = CalcRadiusByTaper(BranchParam.Taper,Stem.length,Stem.radius,(SegIndex + 2.0) / SegCount)
            segment.transform = GTMultMatrix4x4(m_tr,m_rot)

            Stem.segments.append(segment)

            SegGlobIndex = len(Stem.segments) - 1

            SegIndex = SegIndex + 1

def GenStemSegments(TreeParam,TreeData,Stem,GenState,Level,SegCount,StemLength,SegTransform):
    SegLength = StemLength / SegCount

    base_segment        = GTSegment(None,SegLength)
    base_segment.radius = CalcRadiusByTaper(TreeParam.GetBranchParam(Level).Taper,Stem.length,Stem.radius,1.0 / SegCount)

    if SegTransform is None:
        base_segment.transform.SetIdentity()
    else:
        base_segment.transform = SegTransform.Clone()

    Stem.segments.append(base_segment)

    GenStemSegmentsChunk(TreeParam,TreeData,Stem,GenState,Level,0,SegCount,SegLength,0)

# Single stem generation block
def GenStem(TreeParam,TreeData,Level,ParentStem,ScaleTree,LengthBase,ChildOffset=None,ChildTransform=None,ParentSegment=None,ProgressFunc=None):
    if ProgressFunc is not None:
        ProgressFunc(float(Level) / (TreeParam.Levels + 1.0),'Generating level %u' % (Level))

    BranchParam = TreeParam.GetBranchParam(Level)

    if   Level == 0:
        StemLength = CalcLengthTrunk(BranchParam.Length,
                                     BranchParam.LengthV,
                                     ScaleTree)
        StemRadius = CalcRadiusTrunk(StemLength,TreeParam.Ratio,BranchParam.Scale)
    elif Level == 1:
        StemLength = CalcLengthTrunkBranch(TreeData.stems[ParentStem].length,BranchParam.Length,BranchParam.LengthV,ChildOffset,TreeParam.Shape,CalcLengthBase(TreeParam.BaseSize,ScaleTree))
        StemRadius = CalcRadiusBranch(TreeData.stems[ParentStem].radius,StemLength,TreeData.stems[ParentStem].length,TreeParam.RatioPower)
    else:
        StemLength = CalcLengthBranchOther(TreeData.stems[ParentStem].length,BranchParam.Length,BranchParam.LengthV,ChildOffset)
        StemRadius = CalcRadiusBranch(TreeData.stems[ParentStem].radius,StemLength,TreeData.stems[ParentStem].length,TreeParam.RatioPower)

    if FloatEqualToZero(StemLength):
        return

    Stem = GTStem(StemLength,StemRadius)
    Stem.parent_stem    = ParentStem
    Stem.parent_segment = ParentSegment

    SelfStemIndex = len(TreeData.stems)

    TreeData.stems.append(Stem)

    GenState = StemGenState()

    GenStemSegments(TreeParam,TreeData,Stem,GenState,Level,BranchParam.CurveRes,StemLength,ChildTransform)

    if Level < TreeParam.Levels:
        # Generate branches

        ChildBranchParam = TreeParam.GetBranchParam(Level + 1)

        LeavesMode = 0

        if TreeParam.Leaves != 0:
            if Level == TreeParam.Levels - 1:
                LeavesMode = 1

        if LeavesMode:
            StemsMax = TreeParam.Leaves

            if StemsMax < 0:
                #FIXME: fan mode not supported for a while
                StemsMax = -StemsMax

            if Level == 0:
                StemsCount = int((1.0 - TreeParam.BaseSize) * StemsMax + 0.5)
                BaseOffset = LengthBase
            else:
                StemsCount = int(StemsMax * CalcShapeRatio(4.0,ChildOffset / TreeData.stems[Stem.parent_stem].length) * TreeParam.LeafQuality)
                BaseOffset = 0.0
        else:
            StemsMax = ChildBranchParam.Branches

            if   Level == 0:
                StemsCount = int(StemsMax * (StemLength / CalcLengthTrunk(BranchParam.Length,0.0,ScaleTree)) + 0.5)
                BaseOffset = LengthBase
            elif Level == 1:
                StemsCount = int(StemsMax * (0.2 + 0.8 * (StemLength / TreeData.stems[Stem.parent_stem].length) / CalcLengthChildMax(ChildBranchParam.Length,ChildBranchParam.LengthV)) + 0.5)
                BaseOffset = 0.0
            else:
                StemsCount = int(StemsMax * (1.0 - 0.5 * ChildOffset / TreeData.stems[Stem.parent_stem].length) + 0.5)
                BaseOffset = 0.0

        if StemsCount > 0:
            SegLength       = StemLength / BranchParam.CurveRes;
            StemTotalLength = len(Stem.segments) * SegLength
            OffsetStep      = (StemTotalLength - BaseOffset) / StemsCount

            ZRotation = 0.0

            for StemIndex in xrange(StemsCount):
                GlobOffset      = BaseOffset + OffsetStep * StemIndex
                ParentSegIndex  = int(GlobOffset / SegLength)

                BranchOffset = GlobOffset - ParentSegIndex * SegLength
                StemOffset   = BranchOffset

                s = Stem.segments[ParentSegIndex]

                while s.parent is not None:
                    StemOffset = StemOffset + SegLength

                    s = Stem.segments[s.parent]

                if ChildBranchParam.DownAngleV < 0.0:
                    #FIXME: not completely correct (look at +/- sign in expression)
                    XRotAngle = ChildBranchParam.DownAngle +\
                                 ChildBranchParam.DownAngleV * (1.0 - 2.0 * CalcShapeRatio(0,\
                                  (StemLength - StemOffset) / \
                                  (StemLength - LengthBase)))
                else:
                    XRotAngle = ChildBranchParam.DownAngle +\
                                GTMathRNGUniform(-ChildBranchParam.DownAngleV,\
                                                  ChildBranchParam.DownAngleV)

                m_rot = GTMatrix4x4()
                m_rot.SetRotationX(XRotAngle)

                if ChildBranchParam.Rotate < 0.0:
                    ZRotAngle = math.pi + ChildBranchParam.Rotate + \
                            GTMathRNGUniform(-ChildBranchParam.RotateV,\
                                              ChildBranchParam.RotateV)
                    if (StemIndex % 2) == 0:
                        ZRotAngle = -ZRotAngle

                    ZRotation = ZRotAngle
                else:
                    ZRotAngle = ChildBranchParam.Rotate + \
                                GTMathRNGUniform(-ChildBranchParam.RotateV,\
                                                  ChildBranchParam.RotateV)

                    ZRotation = ZRotation + ZRotAngle

                while ZRotation >= (2.0 * math.pi):
                    ZRotation = ZRotation - 2.0 * math.pi

                while ZRotation <= (-2.0 * math.pi):
                    ZRotation = ZRotation + 2.0 * math.pi

                m_rotz = GTMatrix4x4()

                m_rotz.SetRotationZ(ZRotation)

                m_rot = GTMultMatrix4x4(m_rotz,m_rot)

                m_tr = GTMatrix4x4()
                m_tr.SetTranslation(0.0,0.0,BranchOffset)

                m = GTMultMatrix4x4(m_tr,m_rot)

                if LeavesMode:
                    Leave = GTLeaf()
                    Leave.parent_stem    = SelfStemIndex
                    Leave.parent_segment = ParentSegIndex
                    Leave.parent_offset  = StemOffset
                    Leave.transform      = m.Clone()

                    TreeData.stems.append(Leave)
                else:
                    GenStem(TreeParam,TreeData,Level + 1,SelfStemIndex,ScaleTree,LengthBase,StemOffset,m,ParentSegIndex)

def GenTree(TreeParam,ProgressFunc=None):
    ScaleTree  = CalcScaleTree(TreeParam.Scale,TreeParam.ScaleV)
    LengthBase = CalcLengthBase(TreeParam.BaseSize,ScaleTree)

    TreeData = GTTree()

    GenStem(TreeParam,TreeData,0,None,ScaleTree,LengthBase,None,None,None,ProgressFunc)

    return TreeData

def _GTGenTestDumpStem(TreeData,Stem):
    print 'Stem data: (%u segments)' % (len(Stem.segments))
    if len(Stem.segments) == 0:
        print 'Leaf'
        return

    segment_length = Stem.segments[0].length
    for i in xrange(len(Stem.segments)):
        v = GTTreeSegmentPointToWorldSpace(TreeData,Stem,i,0.0,0.0,segment_length)
        print 'segment tip: %.04f %.04f %.04f %.04f' % (v.x,v.y,v.z,v.w)
        if Stem.segments[i].parent is None:
            print 'segment parent: None'
        else:
            print 'segment parent: %u' % (Stem.segments[i].parent)

def _GTGeneratorSelfTest():
    TreeParam = GTTreeParam()
    TreeParam.Shape      = 0
    TreeParam.BaseSize   = 0.05
    TreeParam.Scale      = 1.0
    TreeParam.ScaleV     = 0.0
    TreeParam.ZScale     = 1.0
    TreeParam.ZScaleV    = 0.0
    TreeParam.Levels     = 1
    TreeParam.Ratio      = 0.1
    TreeParam.RatioPower = 1.0
    TreeParam.Lobes      = 1
    TreeParam.LobeDepth  = 0.1
    TreeParam.Flare      = 1.0

    BranchParams = GTTreeBranchParam()

    BranchParams.Scale       = 1.0
    BranchParams.ScaleV      = 0.0
    BranchParams.Length      = 1.0
    BranchParams.LengthV     = 0.0
    BranchParams.Taper       = 1.0
    BranchParams.BaseSplits  = 0
    BranchParams.SegSplits   = 1
    BranchParams.SplitAngle  = math.radians(90.0)
    BranchParams.SplitAngleV = 0.0
    BranchParams.CurveRes    = 4
    BranchParams.Curve       = math.radians(45.0 * 4)
    BranchParams.CurveBack   = 0.0
    BranchParams.CurveV      = 0.0

    TreeParam.Branches.append(BranchParams)

#    TreeParam = GetTreeParamCABlackOak()
#    TreeParam = GetTreeParamBlackTupelo()
    TreeParam = GetTreeParamQuakingAspen()

#    TreeParam.Levels = 3

    GTMathRNGSeed(111)

    TreeData = GenTree(TreeParam)

    for stem in TreeData.stems:
        _GTGenTestDumpStem(TreeData,stem)

if __name__ == '__main__':
    _GTGeneratorSelfTest()

