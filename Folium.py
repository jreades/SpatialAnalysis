# sudo apt-get update
# sudo apt-get install libgdal-dev
# 
# pip install geopandas
# pip uninstall fiona
# In Canopy install fiona using the Package Manager
# In Canopy install pysal, basemap, descartes, folium
# pip install shapely==1.5.12
# pip install pyepsg
#
# To view GeoJSON locally:
# google-chrome --allow-file-access-from-files

import folium  
import pandas as pd
import geopandas as gpd 
import os

srcdir = os.path.join(os.path.expanduser('~'),'Dropbox','KCL Modules','Undergraduate','2nd Year','Spatial Analysis','SpatialAnalysis')
srcdir = os.path.join(os.path.expanduser('~'),'Documents','SpatialAnalysis')
shpdir = os.path.join(srcdir,'shapefiles')
outdir = os.path.join(os.path.expanduser('~'),'Desktop')
LDN_COORDINATES = (51.5180, -0.1134)

# Launch Google Chrome from the Terminal:
# # google-chrome --allow-file-access-from-files
# This is needed to get around a security restriction
# (normally a good thing) in Google Chrome to do with
# loading content from file://...

# 1. Create empty map zoomed in on London
map = folium.Map(location=LDN_COORDINATES, zoom_start=11)
# Add popup for lat/long coordinates
map.lat_lng_popover()
# Output map to HTML
map.create_map(os.path.join(outdir,'test.html'))

# 2. Add marker for King's
map = folium.Map(location=LDN_COORDINATES, zoom_start=13)
# Add Strand Campus
map.simple_marker(location=(51.5115, -0.1162), popup="King's College London")
map.lat_lng_popover()
map.create_map(os.path.join(outdir,'test.html'))

# 3. Add shapefile using geopandas
shpfile = os.path.join(shpdir,'LDN-LSOAs.shp')
df = gpd.GeoDataFrame.from_file(shpfile)

print(df.head())

# Need to convert the shapefile to GeoJSON
# in order to use it with Folium and do 
# things like joins
df.to_crs(epsg=4326, inplace=True)
with open(os.path.join(outdir,'test.geojson'),'w') as f:
    f.write(df.to_json())

# Now load up the geojson file for output
map = folium.Map(location=LDN_COORDINATES, zoom_start=13)
map.geo_json(geo_path=os.path.join(outdir,'test.geojson'), fill_color='blue', line_color='white', fill_opacity=0.5, line_opacity=0.25)
map.create_map(os.path.join(outdir,'test2.html'))

# 4. Choropleth mapping now
datfile = os.path.join(srcdir,'data','NS-SeC-LSOA','Data_NSSHRP_UNIT_URESPOP.csv')
df2 = pd.read_csv(datfile, header=0, skiprows=[1], usecols=range(0,15))
df2.columns = ["CDU_ID","GEO_CODE","GEO_LABEL",       
              "GEO_TYPE", "GEO_TYP2", "Total",        
              "Group1","Group2","Group3","Group4",    
              "Group5","Group6","Group7","Group8","NC"]

map = folium.Map(location=LDN_COORDINATES, zoom_start=11)
map.geo_json(geo_path=os.path.join(outdir,'test.geojson'),
   data_out=os.path.join(outdir,'choro.json'),
   data=df2[df2['Group1'] > 0],          # Some kind of boolean seems to be expected...
   columns=['GEO_CODE','Group1'],        # What do we want from the CSV file?
   key_on='feature.properties.LSOA11CD', # Note that this is Feature['Properties']['LSOA11CD'] in GeoJSON file
   legend_name='Group 1 NS-SeC Total',
   fill_color='BuPu', line_color='dlue', fill_opacity=0.85, line_opacity=0.25, line_weight=2)
map.create_map(os.path.join(outdir,'test3.html'))
