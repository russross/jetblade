# --------------------------------------------------------------------------
# gtparams.py
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

# Tree parameters module.
# 'Quaken Aspen', 'Weeping Willow', 'CA Black Oak' and 'Black Tupelo'
# predefined parameters taken from:
# Jason Weber and Joseph Penn, "Creation and Rendering of Realistic Trees",
# Proceedings of ACM SIGGRAPH 1995: pp. 119-128.

import math

class GTTreeBranchParam:
    def __init__(self):
        self.Scale       = 1.0 # Trunk only
        self.ScaleV      = 0.0 # Trunk only
        self.Length      = 1.0
        self.LengthV     = 0.0
        self.Taper       = 0
        self.BaseSplits  = 0   # Trunk only
        self.SegSplits   = 0.0
        self.SplitAngle  = 0.0
        self.SplitAngleV = 0.0
        self.CurveRes    = 1
        self.Curve       = 0.0
        self.CurveBack   = 0.0
        self.CurveV      = 0.0

        self.DownAngle   = 0.0 # Branches only
        self.DownAngleV  = 0.0 # Branches only
        self.Rotate      = 0.0 # Branches only
        self.RotateV     = 0.0 # Branches only
        self.Branches    = 0   # Branches only

class GTTreeParam:
    def __init__(self):
        self.Shape      = 0
        self.BaseSize   = 0.0 # Relative size of branchless area of the trunk
        self.Scale      = 1.0
        self.ScaleV     = 0.0
        self.ZScale     = 0.0
        self.ZScaleV    = 0.0
        self.Levels     = 1
        self.Ratio      = 0.02
        self.RatioPower = 1.0
        self.Lobes      = 1
        self.LobeDepth  = 0.1
        self.Flare      = 1.0

        self.Leaves      = 0
        self.LeafShape   = 0
        self.LeafScale   = 0.1
        self.LeafScaleX  = 1.0

        self.LeafQuality = 1.0

        self.Branches   = []

    def GetBranchParam(self,Level):
        BranchCount = len(self.Branches)

        if BranchCount > 0:
            if   Level < BranchCount:
                return self.Branches[Level]
            else:
                return self.Branches[BranchCount - 1]
        else:
            raise RuntimeError,'Tree must contain at least one level'

def GetTreeParamQuakingAspen():
    result = GTTreeParam()

    result.Shape = 7
    result.BaseSize = 0.4

    result.Scale      = 13.0
    result.ScaleV     = 3.0
    result.ZScale     = 1.0
    result.ZScaleV    = 0.0
    result.Levels     = 3
    result.Ratio      = 0.015
    result.RatioPower = 1.2
    result.Lobes      = 5
    result.LobeDepth  = 0.07
    result.Flare      = 0.6

    result.Leaves      = 25
    result.LeafShape   = 0
    result.LeafScale   = 0.17
    result.LeafScaleX  = 1.0

    # 0
    branch_params = GTTreeBranchParam()

    branch_params.Scale       = 1.0
    branch_params.ScaleV      = 0.0
    branch_params.Length      = 1.0
    branch_params.LengthV     = 0.0
    branch_params.Taper       = 1.0
    branch_params.BaseSplits  = 0
    branch_params.SegSplits   = 0.0
    branch_params.SplitAngle  = 0.0
    branch_params.SplitAngleV = 0.0
    branch_params.CurveRes    = 3
    branch_params.Curve       = 0.0
    branch_params.CurveBack   = 0.0
    branch_params.CurveV      = 20.0 * math.pi / 180.0

    result.Branches.append(branch_params)

    # 1
    branch_params = GTTreeBranchParam()

    branch_params.Length      = 0.3
    branch_params.LengthV     = 0.0
    branch_params.Taper       = 1.0
    branch_params.SegSplits   = 0.0
    branch_params.SplitAngle  = 0.0
    branch_params.SplitAngleV = 0.0
    branch_params.CurveRes    = 5
    branch_params.Curve       = -40.0 * math.pi / 180.0
    branch_params.CurveBack   = 0.0
    branch_params.CurveV      = 50.0 * math.pi / 180.0

    branch_params.DownAngle   =  60.0 * math.pi / 180.0
    branch_params.DownAngleV  = -50.0 * math.pi / 180.0
    branch_params.Rotate      = 140.0 * math.pi / 180.0
    branch_params.RotateV     =   0.0
    branch_params.Branches    =  50

    result.Branches.append(branch_params)

    # 2
    branch_params = GTTreeBranchParam()

    branch_params.Length      = 0.6
    branch_params.LengthV     = 0.0
    branch_params.Taper       = 1.0
    branch_params.SegSplits   = 0.0
    branch_params.SplitAngle  = 0.0
    branch_params.SplitAngleV = 0.0
    branch_params.CurveRes    = 3
    branch_params.Curve       = -40.0 * math.pi / 180.0
    branch_params.CurveBack   = 0.0
    branch_params.CurveV      = 75.0 * math.pi / 180.0

    branch_params.DownAngle   =  45.0 * math.pi / 180.0
    branch_params.DownAngleV  =  10.0 * math.pi / 180.0
    branch_params.Rotate      =  140.0 * math.pi / 180.0
    branch_params.RotateV     =   0.0
    branch_params.Branches    =  30

    result.Branches.append(branch_params)

    # 3
    branch_params = GTTreeBranchParam()

    branch_params.Length      = 0.0
    branch_params.LengthV     = 0.0
    branch_params.Taper       = 1
    branch_params.SegSplits   = 0
    branch_params.SplitAngle  = 0.0
    branch_params.SplitAngleV = 0.0
    branch_params.CurveRes    = 1
    branch_params.Curve       = 0.0
    branch_params.CurveBack   = 0.0
    branch_params.CurveV      = 0.0

    branch_params.DownAngle   =  45.0 * math.pi / 180.0
    branch_params.DownAngleV  =  10.0 * math.pi / 180.0
    branch_params.Rotate      =  77.0 * math.pi / 180.0
    branch_params.RotateV     =  0.0
    branch_params.Branches    =  10

    result.Branches.append(branch_params)

    return result


