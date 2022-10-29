'''from email.mime import image'''
'''from msilib.schema import Error'''
from xml.dom import minidom

from matplotlib.font_manager import weight_dict
import utils

import aiofiles

class SVGManager():
    def __init__(self, env):
        self.env = env
        self.doc = minidom.parse(env["DEFAULT_SVG_FILE_NAME"])
        self.updating_allowed = True

    def get_path_by_title(self, title):
        for path in self.doc.getElementsByTagName('path'):
            if path.getAttribute('title') == title:
                return path
        raise Error
        
    def set_attribute_on_every_region(self, attribute, value):
        for path in self.doc.getElementsByTagName('path'):
            path.setAttribute(attribute, value)
    
    def set_attribute_on_specific_region(self, region_name, attribute, value):
        for path in self.doc.getElementsByTagName('path'):
            if path.getAttribute('title') == region_name:
                path.setAttribute(attribute, value)
            
    def set_region_as_eliminated(self, region_name):
        self.set_attribute_on_specific_region(region_name, 'fill', 'red')
    
    def set_region_as_winner(self, region_name):
        self.set_attribute_on_specific_region(region_name, 'fill', 'green')

    def set_region_as_in_battle(self, region_name):
        self.set_attribute_on_specific_region(region_name, 'fill', 'orange')
    
    def reset_region_style(self, region_name):
        self.set_attribute_on_specific_region(region_name, 'fill', 'black')
    
    def set_points_to_region(self, points, region_name): 
        for text in self.doc.getElementsByTagName('text'):
            if text.getAttribute('title') == region_name:
                text.firstChild.nodeValue = points

    def reset_all_points(self):
        for text in self.doc.getElementsByTagName('text'):
            text.firstChild.nodeValue = 0

    async def updatesvg(self):
        if self.updating_allowed:
            async with aiofiles.open(self.env["UPDATE_SVG_FILE_NAME"], 'w') as f:
                await f.write(self.doc.toxml())

    def initsvg(self, data_rows):
        for row in data_rows:
            region_name, points, in_battle, eliminated, battle_points = row
            if (in_battle): 
                self.set_region_as_in_battle(region_name)
                self.set_points_to_region(battle_points, region_name)
            else:
                self.set_points_to_region(points, region_name)

            if (eliminated): self.set_region_as_eliminated(region_name)    

    def stop_updating(self):
        self.updating_allowed = False

'''
debug stuff
if __name__ == '__main__':
    m = SVGManager('italy.svg')
    for text in m.doc.getElementsByTagName('text'):
        print (text.firstChild.nodeValue)
def initsvg(self, data_rows):
        for row in data_rows:
            region_name, points, in_battle, eliminated, battle_points = row
            if (in_battle): 
                self.set_region_as_in_battle(region_name)
                self.set_points_to_region(battle_points, region_name)
            else:
                self.set_points_to_region(points, region_name)

            if (eliminated): self.set_region_as_eliminated(region_name)
'''