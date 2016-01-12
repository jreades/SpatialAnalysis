# -*- coding: utf-8 -*-
# Note: this requires shapely version 1.5.12 (*not* 1.5.13 as of Jan 5, 2016)
# > pip uninstall shapely
# > pip install shapely==1.5.12
# > pip install pyepsg
import os
import pyepsg
from cartopy.io import shapereader
import cartopy.crs as ccrs
import matplotlib.pyplot as plt

# This runs the default example of several 
# states in Brazil
kw = dict(resolution='50m', category='cultural',
          name='admin_1_states_provinces')

states_shp = shapereader.natural_earth(**kw)
shp = shapereader.Reader(states_shp)

from __future__ import unicode_literals

states = ('Minas Gerais', 'Mato Grosso', 'Goiás',
          'Bahia', 'Rio Grande do Sul', 'São Paulo')

subplot_kw = dict(projection=ccrs.PlateCarree())

fig, ax = plt.subplots(figsize=(5, 8),
                       subplot_kw=subplot_kw)
ax.set_extent([-82, -32, -45, 10])

ax.background_patch.set_visible(False)
ax.outline_patch.set_visible(False)

for record, state in zip(shp.records(), shp.geometries()):
    name = record.attributes['name'].decode('latin-1')
    if name in states:
        facecolor = 'DarkOrange'
    else:
        facecolor = 'LightGray'
    ax.add_geometries([state], ccrs.PlateCarree(),
                      facecolor=facecolor, edgecolor='black')

# Now for the UK
srcdir = os.path.join(os.path.expanduser('~'),'Dropbox','KCL Modules','Undergraduate','2nd Year','Spatial Analysis','SpatialAnalysis')
shpdir = os.path.join(srcdir,'shapefiles')
outdir = os.path.join(os.path.expanduser('~'),'Desktop')

shp = shapereader.Reader(os.path.join(shpdir,'LDN-LSOAs.shp'))

subplot_kw = dict(projection=ccrs.epsg(27700))

fig, ax = plt.subplots(figsize=(5, 5),
                       subplot_kw=subplot_kw)
ax.set_extent([0, 1000000, 0, 1000000], crs=ccrs.epsg(27700))
ax.background_patch.set_visible(False)
ax.outline_patch.set_visible(False)

for record, state in zip(shp.records(), shp.geometries()):
    name = record.attributes['LSOA11CD'].decode('latin-1')
    if name in states:
        facecolor = 'DarkOrange'
    else:
        facecolor = 'LightGray'
    ax.add_geometries([state], ccrs.epsg(27700),
                      facecolor=facecolor, edgecolor='black')