def GetTreeParamCABlackOak():
    result = GTTreeParam()

    result.Shape = 2
    result.BaseSize = 0.05

    result.Scale      = 10.0
    result.ScaleV     = 10.0
    result.ZScale     = 1.0
    result.ZScaleV    = 0.0
    result.Levels     = 3
    result.Ratio      = 0.018
    result.RatioPower = 1.3
    result.Lobes      = 5
    result.LobeDepth  = 0.1
    result.Flare      = 1.2

    result.Leaves      = 25
    result.LeafShape   = 0
    result.LeafScale   = 0.12
    result.LeafScaleX  = 0.66

    branch_params = GTTreeBranchParam()

    branch_params.Scale       = 1.0
    branch_params.ScaleV      = 0.0
    branch_params.Length      = 1.0
    branch_params.LengthV     = 0.0
    branch_params.Taper       = 0.95
    branch_params.BaseSplits  = 2
    branch_params.SegSplits   = 0.4
    branch_params.SplitAngle  = 10.0 * math.pi / 180.0
    branch_params.SplitAngleV = 0.0
    branch_params.CurveRes    = 8
    branch_params.Curve       = 0.0
    branch_params.CurveBack   = 0.0
    branch_params.CurveV      = 90.0 * math.pi / 180.0

    result.Branches.append(branch_params)

    branch_params = GTTreeBranchParam()

    branch_params.Length      = 0.8
    branch_params.LengthV     = 0.1
    branch_params.Taper       = 1
    branch_params.SegSplits   = 0.2
    branch_params.SplitAngle  = 10.0 * math.pi / 180.0
    branch_params.SplitAngleV = 10.0 * math.pi / 180.0
    branch_params.CurveRes    = 10
    branch_params.Curve       = 40.0 * math.pi / 180.0
    branch_params.CurveBack   = -70.0 * math.pi / 180.0
    branch_params.CurveV      = 150.0 * math.pi / 180.0

    branch_params.DownAngle   =  30.0 * math.pi / 180.0
    branch_params.DownAngleV  = -30.0 * math.pi / 180.0
    branch_params.Rotate      =  80.0 * math.pi / 180.0
    branch_params.RotateV     =   0.0
    branch_params.Branches    =  40

    result.Branches.append(branch_params)

    branch_params = GTTreeBranchParam()

    branch_params.Length      = 0.2
    branch_params.LengthV     = 0.05
    branch_params.Taper       = 1
    branch_params.SegSplits   = 0.1
    branch_params.SplitAngle  = 10.0 * math.pi / 180.0
    branch_params.SplitAngleV = 10.0 * math.pi / 180.0
    branch_params.CurveRes    = 3
    branch_params.Curve       = 0.0
    branch_params.CurveBack   = 0.0
    branch_params.CurveV      = -30.0 * math.pi / 180.0

    branch_params.DownAngle   =  45.0 * math.pi / 180.0
    branch_params.DownAngleV  =  10.0 * math.pi / 180.0
    branch_params.Rotate      =  140.0 * math.pi / 180.0
    branch_params.RotateV     =   0.0
    branch_params.Branches    =  120

    result.Branches.append(branch_params)

    branch_params = GTTreeBranchParam()

    branch_params.Length      = 0.4
    branch_params.LengthV     = 0.0
    branch_params.Taper       = 1
    branch_params.SegSplits   = 0
    branch_params.SplitAngle  = 0.0
    branch_params.SplitAngleV = 0.0
    branch_params.CurveRes    = 1
    branch_params.Curve       = 0.0
    branch_params.CurveBack   = 0.0
    branch_params.CurveV      = 0.0

    branch_params.DownAngle   =  45.0 * math.pi / 180.0
    branch_params.DownAngleV  =  10.0 * math.pi / 180.0
    branch_params.Rotate      =  140.0 * math.pi / 180.0
    branch_params.RotateV     =   0.0
    branch_params.Branches    =   0

    result.Branches.append(branch_params)

    return result

