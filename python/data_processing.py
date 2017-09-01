import xml.etree.ElementTree
import sys

"""
Eats an xml of the format https://wit3.fbk.eu/mt.php?release=2016-01
and outputs a text file which fetches the subtitles of the talk
one subtitle per line
"""

def load_data(filepath,output):
    e = xml.etree.ElementTree.parse(filepath+'.xml').getroot()
    print e.tag
    for child in e:
        print child.tag, child.attrib
    text_file = open(output+".txt", "w")
    for a in e.iter('seg'):
        print a.text
        text_file.write(a.text.encode('utf-8')+'\n')
    text_file.close()

if __name__=='__main__':
    # pass xml file and output name
    load_data(sys.argv[1],sys.argv[2])
