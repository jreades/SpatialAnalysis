from kartograph import Kartograph

config = {
  "proj": {
    "id": "sinusoidal"
  },
  "layers": [
    {
      "id": "grid", 
      "special": "graticule",
      "latitudes": 5,
      "longitudes": 5, 
      "fill": "blue"
    },
    {
      "id": "countries",
      "src": "ne_50m_admin_0_countries.shp",
      "attributes": "all", 
      "styles": {
        "stroke-width": "0.4px",
        "color": "#aaaaaa", 
        "fill": "red"
      }
    }
  ],
  "bounds": {
    "mode": "bbox", 
    "data": [70, 17, 135, 54]
  }
}

K = Kartograph()
K.generate(config, outfile='mymap.svg', stylesheet="world.css")