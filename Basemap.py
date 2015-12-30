
#      projection       map projection. Print the module variable
#                       ``supported_projections`` to see a list of allowed
#                       values.
#      epsg             EPSG code defining projection (see
#                       http://spatialreference.org for a list of
#                       EPSG codes and their definitions).
#      aspect           map aspect ratio
#                       (size of y dimension / size of x dimension).
#      llcrnrlon        longitude of lower left hand corner of the
#                       selected map domain.
#      llcrnrlat        latitude of lower left hand corner of the
#                       selected map domain.
#      urcrnrlon        longitude of upper right hand corner of the
#                       selected map domain.
#      urcrnrlat        latitude of upper right hand corner of the
#                       selected map domain.

import matplotlib.pyplot as plt
import matplotlib.colors as cols
import pyproj
import fiona
import os
import numpy as np

from mpl_toolkits.basemap import Basemap
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from descartes import PolygonPatch

def randomcolour():
    return interpolatecolour([1.0, 0.0, 0.0], [0.0, 0.0, 1.0], np.random.uniform(0,1))
    #r = np.random.uniform(0,1)
    #g = np.random.uniform(0,1)
    #b = np.random.uniform(0,1)
    #return (r, g, b)

def mapvalue(value, low1, high1, low2, high2): 
    return ((float(value)-low1)/(high1-low1)) * (high2-low2) + low2

def normalise(value, low, high):
    return (float(value)-low)/(high-low)

# E.g.: colour1 = np.array([0.0,0.0,0.0])
#       colour2 = np.array([1.0,1.0,1.0])
def interpolatecolour(locolour, hicolour, value):
    acolour = 0.0, 0.0, 0.0
    zcolour = 1.0, 1.0, 1.0
    
    if type(locolour)==str and locolour.startswith('#'): 
        acolour = cols.hex2color(locolour)
    elif type(locolour)==list and all(isinstance(x, float) for x in locolour): 
        acolour = locolour[0], locolour[1], locolour[2]
    elif type(locolour)==np.ndarray and locolour.dtype==np.float64: 
        acolour = float(locolour[0]), float(locolour[1]), float(locolour[2])
    else: 
        raise ValueError("Couldn't make sense of locolour value, needs to be hexadecimal notation with '#', or list of floats, or numpy ndarray.")
    
    if type(hicolour)==str and hicolour.startswith('#'): 
        zcolour = cols.hex2color(hicolour)
    elif type(hicolour)==list and all(isinstance(x, float) for x in locolour): 
        zcolour = hicolour[0], hicolour[1], hicolour[2]
    elif type(hicolour)==np.ndarray and hicolour.dtype==np.float64:
        zcolour = float(hicolour[0]), float(hicolour[1]), float(hicolour[2])
    else: 
        raise ValueError("Couldn't make sense of hicolour value, needs to be hexadecimal notation with '#', or list of floats, or numpy ndarray.")
    
    return value * (zcolour[0]-acolour[0]) + acolour[0], value * (zcolour[1]-acolour[1]) + acolour[1], value * (zcolour[2]-acolour[2]) + acolour[2]

# Subroutine to convert polygons to patches
def polyPatch(poly):
    if 'geometry' in poly and 'coordinates' in poly['geometry']:
        xy = poly['geometry']['coordinates'][0]
        x, y = zip(*xy) 
        if datum == 'OSGB36':
            x1, y1 = pyproj.transform(bng,wgs84,x,y)
            x1, y1 = m(x1, y1)
        else:
            x1, y1 = m(x, y)
        #Turn back into tuple to make patch object
        xyn = zip(x1, y1)
        return xyn
    else:
        print("Error parsing purported polygon: " + type(poly))
        return None

# Some useful projections
bng   = pyproj.Proj(init='epsg:27700')
wgs84 = pyproj.Proj(init='epsg:4326')

############## Map #1 #################
# Map of bit of Australia
m = Basemap(llcrnrlon=130., llcrnrlat=-48, urcrnrlon=170., urcrnrlat=-10., resolution='h', area_thresh=10000)

