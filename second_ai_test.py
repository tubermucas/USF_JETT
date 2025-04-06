from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from msrest.authentication import ApiKeyCredentials

import os
import random
import json
import time
from datetime import datetime

# delete later the code later
def result_from_cam():
    result = {"LIB": random.randint(0, 100), "ENB": random.randint(0, 100), "BSN": random.randint(0, 100), "MDN": random.randint(0, 100)}
    return dict(sorted(result.items(), key=lambda item: item[1]))


def get_random_scedule():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    scheduale_folder = os.path.join(script_dir, "scheduale_data")
    random_sceduale_path = os.path.join(scheduale_folder, random.choice(os.listdir(scheduale_folder)))
    
    if not os.path.exists(random_sceduale_path):
        print(f"Error: The file {random_sceduale_path} does not exist.")
        return None

    return random_sceduale_path

def analyze_schedule(sceduale_path):

    # Map weekday numbers to corresponding letters
    weekday_map = {
        0: 'M',  # Monday
        1: 'T',  # Tuesday
        2: 'W',  # Wednesday
        3: 'R',  # Thursday
        4: 'F',  # Friday
        5: 'S',  # Saturday
        6: 'U'   # Sunday
    }

    with open(sceduale_path, "r") as file:
        sceduale = json.load(file)

    today = datetime.now()

    current_day = weekday_map[today.weekday()]
    current_time = today.time()

    current_time = datetime.strptime("14:00:00.000000", "%H:%M:%S.%f").time() # For testing purposes, set a fixed time
    current_day = "M" # For testing purposes, set a fixed day

    current_class = None
    class_time = None

    for class_data in sceduale:
        for meeting in class_data["Meetings"]:
            if current_day in meeting["Days"]:

                time_range = meeting["Times"]
                start_str = time_range.split('-')[0].strip()
        
                # Convert both times to datetime.time objects
                start_time = datetime.strptime(start_str, "%I:%M%p").time()

                if current_time > start_time and (class_time is None or class_time > start_time):
                    current_class = meeting["Bldg"]
                    class_time = start_time

                
            

    return current_class

def get_map_path():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    map_folder = os.path.join(script_dir, "map")
    map_path = os.path.join(map_folder, "USFMap-1.png")  

    if not os.path.exists(map_path):
        print(f"Error: The file {map_path} does not exist.")
        return None

    return map_path

def ignore_high_occupancy(buildings):
    new_buildings = {}
    for building in buildings.keys():
        if buildings[building] <= 70:
            new_buildings[building] = (0, 0) # Placeholder for coordinates
    
    return new_buildings

def closest_bulding(cur_class_x, cur_class_y, target_x, target_y):
    # Calculate the distance between the two points
    distance = ((cur_class_x - target_x) ** 2 + (cur_class_y - target_y) ** 2) ** 0.5
    return distance
    
def MappingModel():
    # Replace with your actual values
    endpoint = "https://canvasapp.cognitiveservices.azure.com/"
    key = "9ICQboZWpsBjyc8wsf6lHndcHpRu689qfQWrlCtDCLPMORQqATnnJQQJ99BDACYeBjFXJ3w3AAAFACOGz93o"

    # Authenticate client
    client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(key))

    


    # Image to analyze (local file or URL)
    map_path = get_map_path()     

    # Open the image file
    with open(map_path, "rb") as image_stream:
        read_response = client.read_in_stream(image_stream, raw=True)

    # Get operation location (async request)
    operation_location = read_response.headers["Operation-Location"]
    operation_id = operation_location.split("/")[-1]

    # Wait for result
    while True:
        result = client.get_read_result(operation_id)
        if result.status.lower() not in ['notstarted', 'running']:
            break
        time.sleep(1)
    return result


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

                print(f"Current class coordinates: {cur_class_x}, {cur_class_y}")
            else:
                available_buildings[line.text] = (x_center, y_center)

                print(f"Building coordinates: {line.text}: {x_center}, {y_center}")

    if not cur_class_found:
        print("Current class not found on map")
        return list(available_buildings.keys())[0]


    best_building = None
    min_distance = 0.0

    print(f"Buildings: {available_buildings.keys()}")

    print("Distaance calculation:")
    for building in available_buildings.keys():
        
        target_x, target_y = available_buildings[building]

        if target_x == cur_class_x and target_y == cur_class_y:
            best_building = building
            break

        distance = closest_bulding(cur_class_x, cur_class_y, target_x, target_y)

        print(f"Distance from {building} to current class: {distance}")

        print("-" * 20)

        if best_building is None or distance < min_distance:
            best_building = building
            min_distance = distance
        
    
    return best_building

def main():

    all_buildings = result_from_cam() # the first ai is supposed to return sorted buildings by occupancy
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
    
    print(f"Best building to go to: {best_building}")
    print(f"{best_building}: {all_buildings[best_building]}")

    print("Other buildings:")

    for building in all_buildings.keys():
        if building != best_building:
            print(f"{building}: {all_buildings[building]}")
        


if __name__ == "__main__":
    main()