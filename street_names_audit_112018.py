import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

# The Cupertino OSM file and its sample 

OSM_FILE = "cupertino.osm"
# SAMPLE_FILE = "sample.osm"

# Regex to get the last word in a string of words. This is where
# the street type (eg. Street) usually is.
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

# List of expected values i.e. street names that are correct.
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square",
            "Lane", "Road", "Trail", "Parkway", "Commons", "Broadway",
            "Crescent", "Way", "Circle", "Plaza", "Terrace", "West",
            "Portofino", "Sorrento", "Volante", "Loop", "Expressway",
            "Barcelona", "Madrid","Marino","Napoli", "Palamos","East", "Paviso",
            "Seville", "Creek", "Common", "North", "South"]

# Dictionary of street types that I decided to reformat by using "mapping"
mapping = { "Ave" : "Avenue",
            "Blvd": "Boulevard"
            }

def audit_street_type(street_types, street_name):
    """ Takes in an empty dictionary of street type: street name value pairs and
        the street name and uses the regex to isolate the street type. If there
        is a match, the match object is converted to a string and if the street
        type is not in the expected list, adds the street type and street name
        to the dictionary.
    """
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)
        

def is_street_name(element):
    """ Checks whether the attribute k="addr:street".
    Essentially, if the key in an element tag is for a street. Returns True if
    it is.
    """
    return (element.get('k') == "addr:street")


def audit(osmfile):
    """ Iteratively parses through each element in an XML file (in this case
        for OSM). First checks if the element is a node or way element. If
        True, then the function will iterate through each tag in the node or way
        element, and run the 'is_street_name' function on it. If True, the
        function will run the 'audit_street_type' function on it.
            Returns:
                dictionary: street type:street name value pairs.
    """
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, element in ET.iterparse(osmfile, events=("start", )):
        if element.tag == "way" or element.tag == "node":
            for tag in element.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()

    return street_types

def update_name(name, mapping):
    for key,value in mapping.iteritems():
        if key in name:
            return name.replace(key,value)
    return name   

def test():
    street_dict = audit(OSM_FILE)
    pprint.pprint(dict(street_dict))

if __name__ == '__main__':
    test()
