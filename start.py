import geopandas as gpd
from geopandas.tools import sjoin
import csv
'''
    Purpose:



    Data Sources:
        - FCC Mobile Data coverage dataset: https://us-fcc.app.box.com/s/f220avmxeun345o6gzr7rwcnp1wslocf
        - US Fish and Wildlife critical habitat dataset: https://ecos.fws.gov/ecp/report/table/critical-habitat.html

'''
species_dict = {}
ch_df = gpd.read_file(r'data/crithab_all_layers/CRITHAB_POLY.shp')
ch_df['ch_geometry'] = ch_df.geometry
coverage_df = gpd.read_file(r'data/ATT_Mobility_LTE_Data/ATT_Mobility_349875.shp')
coverage_df['coverage_geometry'] = coverage_df.geometry

with open('whitelisted_species.csv', newline='\n') as csvfile:
    whitelisted_items = csv.DictReader(csvfile)
    whitelisted = [row['species'] for row in whitelisted_items]
    #print(whitelisted)
    csvfile.close()

ch_df = ch_df[ch_df.comname.isin(whitelisted)]

joined_geometries = ch_df.sjoin(coverage_df)

for index,row in joined_geometries.iterrows():
    species_name = row['comname']
    # group all the critical habitat polygons together by species
    if species_name not in species_dict:
        species_dict[species_name] = {
            "coverage_area" : 0,
            "original_habitat_area": 0
        }
    species_dict[species_name]['coverage_area'] += row.ch_geometry.intersection(row.coverage_geometry).area
    species_dict[species_name]["original_habitat_area"] += row.ch_geometry.area



for sn in species_dict:
    species_dict[sn]['species_name'] = sn
    # multiply the number of mobility coverage polygons by the area the polygons covered and divide by the sum of all the areas of each species shapefile
    
    species_dict[sn]["percentage_of_area"] = species_dict[sn]["coverage_area"]/species_dict[sn]["original_habitat_area"]
    #print(f'{species_dict[sn]["percentage_of_area"]} = {species_dict[sn]["coverage_area"]}/{species_dict[sn]["original_habitat_area"]}')

# sort each species by critical habitat mobility coverage
species_list = list(species_dict.values())

def sort_by_area(the_dict):
    return the_dict['percentage_of_area']

species_list.sort(key=sort_by_area, reverse=True)

#print(species_list)
for i,row in enumerate(species_list):
    if i >= 10: 
        break
    print(species_list[i]['species_name'], " - ", round(species_list[i]['percentage_of_area']*100, 2),"%")