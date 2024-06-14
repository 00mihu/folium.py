import pandas as pd
import geopandas as gpd

import folium
from folium import Choropleth
from folium.plugins import HeatMap

from learntools.core import binder
binder.bind(globals())
from learntools.geospatial.ex3 import *

def embed_map(m, file_name):
    from IPython.display import IFrame
    m.save(file_name)
    return IFrame(file_name, width='100%', height='500px')

plate_boundaries = gpd.read_file("../input/geospatial-learn-course-data/Plate_Boundaries/Plate_Boundaries/Plate_Boundaries.shp")
plate_boundaries['coordinates'] = plate_boundaries.apply(lambda x: [(b,a) for (a,b) in list(x.geometry.coords)], axis='columns')
plate_boundaries.drop('geometry', axis=1, inplace=True)

plate_boundaries.head()
# head
earthquakes = pd.read_csv("../input/geospatial-learn-course-data/earthquakes1970-2014.csv", parse_dates=["DateTime"])
earthquakes.head()

# base map with plate boundaries
m_1 = folium.Map(location=[35,136], tiles='cartodbpositron', zoom_start=5)
for i in range(len(plate_boundaries)):
    folium.PolyLine(locations=plate_boundaries.coordinates.iloc[i], weight=2, color='black').add_to(m_1)

# map
embed_map(m_1, 'q_1.html')


m_2 = folium.Map(location=[35, 136], tiles='cartodbpositron', zoom_start=5)

# plate boundaries
for i in range(len(plate_boundaries)):
    folium.PolyLine(locations=plate_boundaries.coordinates.iloc[i], weight=2, color='black').add_to(m_2)

# visualize earthquake depth
for i in range(len(earthquakes)):
    folium.Circle(
        location=[earthquakes.iloc[i]['Latitude'], earthquakes.iloc[i]['Longitude']],
        radius=2000,  # Adjust the radius as per your requirement
        color=color_producer(earthquakes.iloc[i]['Depth']),
        fill=True,
        fill_opacity=0.6,
        fill_color=color_producer(earthquakes.iloc[i]['Depth'])).add_to(m_2)

# color each circles based on depth
def color_producer(val):
    if val < 50:
        return 'forestgreen'
    elif val < 100:
        return 'darkorange'
    else:
        return 'darkred'

# map to an html
m_2.save('q_2.html')
m_2

# gdf = GeoDataFrame with prefecture boundaries
prefectures = gpd.read_file("../input/geospatial-learn-course-data/japan-prefecture-boundaries/japan-prefecture-boundaries/japan-prefecture-boundaries.shp")
prefectures.set_index('prefecture', inplace=True)
prefectures.head()

# df containing population of each prefecture
population = pd.read_csv("../input/geospatial-learn-course-data/japan-prefecture-population.csv")
population.set_index('prefecture', inplace=True)

# calc area sq2 of each pref
area_sqkm = pd.Series(prefectures.geometry.to_crs(epsg=32654).area / 10**6, name='area_sqkm')
stats = population.join(area_sqkm)

# density km2 of prefs
stats['density'] = stats["population"] / stats["area_sqkm"]
stats.head()

m_3 = folium.Map(location=[35,136], tiles='cartodbpositron', zoom_start=5)

# choropleth map - population density
Choropleth(geo_data=prefectures.__geo_interface__, 
           data=stats['density'], 
           key_on="feature.properties.prefecture",  # Adjust the key_on parameter
           fill_color='YlGnBu', 
           legend_name='Population Density (people per sqkm)'
          ).add_to(m_3)

# save to HTML
embed_map(m_3, 'q_3.html')
m_3
