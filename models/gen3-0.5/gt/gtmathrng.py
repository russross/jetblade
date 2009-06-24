# --------------------------------------------------------------------------
# gtmathrng.py
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

GTMathRNGSimple_MAX = 2147483647

_Seed = 1234

def GTMathRNGSimpleSeed(Value):
    global _Seed
    _Seed = Value

# Algorithm and constants are taken from "Numerical recipes in C" ch.7 p.278
def GTMathRNGSimpleRand():
    global _Seed

    _Seed = (16807 * _Seed) % (GTMathRNGSimple_MAX)

    return int(_Seed)

def GTMathRNGSimpleRandInt(a,b):
    return a + int((b - a + 1.0) * GTMathRNGSimpleRand() / (GTMathRNGSimple_MAX + 1.0))

def GTMathRNGSimpleUniform(a,b):
    return a + GTMathRNGSimpleRand() / (GTMathRNGSimple_MAX + 1.0) * (b - a)

if __name__ == '__main__':
    for i in xrange(50):
        print GTMathRNGSimpleUniform(-1.0,1.0)

