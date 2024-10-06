import spotipy
from spotipy.oauth2 import SpotifyOAuth
from collections import Counter
import numpy as np
import json
import difflib


# Function to load JSON data from a file
def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def get_color_name(rgb):
    colors = {
            "red": (255, 0, 0),
            "orange": (255, 170, 0), 
            "yellow": (255, 255, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
            "violet": (127, 0, 255),
            "Grayscale": (100, 100, 100)
        }
        min_distance = float("inf")
        closest_color = None
        for color, value in colors.items():
            distance = sum((i - j) ** 2 for i, j in zip(rgb, value))
            if distance < min_distance:
                min_distance = distance
                closest_color = color
        return closest_color

def count_true_colors(color_codes, condition):  # Extract color percentages
    color_rgb_str = color_codes
    cnt = 0
    colorNamesList = []
    for color_data in color_rgb_str:
        color_data = color_data.replace('(', '').replace(')', '')
        rgb = tuple(map(int, color_data.split(', ')))
        colorNamesList.append(get_color_name(rgb))
        cnt += 1
    if condition == 0:
        return colorNamesList
    else:
        return cnt


# Function to extract 'distance', 'type', and 'color_percentages' for a specific title
def extract_data_by_title(data, title):
    for entry in data:
        if entry['title'] == title:
            # Extract 'distance', 'type', and 'color_percentages'
            distance = int(entry['distance'])  # Assuming 'distance' is a string, converting to integer
            entry_type = entry['type']
            colors = [color['colorCode'] for color in entry['color_percentages']]
            percentages = [color['percent'] for color in entry['color_percentages']]

            return distance, entry_type, colors, percentages

    # If the title is not found in the data
    return None

# Load data from the JSON file
file_path = '/Users/alex.inn/Documents/ver2_image_data.json'
data = load_json(file_path)

# Color to Data Dictionary
color_attributes = {
    "Red": (0.9, 0.9),   # (valence, energy)
    "Green": (0.9, 0.4),
    "Yellow": (0.7, 0.8),
    "Orange": (0.8, 0.8),
    "Blue": (0.2, 0.3),
    "Violet": (0.4, 0.1),
    "Grayscale": (0.1, 0.1)
}

# Type to Data Dictionary
type_attributes = {
    "Nebulae": (0.9, 0.9),
    "Supernovae and Remnants": (0.3, 1.0),    #(valence, energy)
    "Clusters": (0.5, 0.4),
    "Galaxies": (0.3, 0.5),
    "Stellar Formations": (0.2, 0.6),
    "Fields": (0.1, 0.1)
}

# Output the result
def imageToAttributes(img_title):
    result = extract_data_by_title(data, img_title)
    distance, entry_type, color_codes, color_percentages = result
    distance = distance
    type = entry_type
    color_codes = count_true_colors(color_codes, 0)

    color_percentages = color_percentages

    total_percentage = sum(color_percentages)
    type_valence = type_attributes[type][0]
    type_energy = type_attributes[type][1]

    distance_tempo = 0

    if distance > 0:
        if distance < 10000:
            distance_tempo = 160
        elif distance < 500000:
            distance_tempo = 120
        elif distance < 2500000:
            distance_tempo = 100
        elif distance < 500000000:
            distance_tempo = 80
        else:
            distance_tempo = 60

    color_valence = 0
    color_energy = 0
    for color in color_codes:
        color_valence += color_attributes[color][0] * (color_percentages[color_codes.index(color)] / total_percentage)
        color_energy += color_attributes[color][1] * (color_percentages[color_codes.index(color)] / total_percentage)

    fin_valence = type_valence * 0.3 + color_valence * 0.7
    fin_energy = type_energy * 0.8 + color_energy * 0.2
    fin_tempo = distance_tempo
    return fin_valence, fin_energy, fin_tempo


# Spotify user authentication
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id='ca6f57d5194d41729b809ce09c5682f3',
    client_secret='dacaa11c0d20434b826d1f4dfea1c487',
    redirect_uri='http://localhost:8888/callback',
    scope='playlist-read-private user-library-read'
))

def analyze_playlist(playlist_id):
    tracks = sp.playlist_tracks(playlist_id)['items']
    artist_ids = {artist['id'] for track in tracks for artist in track['track']['artists']}
    track_ids = [track['track']['id'] for track in tracks]

    # Fetch artist genres
    genres = [genre for artist_id in artist_ids for genre in sp.artist(artist_id)['genres']]
    top_genres = Counter(genres).most_common(3)

    # Fetch track audio features
    features = sp.audio_features(track_ids)
    avg_danceability = np.mean([f['danceability'] for f in features if f])
    avg_speechiness = np.mean([f['speechiness'] for f in features if f])

    # Get artist names
    artist_names = list({artist['name'] for track in tracks for artist in track['track']['artists']})

    return {
        'top_genres': top_genres,
        'avg_danceability': avg_danceability,
        'avg_speechiness': avg_speechiness,
        'artist_names': artist_names
    }