def GetTreeParamBlackTupelo():
    result = GTTreeParam()

    result.Shape = 4
    result.BaseSize = 0.2

    result.Scale      = 23.0
    result.ScaleV     = 5.0
    result.ZScale     = 1.0
    result.ZScaleV    = 0.0
    result.Levels     = 4
    result.Ratio      = 0.015
    result.RatioPower = 1.3
    result.Lobes      = 3
    result.LobeDepth  = 0.1
    result.Flare      = 1.0

    result.Leaves      = 6
    result.LeafShape   = 0
    result.LeafScale   = 0.3
    result.LeafScaleX  = 0.5

    branch_params = GTTreeBranchParam()

    branch_params.Scale       = 1.0
    branch_params.ScaleV      = 0.0
    branch_params.Length      = 1.0
    branch_params.LengthV     = 0.0
    branch_params.Taper       = 1.1
    branch_params.BaseSplits  = 0
    branch_params.SegSplits   = 0.0
    branch_params.SplitAngle  = 0.0
    branch_params.SplitAngleV = 0.0
    branch_params.CurveRes    = 10
    branch_params.Curve       = 0.0
    branch_params.CurveBack   = 0.0
    branch_params.CurveV      = 40.0 * math.pi / 180.0

    result.Branches.append(branch_params)

    branch_params = GTTreeBranchParam()

    branch_params.Length      = 0.3
    branch_params.LengthV     = 0.05
    branch_params.Taper       = 1
    branch_params.SegSplits   = 0.0
    branch_params.SplitAngle  = 0.0
    branch_params.SplitAngleV = 0.0
    branch_params.CurveRes    = 10
    branch_params.Curve       = 0.0
    branch_params.CurveBack   = 0.0
    branch_params.CurveV      = 90.0 * math.pi / 180.0

    branch_params.DownAngle   =  60.0 * math.pi / 180.0
    branch_params.DownAngleV  = -40.0 * math.pi / 180.0
    branch_params.Rotate      = 140.0 * math.pi / 180.0
    branch_params.RotateV     =   0.0
    branch_params.Branches    =  50

    result.Branches.append(branch_params)

    branch_params = GTTreeBranchParam()

    branch_params.Length      = 0.6
    branch_params.LengthV     = 0.1
    branch_params.Taper       = 1
    branch_params.SegSplits   = 0.0
    branch_params.SplitAngle  = 0.0
    branch_params.SplitAngleV = 0.0
    branch_params.CurveRes    = 10
    branch_params.Curve       = -10.0 * math.pi / 180.0
    branch_params.CurveBack   = 0.0
    branch_params.CurveV      = 150.0 * math.pi / 180.0

    branch_params.DownAngle   =  30.0 * math.pi / 180.0
    branch_params.DownAngleV  =  10.0 * math.pi / 180.0
    branch_params.Rotate      =  140.0 * math.pi / 180.0
    branch_params.RotateV     =   0.0
    branch_params.Branches    =  25

    result.Branches.append(branch_params)

    branch_params = GTTreeBranchParam()

    branch_params.Length      = 0.4
    branch_params.LengthV     = 0.0
    branch_params.Taper       = 1
    branch_params.SegSplits   = 0
    branch_params.SplitAngle  = 0.0
    branch_params.SplitAngleV = 0.0
    branch_params.CurveRes    = 1
    branch_params.Curve       = 0.0
    branch_params.CurveBack   = 0.0
    branch_params.CurveV      = 0.0

    branch_params.DownAngle   =  45.0 * math.pi / 180.0
    branch_params.DownAngleV  =  10.0 * math.pi / 180.0
    branch_params.Rotate      =  140.0 * math.pi / 180.0
    branch_params.RotateV     =   0.0
    branch_params.Branches    =   12

    result.Branches.append(branch_params)

    return result

