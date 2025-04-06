from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from msrest.authentication import ApiKeyCredentials

import os
import random
import shutil
import json
import time
from datetime import datetime


# Initialize the Custom Vision client for detecting people and tables (CAM_AI)
ENDPOINT_1 = "https://tableemptypredictor.cognitiveservices.azure.com/"
PREDICTION_KEY_1 = "ExYj2VC82WJsTbgsB5JcdfvAJArTjTXtw01JxyYfV9iUgVTAe2qdJQQJ99BDACYeBjFXJ3w3AAAIACOGOjam"
PROJECT_ID = "38320eb8-3bf2-43e2-8766-00fda8ed5144"
PUBLISHED_NAME = "Iteration1"

credentials = ApiKeyCredentials(in_headers={"Prediction-key": PREDICTION_KEY_1})
predictor = CustomVisionPredictionClient(ENDPOINT_1, credentials)


# Initialize the Computer Vision client for OCR on the USF map (MAP_AI)
ENDPOINT_2 = "https://canvasapp.cognitiveservices.azure.com/"
PREDICTION_KEY_2 = "9ICQboZWpsBjyc8wsf6lHndcHpRu689qfQWrlCtDCLPMORQqATnnJQQJ99BDACYeBjFXJ3w3AAAFACOGz93o"

client = ComputerVisionClient(ENDPOINT_2, CognitiveServicesCredentials(PREDICTION_KEY_2))

# Initialize FastAPI app
app = FastAPI()

# Enable CORS for all origins 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CAM_AI: Table Occupancy Detection Functions

# Detect objects (e.g., person, table) in the image using Custom Vision
def detect_objects(image_path):
    with open(image_path, "rb") as image_data:
        results = predictor.detect_image(PROJECT_ID, PUBLISHED_NAME, image_data.read())
    return results.predictions

# Check whether two bounding boxes overlap (used to detect if a person is at a table)
def is_overlap(box1, box2):
    l1_x = box1.left
    l1_y = box1.top
    r1_x = box1.left + box1.width
    r1_y = box1.top + box1.height

    l2_x = box2.left
    l2_y = box2.top
    r2_x = box2.left + box2.width
    r2_y = box2.top + box2.height

    if l1_x > r2_x or l2_x > r1_x:
        return False
    if l1_y > r2_y or l2_y > r1_y:
        return False
    return True

# Returns the total number of occupied tables and total tables in the image
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

# Imitate the camera footage for each building
def get_random_camera_footage(building_name):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    building_folder = os.path.join(script_dir, "camera_footages", building_name)
    random_footage_path = os.path.join(building_folder, random.choice(os.listdir(building_folder)))

    if not os.path.exists(random_footage_path):
        return None
    return random_footage_path

    

# Get occupancy percentage for each building using CAP_AI
@app.get("/api/current-occupancies")
def get_current_occupancies():
    
    available_buildings = {"LIB": None, "BSN": None, "ENB": None, "MDN": None}

    for building in available_buildings.keys():
        image_path = get_random_camera_footage(building)
        if not image_path:
            continue

        predictions = detect_objects(image_path)
        occupied, total = count_occupied_tables(predictions)
        percent_of_occupied = (occupied / total) * 100 if total > 0 else None

        available_buildings[building] = percent_of_occupied
    
    sorted_buildings = dict(sorted(available_buildings.items(), key=lambda item: item[1]))

    
    # Delete it later
    """
    # Format the response
    response = [
        {"building": building, "percent_occupied": percent}
        for building, percent in available_buildings.items()
        if percent is not None
    ]

    return JSONResponse(response)

@app.post("/api/upload-image")
async def upload_image(image: UploadFile = File(...)):
    """
# Upload an image and return the prediction results.
    try:
        upload_dir = "uploaded_images"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, image.filename)

        with open(file_path, "wb") as f:
            shutil.copyfileobj(image.file, f)

        predictions = detect_objects(file_path)
        occupied, total = count_occupied_tables(predictions)
        percent_occupied = (occupied / total) * 100 if total > 0 else None
        os.remove(file_path)  

        return {"percent_occupied": percent_occupied}
    except Exception as e:
        return JSONResponse(
            {"error": str(e)}, status_code=500
        )
    
    return sorted_buildings
    

# MAP_AI: Map Analysis Functions

# Randomly select a student schedule file
def get_random_scedule():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    scheduale_folder = os.path.join(script_dir, "scheduale_data")
    random_sceduale_path = os.path.join(scheduale_folder, random.choice(os.listdir(scheduale_folder)))
    
    if not os.path.exists(random_sceduale_path):
        print(f"Error: The file {random_sceduale_path} does not exist.")
        return None

    return random_sceduale_path

# Analyze current user location based on schedule data and current day/time
def analyze_schedule(sceduale_path):

    # Map weekday numbers to corresponding letters
    weekday_map = {
        0: 'M', 1: 'T', 2: 'W', 3: 'R', 4: 'F', 5: 'S', 6: 'U'   
    }

    with open(sceduale_path, "r") as file:
        sceduale = json.load(file)

    today = datetime.now()

    current_day = weekday_map[today.weekday()]
    current_time = today.time()

    current_class = None
    class_time = None

    for class_data in sceduale:
        for meeting in class_data["Meetings"]:
            if current_day in meeting["Days"]:

                time_range = meeting["Times"]
                start_str = time_range.split('-')[0].strip()
                start_time = datetime.strptime(start_str, "%I:%M%p").time()

                if current_time > start_time and (class_time is None or class_time > start_time):
                    current_class = meeting["Bldg"]
                    class_time = start_time

    return current_class