# Manual genre mapping dictionary
manual_genre_mapping = {
    "rap": "hip-hop",
    "electronic": "dance",
    "k-rap": "hip-hop",
    "trap": "trip-hop",
    "hyperpop": "pop",
    "glitchcore": "IDM"
    # Add any additional mappings here
}

# Function to print available genres
def print_available_genres():
    available_genres = sp.recommendation_genre_seeds()['genres']
    print("Available Genres:")
    for genre in available_genres:
        print(genre)

# Call the function to print the available genres for reference
print_available_genres()

def map_to_available_genres(playlist_genres, available_genres):
    mapped_genres = []
    
    # Normalize available genres (lowercase, replace spaces with hyphens, etc.)
    available_genres_normalized = {genre.lower().replace(" ", "-"): genre for genre in available_genres}

     # First, check the manual genre mapping
    for genre in playlist_genres:
        normalized_genre = genre.lower().replace(" ", "-")  # Normalize playlist genres

        # Check if the genre is in the manual mapping
        if normalized_genre in manual_genre_mapping:
            mapped_genres.append(manual_genre_mapping[normalized_genre])
        else:
            # If not found in manual mapping, check in available genres
            if normalized_genre in available_genres_normalized:
                mapped_genres.append(available_genres_normalized[normalized_genre])
            else:
                # Use difflib to find the closest match for unmatched genres
                closest_match = difflib.get_close_matches(normalized_genre, available_genres_normalized.keys(), n=1)
                if closest_match:
                    mapped_genres.append(available_genres_normalized[closest_match[0]])

    return list(set(mapped_genres))  # Ensure uniqueness of genres

def validate_inputs(avg_danceability, avg_speechiness, fin_valence, fin_energy):
    # Ensure values are within the range of 0.0 to 1.0
    avg_danceability = max(0, min(avg_danceability, 1))
    avg_speechiness = max(0, min(avg_speechiness, 1))
    fin_valence = max(0, min(fin_valence, 1))
    fin_energy = max(0, min(fin_energy, 1))
    return avg_danceability, avg_speechiness, fin_valence, fin_energy

def recommend_songs(playlist_id, img_title):
    # Analyze playlist
    playlist_features = analyze_playlist(playlist_id)

    # Extract image attributes
    fin_valence, fin_energy, fin_tempo = imageToAttributes(img_title)

    # Generate recommendations based on avg_danceability, avg_speechiness, and image attributes
    avg_danceability = playlist_features['avg_danceability']
    avg_speechiness = playlist_features['avg_speechiness']

    # Validate input ranges
    avg_danceability, avg_speechiness, fin_valence, fin_energy = validate_inputs(
        avg_danceability, avg_speechiness, fin_valence, fin_energy)

    # Get top genres
    top_genres = [genre[0] for genre in playlist_features['top_genres'][:3]]

    # Get available genres from Spotify
    available_genres = sp.recommendation_genre_seeds()['genres']

    # Map top genres to available genres
    seed_genres = map_to_available_genres(top_genres, available_genres)
    print(f"Top genres: {top_genres}")
    print(f"Mapped seed genres: {seed_genres}")

    # Fallback: If no seed genres were mapped, use a default set of genres
    if not seed_genres:
        seed_genres = ['pop', 'hip-hop', 'electronic']  # Fallback genres
        print(f"No valid genres found in top genres. Using fallback genres: {seed_genres}")
    else:
        print(f"Mapped seed genres: {seed_genres}")

    # Fetch song recommendations from Spotify
    recommendations = sp.recommendations(seed_genres=seed_genres[:3],
                                         target_danceability=avg_danceability,
                                         target_speechiness=avg_speechiness,
                                         target_valence=fin_valence,
                                         target_energy=fin_energy,
                                         target_tempo=fin_tempo)

    # Extract track names from the recommendations
    # Extract track details, including popularity and artist name
    user_artists = set(playlist_features['artist_names'])

    # Extract track details and rank them
    ranked_tracks = []
    for track in recommendations['tracks']:
        track_name = track['name']
        artist_name = track['artists'][0]['name']
        popularity = track['popularity']
        listening_link = track['external_urls']['spotify']

        # Check if the artist is in the user's playlist
        is_user_artist = artist_name in user_artists

        # Append track details with a priority flag
        ranked_tracks.append((track_name, artist_name, popularity, listening_link, is_user_artist))

    # Sort tracks: first by user artist priority, then by popularity
    ranked_tracks.sort(key=lambda x: (not x[4], -x[2]))  # prioritize user artists first, then by popularity

    # Return the ranked tracks
    most_recommended_track = ranked_tracks[0]
    # Create a dictionary for the most recommended track
    most_recommended_json = {
        "most_recommended": {
            "title": most_recommended_track[0],
            "artist": most_recommended_track[1],
            "link": most_recommended_track[3]
        }
    }
    
    # Return the JSON
    print(json.dumps(most_recommended_json, indent=2))


# Example usage:
title_input = "Crab Nebula"
playlist_id = '1NGqMCRo4drDeNa9JpGEip'

recommend_songs(playlist_id, title_input)
