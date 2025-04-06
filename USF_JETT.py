from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import ApiKeyCredentials

import os
import random

ENDPOINT = "https://tableemptypredictor.cognitiveservices.azure.com/"
PREDICTION_KEY = "ExYj2VC82WJsTbgsB5JcdfvAJArTjTXtw01JxyYfV9iUgVTAe2qdJQQJ99BDACYeBjFXJ3w3AAAIACOGOjam"
PROJECT_ID = "38320eb8-3bf2-43e2-8766-00fda8ed5144"
PUBLISHED_NAME = "Iteration1"

credentials = ApiKeyCredentials(in_headers={"Prediction-key": PREDICTION_KEY})
predictor = CustomVisionPredictionClient(ENDPOINT, credentials)

# delete the code later


def detect_objects(image_path):
    with open(image_path, "rb") as image_data:
        results = predictor.detect_image(PROJECT_ID, PUBLISHED_NAME, image_data.read())

    return results.predictions

def is_overlap(box1, box2):
    # Convert normalized coordinates (0 to 1) to absolute positions if needed
    l1_x = box1.left
    l1_y = box1.top
    r1_x = box1.left + box1.width
    r1_y = box1.top + box1.height

    l2_x = box2.left
    l2_y = box2.top
    r2_x = box2.left + box2.width
    r2_y = box2.top + box2.height

    # Check for no overlap cases
    if l1_x > r2_x or l2_x > r1_x:
        return False
    if l1_y > r2_y or l2_y > r1_y:
        return False
    return True

def count_occupied_tables(predictions):

    people = [p for p in predictions if p.tag_name == "Person" and p.probability > 0.7]
    tables = [t for t in predictions if t.tag_name == "table" and t.probability > 0.7]

    occupied = 0
    for table in tables:
        for person in people:
            if is_overlap(table.bounding_box, person.bounding_box):
                occupied += 1
                break  

    total_tables = len(tables)
    return occupied, total_tables

def get_random_camera_footage(building_name):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    building_folder = os.path.join(script_dir, "camera_footages", building_name)
    random_footage_path = os.path.join(building_folder, random.choice(os.listdir(building_folder)))

    if not os.path.exists(random_footage_path):
        print(f"Error: The file {random_footage_path} does not exist.")
        return None
    return random_footage_path

def main():
    available_buildings = {"LIB": None, "BSN": None, "ENB": None, "MDN": None}

    for building in available_buildings.keys():

        image_path = get_random_camera_footage(building)
        if not image_path:
            return
        
        predictions = detect_objects(image_path)
        occupied, total = count_occupied_tables(predictions)

        precent_of_occupied = (occupied / total) * 100 if total > 0 else None

        available_buildings[building] = precent_of_occupied
    
    print("Occupied tables in each building:")
    for building, percent in available_buildings.items():
        if percent is not None:
            print(f"{building}: {percent:.2f}% occupied")
        else:
            print(f"{building}: No footage available")

if __name__ == "__main__":
    main()