m.drawcoastlines()
m.fillcontinents()
m.drawcountries(linewidth=2)
m.drawstates()

m.drawmapboundary(fill_color='aqua')

plt.legend()
plt.show()
del(m)

############## Map #2 #################
# Map of bit of Britain
xmin, ymin = pyproj.transform(bng, wgs84, 0, 0)
xmax, ymax = pyproj.transform(bng, wgs84, 667000, 1250000)

m = Basemap(epsg=27700, llcrnrlon=xmin, llcrnrlat=ymin, urcrnrlon=xmax, urcrnrlat=ymax, resolution='i')

m.drawcoastlines()
m.fillcontinents()
m.drawcountries(linewidth=2)
m.drawstates()

m.drawmapboundary(fill_color='blue')

plt.legend()
plt.show()
del(m)

############## Map #3 #################
# Map of bit of London with a shapefile
# and using the shapefile to work out the
# extents
ldn_lsoa = fiona.open(os.path.join('shapefiles','LDN-LSOAs.shp'))

fig = plt.figure()
ax  = fig.add_subplot(111)
w,h = xmax-xmin, ymax-ymin

m = Basemap(epsg=27700, llcrnrlon=xmin-0.2*w, llcrnrlat=ymin-0.2*h, urcrnrlon=xmax+0.2*w, urcrnrlat=ymax+0.2*h, resolution='i')

m.fillcontinents(color='gray',lake_color='aqua')

shplist = [ldn_lsoa]
for shpfile in shplist:
    for geom in shpfile:
        #get the geom
        #print geom['geometry']['type']
        xy = geom['geometry']['coordinates']
        datum = shpfile.crs.get('datum', 'none')
        if geom['geometry']['type']=='Point':
            #do something
            #print xy
            x = xy[0]
            y = xy[1]
            if datum == 'OSGB36':
                x1, y1 = pyproj.transform(bng,wgs84,x,y)
            else:
                x1, y1 = x, y
            x1, y1 = m(x1, y1)
            m.plot(x1, y1, 'bo')
        elif geom['geometry']['type']=='Polygon':
            #print 'Polygon'
            xy = geom['geometry']['coordinates'][0]
            x, y = zip(*xy) 
            if datum == 'OSGB36':
                x1, y1 = pyproj.transform(bng,wgs84,x,y)
                x1, y1 = m(x1, y1)
            else:
                x1, y1 = m(x, y)
            #Turn back into tuple to make patch object
            try:
                xy = zip(x1, y1)
                poly = Polygon(xy, facecolor=randomcolour(), alpha=0.4)
                plt.gca().add_patch(poly)
            except Exception as e:
                print e
            #m.plot(x1, y1, marker=None,color='b')
        elif geom['geometry']['type']=='MultiPolygon':
            print 'MultiPolygon'
            xy = geom['geometry']['coordinates'][0][0]
            x, y = zip(*xy) 
            if datum == 'OSGB36':
                x1, y1 = pyproj.transform(bng,wgs84,x,y)
                x1, y1 = m(x1, y1)
            else:
                x1, y1 = m(x, y)
            #Turn back into tuple to make patch object
            try:
                xy = zip(x1, y1)
                poly = Polygon(xy, facecolor=randomcolour(), alpha=0.4)
                plt.gca().add_patch(poly)
            except Exception as e:
                print e
        else:
            x, y = zip(*xy) 
            #transform the geom to wgs84
            if datum == 'OSGB36':
                x1, y1 = pyproj.transform(bng,wgs84,x,y)
                x1, y1 = m(x1, y1)
            else:
                x1, y1 = m(x, y)
            #x1 = list(x1)
            #y1 = list(y1)
            #print x1, y1
            m.plot(x1, y1, marker=None,color=randomcolour(), linewidth=2.0)

#cb = m.colorbar , "right", size="2%", pad="1%")
plt.show()