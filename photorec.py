'''
distance = item['facts'].get('Distance', '')
caption = item.get('caption', '')
image_link = item.get('image_url', '')
obj_type = item['facts'].get('Object Description', '')
color_info = item['facts'].get('Color Info', '')
'''

import json
import random
from flask import Flask, render_template, request, jsonify, make_response
from flask_cors import CORS
from flask import send_from_directory
import os

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def index():
    return render_template('index.html')  # Input HTML file for user preferences

@app.route('/survey.html')
def survey():
    return render_template('survey.html')

@app.route('/results.html')
def survey():
    return render_template('results.html')

@app.route('/get_image', methods=['POST','GET'])
def get_image():
    # Get user inputs from the request
    user_inputs = request.json
    # Call the existing photorec function
    selected_image = photorec(user_inputs)  # Modify photorec to accept parameters

    # Create response with JSON data
    response = make_response(jsonify(selected_image))
    
    # Add CORS headers
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    
    return response
    # return jsonify(selected_image)


def photorec(user_inputs):
    # Unpack the user inputs
    color_input = {
        "red": user_inputs.get('red', False),
        "orange": user_inputs.get('orange', False),
        "yellow": user_inputs.get('yellow', False),
        "green": user_inputs.get('green', False),
        "blue": user_inputs.get('blue', False),
        "violet": user_inputs.get('violet', False),
    }
    
    # Optional preferences (expand logic if necessary)
    vastness = user_inputs.get('vastness', None)
    distance = user_inputs.get('distance', None)
    vibrance = user_inputs.get('vibrance', None)
    user_name = user_inputs.get('name', 'Guest')  # Get user name
    
    # Load image data from JSON file
    input_file_path = 'static/data/ver2_image_data.json'
    with open(input_file_path, 'r') as file:
        data = json.load(file)

    # Function to determine the color category based on RGB value
    def get_color_name(rgb):
        colors = {
            "red": (255, 0, 0),
            "orange": (255, 170, 0), 
            "yellow": (255, 255, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
            "violet": (127, 0, 255)
        }
        min_distance = float("inf")
        closest_color = None
        for color, value in colors.items():
            distance = sum((i - j) ** 2 for i, j in zip(rgb, value))
            if distance < min_distance:
                min_distance = distance
                closest_color = color
        return closest_color
        
    # Function to count true colors in each image
    def count_true_colors(image_data):
        color_percentages = image_data.get('color_percentages', [])
        
        sum_colors = 0
        cnt = 0
        for color_data in color_percentages:
            color_rgb_str = color_data['colorCode'].strip('()')
            rgb = tuple(map(int, color_rgb_str.split(', ')))
            color_name = get_color_name(rgb)
            cnt += 1
            
            if color_name and color_input.get(color_name, False):
                sum_colors += 1
        
        return sum_colors, cnt

    # Create a separate list to store images with color information
    processed_images = []
    
    for item in data:
        colors = count_true_colors(item)
        
        processed_images.append({
            'title': item['title'],
            'color_score': colors[0],
            'distance': item['distance'],
            'type': item['type'],
            'link': item['image_link'],
            'color_count': colors[1]
        })
        
    # Sort the images by the color score in descending order
    sorted_images = sorted(processed_images, key=lambda x: x['color_score'], reverse=True)
    
    # Remove images with a color score of 0
    sorted_images = [image for image in sorted_images if image['color_score'] > 0]

    # Look thorugh vastness
    vasttypes = ['Clusters', 'Fields', 'Stellar Formations']
    
    if vastness:
        vast_sorted_images = [image for image in sorted_images if image['type'] in vasttypes]
    else:
        vast_sorted_images = [image for image in sorted_images if image['type'] not in vasttypes]

    half_index = len(vast_sorted_images) // 2
    vast_sorted_images = vast_sorted_images[half_index:]
    
    # Look through distance
    if distance:
        distance_sorted_images = sorted(vast_sorted_images, key=lambda x: x['distance'], reverse=True)
    else:
        distance_sorted_images = sorted(vast_sorted_images, key=lambda x: x['distance'])

    half_index = len(distance_sorted_images) // 2
    distance_sorted_images = distance_sorted_images[half_index:]
    
    # Look through vibrance
    if vibrance:
        vibrance_sorted_images = sorted(distance_sorted_images, key=lambda x: x['color_count'], reverse=True)
    else:
        vibrance_sorted_images = sorted(distance_sorted_images, key=lambda x: x['color_count'])

    half_index = len(vibrance_sorted_images) // 2
    vibrance_sorted_images = vibrance_sorted_images[half_index:]

    return random.choice(vibrance_sorted_images)

    # Randomly select an image from the filtered list
    selected_image = random.choice(vibrance_sorted_images)
    return {
        "image": selected_image
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))



'''
Input colors, Vastness, Distance, Vibrance

If many colors, get colorful?

If vast -> clusters, fields, stellar formations, 
if not vast -> galaxies, supernovae, nebulae, planets

If distance -> Longer distance
if not distant -> shorter distance

If vibrant -> choose photos with multiple colors
if not vibrant -> choose photos with one or two colors

Look through list of images from json and pick an image that respectively passes through each standard:
    Look through for color
    Look through for vast
    Look through for vibrance
    Look through for distance
''' 
