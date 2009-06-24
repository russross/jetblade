# --------------------------------------------------------------------------
# gteximtl.py
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

import math
from gtparams import *

def _GetParamInt(ParamSet,Name,Default,Level=None):
    if Level is not None:
        Name = '%u%s' % (Level,Name)
    try:
        Value = ParamSet[Name]
    except:
        return Default

    try:
        Value = int(Value)

        return Value
    except:
        raise RuntimeError,"invalid integer value '%s' in parameter '%s'" % (Name,Value)

def _GetParamFloat(ParamSet,Name,Default,Level=None):
    if Level is not None:
        Name = '%u%s' % (Level,Name)
    try:
        Value = ParamSet[Name]
    except:
        return Default

    try:
        Value = float(Value)

        return Value
    except:
        raise RuntimeError,"invalid float value '%s' in parameter '%s'" % (Name,Value)

def MakeParamsFromParamSet(ParamSet):
    tree_param = GTTreeParam()

    tree_param.Shape      = _GetParamInt(ParamSet,'Shape',0)
    tree_param.BaseSize   = _GetParamFloat(ParamSet,'BaseSize',0.0)
    tree_param.Scale      = _GetParamFloat(ParamSet,'Scale',1.0)
    tree_param.ScaleV     = _GetParamFloat(ParamSet,'ScaleV',0.0)
    tree_param.ZScale     = _GetParamFloat(ParamSet,'ZScale',0.0)
    tree_param.ZScaleV    = _GetParamFloat(ParamSet,'ZScaleV',0.0)
    tree_param.Levels     = _GetParamInt(ParamSet,'Levels',0)
    tree_param.Ratio      = _GetParamFloat(ParamSet,'Ratio',0.02)
    tree_param.RatioPower = _GetParamFloat(ParamSet,'RatioPower',1.0)
    tree_param.Lobes      = _GetParamInt(ParamSet,'Lobes',0)
    tree_param.LobeDepth  = _GetParamFloat(ParamSet,'LobeDepth',0.1)
    tree_param.Flare      = _GetParamFloat(ParamSet,'Flare',1.0)

    tree_param.Leaves      = _GetParamInt(ParamSet,'Leaves',0)
    tree_param.LeafShape   = 0
    tree_param.LeafScale   = _GetParamFloat(ParamSet,'LeafScale',0.1)
    tree_param.LeafScaleX  = _GetParamFloat(ParamSet,'LeafScaleX',1.0)

    tree_param.LeafQuality = _GetParamFloat(ParamSet,'LeafQuality',1.0)

#    for Level in xrange(tree_param.Levels + 1):
    for Level in xrange(4):
        branch_param = GTTreeBranchParam()

        branch_param.Scale       = _GetParamFloat(ParamSet,'Scale',1.0,Level)
        branch_param.ScaleV      = _GetParamFloat(ParamSet,'ScaleV',0.0,Level)
        branch_param.Length      = _GetParamFloat(ParamSet,'Length',1.0,Level)
        branch_param.LengthV     = _GetParamFloat(ParamSet,'LengthV',0.0,Level)
        branch_param.Taper       = _GetParamFloat(ParamSet,'Taper',0.0,Level)
        branch_param.BaseSplits  = _GetParamInt(ParamSet,'BaseSplits',0.0,Level)
        branch_param.SegSplits   = _GetParamFloat(ParamSet,'SegSplits',0.0,Level)
        branch_param.SplitAngle  = math.radians(_GetParamFloat(ParamSet,'SplitAngle',0.0,Level))
        branch_param.SplitAngleV = math.radians(_GetParamFloat(ParamSet,'SplitAngleV',0.0,Level))
        branch_param.CurveRes    = _GetParamInt(ParamSet,'CurveRes',1,Level)
        branch_param.Curve       = math.radians(_GetParamFloat(ParamSet,'Curve',0.0,Level))
        branch_param.CurveBack   = math.radians(_GetParamFloat(ParamSet,'CurveBack',0.0,Level))
        branch_param.CurveV      = math.radians(_GetParamFloat(ParamSet,'CurveV',0.0,Level))
        branch_param.DownAngle   = math.radians(_GetParamFloat(ParamSet,'DownAngle',0.0,Level))
        branch_param.DownAngleV  = math.radians(_GetParamFloat(ParamSet,'DownAngleV',0.0,Level))
        branch_param.Rotate      = math.radians(_GetParamFloat(ParamSet,'Rotate',0.0,Level))
        branch_param.RotateV     = math.radians(_GetParamFloat(ParamSet,'RotateV',0.0,Level))
        branch_param.Branches    = _GetParamInt(ParamSet,'Branches',0,Level)

        tree_param.Branches.append(branch_param)

    return tree_param

