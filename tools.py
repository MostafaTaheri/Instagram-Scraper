import json
import os
from urllib import request

class Tools():
    @staticmethod
    def write_json(file_name, content):
        with open(file_name, 'a') as file:
                json.dump(content, file) 
    
    @staticmethod
    def read_json(file):
        try:
            with open(file, 'r') as json_file:
                return json.load(json_file)
        except:
            None
    
    @staticmethod
    def print_info(**kwargs):
        """ Print items of dictionary """
        for item in kwargs.items():
            if item:
                print(item)   
    
    @staticmethod
    def packer(**kwargs):
        """ Make dictionary """
        return kwargs
    
    @staticmethod
    def clean():
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def downloader(url, file_name, output):
        """
            Downlaod and save file into your path
        """
        try:
            if not os.path.exists(output):
                os.makedirs(output)
            
            request.urlretrieve(url, "{}/{}".format(output, file_name))
            return True
        except:
            return False
    
    @staticmethod
    def join_string(part_1, part_2):
        """
            Join two strings whith each other
        """
        return "{}{}".format(part_1, part_2)