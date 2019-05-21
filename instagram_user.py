import urllib.error
from bs4 import BeautifulSoup
import instaloader


class InstagramUser():        
    def obtain_uer_info(self, user_id = None, user_name = None):
        """
            extract Instagram user's profile information
        """
        try:
            loader = instaloader.Instaloader()
            if user_id != None:
                return instaloader.Profile.from_id(\
                    loader.context, user_id)
            elif user_name != None:
                return instaloader.Profile.from_username(\
                    loader.context, user_name)
            
            return None

        except:
            return None
    
    @staticmethod
    def obtain_user_post_count(user_name, context):
        """
            Obtain count of user's posts
        """
        html = urllib.request.urlopen('https://www.instagram.com/' + user_name\
            , context= context).read()
        soup = BeautifulSoup(html, 'html.parser')
        data = soup.find_all('meta', attrs = {'property' : 'og:description'})
        return data[0].get('content').split()[4]