# Get the static map path
def get_map_path():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    map_folder = os.path.join(script_dir, "map")
    map_path = os.path.join(map_folder, "USFMap-1.png")  

    if not os.path.exists(map_path):
        print(f"Error: The file {map_path} does not exist.") # how print the error in the frontend? Or just delete it later
        return None

    return map_path

# Filter buildings with high occupancy (>70%)
def ignore_high_occupancy(buildings):
    new_buildings = {}
    for building in buildings.keys():
        if buildings[building] <= 70:
            new_buildings[building] = (0, 0) # Placeholder for coordinates
    
    return new_buildings

# Calculate the distance between two points (used to find the closest building)
def closest_bulding(cur_class_x, cur_class_y, target_x, target_y):
    distance = ((cur_class_x - target_x) ** 2 + (cur_class_y - target_y) ** 2) ** 0.5
    return distance
    
# Perform OCR on the map image to find building coordinates
def MappingModel():
    map_path = get_map_path()     

    with open(map_path, "rb") as image_stream:
        read_response = client.read_in_stream(image_stream, raw=True)

    operation_location = read_response.headers["Operation-Location"]
    operation_id = operation_location.split("/")[-1]

    while True:
        result = client.get_read_result(operation_id)
        if result.status.lower() not in ['notstarted', 'running']:
            break
        time.sleep(1)
    return result

# Suggest best nearby building with low occupancy based on current class location
def best_suggestion(available_buildings, cur_class):

    cur_class_found = False

    cur_class_x = 0
    cur_class_y = 0

    result = MappingModel()
    page =  result.analyze_result.read_results[0]

    for line in page.lines:
        if (line.text in available_buildings.keys() or line.text == cur_class):

            x1 = line.bounding_box[0]
            y1 = line.bounding_box[1]
            x2 = line.bounding_box[4]
            y2 = line.bounding_box[5]

            x_center = (x1+x2)/2
            y_center =  (y1+y2)/2

            if line.text == cur_class:
                cur_class_found = True

                cur_class_x = x_center
                cur_class_y = y_center

                # delete it later
                print(f"Current class coordinates: {cur_class_x}, {cur_class_y}")
            else:
                available_buildings[line.text] = (x_center, y_center)

                # delete it later
                print(f"Building coordinates: {line.text}: {x_center}, {y_center}")

    if not cur_class_found:
        print("Current class not found on map") # Print smth similiar in the frontend
        return list(available_buildings.keys())[0]


    best_building = None
    min_distance = 0.0

    # Delete it later
    print(f"Buildings: {available_buildings.keys()}")

    print("Distaance calculation:")
    for building in available_buildings.keys():
        
        target_x, target_y = available_buildings[building]

        if target_x == cur_class_x and target_y == cur_class_y:
            best_building = building
            break

        distance = closest_bulding(cur_class_x, cur_class_y, target_x, target_y)

        # delete it later
        print(f"Distance from {building} to current class: {distance}")

        print("-" * 20)

        if best_building is None or distance < min_distance:
            best_building = building
            min_distance = distance
        
    
    return best_building

def upload_user_sceduale(file_path):
    from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import json


#The code is only able to process new schedule images if the new schedule only has one assign meeting time. Mainly works best
# With the schedule already provided

def extract_schedule_section(text: str) -> str:
    start_marker = "Meeting Times"
    end_marker = "Total Hours"

    start_idx = text.find(start_marker)
    end_idx = text.find(end_marker)

    if start_idx == -1 or end_idx == -1:
        return "Markers not found in the text."

    # Extract the substring between the markers
    return text[start_idx:end_idx].strip()


# Main function, will be called other way when using FastAPI
def main():

    # DELETE PRINTS


    all_buildings = get_current_occupancies() # the first ai is supposed to return sorted buildings by occupancy
    available_buildings = ignore_high_occupancy(all_buildings)

    random_sceduale_path = get_random_scedule()
    print(f"Random schedule path: {random_sceduale_path}")

    cur_class = analyze_schedule(random_sceduale_path)
    

    print(f"Current class: {cur_class}")

    if cur_class is None:
        first_building = list(all_buildings.keys())[0]

        print("Best building to go to:")
        print(f"{first_building}: {all_buildings[first_building]}")

        print("Other buildings:")

        for building in list(all_buildings.keys())[1:]:
            print(f"{building}: {all_buildings[building]}")
        
        return
    
    if cur_class in available_buildings.keys():
        best_building = cur_class
    else:
        best_building = best_suggestion(available_buildings, cur_class)
    
    print("Best building to go to:")
    print(f"{best_building}: {all_buildings[best_building]}")

    print("Other buildings:")

    for building in all_buildings.keys():
        if building != best_building:
            print(f"{building}: {all_buildings[building]}")
        


if __name__ == "__main__":
    main()
