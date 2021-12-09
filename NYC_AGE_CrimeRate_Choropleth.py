"""
Name: Shamim Rahman
Email: shamim.rahman78@myhunter.cuny.edu
Website URL: https://sramen1999.github.io/NYC_Age_CrimeRate_difference_Heat_Map/
Title: NYC Age Crime Rate difference Heat Map
Resources: geoJson file https://data.cityofnewyork.us/City-Government/Borough-Boundaries/tqmj-j8zm
data set file https://data.cityofnewyork.us/Public-Safety/NYPD-Arrest-Data-Year-to-Date-/uip8-fykc

NYC_AGE_CrimeRate_Choropleth.py: shows multiple choropleth map of NYC based on each borough and shows the
different amount of crime based on different age groups compared to each other on the same threshold_scale
CSci 39542:  Introduction to Data Science
Hunter College, City University of New York
Updated with ideas from:  https://towardsdatascience.com/using-folium-to-generate-choropleth-map-with-customised-tooltips-12e4cec42af2
"""

import pandas as pd
import pandasql as psql
import folium
import requests

'''
geoJson file
https://data.cityofnewyork.us/City-Government/Borough-Boundaries/tqmj-j8zm

data set file
https://data.cityofnewyork.us/Public-Safety/NYPD-Arrest-Data-Year-to-Date-/uip8-fykc

'''

# ChoroplethMap maker based on different age_group
def makeChoroplethMap(age, outFile, geoData, csvData):
   # Center map at Hunter:  40.7678° N, 73.9645° W
   m = folium.Map(location=[40.7678, -73.9645], scale=13, tiles="cartodbpositron")

   # Add in a choice of map tiles & icon to switch layers:
   tiles = ['stamenwatercolor', 'cartodbpositron', 'openstreetmap', 'stamenterrain']
   for tile in tiles:
      folium.TileLayer(tile).add_to(m)

   # Set the legend title to use the year and column selected:
   legendTitle = age + " Age Crime Rate "

   # Set up the shading (choropleth) map based on school district values for col:
   choropleth = folium.Choropleth(
      geo_data=geoData,
      name="choropleth",
      data=csvData,
      columns=["boro", age],
      key_on="feature.properties.boro_name",
      fill_color="Reds",
      fill_opacity=0.75,
      line_opacity=0.75,
      threshold_scale=[0, 1050, 3000, 6000, 9000, 12000, 15000, 18000],
      legend_name=legendTitle,
      highlight=True
   ).add_to(m)

   # Add in the layer with the shading:
   folium.LayerControl().add_to(m)
   # Add the labels when hovering:
   choropleth.geojson.add_child(folium.features.GeoJsonTooltip(["boro_name"], labels=True))

   # Save the html to the specified output file:
   m.save(outFile)

# function that downloads a file from a url
def downloadURL(url, name):
   req = requests.get(url)
   url_content = req.content
   csv_file = open(name, 'wb')
   csv_file.write(url_content)
   csv_file.close()

# download the csv file
url = 'https://data.cityofnewyork.us/resource/uip8-fykc.csv?$limit=115300'
name1 = 'NYPD_Arrest_Data_Year_to_Date_.csv'
downloadURL(url,name1)

# download the geojson file
url2 = 'https://data.cityofnewyork.us/resource/7t3b-ywvw.geojson'
name2 = 'Borough_Boundaries.geojson'
downloadURL(url2,name2)

# read the csv and geojson files
NYC_geo = 'Borough_Boundaries.geojson'
df0 = pd.read_csv("NYPD_Arrest_Data_Year_to_Date_.csv")


# create a dataframe with only arrest_boro and age_group
df = pd.DataFrame()
df['arrest_boro'] = df0['arrest_boro']
df['age_group'] = df0['age_group']

#Change the name of the borough to its full name
df['arrest_boro'] = df['arrest_boro'].replace(['B'],'Bronx')
df['arrest_boro'] = df['arrest_boro'].replace(['K'],'Brooklyn')
df['arrest_boro'] = df['arrest_boro'].replace(['M'],'Manhattan')
df['arrest_boro'] = df['arrest_boro'].replace(['Q'],'Queens')
df['arrest_boro'] = df['arrest_boro'].replace(['S'],'Staten Island')

# use pandasql to filter the data based on age and create a new column that counts the amount
# of crimes in each borough

# <18
less_than_18 = 'SELECT distinct("arrest_boro") as boro, count("arrest_boro") as "4-18" from df where age_group = "<18" group by boro'
res1 = psql.sqldf(less_than_18)
#print(res1)


# 18-24
eighteen_through_24 = 'SELECT distinct("arrest_boro") as boro, count("arrest_boro") as count from df where age_group = "18-24" group by boro'
res2 = psql.sqldf(eighteen_through_24)
#print(res2)

# 25-44
twenty_five_through_44 = 'SELECT distinct("arrest_boro") as boro, count("arrest_boro") as count from df where age_group = "25-44" group by boro'
res3= psql.sqldf(twenty_five_through_44)
#print(res3)

# 45-64
forty_five_through_64 = 'SELECT distinct("arrest_boro") as boro, count("arrest_boro") as count from df where age_group = "45-64" group by boro'
res4 = psql.sqldf(forty_five_through_64)
#print(res4)

# 65+
sixty_five_plus = 'SELECT distinct("arrest_boro") as boro, count("arrest_boro") as count from df where age_group = "65+" group by boro'
res5 = psql.sqldf(sixty_five_plus)
#print(res5)

# add the 5 dataframes back together
df2 = pd.DataFrame(res1)
df2["18-24"] = res2["count"]
df2["25-44"] = res3["count"]
df2["45-64"] = res4["count"]
df2["65+"] = res5["count"]
print(df2)

# names of the choropleth maps
outFile1 = "NYC_Age_CrimeRate_HeatMap_LessThan18.html"
outFile2 = "NYC_Age_CrimeRate_HeatMap_18Through24.html"
outFile3 = "NYC_Age_CrimeRate_HeatMap_25Through44.html"
outFile4 = "NYC_Age_CrimeRate_HeatMap_45Through64.html"
outFile5 = "NYC_Age_CrimeRate_HeatMap_65Plus.html"

# call the makeChoroplethMap function
makeChoroplethMap("4-18", outFile1, NYC_geo, df2)
makeChoroplethMap("18-24",outFile2,NYC_geo,df2)
makeChoroplethMap("25-44",outFile3,NYC_geo,df2)
makeChoroplethMap("45-64",outFile4,NYC_geo,df2)
makeChoroplethMap("65+",outFile5,NYC_geo,df2)

