import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

# The Cupertino OSM file and its sample """

OSM_FILE = "cupertino.osm"
#SAMPLE_FILE = "sample.osm"

"""Regex to get the five integer US zip code.""" 
#post_code_re = re.compile(r'\d{5}')
post_code_re = re.compile(r'^\d{5}$')


""" Checks if the key in an element tag is for a postal code. Returns True if it is."""
def is_post_code(element):
    return (element.get('k') == "addr:postcode")


"""This function adds the value to a data structure."""
def audit_post_code_type(post_code_types, post_code):
    post_code_types.append(post_code)    


""" Iteratively parses through each element in an XML file (in this case
    for OSM). First, checks if the element is a node or way element. If
    True then the function will iterate through each tag in the node or way
    element, and run the 'is_post_code' function on it. If True, the
    function will run the 'audit_post_code_type' function on it.
        Returns:
            dictionary: post code type:postcode value pairs.
"""
def audit(osmfile):
    osm_file = open(osmfile, "r")
    post_code_types = []
    for event, element in ET.iterparse(osmfile, events=("start", )):
        if element.tag == "way" or element.tag == "node":
            for tag in element.iter("tag"):
                if is_post_code(tag):
                    audit_post_code_type(post_code_types, tag.attrib['v'])
    osm_file.close()

    return post_code_types

def test():
    post_code_dict = audit(OSM_FILE)
    post_code_set = set(post_code_dict)
    pprint.pprint(post_code_set)

if __name__ == '__main__':
    test()