from sympy import Point, Polygon
from shapely.geometry import shape
import shapefile
import shapely

'''
    Purpose:



    Data Sources:
        - FCC Mobile Data coverage dataset: https://us-fcc.app.box.com/s/f220avmxeun345o6gzr7rwcnp1wslocf
        - US Fish and Wildlife critical habitat dataset: https://ecos.fws.gov/ecp/report/table/critical-habitat.html

'''
species_dict = {}
ch_shape = shapefile.Reader("data/crithab_all_layers/CRITHAB_POLY.shp")
ch_shaperecords = ch_shape.shapeRecords()
coverage_shape = shapefile.Reader("data/ATT_Mobility_LTE_Data/ATT_Mobility_349875.shp")
coverage_shaperecords = coverage_shape.shapeRecords()

'''
# print species names
species_names = []
for x in range(0, len(ch_shaperecords)):
    if ch_shaperecords[x].record[1] not in species_names:
        species_names.append(ch_shaperecords[x].record[1])
'''
coverage_standard_area = shape(coverage_shaperecords[0].shape).area

# go through each critical habitat polygon and check how many mobility coverage polygons fit within it
for x in range(0, len(ch_shaperecords)):
    print(x)
    if ch_shaperecords[x].record[1].find("larkspur") == -1:
         continue
    habitat_shape = shape(ch_shaperecords[x].shape)
    species_name = ch_shaperecords[x].record[1]
    for y in range(0, len(coverage_shaperecords)):
        print("    ",y)
        coverage_shape = shape(coverage_shaperecords[y].shape)
        if habitat_shape.contains(coverage_shape):
            # group all the critical habitat polygons together by species
            if species_name not in species_dict:
                species_dict[species_name] = {
                    "score" : 0,
                    "habitat_area": 0
                }
            species_dict[species_name]['score'] += 1
            species_dict[species_name]["habitat_area"] += habitat_shape.area


for sn in species_dict:
    species_dict[sn]['species_name'] = sn
    # multiply the number of mobility coverage polygons by the area the polygons covered and divide by the sum of all the areas of each species shapefile
    species_dict[sn]["percentage_of_area"] = species_dict[sn]['score']*coverage_standard_area/species_dict[sn]["habitat_area"]

# sort each species by critical habitat mobility coverage
species_list = (species_dict.values()).sort(key="percentage_of_area")

print(species_list)