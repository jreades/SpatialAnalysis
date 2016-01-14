# -*- coding: utf-8 -*-
# from lxml import etree
import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.colors import Normalize
from matplotlib.collections import PatchCollection
from mpl_toolkits.basemap import Basemap
from shapely.geometry import Point, Polygon, MultiPoint, MultiPolygon
from shapely.prepared import prep
from pysal.esda.mapclassify import Natural_Breaks as nb
from descartes import PolygonPatch
import fiona
import pyproj 
import os
from itertools import chain

srcdir = os.path.join(os.path.expanduser('~'),'Dropbox','KCL Modules','Undergraduate','2nd Year','Spatial Analysis','SpatialAnalysis')

# Load the NS-SeC data
df = pd.read_csv(os.path.join(srcdir,'data','NS-SeC-LSOA','Data_NSSHRP_UNIT_URESPOP.csv'), header=0, skiprows=[1], usecols=range(0,15))
df.columns = ["CDU_ID","GEO_CODE","GEO_LABEL",       
              "GEO_TYPE", "GEO_TYP2", "Total",        
              "Group1","Group2","Group3","Group4",    
              "Group5","Group6","Group7","Group8","NC"]
print(df.head())

# Load the LSOA data into a GeoPandas data frame
gdf = gpd.GeoDataFrame.from_file(os.path.join(srcdir,'shapefiles','LDN-LSOAs.shp'))
print(gdf.head())

# Need to convert the shapefile to GeoJSON
# in order to use it with Folium and do 
# things like joins
# df.to_crs(epsg=4326, inplace=True)

# Now, open the shapefile a second time in order to get some data out of it
# so that we can set up our basemap:
shp = fiona.open(os.path.join(srcdir,'shapefiles','LDN-LSOAs.shp'))
bds = shp.bounds
shp.close()

# We now need to reproject our input data
bng   = pyproj.Proj(init='epsg:27700')
wgs84 = pyproj.Proj(init='epsg:4326')

xmin, ymin = pyproj.transform(bng, wgs84, bds[0], bds[1])
xmax, ymax = pyproj.transform(bng, wgs84, bds[2], bds[3])

