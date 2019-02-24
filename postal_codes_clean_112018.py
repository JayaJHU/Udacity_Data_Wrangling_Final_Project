import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

'''
We want all the postal codes in the standard 5 digit style. This means we have to change the following 
postal codes:-
1. Postal codes with more than 5 digits
2. Postal codes with "CA" next to it 
3. Postal codes that differ from the standard 5 digit style

'''


postcode_type_re = re.compile(r'^\d{5}$')

postcode_types = defaultdict(set)

expected_postcode = {}

def audit_post_codes(postcode_types, postcode_name, regex, expected_postcode):
    m = regex.search(postcode_name)
    if m:
        postcode_type = m.group()
        if postcode_type not in expected_postcode:
             postcode_types[postcode_type].add(postcode_name)

def is_postcode_name(elem):
    return (elem.attrib['k'] == "addr:postcode")


def audit(filename, regex):
    for event, elem in ET.iterparse(filename, events=("start",)):
        if elem.tag == "way" or elem.tag == "node":
            for tag in elem.iter("tag"):
                if is_postcode_name(tag):
                    audit_post_codes(postcode_types, tag.attrib['v'], regex, expected_postcode)
    pprint.pprint(dict(postcode_types))


'''
Using the OSM_FILE as an input to audit the postcodes
'''   
    
audit(OSM_FILE, postcode_type_re)


for postcode_type, ways in postcode_types.iteritems(): 
        for name in ways:
            if "-" in name:
                name = name.split("-")[0].strip()
            if "CA " in name:
                name = name.split("CA ")[1].strip('CA ')
            elif len(str(name))>5:
                name=name[0:5]
            elif name.isdigit()==False:
                print 'OK'
            print name