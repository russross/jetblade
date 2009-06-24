# --------------------------------------------------------------------------
# gteximtxt.py
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

from gteximtl import *

def ParseLine(string):
    key,value = tuple(string.strip().split('=',1))

    return key.strip(),value.strip()

class Gen3SourceStream:
    def __init__(self,source):
        self.source = source
        self.line   = self.SkipEmpty()

    def Eof(self):
        if self.line == '':
            return 1
        else:
            return 0

    def ReadLine(self):
        result    = self.line
        self.line = self.SkipEmpty()

        return result

    def SkipEmpty(self):
        ready  = 0

        while not ready:
            result = self.source.readline()

            if result == '':
                ready = 1 # EOF
            elif result.strip() == '':
                pass
            else:
                if result[0] != '#':
                    ready = 1

        return result

def _GetParamFromLine(ParamSet,line):
    key,value = ParseLine(line)

    ParamSet[key] = value

def ImportParamGen3(source):
    buffer = source.readline()

    key,val = ParseLine(buffer)

    if (key == 'GEN3') and ((val == '0.4') or (val == '0.5')):
        pass
    else:
        raise RuntimeError,"invalid file format"

    stream = Gen3SourceStream(source)

    ParamSet = {}

    while not stream.Eof():
        _GetParamFromLine(ParamSet,stream.ReadLine())

    return MakeParamsFromParamSet(ParamSet)

def _ExportParamInt(target,key,value,level=None):
    if level is not None:
        key = '%u%s' % (level,key)

    target.write('%s = %d\n' % (key,value))

def _ExportParamFloat(target,key,value,level=None):
    if level is not None:
        key = '%u%s' % (level,key)

    target.write('%s = %.04f\n' % (key,value))

def ExportParamGen3(target,tree_param):
    target.write('GEN3 = 0.5\n')

    _ExportParamInt(target,'Shape',tree_param.Shape)
    _ExportParamFloat(target,'BaseSize',tree_param.BaseSize)
    _ExportParamFloat(target,'Scale',tree_param.Scale)
    _ExportParamFloat(target,'ScaleV',tree_param.ScaleV)
    _ExportParamFloat(target,'ZScale',tree_param.ZScale)
    _ExportParamFloat(target,'ZScaleV',tree_param.ZScaleV)
    _ExportParamInt(target,'Levels',tree_param.Levels)
    _ExportParamFloat(target,'Ratio',tree_param.Ratio)
    _ExportParamFloat(target,'RatioPower',tree_param.RatioPower)
    _ExportParamInt(target,'Lobes',tree_param.Lobes)
    _ExportParamFloat(target,'LobeDepth',tree_param.LobeDepth)
    _ExportParamFloat(target,'Flare',tree_param.Flare)

    _ExportParamInt(target,'Leaves',tree_param.Leaves)
    _ExportParamInt(target,'LeafShape',tree_param.LeafShape)
    _ExportParamFloat(target,'LeafScale',tree_param.LeafScale)
    _ExportParamFloat(target,'LeafScaleX',tree_param.LeafScaleX)
    _ExportParamFloat(target,'LeafQuality',tree_param.LeafQuality)

    for branch_index in xrange(len(tree_param.Branches)):
        target.write('\n# Branch level %u\n\n' % branch_index)

        branch_param = tree_param.Branches[branch_index]

        _ExportParamFloat(target,'Scale',branch_param.Scale,branch_index)
        _ExportParamFloat(target,'ScaleV',branch_param.ScaleV,branch_index)
        _ExportParamFloat(target,'Length',branch_param.Length,branch_index)
        _ExportParamFloat(target,'LengthV',branch_param.LengthV,branch_index)
        _ExportParamFloat(target,'Taper',branch_param.Taper,branch_index)
        _ExportParamInt(target,'BaseSplits',branch_param.BaseSplits,branch_index)
        _ExportParamFloat(target,'SegSplits',branch_param.SegSplits,branch_index)

        _ExportParamFloat(target,'SplitAngle',math.degrees(branch_param.SplitAngle),branch_index)
        _ExportParamFloat(target,'SplitAngleV',math.degrees(branch_param.SplitAngleV),branch_index)

        _ExportParamInt(target,'CurveRes',branch_param.CurveRes,branch_index)

        _ExportParamFloat(target,'Curve',math.degrees(branch_param.Curve),branch_index)
        _ExportParamFloat(target,'CurveBack',math.degrees(branch_param.CurveBack),branch_index)
        _ExportParamFloat(target,'CurveV',math.degrees(branch_param.CurveV),branch_index)
        _ExportParamFloat(target,'DownAngle',math.degrees(branch_param.DownAngle),branch_index)
        _ExportParamFloat(target,'DownAngleV',math.degrees(branch_param.DownAngleV),branch_index)
        _ExportParamFloat(target,'Rotate',math.degrees(branch_param.Rotate),branch_index)
        _ExportParamFloat(target,'RotateV',math.degrees(branch_param.RotateV),branch_index)

        _ExportParamInt(target,'Branches',branch_param.Branches,branch_index)

