import logging

import requests


# Imgur credentials
CLIENT_ID = 'eb6223e9384246d'
CLIENT_SECRET = 'fed4a7e79366b16080aa4433dd45c9cfc414daa3'


def get_data_from_imgur():
    """
    :return: {
        "data": [], list of posts,
        "success": bool,
        "status": int, code 200 | 40X
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
    logging.info(f'Response code: {response.status_code}')
    return response.json()
