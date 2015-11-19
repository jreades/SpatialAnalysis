# -*- coding: utf-8 -*-
import os
import pandas as pd
import numpy as np
from matplotlib.colors import Normalize
from matplotlib.collections import PatchCollection
from mpl_toolkits.basemap import Basemap
from shapely.geometry import Point, Polygon, MultiPoint, MultiPolygon
from shapely.prepared import prep
from pysal.esda.mapclassify import Natural_Breaks as nb
from descartes import PolygonPatch
import fiona

from scipy.interpolate import interp1d

basedir = os.path.join(os.path.expanduser("~"),"Documents","Output","NS Divide")
sf      = os.path.join(basedir,'Shapefiles','district_borough_unitary_region_simple.shp')

# Read the shapefile
shp = fiona.open(sf)

# Get the bounding box
bds = shp.bounds

fields  = sf.fields    # What are the columns for the table data?
recs    = sf.records() # Extract table data from the shapefile
shapes  = sf.shapes()  # Extract spatial data from the shapefile
Nshp    = len(shapes)  # Number of shapes in the shapefile

# Iterate over the shape records to figure out 
# the bounding box: order is left, bottom, right top (I think)
frame = [100000, 100000, 100000, 100000]
for nshp in xrange(Nshp):
    
    # Get the bounding box for this
    # particular geometry
    edges = shapes[nshp].bbox
    
    # And assign it's value to the 
    # appropriate bit of the frame 
    # if it falls outside of the 
    # existing frame
    if frame[0] > edges[0]:
        frame[0] = edges[0]
    
    if frame[1] > edges[1]:
        frame[1] = edges[1]
    
    if frame[2] < edges[2]:
        frame[2] = edges[2]
    
    if frame[3] < edges[3]:
        frame[3] = edges[3]
    

cns     = []

# Iterate over the table records
for nshp in xrange(Nshp): 
    # This copies a column/set of column 
    # to the new list called cns
    print(recs[nshp][1])
    cns.append(recs[nshp][1])

# Convert cns to an array
cns   = array(cns)

# Set a colourmap
cm    = get_cmap('Dark2')
# Specify this colourmap for use 
# with the number of objects we 
# want to show
cccol = cm(1.*arange(Nshp)/Nshp)

#   -- plot --
pltheight = 8
ydist = frame[3] - frame[1]
xdist = frame[2] - frame[0]

m = interp1d([0,frame[3]],[0,pltheight])

fig     = plt.figure(figsize=(round(m(frame[2]),2),pltheight), dpi=96)
ax      = fig.add_subplot(111)

# For each shape record
for nshp in xrange(Nshp):
    # Set up a patches list with which to 
    # manage the colour display of the 
    # area that we want to show
    ptchs   = []
    
    # Get the points associated with that 
    # object as an array of arrays (those 
    # contain x/y coordinate pairs). 
    pts     = array(shapes[nshp].points)
    
    # Get the number of parts associated 
    # with that shape
    prt     = shapes[nshp].parts
    
    # This somehow combines the numbers 
    # of parts with the number of points
    par     = list(prt) + [pts.shape[0]]
    
    # For each part in the shape
    for pij in xrange(len(prt)):
        # Get all of the points: 
        # • par[pij] = this part (A)
        # • par[pij+1] = next part (B)
        # • So pts[A:B] = points associated with this part
        # We then turn this into a polygon, and 
        # append it to the ptchs array.
        ptchs.append(Polygon(pts[par[pij]:par[pij+1]]))
    
    # Add this new ptchs array to the general
    # collection of patches, associated a facecolor, 
    # edgecolor, and linewidth
    ax.add_collection(PatchCollection(ptchs,facecolor=cccol[nshp,:],edgecolor='k', linewidths=.1))
    
# And now set the x/y-limits so that we get 
# everything on the figure.  
ax.set_xlim(0,+frame[2])
ax.set_ylim(0,+frame[3])

plot()

#print ggplot(pts, aes('x','y')) + geom_point(colour='steelblue')