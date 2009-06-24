# --------------------------------------------------------------------------
# gtgui.py
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

import Blender
from Blender.BGL import *

# Event id generator #
_GTGUIEventIdCurrent = 100

def _GenerateEventId():
    global _GTGUIEventIdCurrent

    _GTGUIEventIdCurrent = _GTGUIEventIdCurrent + 1

    return _GTGUIEventIdCurrent

class Control:
    def __init__(self,tags):
        self.__visible = 1
        self.__tags    = tags
        self.x         = 0
        self.y         = 0

    def Hide(self):
        self.__visible = 0

    def Show(self):
        self.__visible = 1

    def IsVisible(self):
        return self.__visible

    def HasTag(self,tag):
        if tag in self.__tags:
            return 1
        else:
            return 0

    def Draw(self):
        raise NotImplementedError

    def ProcessEvent(self):
        raise NotImplementedError

class ControlNumberEdit(Control):
    def __init__(self,name,x,y,width,height,inititial,min,max,tooltip='',tags=''):
        Control.__init__(self,tags)
        self.__name    = name
        self.x         = x
        self.y         = y
        self.__width   = width
        self.__height  = height
        self.__value   = inititial
        self.__min     = min
        self.__max     = max
        self.__tooltip = tooltip
        self.__eventid = _GenerateEventId()
        self.__button  = None

    def Draw(self):
        self.__button = Blender.Draw.Number(self.__name,
                                            self.__eventid,
                                            self.x,
                                            self.y,
                                            self.__width,
                                            self.__height,
                                            self.__value,
                                            self.__min,
                                            self.__max,
                                            self.__tooltip)

    def ProcessEvent(self):
        self.__value = self.__button.val

    def GetValue(self):
        return self.__value

    def SetValue(self,value):
        self.__value = value

    def GetEventId(self):
        return self.__eventid

class ControlSlider(Control):
    def __init__(self,name,x,y,width,height,inititial,min,max,tooltip='',tags=''):
        Control.__init__(self,tags)
        self.__name    = name
        self.x         = x
        self.y         = y
        self.__width   = width
        self.__height  = height
        self.__value   = inititial
        self.__min     = min
        self.__max     = max
        self.__tooltip = tooltip
        self.__eventid = _GenerateEventId()
        self.__button  = None

    def Draw(self):
        self.__button = Blender.Draw.Slider(self.__name,
                                            self.__eventid,
                                            self.x,
                                            self.y,
                                            self.__width,
                                            self.__height,
                                            self.__value,
                                            self.__min,
                                            self.__max,
                                            1,
                                            self.__tooltip)

    def ProcessEvent(self):
        self.__value = self.__button.val

    def GetValue(self):
        return self.__value

    def GetEventId(self):
        return self.__eventid

class ControlCommandButton(Control):
    def __init__(self,name,x,y,width,height,callback,tooltip='',tags=''):
        Control.__init__(self,tags)
        self.__name     = name
        self.x          = x
        self.y          = y
        self.__width    = width
        self.__height   = height
        self.__callback = callback
        self.__tooltip  = tooltip
        self.__eventid  = _GenerateEventId()
        self.__button   = None

    def Draw(self):
        self.__button = Blender.Draw.PushButton(self.__name,
                                                self.__eventid,
                                                self.x,
                                                self.y,
                                                self.__width,
                                                self.__height,
                                                self.__tooltip)

    def ProcessEvent(self):
        self.__callback()

    def GetEventId(self):
        return self.__eventid

class ControlToggleButton(Control):
    def __init__(self,name,x,y,width,height,state,callback=None,tooltip='',tags=''):
        Control.__init__(self,tags)
        self.__name     = name
        self.x          = x
        self.y          = y
        self.__width    = width
        self.__height   = height
        self.__state    = state
        self.__callback = callback
        self.__tooltip  = tooltip
        self.__eventid  = _GenerateEventId()
        self.__button   = None

    def Draw(self):
        self.__button = Blender.Draw.Toggle(self.__name,
                                            self.__eventid,
                                            self.x,
                                            self.y,
                                            self.__width,
                                            self.__height,
                                            self.__state,
                                            self.__tooltip)

    def ProcessEvent(self):
        if self.__callback is not None:
            self.__state = self.__callback()
        else:
            self.__state = 1 - self.__state

    def GetEventId(self):
        return self.__eventid

    def GetValue(self):
        return self.__state

    def SetValue(self,value):
        self.__state = value

class ControlDropDownList(Control):
    def __init__(self,name,x,y,width,height,tooltip='',tags=''):
        Control.__init__(self,tags)
        self.__name     = name
        self.x          = x
        self.y          = y
        self.__width    = width
        self.__height   = height
        self.__tooltip  = tooltip
        self.__eventid  = _GenerateEventId()
        self.__button   = None
        self.__default  = 0

        self.__items    = []

        self.__current  = self.__default

    def ClearList(self):
        self.__items = []

    def AppendItem(self,name,id,default=0):
        self.__items.append((name,id))

        if default:
            self.__default = id
            self.__current = id

    def Draw(self):
        desc = self.__name + ' %t'

        for item in self.__items:
            name,id = item

            desc = desc + "|" + name + " %x" + ("%d" % id)

        self.__button = Blender.Draw.Menu(desc,
                                          self.__eventid,
                                          self.x,
                                          self.y,
                                          self.__width,
                                          self.__height,
                                          self.__current,
                                          self.__tooltip)

    def ProcessEvent(self):
        self.__current = self.__button.val

    def GetEventId(self):
        return self.__eventid

    def SetValue(self,value):
        self.__current = value

    def GetValue(self):
        return self.__current

class Workspace:
    def __init__(self):
        self.__controls = []

    def AppendControl(self,control):
        self.__controls.append(control)

    def Draw(self):
        glClearColor(0.5,0.5,0.5,1)
        glClear(GL_COLOR_BUFFER_BIT)
        glColor3f(0.0,0.0,0.0)

        for control in self.__controls:
            if control.IsVisible():
                control.Draw()

    def Close():
        Blender.Draw.Exit()

    def ProcessEvent(self,event):
        for control in self.__controls:
            if event == control.GetEventId():
                control.ProcessEvent()

                return

    def ProcessEvent2(self,event,value):
        if event == Blender.Draw.ESCKEY:
            Blender.Draw.Exit()
            return

    def Run(self):
        draw_func   = lambda self=self : self.Draw()
        kevent_func = lambda event,value,self=self : self.ProcessEvent2(event,value)
        event_func  = lambda event,self=self : self.ProcessEvent(event)

        Blender.Draw.Register(draw_func,kevent_func,event_func)

    def GetTaggedValue(self,tag):
        control = self.GetControlByTag(tag)

        if control is not None:
            return control.GetValue()
        else:
            return None

    def SetTaggedValue(self,tag,value):
        control = self.GetControlByTag(tag)

        if control is not None:
            control.SetValue(value)

    def HideByTag(self,tag):
        for control in self.__controls:
            if control.HasTag(tag):
                control.Hide()

    def ShowByTag(self,tag):
        for control in self.__controls:
            if control.HasTag(tag):
                control.Show()

    def GetControlByTag(self,tag):
        for control in self.__controls:
            if control.HasTag(tag):
                return control

        return None

    def ReorderControlsByColumns(self):
        #FIXME: perfomance hit - rewrite it later
        def cmp_func(a,b):
            if a.x < b.x:
                return -1
            elif a.x > b.x:
                return 1
            else:
                if a.y > b.y:
                    return -1
                elif a.y < b.y:
                    return 1
                else:
                    return 0

        self.__controls.sort(cmp_func)

