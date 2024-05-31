import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
from collections import defaultdict

# Function to add a grid for each time step
def add_grid_for_time(collection, time, attributes, g_name='mesh'):
    new_grid = ET.SubElement(collection, 'Grid', {
        'Name': g_name,
        'GridType': 'Uniform'
    })
    ET.SubElement(new_grid, 'Time', {'Value': time})

    for attr in attributes:
        new_attribute = ET.SubElement(new_grid, 'Attribute', {
            'Name': attr.get('Name'),
            'AttributeType': attr.get('AttributeType'),
            'Center': attr.get('Center')
        })
        new_data_item = ET.SubElement(new_attribute, 'DataItem', {
            'Dimensions': attr.find('DataItem').get('Dimensions'),
            'Format': attr.find('DataItem').get('Format')
        })
        new_data_item.text = attr.find('DataItem').text

    # Preserve the xi:include tag from the original grid
    xi_include = ET.SubElement(new_grid, '{https://www.w3.org/2001/XInclude}include', {
        'xpointer': "xpointer(/Xdmf/Domain/Grid[@GridType='Uniform'][1]/*[self::Topology or self::Geometry])"
    })

def xdmf_convert(source_folder, source_file, source_file_extension, g_name='density'):
    # Parse the source XML file
    source_tree = ET.parse(source_folder + source_file + source_file_extension)
    source_root = source_tree.getroot()

    # Create a new target XML structure
    target_root = ET.Element('Xdmf', {
        'Version': '3.0',
        'xmlns:xi': 'https://www.w3.org/2001/XInclude'
    })
    domain = ET.SubElement(target_root, 'Domain')

    # Preserve the initial "mesh" grid
    mesh_grid = source_root.find('.//Grid[@Name="mesh"]')
    domain.append(mesh_grid)

    # Collect grids and group by time values
    time_grids = defaultdict(list)

    ttt = source_root.findall('.//Grid')

    for grid in source_root.findall('.//Grid'):
        # Excluding search for non-existing values
        if grid.find('Time') is None:
            continue
        name = grid.get('Name')
        if name == 'mesh':
            continue  # Skip the "mesh" grid
        time_value = grid.find('Time').get('Value')
        time_grids[time_value].append(grid)

    # Create a new grid collection
    grid_collection = ET.SubElement(domain, 'Grid', {
        'Name': 'TimeSeries',
        'GridType': 'Collection',
        'CollectionType': 'Temporal'
    })

    # Add grids for each time step to the target collection
    for time_value, grids in time_grids.items():
        attributes = []
        for grid in grids:
            for element in grid:
                if element.tag == '{https://www.w3.org/2001/XInclude}include':
                    continue  # Skip the xi:include tag
                if element.tag == 'Attribute':
                    attributes.append(element)
        add_grid_for_time(grid_collection, time_value, attributes)

    # Convert the target XML to a string with indentation
    target_str = ET.tostring(target_root, encoding='unicode')
    pretty_target_str = minidom.parseString(target_str).toprettyxml(indent="  ")

    # Write the pretty-printed XML to a file
    with open(source_folder + source_file + '_adjust' + source_file_extension, 'w', encoding='utf-8') as f:
        f.write(pretty_target_str)