"""
1. Use the iterparse to iteratively step through each top level element in XML
2. Shaping each element into certain data structures
3. Write each data structure to the appropriate csv files
Reference: this code was modified from
'Case study: OpenStreetMap Data[SQL] Quiz 11'
"""

import xml.etree.ElementTree as ET
import pprint
from collections import defaultdict
import re
import csv
import codecs
import cerberus
import schema
import sqlite3

OSM_PATH = "cupertino.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

# Functions used in the shape_element function to format the street names
def update_street_name(name, mapping):
    for key,value in mapping.iteritems():
        if key in name:
            return name.replace(key,value)
    return name       


def audit_street_name_tag(element): 
    street_name=element.get('v')
    m = street_type_re.search(street_name)
    if m:
        better_street_name=update_street_name(street_name,mapping)
        return better_street_name
    return street_name

# Functions used in the shape_element function to format the postal codes
def update_postcode(name): 
    if "-" in name:
        name = name.split("-")[0].strip()
    elif "CA" in name:
        name = name.split("CA ")[1].strip('CA ')
    elif len(str(name))>5:
        name=name[0:5]
    elif name.isdigit()==False:
         name=00000
    return name

def audit_postcode_tag(element,regex=re.compile(r'^\d{5}$')):
    post_code=element.get('v')
    m = regex.search(post_code)
    if m:
        better_postcode=update_postcode(post_code)
        return better_postcode
    return post_code

"""Clean and shape node or way XML element to Python dictionary"""

def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    
    
    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = [] # Handle secondary tags the same way for both node and way elements
              

    if element.tag=='node':
        for field in node_attr_fields:
            node_attribs[field]=element.get(field)
                 
        if element.find('tag') is None:
            pass
#           print 'No Tags'
           
        elif element.find('tag') is not None:
            tag_attrib={}
            node_tag_fields=NODE_TAGS_FIELDS
            for tag in element.iter('tag'):
                if PROBLEMCHARS.search(tag.attrib['k']):
                    pass
                elif LOWER_COLON.search(tag.attrib['k']):
                    tag_attrib[node_tag_fields[0]]=element.get('id')
                    tag_attrib[node_tag_fields[1]]=tag.get('k')[(tag.get('k').find(':')+1):]
                    if tag.attrib['k']== "addr:street":
                        tag_attrib[node_tag_fields[2]]=audit_street_name_tag(tag)
                    elif tag.attrib['k']== "addr:postcode":
                        tag_attrib[node_tag_fields[2]]=audit_postcode_tag(tag)       
                    else:
                        tag_attrib[node_tag_fields[2]]=tag.get('v')
                    tag_attrib[node_tag_fields[3]]=tag.get('k').split(':')[0]
                    tags.append(tag_attrib.copy())
                    
                else:
                    tag_attrib[node_tag_fields[0]]=element.get('id')
                    tag_attrib[node_tag_fields[1]]=tag.get('k')
                    if tag.attrib['k']== "addr:street":
                        tag_attrib[node_tag_fields[2]]=audit_street_name_tag(tag)
                    elif tag.attrib['k']== "addr:postcode":
                        tag_attrib[node_tag_fields[2]]=audit_postcode_tag(tag)    
                    else:    
                        tag_attrib[node_tag_fields[2]]=tag.get('v')
                    tag_attrib[node_tag_fields[3]]=default_tag_type
                    tags.append(tag_attrib.copy())
            
#        pprint.pprint( {'node':node_attribs,'node_tags':tags})        
                
    elif element.tag=='way':
        for field in way_attr_fields:
            way_attribs[field]=element.get(field)
    
        way_node_attrib={}
        way_node_fields=WAY_NODES_FIELDS
        for nd in element.findall('nd'):
            way_node_attrib[way_node_fields[0]]=element.get('id')
            way_node_attrib[way_node_fields[1]]=nd.get('ref')
            way_node_attrib[way_node_fields[2]]=element.findall('nd').index(nd)
            way_nodes.append(way_node_attrib.copy())
#       pprint.pprint({'way':way_attribs,'way_nodes':way_nodes})
        
           
        
        if element.find('tag') is None:
            pass
#           print 'No Tags'
           
        elif element.find('tag') is not None:
            way_tag_attrib={}
            way_tag_fields=WAY_TAGS_FIELDS
            for tag in element.iter('tag'):
                if PROBLEMCHARS.search(tag.attrib['k']):
                    pass
                elif LOWER_COLON.search(tag.attrib['k']):
                    way_tag_attrib[way_tag_fields[0]]=element.get('id')
                    way_tag_attrib[way_tag_fields[1]]=tag.get('k')[(tag.get('k').find(':')+1):]
                    if tag.attrib['k']== "addr:street":
                        way_tag_attrib[way_tag_fields[2]]=audit_street_name_tag(tag)
                    elif tag.attrib['k']== "addr:postcode":
                        way_tag_attrib[way_tag_fields[2]]=audit_postcode_tag(tag)    
                    else:
                        way_tag_attrib[way_tag_fields[2]]=tag.get('v')
                    way_tag_attrib[way_tag_fields[3]]=tag.get('k').split(':')[0]
                    tags.append(way_tag_attrib.copy())
                    
                else:
                    way_tag_attrib[way_tag_fields[0]]=element.get('id')
                    way_tag_attrib[way_tag_fields[1]]=tag.get('k')
                    if tag.attrib['k']== "addr:street":
                        way_tag_attrib[way_tag_fields[2]]=audit_street_name_tag(tag) 
                    elif tag.attrib['k']== "addr:postcode":
                        way_tag_attrib[way_tag_fields[2]]=audit_postcode_tag(tag)    
                    else:   
                        way_tag_attrib[way_tag_fields[2]]=tag.get('v')
                    way_tag_attrib[way_tag_fields[3]]=default_tag_type
                    tags.append(way_tag_attrib.copy())
#        pprint.pprint({'way':way_attribs,'way_tags':tags})
#        pprint.pprint({'way':way_attribs,'way_nodes':way_nodes,'way_tags':tags})
        
    

    
    if element.tag == 'node':
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}

# ================================================== #
#               Helper Functions                     #
# ================================================== #

def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

# ================================================== #
#               Main Function                        #
# ================================================== #

def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])

if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=True)