import xml.etree.ElementTree as ET

def parse_hierarchy(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    def print_node(node, indent=0):
        print("  " * indent + f"<{node.tag} ", end="")
        for key, value in node.attrib.items():
            print(f'{key}="{value}" ', end="")
        print(">")
        for child in node:
            print_node(child, indent + 1)
        print("  " * indent + f"</{node.tag}>")

    print_node(root)

parse_hierarchy("hierarchy.xml")