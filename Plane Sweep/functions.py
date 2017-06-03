import vtk
import numpy as np
from numpy import *
from scipy.spatial import ConvexHull

# created for lambda expression to sort list
def getKey(item):
  return item[0]

def sortPoints(pts):
  """Sort 2d array of unsorted points according to the x component 
  Args:
      pts(numpy 2d array): Unsorted 2d points (#points x 2)
      
  Returns:
      Sorted  2d (numpy )array of input points
  """
  #sort the points in increasing order for the x component
  sortedPts = np.array(sorted(pts, key=getKey))

  return sortedPts

def intersect(p1, p2, p3, p4):
  """ Tests if two line segments intersect
  Args:
    p1 (numpy array): start point of first  line segment
    p2 (numpy array): end   point of first  line segment
    p3 (numpy array): start point of second line segment
    p4 (numpy array): end   point of second line segment
  
  Returns:
    True if line segments intersects
    False otherwise
  """
  
  line13 = (p3[0] - p1[0]) * (p3[1] + p1[1])
  line34 = (p4[0] - p3[0]) * (p4[1] + p3[1])
  line41 = (p1[0] - p4[0]) * (p1[1] + p4[1])
  line23 = (p3[0] - p2[0]) * (p3[1] + p2[1])
  line42 = (p2[0] - p4[0]) * (p2[1] + p4[1])
  
  CCW1 = (line13 + line34 + line41)
  CCW2 = (line23 + line34 + line42)
  
  if CCW1 * CCW2 >= 0:
    return False
    
  line12 = (p2[0] - p1[0]) * (p2[1] + p1[1])
  line23 = (p3[0] - p2[0]) * (p3[1] + p2[1])
  line31 = (p1[0] - p3[0]) * (p1[1] + p3[1])
  line24 = (p4[0] - p2[0]) * (p4[1] + p2[1])
  line41 = (p1[0] - p4[0]) * (p1[1] + p4[1])
  
  CCW1 = (line12 + line23 + line31)
  CCW2 = (line12 + line24 + line41)
  
  if CCW1 * CCW2 >= 0:
    return False
  
  return True

def isVisible(pts,edgeList,currentPoint,pointInConvexHull):
  """Returns  1 when currentPoint can "see" a point in the convex hull
      (No edge is intersected by the edge that would be introduced by currentPoint and pointInConvexHull)
  Args:
      pts               (numpy 2d array)  : sorted points 
      edgeList          (list ) : list of edges(current triangulation).
                                  An entry contains p1 and p2
      currentPoint      ( int ) : index for point of interessed 
      pointInConvexHull ( int ) : index of a point on the convex Hull

  Returns:
      1 if no intersection between the current triangulation was found
      else 0 
  """

  visible=1

  for i in range(np.size(edgeList, 0)):
    if intersect(pts[edgeList[i][0], :], pts[edgeList[i][1], :], pts[currentPoint, :], pts[pointInConvexHull, :]):
      visible = 0
      break

  return visible

def createSpheresForPoints(renderer,points):
  """ Create spheres for given points and adds these to the renderer
  Args:
      renderer(vtkRenderer) : Vtk Renderer
      pts (numpy array)     : 2d points as a numpy array (#points x 2)
  """
  
  # for each point in points, create a sphere (vtk has a source for that),
  # a PolyDataMapper, and an actor, which you then add to the renderer
  # HINTS: 1] you will need to set a 3D position for the sphere
  #           simply set the z component to zero
  #        2] set the radius of the sphere to, e.g., 0.1 
  dummy=0
  radius=0.1
  for point in points:
    # create sphere source
    sphere = vtk.vtkSphereSource()
    sphere.SetCenter(point[0], point[1], dummy)
    sphere.SetRadius(radius)
    # create mapper
    sphereMapper = vtk.vtkPolyDataMapper()
    sphereMapper.SetInputConnection(sphere.GetOutputPort())
    # create actor
    sphereActor = vtk.vtkActor()
    sphereActor.SetMapper(sphereMapper)
    # assign actor to the renderer
    renderer.AddActor(sphereActor)

def addLineToRenderer(renderer,p1,p2):
  """ Adds a line to the renderer that will be rendered
  Args: 
    renderer (vtkRenderer) : the vtk renderer 
    p1 (numpy array) : 3d coordinate of point 1 
    p2 (numpy array) : 3d coordinate of point 2
  """
  # This function should add a line segment that connects points p1 and p2
  # to the renderer.
  # You will have to create a vtkPolyData object to which you add both points.
  # Note that, in this case, p1 and p2 are already 3D points, with z=0.
  # You will then have to add a vtkLine that connects the points to a
  # vtkCellArray and add that to the vtkPolyData object.
  # Finally, the vtkPolyData can be rendered using a PolyDataMapper
  # and an Actor, similar to the previous task.
  dummy=0
  # create polyData for lines
  polyData = vtk.vtkPolyData()
  # define points for vertex
  points = vtk.vtkPoints()
  points.SetNumberOfPoints(2)
  points.SetPoint(0, p1[0], p1[1], p1[2])
  points.SetPoint(1, p2[0], p2[1], p2[2])
  # create cell array to store our lines
  line = vtk.vtkLine()
  # SetId(a, b), a=order b=index of point
  line.GetPointIds().SetId(0,0) # the second 0 is the index of the Origin in the vtkPoints
  line.GetPointIds().SetId(1,1) # the second 1 is the index of P0 in the vtkPoints
  lines = vtk.vtkCellArray()
  lines.InsertNextCell(line)
  # set points and lines in vtkPolyData()
  polyData.SetLines(lines)
  polyData.SetPoints(points)
  
  polygonMapper = vtk.vtkPolyDataMapper()
  polygonMapper.SetInput(polyData)

  polygonActor = vtk.vtkActor()
  polygonActor.SetMapper(polygonMapper)

  renderer.AddActor(polygonActor)

def getccwids(hull,startId):
  """Returns IDs of convex hull in CCW order, starting at startId
  Args:
      hull (list): IDs of the convex hull in CCW order
      startId (int): ID at which to start returned list

  Returns:
      The list of IDs in hull, rotated so that startId is the first element.

  Raises:
      ValueError: If startId is not part of hull.
  """

  return hull[hull.index(startId):]+hull[:hull.index(startId)]

def createPoints():
  """ Returns a 2d numpy array of some predefined points
  Returns:
    pts(numpy array): unsoretd predefined points
  """
  #creating 2d points as numpy array
  pts=np.array([[11,11],[2,12],[ 9,9],
                [ 7,11],[8, 4],[ 1,7],
                [ 3, 5],[5, 6],[10,6]])
  return pts

def addEdgeToList(list,p1,p2):
  """ Adds an edge to the current triangulation
  Args: 
    list (list): current triangulation
    p1 ( int ) : index of first point
    p2 ( int ) : index of second point
  """
  edge=[p1,p2]
  list.append(edge)

def createTriangulationFromEdgeList(pts,edgeList,renderer):
  """ Creates triangulation from points and edgeList and adds these to 
      the renderer.
  Args: 
    pts (numpy array) : 2d points 
    edgeList ( list ) : triangulation given as edges between 2 points 
    renderer(vtkRenderer): vtk renderer where we add the actors 
  """
  for i in range(0,len(edgeList)):
    id1=edgeList[i][0]
    id2=edgeList[i][1]
    pd1=pts[id1,:]
    pd2=pts[id2,:]
    p1=np.append(pd1,0)
    p2=np.append(pd2,0)
    addLineToRenderer(renderer,p1,p2)
