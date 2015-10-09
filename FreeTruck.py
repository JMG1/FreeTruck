# -*- coding: utf-8 -*-
# FreeCAD 'FreeTruck' game script
# (c) 2014 Javier Martínez García
 
#***************************************************************************
#*   (c) Javier Martínez García 2014                                       *   
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU Lesser General Public License (LGPL)    *
#*   as published by the Free Software Foundation; either version 2 of     *
#*   the License, or (at your option) any later version.                   *
#*   for detail see the LICENCE text file.                                 *
#*                                                                         *
#*   This macro is distributed in the hope that it will be useful,         *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        * 
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#*   GNU Lesser General Public License for more details.                   *
#*                                                                         *
#*   You should have received a copy of the GNU Library General Public     *
#*   License along with FreeCAD; if not, write to the Free Software        * 
#*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
#*   USA                                                                   *
#*                                                                         *
#***************************************************************************/

# Open FreeTruck.fcstd and copy paste this script or run it as a macro
# Speed:  w, s
# Steering: q, e
# Camera: x, c
# More FreeCAD projects http://linuxforanengineer.blogspot.com.es/

########################### SCRIPT #############################################
from PySide import QtCore
from pivy import coin
#------------------------------------------------------------------------------#
# aux functions
#------------------------------------------------------------------------------#
def retrieveObject(name):
  return FreeCAD.ActiveDocument.getObject(name)

def VectorFromEdge(edge):
  return (edge.Curve.EndPoint - edge.Curve.StartPoint ).normalize()

def Vec3(x,y,z):
  return FreeCAD.Vector( x,y,z)

def edgeNumber():
  parent_shape = FreeCAD.Gui.Selection.getSelectionEx()[0].Object
  edgeA = FreeCAD.Gui.Selection.getSelectionEx()[0].SubObjects[0]
  i = 0
  for edgeB in parent_shape.Shape.Edges:
    try:
      if (edgeA.Curve.StartPoint-edgeB.Curve.StartPoint).Length < 0.001:
        if (edgeA.Curve.EndPoint - edgeB.Curve.EndPoint).Length < 0.001:
          return i
    except:
      pass
    i += 1

def faceNumber():
  parent_shape = FreeCAD.Gui.Selection.getSelectionEx()[0].Object
  FaceA = FreeCAD.Gui.Selection.getSelectionEx()[0].SubObjects[0]
  i = 0
  for FaceB in parent_shape.Shape.Faces:
    if (FaceB.CenterOfMass - FaceA.CenterOfMass).Length < 0.001:
      return i
    
    i += 1

#------------------------------------------------------------------------------#
# camera
#------------------------------------------------------------------------------#
class scene_camera:
  def __init__(self):
    self.chase_cam = False
    self.cam = FreeCADGui.ActiveDocument.ActiveView.getCameraNode()
    
  def cameraUpdate(self):
    if self.chase_cam:
      VPos = FreeCAD.ActiveDocument.getObject('Pocket001').Shape.Faces[13].CenterOfMass
      self.cam.position.setValue(VPos + Vec3(0,0,50) + tb.dir_x*100)
      VLook = VPos + tb.dir_x*-100
      self.cam.pointAt( coin.SbVec3f( VLook[0], VLook[1], VLook[2]) , coin.SbVec3f( 0, 0, 1 ) )
    
    else:
      VPos = FreeCAD.ActiveDocument.getObject('Pocket001').Shape.Faces[13].CenterOfMass
      self.cam.pointAt( coin.SbVec3f( VPos[0], VPos[1], VPos[2]) , coin.SbVec3f( 0, 0, 1 ) )

#------------------------------------------------------------------------------#
# truck
#------------------------------------------------------------------------------#
class truck_base:
  def __init__(self):
    self.forward_speed = 0.0
    self.throttle_position = 0.0
    self.yaw_angle = 0.0

  def update(self):
    base_obj = retrieveObject('Pocket001')
    self.dir_x = VectorFromEdge( base_obj.Shape.Edges[30] )
    self.dir_y = VectorFromEdge( base_obj.Shape.Edges[31] )
    if self.yaw_angle > 360:
      self.yaw_angle = self.yaw_angle - 360
    
    if self.yaw_angle < 0:
      self.yaw_angle = self.yaw_angle + 360
    
    basePlacement = base_obj.Placement.Base
    
    new_position =  FreeCAD.Placement( basePlacement + self.dir_x*-self.forward_speed,
                      FreeCAD.Rotation(Vec3(0,0,1),self.yaw_angle))
    

    FreeCAD.ActiveDocument.getObject('Pocket001').Placement = new_position
    cm.cameraUpdate()
    cl.update()
    FreeCAD.Gui.updateGui()
    

#------------------------------------------------------------------------------#
# collision detector
#------------------------------------------------------------------------------#
scenery_shape = FreeCAD.ActiveDocument.getObject("Pad004005")
"""
Collision vertexes
22-10    
|  |    / \
|  |     |
8 -7
"""
class collision:
  def __init__(self):
    self.collision_vertexes = (10, 22, 8, 7 )
    self.scenery_shape = FreeCAD.ActiveDocument.getObject("Pad004005").Shape
    
  def update(self):
    # stop truck if it collides with the scenery
    base_obj = retrieveObject('Pocket001')
    for vertex in self.collision_vertexes:
      test_point = base_obj.Shape.Vertexes[vertex].Point
      if self.scenery_shape.isInside( test_point, 1, True ):
        tb.forward_speed = 0.0




tb = truck_base()
cm = scene_camera()
cl = collision()

    
#------------------------------------------------------------------------------#
# keyboard events
# Thanks to mario52  http://forum.freecadweb.org/viewtopic.php?t=8304 )
#------------------------------------------------------------------------------#
class Keyboard:
  def printOnPress(self, info):
    key = info["Key"]
    down = (info["State"] == "DOWN")
    if key == 'w' and (down):
      if tb.throttle_position < 20:
        tb.throttle_position += 1
        tb.forward_speed = tb.throttle_position
    
    if key == 's' and (down):
      if tb.throttle_position < 3 and tb.throttle_position > -3:
        tb.forward_speed = 0
        tb.throttle_position -= 1
      
      elif not(tb.throttle_position < -10):
        tb.throttle_position -= 1
        tb.forward_speed = tb.throttle_position
    
    if key == 'q' and (down):
      tb.yaw_angle += 1*tb.forward_speed/7.0
    
    if key == 'e' and (down):
      tb.yaw_angle -= 1*tb.forward_speed/7.0
    
    if key == 'c' and (down):
      cm.chase_cam = True
    
    if key == 'x' and (down):
      cm.chase_cam = False


v=Gui.ActiveDocument.ActiveView
o = Keyboard()
c = v.addEventCallback("SoKeyboardEvent", o.printOnPress)

#------------------------------------------------------------------------------#
# animation timer
#------------------------------------------------------------------------------#
timer = QtCore.QTimer()
timer.timeout.connect( tb.update)
timer.start(50)




