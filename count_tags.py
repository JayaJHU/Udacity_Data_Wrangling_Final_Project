import xml.etree.cElementTree as ET
from collections import defaultdict
import pprint

"""
We are using the iterative parsing to process the map file. We are going to 
find out not only what tags are there but also how many tags.  This is to get a sense 
on how much of which data we can expect to have in the map.
The count_tags function should return a dictionary with the 
tag name as the key and the number of times this tag can be encountered in 
the map as value.

"""

def count_tags(filename):
        
    tags = {}
    for event, elem in ET.iterparse(filename):
        if elem.tag in tags.keys():
            tags[elem.tag] += 1
        else:
            tags[elem.tag] = 1
        
    return tags
def test():

    tags = count_tags('cupertino.osm')
    pprint.pprint(tags)
      

if __name__ == "__main__":
    test()