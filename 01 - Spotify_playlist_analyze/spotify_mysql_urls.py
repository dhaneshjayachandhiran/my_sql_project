import re
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import mysql.connector
import csv

# Set up Spotify API credentials
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id='3ebac30f04b7473ab11da8e3550710ff',  # Replace with your Client ID
    client_secret='48232116171e44f991d2b66b791a5471'  # Replace with your Client Secret
))

# MySQL Database Connection
db_config = {
    'host': 'localhost',           # Change to your MySQL host
    'user': 'root',       # Replace with your MySQL username
    'password': 'root',   # Replace with your MySQL password
    'database': 'spotify_db'       # Replace with your database name
}

# Connect to the database
connection = mysql.connector.connect(**db_config)
cursor = connection.cursor()

# Spotify Playlist URL
playlist_url = "hhttps://open.spotify.com/playlist/1av9d5kKNZ1mXSL0aysxZu?si=cisMXIf7RMuO8DR4RmuJUw"  # Replace this with your playlist URL
playlist_id = playlist_url.split("/")[-1].split("?")[0]

# Fetch all tracks from the playlist
track_urls = []
results = sp.playlist_tracks(playlist_id)
tracks = results['items']

while results['next']:
    results = sp.next(results)
    tracks.extend(results['items'])

for item in tracks:
    track = item['track']
    if track:
        track_urls.append(track['external_urls']['spotify'])


# Process each URL
for track_url in track_urls:
    track_url = track_url.strip()  # Remove any leading/trailing whitespace
    try:
        # Extract track ID from URL
        track_id = re.search(r'track/([a-zA-Z0-9]+)', track_url).group(1)

        # Fetch track details from Spotify API
        track = sp.track(track_id)

        # Extract metadata
        track_data = {
            'Track Name': track['name'],
            'Artist': track['artists'][0]['name'],
            'Album': track['album']['name'],
            'Popularity': track['popularity'],
            'Duration (minutes)': track['duration_ms'] / 60000
        }

        # Insert data into MySQL
        insert_query = """
        INSERT INTO spotify_tracks (track_name, artist, album, popularity, duration_minutes)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            track_data['Track Name'],
            track_data['Artist'],
            track_data['Album'],
            track_data['Popularity'],
            track_data['Duration (minutes)']
        ))
        connection.commit()

        print(f"Inserted: {track_data['Track Name']} by {track_data['Artist']}")

    except Exception as e:
        print(f"Error processing URL: {track_url}, Error: {e}")

# Save to CSV file
csv_file = "spotify_tracks.csv"
fieldnames = ['Track Name', 'Artist', 'Album', 'Popularity', 'Duration (minutes)']

# Collect all track data into a list
all_tracks = []

# Go back and modify the insert loop to collect track_data
for track_url in track_urls:
    track_url = track_url.strip()
    try:
        track_id = re.search(r'track/([a-zA-Z0-9]+)', track_url).group(1)
        track = sp.track(track_id)

        track_data = {
            'Track Name': track['name'],
            'Artist': track['artists'][0]['name'],
            'Album': track['album']['name'],
            'Popularity': track['popularity'],
            'Duration (minutes)': track['duration_ms'] / 60000
        }

        # Save to MySQL
        insert_query = """
        INSERT INTO spotify_tracks (track_name, artist, album, popularity, duration_minutes)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            track_data['Track Name'],
            track_data['Artist'],
            track_data['Album'],
            track_data['Popularity'],
            track_data['Duration (minutes)']
        ))
        connection.commit()

        # Append to CSV list
        all_tracks.append(track_data)

        print(f"Inserted: {track_data['Track Name']} by {track_data['Artist']}")

    except Exception as e:
        print(f"Error processing URL: {track_url}, Error: {e}")

# After the loop, write to CSV
with open(csv_file, 'w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_tracks)

print(f"CSV file '{csv_file}' created with {len(all_tracks)} tracks.")
# Close the connection
cursor.close()

connection.close()

print("All tracks have been processed and inserted into the database.")
