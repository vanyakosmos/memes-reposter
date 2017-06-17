import logging

import requests

from settings import CLIENT_ID

logger = logging.getLogger('🐕 ' + __name__)


def log_status(message, code):
    if code == 200:
        logger.info(f"Successfully received {message} data from Imgur.")
    else:
        logger.warning(f"Failed to receive {message} data from Imgur.")


def get_gallery() -> dict:
    """
    Return:
        dict: This dictionary contains information about response succession 
        and list dictionaries that describe posts.
        
        Example::
         
            {
                "data": [],
                "success": True,
                "status": 200
            }
    """
    section = 'hot'  # hot | top | user
    sort = 'viral'  # viral | top | time | rising (only available with user section)
    show_viral = 'true'
    show_mature = 'true'
    album_previews = 'false'

    url = f'https://api.imgur.com/3/gallery/{section}/{sort}'
    querystring = {"showViral": f"{show_viral}", "mature": f"{show_mature}", "album_previews": f"{album_previews}"}
    headers = {'authorization': f'Client-ID {CLIENT_ID}'}
    response = requests.request("GET", url, headers=headers, params=querystring)

    log_status('gallery', response.status_code)
    return response.json()


def get_album(post_id: str) -> dict:
    """
    Args:
        post_id (str): 
        
    Returns: 
        dict: This dictionary contains information about response succession 
        and list dictionaries that describe images.
        
        Example::
        
            {
                "data": []
                "success": True,
                "status": 200
            }
    """

    url = f'https://api.imgur.com/3/album/{post_id}/images'
    headers = {'authorization': f'Client-ID {CLIENT_ID}'}
    response = requests.request("GET", url, headers=headers)

    log_status(f"album(id='{post_id}')", response.status_code)
    return response.json()
