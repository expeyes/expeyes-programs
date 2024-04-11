# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import argparse, json
from json import JSONEncoder
import struct

import xml.etree.ElementTree as ET

propMap = {}
imageMap = {}


def get_png_dimensions(image_path):
    with open(image_path, 'rb') as file:
        header = file.read(24)
    width, height = struct.unpack('!II', header[16:24])
    return width, height


class Element:
    ID = ""
    desc = ""
    x = ""
    y = ""

    def __init__(self, identifier, xc, yc, description):
        self.x = xc
        self.y = yc
        self.ID = identifier
        self.desc = description

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


class MyEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


elements = {}


def load_defaults():
    global propMap, imageMap, elements
    with open('../defaults.aiken', 'rb') as file:
        buffer = file.read()

    DefaultPropsFile = buffer.decode('utf-8')
    lines = DefaultPropsFile.split('\n')
    currentProp = ''

    for line in lines:
        if len(line) == 0:
            continue  # ignore blank lines

        if '.svg' in line or '.png' in line or '.jpg' in line:
            currentProp = line.split('.')[0]
            propMap[currentProp] = ''  # description goes here
            imageMap[currentProp] = line  # Image filename
        else:
            propMap[currentProp] += '\n' + line


def extract_svg_description(input_file, output_file):
    tree = ET.parse(input_file)
    root = tree.getroot()
    raster_file_name = input_file.replace('.svg', '.png')
    raster_width, raster_height = get_png_dimensions(raster_file_name)
    vector_width = float(root.attrib['width'])
    vector_height = float(root.attrib['height'])

    # namespace = {'svg': 'http://www.w3.org/2000/svg'}
    namespace = {
        "svg": "http://www.w3.org/2000/svg",
        "dc": "http://purl.org/dc/elements/1.1/"
    }
    text_nodes = []

    # Find the elements
    for text_elem in root.findall('.//svg:text', namespace):
        x = float(text_elem.attrib['x']) if 'x' in text_elem.attrib else 0
        y = float(text_elem.attrib['y']) if 'y' in text_elem.attrib else 0
        ID = text_elem.attrib.get('id', '')
        children = list(text_elem)
        desc = ''
        textid = ''
        identifier = text_elem.attrib['id']

        for a in children:
            if a.tag.__contains__('desc'):
                desc = a.text
            if a.tag.__contains__('tspan'):
                textid = a.text

        print('identifier', identifier, textid)

        if textid in propMap:  # Text based ID takes preference over internal ID
            identifier = textid

        if textid is not None:  # Text based ID takes preference over internal ID
            if textid in propMap or len(textid.split(':')) > 1:
                identifier = textid

        identifier_parts = identifier.split(':')
        if identifier in propMap or len(identifier_parts) >= 2:  # TODO : Add supported sensors list
            if x >= 0:
                x = raster_width * x / vector_width
                y = raster_height * y / vector_height
                # print(identifier, 'xymod:', x, y)
                elements[identifier] = Element(identifier, x, y, desc)

    # Store Help content
    description = root.find('.//dc:description', namespace)
    if description is not None:
        with open(output_file.replace('.json', '.help'), 'w') as helpfile:  # Writing to file here
            helpfile.write(description.text.strip())

    # Store automatic record configuration
    contrib = root.find('.//dc:contributor', namespace)
    if contrib is not None:
        contrib = contrib.find('.//dc:title', namespace)
        if contrib is not None:
            with open(output_file.replace('.json', '.record'), 'w') as recfile:  # Writing to file here
                recfile.write('[default]\n') #Required for configparser module
                recfile.write(contrib.text)

    # Store Creator Infor
    '''
    #Store Help external source file name
    description = root.find('.//dc:source', namespace)
    if description is not None:
        params['source'] = description.text.strip()

    contrib = root.find('.//dc:creator', namespace)
    if contrib is not None:
        contrib = contrib.find('.//dc:title', namespace)
        if contrib is not None:
            params['creator'] = contrib.text
    '''

    with open(output_file, 'w') as jsonfile:  # Writing to file here
        jsonfile.write(json.dumps(elements, cls=MyEncoder, sort_keys=True, indent=4))

    print(f"Description metadata and json extracted '. , {elements.keys()}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='SVG Description Extractor')
    parser.add_argument('input_file', type=str, help='Input SVG file')
    parser.add_argument('-o', '--output_file', type=str, default='output.txt', help='Output text file')

    args = parser.parse_args()
    load_defaults()

    extract_svg_description(args.input_file, args.output_file)