m = Basemap(epsg=27700, llcrnrlon=xmin, llcrnrlat=ymin, urcrnrlon=xmax, urcrnrlat=ymax

extra = 0.01
w, h = xmax - xmin, ymax - ymin

# We've done two things here:
# - extracted the map boundaries
# - Calculated the extent, width and height of our basemap
# We're ready to create a Basemap instance, which we can use to plot our maps on.

m = Basemap(
    projection='tmerc',
    epsg=27700, 
    lon_0=-2.,
    lat_0=49.,
    ellps = 'WGS84',
    llcrnrlon=xmin - extra * w,
    llcrnrlat=ymin - extra + 0.01 * h,
    urcrnrlon=xmax + extra * w,
    urcrnrlat=ymax + extra + 0.01 * h,
    lat_ts=0,
    resolution='i',
    suppress_ticks=True)
m.readshapefile(
    os.path.join(srcdir,'shapefiles','LDN-LSOAs'),
    'london',
    color='none',
    zorder=2)

# The transverse mercator projection, because it exhibits less 
# distortion over areas with a small east-west extent. This projection 
# requires us to specify a central longitude and latitude, which I've set as -2, 49.

# set up a map dataframe
df_map = pd.DataFrame({
    'poly': [Polygon(xy) for xy in m.london],
    'ward_name': [ward['NAME'] for ward in m.london_info]})
df_map['area_m'] = df_map['poly'].map(lambda x: x.area)
df_map['area_km'] = df_map['area_m'] / 100000

# Create Point objects in map coordinates from dataframe lon and lat values
map_points = pd.Series(
    [Point(m(mapped_x, mapped_y)) for mapped_x, mapped_y in zip(df['lon'], df['lat'])])
plaque_points = MultiPoint(list(map_points.values))
wards_polygon = prep(MultiPolygon(list(df_map['poly'].values)))
# calculate points that fall within the London boundary
ldn_points = filter(wards_polygon.contains, plaque_points)

# Note that the map_points series was created by passing longitude and latitude values to our Basemap instance, m. This converts the coordinates from long and lat degrees to map projection coordinates, in metres. Our df_map dataframe now contains columns holding:
# - a polygon for each ward in the shapefile
# - its description
# - its area in square metres
# - its area in square kilometres
# We've also created a prepared geometry object from the combined ward polygons. We've done this in order to speed up our membership-checking operation significantly. We perform the membership check by creating a MultiPolygon from map_points, then filtering using the contains() method, which is a binary predicate returning all points which are contained within wards_polygon. The result is a Pandas series, ldn_points, which we will be using to make our maps.

# The two functions below make it easier to generate colour bars for our maps. Have a look at the docstrings for more detail – in essence, one of them discretises a colour ramp, and the other labels colour bars more easily.

# Convenience functions for working with colour ramps and bars
def colorbar_index(ncolors, cmap, labels=None, **kwargs):
    """
    This is a convenience function to stop you making off-by-one errors
    Takes a standard colour ramp, and discretizes it,
    then draws a colour bar with correctly aligned labels
    """
    cmap = cmap_discretize(cmap, ncolors)
    mappable = cm.ScalarMappable(cmap=cmap)
    mappable.set_array([])
    mappable.set_clim(-0.5, ncolors+0.5)
    colorbar = plt.colorbar(mappable, **kwargs)
    colorbar.set_ticks(np.linspace(0, ncolors, ncolors))
    colorbar.set_ticklabels(range(ncolors))
    if labels:
        colorbar.set_ticklabels(labels)
    return colorbar

def cmap_discretize(cmap, N):
    """
    Return a discrete colormap from the continuous colormap cmap.

        cmap: colormap instance, eg. cm.jet. 
        N: number of colors.

    Example
        x = resize(arange(100), (5,100))
        djet = cmap_discretize(cm.jet, 5)
        imshow(x, cmap=djet)

    """
    if type(cmap) == str:
        cmap = get_cmap(cmap)
    colors_i = np.concatenate((np.linspace(0, 1., N), (0., 0., 0., 0.)))
    colors_rgba = cmap(colors_i)
    indices = np.linspace(0, 1., N + 1)
    cdict = {}
    for ki, key in enumerate(('red', 'green', 'blue')):
        cdict[key] = [(indices[i], colors_rgba[i - 1, ki], colors_rgba[i, ki]) for i in xrange(N + 1)]
    return matplotlib.colors.LinearSegmentedColormap(cmap.name + "_%d" % N, cdict, 1024)

# Let's make a scatter plot
# draw ward patches from polygons
df_map['patches'] = df_map['poly'].map(lambda x: PolygonPatch(
    x,
    fc='#555555',
    ec='#787878', lw=.25, alpha=.9,
    zorder=4))

plt.clf()
fig = plt.figure()
ax = fig.add_subplot(111, axisbg='w', frame_on=False)

# we don't need to pass points to m() because we calculated using map_points and shapefile polygons
dev = m.scatter(
    [geom.x for geom in ldn_points],
    [geom.y for geom in ldn_points],
    5, marker='o', lw=.25,
    facecolor='#33ccff', edgecolor='w',
    alpha=0.9, antialiased=True,
    label='Blue Plaque Locations', zorder=3)
# plot boroughs by adding the PatchCollection to the axes instance
ax.add_collection(PatchCollection(df_map['patches'].values, match_original=True))
# copyright and source data info
smallprint = ax.text(
    1.03, 0,
    'Total points: %s\nContains Ordnance Survey data\n$\copyright$ Crown copyright and database right 2013\nPlaque data from http://openplaques.org' % len(ldn_points),
    ha='right', va='bottom',
    size=4,
    color='#555555',
    transform=ax.transAxes)

# Draw a map scale
m.drawmapscale(
    coords[0] + 0.08, coords[1] + 0.015,
    coords[0], coords[1],
    10.,
    barstyle='fancy', labelstyle='simple',
    fillcolor1='w', fillcolor2='#555555',
    fontcolor='#555555',
    zorder=5)
plt.title("Blue Plaque Locations, London")
plt.tight_layout()
# this will set the image width to 722px at 100dpi
fig.set_size_inches(7.22, 5.25)
plt.savefig('data/london_plaques.png', dpi=100, alpha=True)
plt.show()

# Scatter Plot

# We've drawn a scatter plot on our map, containing points with a 50 metre diameter, corresponding to each point in our dataframe.

# This is OK as a first step, but doesn't really tell us anything interesting about the density per ward – merely that there are more plaques found in central London than in the outer wards.

Creating a Choropleth Map, Normalised by Ward Area
df_map['count'] = df_map['poly'].map(lambda x: int(len(filter(prep(x).contains, ldn_points))))
df_map['density_m'] = df_map['count'] / df_map['area_m']
df_map['density_km'] = df_map['count'] / df_map['area_km']
# it's easier to work with NaN values when classifying
df_map.replace(to_replace={'density_m': {0: np.nan}, 'density_km': {0: np.nan}}, inplace=True)
We've now created some additional columns, containing the number of points in each ward, and the density per square metre and square kilometre, for each ward. Normalising like this allows us to compare wards.

# We're almost ready to make a choropleth map, but first, we have to divide our wards into classes, in order to easily distinguish them. We're going to accomplish this using an iterative method called Jenks Natural Breaks.

# Calculate Jenks natural breaks for density
breaks = nb(
    df_map[df_map['density_km'].notnull()].density_km.values,
    initial=300,
    k=5)
# the notnull method lets us match indices when joining
jb = pd.DataFrame({'jenks_bins': breaks.yb}, index=df_map[df_map['density_km'].notnull()].index)
df_map = df_map.join(jb)
df_map.jenks_bins.fillna(-1, inplace=True)

# We've calculated the classes (five, in this case) for all the wards containing one or more plaques (density_km is not Null), and created a new dataframe containing the class number (0 - 4), with the same index as the non-null density values. This makes it easy to join it to the existing dataframe. The final step involves assigning the bin class -1 to all non-valued rows (wards), in order to create a separate zero-density class.

# We also want to create a sensible label for our classes:

jenks_labels = ["<= %0.1f/km$^2$(%s wards)" % (b, c) for b, c in zip(
    breaks.bins, breaks.counts)]
jenks_labels.insert(0, 'No plaques (%s wards)' % len(df_map[df_map['density_km'].isnull()]))

# This will show density/square km, as well as the number of wards in the class.

# We're now ready to plot our choropleth map:

plt.clf()
fig = plt.figure()
ax = fig.add_subplot(111, axisbg='w', frame_on=False)

# use a blue colour ramp - we'll be converting it to a map using cmap()
cmap = plt.get_cmap('Blues')
# draw wards with grey outlines
df_map['patches'] = df_map['poly'].map(lambda x: PolygonPatch(x, ec='#555555', lw=.2, alpha=1., zorder=4))
pc = PatchCollection(df_map['patches'], match_original=True)
# impose our colour map onto the patch collection
norm = Normalize()
pc.set_facecolor(cmap(norm(df_map['jenks_bins'].values)))
ax.add_collection(pc)

# Add a colour bar
cb = colorbar_index(ncolors=len(jenks_labels), cmap=cmap, shrink=0.5, labels=jenks_labels)
cb.ax.tick_params(labelsize=6)

# Show highest densities, in descending order
highest = '\n'.join(
    value[1] for _, value in df_map[(df_map['jenks_bins'] == 4)][:10].sort().iterrows())
highest = 'Most Dense Wards:\n\n' + highest
# Subtraction is necessary for precise y coordinate alignment
details = cb.ax.text(
    -1., 0 - 0.007,
    highest,
    ha='right', va='bottom',
    size=5,
    color='#555555')

# Bin method, copyright and source data info
smallprint = ax.text(
    1.03, 0,
    'Classification method: natural breaks\nContains Ordnance Survey data\n$\copyright$ Crown copyright and database right 2013\nPlaque data from http://openplaques.org',
    ha='right', va='bottom',
    size=4,
    color='#555555',
    transform=ax.transAxes)

# Draw a map scale
m.drawmapscale(
    coords[0] + 0.08, coords[1] + 0.015,
    coords[0], coords[1],
    10.,
    barstyle='fancy', labelstyle='simple',
    fillcolor1='w', fillcolor2='#555555',
    fontcolor='#555555',
    zorder=5)
# this will set the image width to 722px at 100dpi
plt.tight_layout()
fig.set_size_inches(7.22, 5.25)
plt.savefig('data/london_plaques.png', dpi=100, alpha=True)
plt.show()