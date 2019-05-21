import requests
import urllib.request
import urllib.parse
import urllib.error
from bs4 import BeautifulSoup
import ssl
import json
import configparser
import threading
from instagram_user import InstagramUser
from instagram_hashtag import InstagramHashtag
from tools import Tools
from json import JSONDecoder

class Instagram():
    def __init__(self, config_file_path):
        try:
            Tools.clean()
            self.ctx = ssl.create_default_context()
            self.ctx.check_hostname = False
            self.ctx.verify_mode = ssl.CERT_NONE
            self.info_arr = []
            self.config_file_path = config_file_path
            self.arr_meta_data_info = []

            # choose operation
            self.__choose_operation()
            user_input = int(input(">> "))

            if user_input not in (2, 3, 4):
                return
            
            # obtain config's information
            config_file = self.__load_settings(self.config_file_path)

            # obtain user's info
            if user_input == 2:
                self.__extract_user_info(\
                    config_file["users_list"], config_file["user_output"])         

            # obtain image links from hashtags
            if user_input == 3:            
                self.__extract_hashtag_data(config_file)
            
            # download files
            if user_input == 4:
                self.__downloader(config_file['hashtag_output'], config_file)
        except:
            print('Occurred some errors')
    
    def __load_settings(self, config_file_path):
        """
            Loading and assigning global variables
        """
        try:
            config_parser = configparser.RawConfigParser()
            config_parser.read(config_file_path)

            users_list = config_parser.get('My-configs', 'Users_List')
            user_output = config_parser.get('My-configs', 'User_output')
            hashtag_list = config_parser.get('My-configs', 'Hashtag_List')
            hashtag_output = config_parser.get('My-configs', 'Hashtag_output')
            url = config_parser.get('My-configs', 'Url')
            video_download = config_parser.get('My-configs', 'Video_Downloads')
            image_download = config_parser.get('My-configs', 'Image_Downloads')

            settings = {
                'users_list': users_list,
                'user_output' : user_output,
                'hashtag_list' : hashtag_list,
                'hashtag_output' : hashtag_output,
                'Url' : url,
                'video_download' : video_download,
                'image_download' : image_download
            }
            return settings
        except:
            return None

    def __choose_operation(self):
        print(""" Pleas choose your operation
            1- Exit
            2- Get user's page information
            3- Extract data base on the hashtag
            4- download files
        """)
    
    def __extract_user_info(self, url_list, output):
        """
            extract Instagram user's profile information
        """
        try:
            # obtain url from list
            with open(url_list, 'r',  encoding = "utf-8") as file:
                self.content = file.readlines()

            if self.content != '' :
                self.content = [x.strip() for x in self.content]

                for user in self.content:  
                    profile_info = InstagramUser.obtain_uer_info\
                        (None, user_name = user)
                    self.info_arr.append(Tools.packer(\
                        User_Name = profile_info.username,
                        User_Id = profile_info.userid,\
                        Bio = profile_info.biography,
                        Profile_Image = profile_info.profile_pic_url,\
                        Posts_Count = InstagramUser.obtain_user_post_count\
                            (profile_info.username, self.ctx),
                        Followers = profile_info.followers,\
                        Following = profile_info.followees,
                        Is_Private = profile_info.is_private,
                        Is_Verified = profile_info.is_verified))  

                    print("took {}'s information".format(user)) 
                    print('-' * 50)
                Tools.write_json(output, self.info_arr) 
        except:
            print('Occurred some errors')
    
    def __extract_hashtag_data(self,config_file):
        """
            extract Instagram data based on hashtag
        """
        try:
            insta_hashtag = InstagramHashtag()
            # read list of hashtag
            with open(config_file["hashtag_list"],\
                 'r', encoding = "utf-8") as file:
                self.content = file.readlines()
            
            self.content = [x.strip().replace('\ufeff', '')\
                 for x in self.content]

            for hashtag in self.content:
                print('Scraping links with #{}, please wait just for moments'\
                    .format(hashtag))
                self.arr_meta_data_info.append(\
                    insta_hashtag.extract_data(hashtag, config_file))

            Tools.write_json(config_file['hashtag_output'],\
                 self.arr_meta_data_info)

        except:
            print('Occurred some errors')
    
    def __config_downloader(self, file, config_file, is_video = False):
        """
            Download files from your infromation's list
        """
        try:
            print("Please wait just for moments ...")

            self.file = file
            self.content = Tools.read_json(self.file)
            self.config_file = config_file
            self.is_video = is_video
            insta_hashtag = InstagramHashtag()

            #  image downloader
            if not self.is_video:
                for image_item in self.__extract_image_list(self.content):
                    insta_hashtag.downloader(\
                        self.config_file['image_download'], image_item)
            else:
                # video downloader
                for video_item in self.__extract_video_list(self.content):
                    insta_hashtag.downloader(\
                        self.config_file['video_download'], video_item, True)
        except:
            print('Occurred some errors')
    
    def __extract_video_list(self, content):
        try:
            self.content = content
            self.video_nodes = []
            self.video_list = []

            for item in self.content:
                self.video_nodes.extend([input_list for input_list in \
                    [input_list for input_list in item if len(item) > 0]\
                    if input_list['Is_Video']])
            
            for video_row in self.video_nodes:
                for key, val in video_row.items():
                    if key == 'Short_Code':
                        self.video_list.append(val)
            return self.video_list           

        except:
            None
    
    def __extract_image_list(self, content):
        try:
            self.content = content
            self.image_nodes = []
            self.image_list = []

            for item in self.content:
                self.image_nodes.extend([input_list for input_list in \
                    [input_list for input_list in item if len(item) > 0]\
                    if not input_list['Is_Video']])
            
            for image_row in self.image_nodes:
                for key, val in image_row.items():
                    if key == 'Short_Code':
                        self.image_list.append(val) 
            return self.image_list             
        except:
            None
    
    def __downloader(self, file, config_file):    
         self.__config_downloader(file, config_file)
         self.__config_downloader(file, config_file, True)