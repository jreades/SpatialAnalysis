# -*- coding: utf-8 -*-
import os
import geopandas as pd
import numpy as np

from scipy.interpolate import interp1d

basedir = os.path.join(os.path.expanduser("~"),"Documents","Output","NS Divide")
sf      = os.path.join(basedir,'Shapefiles','district_borough_unitary_region_simple.shp')

shp = pd.GeoDataFrame.from_file(sf)

shp.plot()
