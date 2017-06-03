import vtk
import numpy as np
from functions import * 
renderer=vtk.vtkRenderer()

pts=createPoints()
sortedPts=sortPoints(pts)

#create spheres for the points in vtk
createSpheresForPoints(renderer,sortedPts)

# create triangle from first 3 points of data
edgeList=[];
usedPoints=[];

addEdgeToList(edgeList,0,1)
addEdgeToList(edgeList,0,2)
addEdgeToList(edgeList,2,1)

# we store the convex hull as a counterclockwise list of indices into
# the sorted points array
currentConvexHull=[2,1,0]

# sweep through
for i in range(3, np.size(sortedPts, 0)):
    usedPoints = []
    rightpoint = None
    ccwids = getccwids(currentConvexHull, i-1)

    for j in ccwids:
        if isVisible(sortedPts, edgeList, i, j):
            addEdgeToList(edgeList, i, j)
            usedPoints.append(j)
        else:
            rightpoint = usedPoints.pop()
            break

    while len(usedPoints) > 1:
        currentConvexHull.remove(usedPoints.pop())

    for j in reversed(ccwids):
        if isVisible(sortedPts, edgeList, i, j):
            addEdgeToList(edgeList, i, j)
            usedPoints.append(j)
        else:
            usedPoints.pop()
            break

    while len(usedPoints) > 0:
        currentConvexHull.remove(usedPoints.pop())

    currentConvexHull.insert(currentConvexHull.index(rightpoint), i)


createTriangulationFromEdgeList(sortedPts,edgeList,renderer)

#Create Render Window
window=vtk.vtkRenderWindow()
window.AddRenderer(renderer)
#Create Interactor
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(window)
interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
interactor.Initialize()
interactor.Start()
