import configparser
import spotipy
import csv
from spotipy.oauth2 import SpotifyOAuth

#-----------CONFIG TO ACCESS ACCOUNT-------------------#
config = configparser.ConfigParser()
config.read("config.ini")

CLIENT_ID = config["auth"]["Client_ID"]
CLIENT_SECRET = config["auth"]["Client_Secret"]
REDIRECT_URI = "http://127.0.0.1:8000/callback"
SCOPE = "playlist-read-private user-read-recently-played user-top-read" #-------> Used to give permission on what to access

#------------AUTH TO LOG IN------------------#
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope=SCOPE))  #Access to the API

# -----------------TEST to confirm user log in-----------------#
# Get current user info
user = sp.current_user()
print(f"Logged in as: {user["display_name"]} ({user["id"]})")


# # TEST to see if I can get top 5 song - Works
# # Just for fun
top_songs = sp.current_user_top_tracks(limit=5, time_range="short_term") # short_term = 4 weeks, medium_term = 6 months, long_term = couple of years
print("Your Top 5 Tracks Right Now:")
for i, item in enumerate(top_songs["items"], start=1):
    track_name = item["name"]
    artists = ", ".join(artist["name"] for artist in item["artists"])
    print(f"{i}. {track_name} by {artists}")


#------------------CSV------------------------------------------#
with open ("spotify_" + user["display_name"]+ ".csv", mode="w", newline="", encoding ="utf-8") as csvfile:
    csv_writer = csv.writer(csvfile)

    csv_writer.writerow(["Playlist Name", "Playlist ID", "Track Name", "Artists"]) # Writes headers 
#------------GETTING PLAYLISTS------------------#
    # Get a list of the playlists
    print("Your Playlists:")
    playlists = sp.current_user_playlists()
    for playlist in playlists["items"]:   

    # To try to handle non standard playlist names (i.e Playlist with emojis)
        try:
            name = playlist["name"]
            print(f"- {name} (ID: {playlist["id"]})")
        except UnicodeEncodeError:
            print(f"- [undefined playlist name] (ID: {playlist["id"]})") #Got it to work but it will define all unreadable playlist name as undefined

    #---------------SONGS-----------------------------------#
    # Get songs from the playlist
        results = sp.playlist_items(playlist["id"])

        # Loop through each track
        for item in results['items']:
            track = item.get('track')

            if not track:
                print("   - [Unknown or removed track]")
                continue

            # Check if 'artists' exists before accessing it
            if 'artists' not in track:
                try:
                    print(f"   - {track.get('name', '[Unknown track name]')} by [Unknown artists]")
                except UnicodeEncodeError:
                    print("   - [undefined song]")
                continue

            # Safely get song name and artists list
            song_name = track.get('name', '[Unknown track name]')
            artists = ", ".join(artist.get('name', '[Unknown artist]') for artist in track['artists'])

            try:
                print(f"   - {song_name} by {artists}")
            except UnicodeEncodeError:
                print("   - [undefined song]")


            csv_writer.writerow([name, playlist["id"], song_name, artists])