# Goal

I set out to build a website that would allow users to create an account, log in
to the website, connect to their Spotify accounts and then match with other users
based on the songs that they listen to. The users would then be able to send an email
to the users that they match with.

# Implementation

I first modelled my website based on the CS50 Finance website, using the same bootstrap
choices. I made some small changes such as changing the colors of the title in the
navigation bar to better fit the Spotify theme of black and green.

I decided to use the user's 50 most recently played songs to match with other users so
as to add a dynamic quality to the matching algorthm where a user could get different
matches with another specific user at different times. I felt that this was better than
using the users' Spotify playlists because all Spotify user's have some songs they listen
to b ut not all create playlists. Also not all Spotify users create playlists of all the
songs they like to listen to. This design choice allows the best matching based on user's
song choices that may not necessarily be reflected in their playlists.

The next step I had to figure out was how to connect to Spotify's API and then get data
about a specific user, which I could then use to match with other users. I read
Spotify's Web API and realized that their examples were all written in Javascript
whereas my application would be in python. I therefore knew I had to find a python
friendly way to get access to Spotify's API. Through research, I was able to find
Spotipy, which is a thin client library for the Spotify Web API that allows me to
access Spotify and get data from it.

Once I installed the Spotipy library and read it's documentation, I realized that I
would have to make some changes to my implementation of it in order to work for me.

## Spotipy Changes

1. util.py Changes

    In order to get authorization access, the original Spotipy code popped open a
    browser and required the user to log in using that browser and then copy and
    paste that url into the terminal for th authorization process to continue. This
    was unnecessary for me since I was building a web application so in spotipy/util.py
    I wrote the functions "redirect-user" & "get-token" to redirect the user to the
    Spotify login page, and then redirect them back to my website after successful log
    in where I could then access their authorization token from the url using "get_token"

2. oAuth2.py Changes

    When I first started using the website and connecting users to Spotify, I encountered
    a problem where the different users would still get logged in to the same Spotify
    account. I fixed this by changing the parameter 'show_dialog' for the function
    'get_authorize_url' to be True and this made it such that every time the website
    connected to Spotify, it would prompt the user to confirm their account and switch to
    another account if that was not the case.

# Conclusion

With the design changes I implemented, Connectify works well and meets all the set out
goals for the application which were
    1. Allow users to create an account and log in to the website
    2. Allow users to connect to their Spotify Accounts
    3. Allow users to view a personalised homepage.
    4. Allow users to match with other users based on their Spotify music.
    5. Allow users to send an email to matched users.