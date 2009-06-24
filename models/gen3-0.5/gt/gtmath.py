# --------------------------------------------------------------------------
# gtmath.py
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

#!/usr/bin/python

import math

try:
    import random
    GTMathRNGSeed    = random.seed
    GTMathRNGRandInt = random.randint
    GTMathRNGUniform = random.uniform
except:
    import gtmathrng
    GTMathRNGSeed    = gtmathrng.GTMathRNGSimpleSeed
    GTMathRNGRandInt = gtmathrng.GTMathRNGSimpleRandInt
    GTMathRNGUniform = gtmathrng.GTMathRNGSimpleUniform

GTEpsilon = 0.000005

def FloatRound(v):
    return int(v + 0.5)

def FloatEqualToZero(v):
    if (v >= -GTEpsilon) and (v <= GTEpsilon):
        return 1
    else:
        return 0

class GTVector3(object):
    __slots__ = [ 'x','y','z']
    def __init__(self,x = 0.0,y = 0.0,z = 0.0):
        self.x = x
        self.y = y
        self.z = z

    def Normalize(self):
        length = math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

        self.x = self.x / length
        self.y = self.y / length
        self.z = self.z / length

    def Clone(self):
        return GTVector3(self.x,self.y,self.z)

class GTVector4(object):
    __slots__ = [ 'x','y','z','w']
    def __init__(self,x = 0.0,y = 0.0,z = 0.0,w = 1.0):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def Normalize(self):
        length = math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z + self.w * self.w)

        self.x = self.x / length
        self.y = self.y / length
        self.z = self.z / length
        self.w = self.w / length

    def Clone(self):
        return GTVector4(self.x,self.y,self.z,self.w)

GTMathMatrix4x4Identity = \
 [ 1.0, 0.0, 0.0, 0.0,
   0.0, 1.0, 0.0, 0.0,
   0.0, 0.0, 1.0, 0.0,
   0.0, 0.0, 0.0, 1.0 ]

# Column-major presentation
class GTMatrix4x4(object):
    __slots__ = ['m']
    def __init__(self):
        pass

    def __str__(self):
        return '[ %.04f %.04f %.04f %.04f]\n[ %.04f %.04f %.04f %.04f]\n[ %.04f %.04f %.04f %.04f]\n[ %.04f %.04f %.04f %.04f]\n' % \
               (self.m[0],self.m[4],self.m[8],self.m[12],
                self.m[1],self.m[5],self.m[9],self.m[13],
                self.m[2],self.m[6],self.m[10],self.m[14],
                self.m[3],self.m[7],self.m[11],self.m[15])

    def SetIdentity(self):
        self.m = GTMathMatrix4x4Identity[:]

    def SetZero(self):
        self.m = [ 0.0 for i in xrange(16)]

    def SetTranslation(self,x,y,z):
        self.SetIdentity()

        self.m[12] = x
        self.m[13] = y
        self.m[14] = z

    def SetRotationX(self,angle):
        self.SetIdentity()

        asin = math.sin(angle)
        acos = math.cos(angle)

        self.m[5]  =  acos
        self.m[6]  =  asin
        self.m[9]  = -asin
        self.m[10] = acos

    def SetRotationY(self,angle):
        self.SetIdentity()

        asin = math.sin(angle)
        acos = math.cos(angle)

        self.m[0]  =  acos
        self.m[2]  = -asin
        self.m[8]  =  asin
        self.m[10] =  acos

    def SetRotationZ(self,angle):
        self.SetIdentity()

        asin = math.sin(angle)
        acos = math.cos(angle)

        self.m[0]  =  acos
        self.m[1]  =  asin
        self.m[4]  = -asin
        self.m[5]  =  acos

    def SetRotation(self,axis,angle):
        n = axis.Clone()

        n.Normalize()

        asin = math.sin(angle)
        acos = math.cos(angle)
        acos1 = 1.0 - acos

        self.SetIdentity()

        self.m[0] = n.x * n.x * acos1 +       acos
        self.m[1] = n.x * n.y * acos1 + n.z * asin
        self.m[2] = n.x * n.z * acos1 - n.y * asin

        self.m[4] = n.x * n.y * acos1 - n.z * asin
        self.m[5] = n.y * n.y * acos1 +       acos
        self.m[6] = n.y * n.z * acos1 + n.x * asin

        self.m[8]  = n.x * n.z * acos1 + n.y * asin
        self.m[9]  = n.y * n.z * acos1 - n.x * asin
        self.m[10] = n.z * n.z * acos1 +       acos

    def GetRotationOnly(self):
        result = GTMatrix4x4()
        result.SetIdentity()

        result.m[0] = self.m[0]
        result.m[1] = self.m[1]
        result.m[2] = self.m[2]

        result.m[4] = self.m[4]
        result.m[5] = self.m[5]
        result.m[6] = self.m[6]

        result.m[8]  = self.m[8]
        result.m[9]  = self.m[9]
        result.m[10] = self.m[10]

        return result

    def GetTranspose(self):
        result = GTMatrix4x4()
        result.m = []

        for x in xrange(4):
            for y in xrange(4):
                result.m.append(self.m[y * 4 + x])

        return result

    def Clone(self):
        result = GTMatrix4x4()
        result.m = self.m[:]

        return result