def GetTreeParamWeepingWillow():
    result = GTTreeParam()

    result.Shape = 3
    result.BaseSize = 0.05

    result.Scale      = 15.0
    result.ScaleV     = 5.0
    result.ZScale     = 1.0
    result.ZScaleV    = 0.0
    result.Levels     = 4
    result.Ratio      = 0.03
    result.RatioPower = 2.0
    result.Lobes      = 9
    result.LobeDepth  = 0.03
    result.Flare      = 0.75

    result.Leaves      = 15
    result.LeafShape   = 0
    result.LeafScale   = 0.12
    result.LeafScaleX  = 0.2

    # 0
    branch_params = GTTreeBranchParam()

    branch_params.Scale       = 1.0
    branch_params.ScaleV      = 0.0
    branch_params.Length      = 0.8
    branch_params.LengthV     = 0.0
    branch_params.Taper       = 1.0
    branch_params.BaseSplits  = 2
    branch_params.SegSplits   = 0.1
    branch_params.SplitAngle  = 3.0 * math.pi / 180.0
    branch_params.SplitAngleV = 0.0
    branch_params.CurveRes    = 8
    branch_params.Curve       = 0.0
    branch_params.CurveBack   = 20.0 * math.pi / 180.0
    branch_params.CurveV      = 120.0 * math.pi / 180.0

    result.Branches.append(branch_params)

    # 1
    branch_params = GTTreeBranchParam()

    branch_params.Length      = 0.5
    branch_params.LengthV     = 0.1
    branch_params.Taper       = 1.0
    branch_params.SegSplits   = 0.2
    branch_params.SplitAngle  = 30.0 * math.pi / 180.0
    branch_params.SplitAngleV = 10.0 * math.pi / 180.0
    branch_params.CurveRes    = 16
    branch_params.Curve       = 40.0 * math.pi / 180.0
    branch_params.CurveBack   = 80.0 * math.pi / 180.0
    branch_params.CurveV      = 90.0 * math.pi / 180.0

    branch_params.DownAngle   = 20.0 * math.pi / 180.0
    branch_params.DownAngleV  = 10.0 * math.pi / 180.0
    branch_params.Rotate      = -120.0 * math.pi / 180.0
    branch_params.RotateV     =  30.0 * math.pi / 180.0
    branch_params.Branches    =  25

    result.Branches.append(branch_params)

    # 2
    branch_params = GTTreeBranchParam()

    branch_params.Length      = 1.5
    branch_params.LengthV     = 0.0
    branch_params.Taper       = 1.0
    branch_params.SegSplits   = 0.2
    branch_params.SplitAngle  = 45.0 * math.pi / 180.0
    branch_params.SplitAngleV = 20.0 * math.pi / 180.0
    branch_params.CurveRes    = 12
    branch_params.Curve       = 0.0
    branch_params.CurveBack   = 0.0
    branch_params.CurveV      = 0.0

    branch_params.DownAngle   =  30.0 * math.pi / 180.0
    branch_params.DownAngleV  =  10.0 * math.pi / 180.0
    branch_params.Rotate      =  -120.0 * math.pi / 180.0
    branch_params.RotateV     =  30.0 * math.pi / 180.0
    branch_params.Branches    =  10

    result.Branches.append(branch_params)

    # 3
    branch_params = GTTreeBranchParam()

    branch_params.Length      = 0.1
    branch_params.LengthV     = 0.0
    branch_params.Taper       = 1
    branch_params.SegSplits   = 0
    branch_params.SplitAngle  = 0.0
    branch_params.SplitAngleV = 0.0
    branch_params.CurveRes    = 1
    branch_params.Curve       = 0.0
    branch_params.CurveBack   = 0.0
    branch_params.CurveV      = 0.0

    branch_params.DownAngle   =  20.0 * math.pi / 180.0
    branch_params.DownAngleV  =  10.0 * math.pi / 180.0
    branch_params.Rotate      =  140.0 * math.pi / 180.0
    branch_params.RotateV     =  0.0
    branch_params.Branches    =  300

    result.Branches.append(branch_params)

    return result


