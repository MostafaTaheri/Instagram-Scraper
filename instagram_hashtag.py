import requests
import urllib.request
import urllib.parse
import urllib.error
import ssl
import json
import configparser
import linecache
import re
import instaloader
from instagram_user import InstagramUser
from tools import Tools
from bs4 import BeautifulSoup


class InstagramHashtag():        
    def extract_data(self, hashtag, config_file):
        try:
            self.hashtag = hashtag
            self.base_url = config_file['Url'] + hashtag + '/?__a=1'
            self.url2 = config_file['Url'] + hashtag + '/?__a=1'
            self.flag = True
            self.arr_meta_data_info = []
            
            while self.flag:
                response = urllib.request.urlopen(self.url2)
                json_file = json.load(response)                    
                post_count = json_file['graphql']['hashtag']\
                    ['edge_hashtag_to_media']['count']

                for post in json_file['graphql']['hashtag']\
                        ['edge_hashtag_to_media']['edges']:
                    self.arr_meta_data_info.append(Tools.packer(\
                    Hashtag = hashtag,
                    Is_Video = post['node']['is_video'],
                    Thumbnail_url = post['node']['display_url'],
                    Short_Code = post['node']['shortcode'],
                    Like_Count = post['node']['edge_liked_by']['count'],
                    Video_View_Count = \
                    self.extract_video_view_count(post['node']),
                    Time_Stamp = post['node']['taken_at_timestamp'],
                    Caption = self.extract_caption(post['node']),
                    Owner_Id = post['node']['owner']['id']))

            
                # detect pages
                if json_file['graphql']['hashtag']\
                    ['edge_hashtag_to_media']['page_info']\
                    ['has_next_page'] == True:
                    end_cursor = json_file['graphql']['hashtag']\
                    ['edge_hashtag_to_media']\
                    ['page_info']['end_cursor']
                    self.url2 = self.base_url + '&max_id=' + end_cursor
                    json_file =None
                else:
                    self.flag = False

            return self.arr_meta_data_info           
        except:
            print('Occurred some errors')

    def downloader(self, directory, short_code, is_video = False):
        self.directory = directory
        self.short_code = short_code
        self.is_video = is_video
        
        if is_video:
            return self.__video_downloader(self.short_code, self.directory)
        
        return self.__image_downloader(self.short_code, self.directory)

    def __extract_user_info(self, userid):
        insta_user = InstagramUser()
        profile_info = insta_user.obtain_uer_info\
                (user_id = userid, user_name = None)
        Tools.packer(User_Name = profile_info.username,\
                    User_Id = profile_info.userid,\
                    Bio = profile_info.biography,
                    Profile_Image = profile_info.profile_pic_url,\
                    Followers = profile_info.followers,\
                    Following = profile_info.followees,
                    Is_Private = profile_info.is_private,
                    Is_Verified = profile_info.is_verified)

    def __video_downloader(self, short_code, directory):
        try:
            self.short_code = short_code
            self.directory = directory
            return Tools.downloader(self.extract_video_url(self.short_code),\
                    "{}{}".format(self.short_code, '.mp4'), self.directory)
        except:
            return None
    
    def __image_downloader(self, short_code, directory):
        try:
            self.short_code = short_code
            self.directory = directory
            return Tools.downloader(self.extract_image_url(self.short_code),\
                    "{}{}".format(self.short_code, '.jpg'), self.directory)
        except:
            return None

    @staticmethod
    def extract_caption(node):
        """ 
            Extract caption from node
            if the caption being null then return
            null value
        """
        if len(node['edge_media_to_caption']['edges']) > 0:
            return node['edge_media_to_caption']['edges'][0]['node']['text']
        else:
            return None
    
    @staticmethod
    def extract_video_view_count(node):
        if node['is_video'] == True:
            return node['video_view_count']
        else:
            return 0
    
    @staticmethod
    def extract_video_url(short_code):
        """
            Extract video url based on shortcode
        """
        try:
            url = "https://www.instagram.com/p/{}/?__a=1".format\
                (short_code)
            response = urllib.request.urlopen(url)
            json_file = json.load(response)
            return json_file['graphql']['shortcode_media']['video_url']
        except:
            return None
    
    @staticmethod
    def extract_image_url(short_code):
        """
            Extract image url based on shortcode
        """
        try:
            url = "https://www.instagram.com/p/{}/?__a=1".format\
                (short_code)
            response = urllib.request.urlopen(url)
            json_file = json.load(response)
            return json_file['graphql']['shortcode_media']['display_url']
        except:
            return None
