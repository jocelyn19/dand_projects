# -*- coding: utf-8 -*-
# Export to JSON for MONGO DB------------------------------------------------------------------------------
# the corrected data are shaped in a dictionary in order to be saved into a JSON file in order to be imported by MongoDB later on.
# The following operations are performed:
# •only 2 types of top level tags: "node" and "way" are processed
# •all attributes of "node" and "way" are turned into regular key/value pairs
# •some attributes "version", "changeset", "timestamp", "user", "uid" are added under a key "created"
# •attributes for latitude and longitude are added to a "pos" array,
# •address related items are added to the tag "address"
# •other second level tag "k" are added to the field "others"
# script 4-data.py
import codecs
import json
import xml.etree.cElementTree as ET
from bson import json_util
OSM_FILE = "france-finistere-sud_export.osm" 
# List of structure fields for created for the json file
CREATED = [ "version", "changeset", "timestamp", "user", "uid"]
#OSM_FILE = "finistere-sud-france_export.osm"

def shape_element(element):
# Create a JSON file as a preparation step for MongoDB DataBase
# Shape the XML file into a JSON alike structure
    node = {}
    # process only 2 types of top level tags: "node" and "way"
    if element.tag == "node" or element.tag == "way" :
        # "type"
        node['type'] = element.tag
        # "id"
        if 'id' in element.attrib:
            node['id'] = element.get('id')
        # "visible"
        if 'visible' in element.attrib:
            node['visible'] = "true"
            node['visible'] = element.get('visible')
        # "pos"
        if 'lat' in element.attrib and 'lon' in element.attrib:
            node['pos'] = [0,0]
            node['pos'][0] = float(element.get('lat'))
            node['pos'][1] = float(element.get('lon'))
        # "created"
        for key in element.attrib:
            value = element.attrib[key]
            if "created" not in node.keys():
                    node["created"] = {}
            if key in CREATED:
                node["created"][key] = value
        # 2nd level "address"
        for tag in element.iter("tag"):
            key = tag.attrib['k']
            value = tag.attrib['v']
            # Apply correction
            if is_street_name(tag): # if the key value is "addr:street"
                m = street_type_re.search(value)
                if m:
                    street_type = m.group() # Boulevard
                    if street_type not in mapping:
                        value = update_name(value, mapping)
        # 2nd level "others"
            elif not problemchars.match(key):
                if "others" not in node.keys():
                    node["others"] = {}
                node["others"][key] = value
        # 2nd level "way"
        for tag in element.iter("nd"):
            if "node_refs" not in node.keys():
                node["node_refs"] = []
            node["node_refs"].append(tag.attrib['ref'])
        return node
    else:
        return None

def process_map(file_in, pretty = False):
    file_out = "{0}.json".format(file_in)
    with open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                if pretty:
                    fo.write(json.dumps(el, indent=2, default=json_util.default)+"\n")
                else:
                    fo.write(json.dumps(el, default=json_util.default) + "\n")

print ("# JSON file for import into Mongo DB")
process_map(OSM_FILE, True)
print ('--> Done!')
