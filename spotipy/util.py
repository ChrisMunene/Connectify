
# shows a user's playlists (need to be authenticated via oauth)

from __future__ import print_function
import os
from . import oauth2
import spotipy


scope = 'user-library-read user-read-recently-played'
client_id='a87374f58bfd4fd0b620603295750581'
client_secret='b1f668733dc74665bffdd4073a74c6d7'
redirect_uri='http://ide50-eomondi.cs50.io:8080/spotifylogin'


def redirect_user():
    ''' prompts the user to login if necessary and returns
        the url that will direct the user to the Spotify authorization page

        Parameters:
         - scope - the desired scope of the request
         - client_id - the client id of your app
         - client_secret - the client secret of your app
         - redirect_uri - the redirect URI of your app
    '''
    sp_oauth = oauth2.SpotifyOAuth(client_id, client_secret, redirect_uri,
        scope=scope)

    # send the user to a web page where they can authorize this app
    return sp_oauth.get_authorize_url()


# change function name
def get_token(response=None):
    # create token
    sp_oauth = oauth2.SpotifyOAuth(client_id, client_secret, redirect_uri,
        scope=scope)
    code = sp_oauth.parse_response_code(response)
    token_info = sp_oauth.get_access_token(code)
    code =  None
    # Auth'ed API request
    if token_info:
        return token_info['access_token']
    else:
        return None
