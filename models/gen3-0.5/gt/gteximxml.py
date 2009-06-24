# --------------------------------------------------------------------------
# gteximxml.py
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

import xml.dom.minidom
from gteximtl import *

def _GetParamFromElement(ParamSet,element):
    name  = element.getAttribute('name')
    value = element.getAttribute('value')

    ParamSet[name] = value

def ImportParamArbaro(source):
    dom = xml.dom.minidom.parse(source)

    doc_element = dom.documentElement

    if doc_element.tagName != 'arbaro':
        raise RuntimeError,"invalid document element"

    species_elements = doc_element.getElementsByTagName('species')

    if len(species_elements) == 0:
        raise RuntimeError,"no parameters found"

    param_elements = species_elements[0].getElementsByTagName('param')

    ParamSet = {}

    for element in param_elements:
        _GetParamFromElement(ParamSet,element)

    return MakeParamsFromParamSet(ParamSet)

