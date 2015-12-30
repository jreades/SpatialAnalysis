# -*- coding: utf-8 -*-
import os
import fiona
import pandas as pd
import geopandas as gpd
import numpy as np

from scipy.interpolate import interp1d

basedir = os.path.join(os.path.expanduser("~"),"git","SpatialAnalysis")
shpfile = os.path.join(basedir,'shapefiles','LDN-LSOAs.shp')
datfile = os.path.join(basedir,'data','NS-SeC-LSOA','Data_NSSHRP_UNIT_URESPOP.csv')

shp = gpd.GeoDataFrame.from_file(shpfile)
basedir = os.path.join(os.path.expanduser("~"),"git","SpatialAnalysis")
shpfile = os.path.join(basedir,'shapefiles','LDN-LSOAs.shp')
datfile = os.path.join(basedir,'data','NS-SeC-LSOA','Data_NSSHRP_UNIT_URESPOP.csv')

shp = gpd.GeoDataFrame.from_file(shpfile)

df  = pd.read_csv(datfile, header=0, skiprows=[1], usecols=range(0,15))
df.columns = ["CDU_ID","GEO_CODE","GEO_LABEL",       
              "GEO_TYPE", "GEO_TYP2", "Total",        
              "Group1","Group2","Group3","Group4",    
              "Group5","Group6","Group7","Group8","NC"]
df.set_index('GEO_CODE')

print(type(shp))

shp.head()

print(type(shp.LSOA11NM))
print(type(shp.geometry))

print(shp.geometry.area.head())

shpdf = pd.merge(shp, df, left_on='LSOA11CD', right_on='GEO_CODE', how='left')

shp['centroid'] = gpd.GeoSeries(shp.geometry.representative_point(), index=shp.index)

shpdf.plot(column='Group1', figsize=(4,3), scheme='natural_breaks', k=7, colormap='Blues', linewidth=0)
shpdf.Group1.plot(column='geometry', scheme='natural_breaks', k=7, colormap='Blues', linewidth=0)

fig = plt.figure(dpi=300)
ax = fig.add_subplot(111, axisbg='w', frame_on=True)
shpdf.plot(column='Group5', scheme='natural_breaks', k=7, colormap='Blues', axes=ax)
plt.tight_layout()
plt.show()