def GetTreeParamFurTree():
    result = GTTreeParam()

    result.Shape = 0
    result.BaseSize = 0.1

    result.Scale      = 20.0
    result.ScaleV     = 5.0
    result.ZScale     = 1.0
    result.ZScaleV    = 0.0
    result.Levels     = 2
    result.Ratio      = 0.015
    result.RatioPower = 1.5
    result.Lobes      = 0
    result.LobeDepth  = 0.0
    result.Flare      = 0.0

    result.Leaves      = 0
    result.LeafShape   = 0
    result.LeafScale   = 0.0
    result.LeafScaleX  = 0.0

    branch_params = GTTreeBranchParam()

    branch_params.Scale       = 1.0
    branch_params.ScaleV      = 0.0
    branch_params.Length      = 1.0
    branch_params.LengthV     = 0.0
    branch_params.Taper       = 1.0
    branch_params.BaseSplits  = 0
    branch_params.SegSplits   = 0.0
    branch_params.SplitAngle  = 0.0
    branch_params.SplitAngleV = 0.0
    branch_params.CurveRes    = 5
    branch_params.Curve       = 0.0 * math.pi / 180.0
    branch_params.CurveBack   = 0.0
    branch_params.CurveV      = 10.0 * math.pi / 180.0

    result.Branches.append(branch_params)

    branch_params = GTTreeBranchParam()

    branch_params.Scale       = 1.0
    branch_params.ScaleV      = 0.0
    branch_params.Length      = 0.5
    branch_params.LengthV     = 0.0
    branch_params.Taper       = 1.0
    branch_params.BaseSplits  = 0
    branch_params.SegSplits   = 0.0
    branch_params.SplitAngle  = 0.0
    branch_params.SplitAngleV = 0.0
    branch_params.CurveRes    = 5
    branch_params.Curve       = -30.0 * math.pi / 180.0
    branch_params.CurveBack   = 0.0
    branch_params.CurveV      = 10.0 * math.pi / 180.0

    branch_params.DownAngle   =  40.0 * math.pi / 180.0
    branch_params.DownAngleV  =  -50.0 * math.pi / 180.0
    branch_params.Rotate      =  140.0 * math.pi / 180.0
    branch_params.RotateV     =   0.0
    branch_params.Branches    =  40

    result.Branches.append(branch_params)

    branch_params = GTTreeBranchParam()

    branch_params.Scale       = 1.0
    branch_params.ScaleV      = 0.0
    branch_params.Length      = 0.2
    branch_params.LengthV     = 0.0
    branch_params.Taper       = 1.0
    branch_params.BaseSplits  = 0
    branch_params.SegSplits   = 0.0
    branch_params.SplitAngle  = 0.0
    branch_params.SplitAngleV = 0.0
    branch_params.CurveRes    = 5
    branch_params.Curve       = 0.0
    branch_params.CurveBack   = 0.0
    branch_params.CurveV      = 20.0 * math.pi / 180.0

    branch_params.DownAngle   =  30.0 * math.pi / 180.0
    branch_params.DownAngleV  =  10.0 * math.pi / 180.0
    branch_params.Rotate      =  140.0 * math.pi / 180.0
    branch_params.RotateV     =   0.0
    branch_params.Branches    =  50

    result.Branches.append(branch_params)

    return result

try:
    import xml.dom.minidom

    import gteximxml

    GTImportParamsArbaro = gteximxml.ImportParamArbaro
except:
    # xml.dom.minidom is not present - disable 'Arbaro' import support
    GTImportParamsArbaro = None

import gteximtxt

GTImportParamsGen3 = gteximtxt.ImportParamGen3
GTExportParamsGen3 = gteximtxt.ExportParamGen3