def GTMultMatrix4x4Vec4(m,v):
    mm = m.m

    vx = v.x
    vy = v.y
    vz = v.z
    vw = v.w

    rx = mm[0] * vx + mm[4] * vy + mm[8]  * vz + mm[12] * vw
    ry = mm[1] * vx + mm[5] * vy + mm[9]  * vz + mm[13] * vw
    rz = mm[2] * vx + mm[6] * vy + mm[10] * vz + mm[14] * vw
    rw = mm[3] * vx + mm[7] * vy + mm[11] * vz + mm[15] * vw

    return GTVector4(rx,ry,rz,rw)

def GTMultMatrix4x4(m1,m2):
    c = []
    a = m1.m
    b = m2.m

    c.append(a[0] * b[0] + a[4] * b[1] + a[8] * b[2] + a[12] * b[3])
    c.append(a[1] * b[0] + a[5] * b[1] + a[9] * b[2] + a[13] * b[3])
    c.append(a[2] * b[0] + a[6] * b[1] + a[10] * b[2] + a[14] * b[3])
    c.append(a[3] * b[0] + a[7] * b[1] + a[11] * b[2] + a[15] * b[3])

    c.append(a[0] * b[4] + a[4] * b[5] + a[8] * b[6] + a[12] * b[7])
    c.append(a[1] * b[4] + a[5] * b[5] + a[9] * b[6] + a[13] * b[7])
    c.append(a[2] * b[4] + a[6] * b[5] + a[10] * b[6] + a[14] * b[7])
    c.append(a[3] * b[4] + a[7] * b[5] + a[11] * b[6] + a[15] * b[7])

    c.append(a[0] * b[8] + a[4] * b[9] + a[8] * b[10] + a[12] * b[11])
    c.append(a[1] * b[8] + a[5] * b[9] + a[9] * b[10] + a[13] * b[11])
    c.append(a[2] * b[8] + a[6] * b[9] + a[10] * b[10] + a[14] * b[11])
    c.append(a[3] * b[8] + a[7] * b[9] + a[11] * b[10] + a[15] * b[11])

    c.append(a[0] * b[12] + a[4] * b[13] + a[8] * b[14] + a[12] * b[15])
    c.append(a[1] * b[12] + a[5] * b[13] + a[9] * b[14] + a[13] * b[15])
    c.append(a[2] * b[12] + a[6] * b[13] + a[10] * b[14] + a[14] * b[15])
    c.append(a[3] * b[12] + a[7] * b[13] + a[11] * b[14] + a[15] * b[15])

    result   = GTMatrix4x4()
    result.m = c

    return result

def __GTTestAll():
    pass

if __name__ == '__main__':
    __GTTestAll()

