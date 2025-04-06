from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
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

app = FastAPI()

def detect_objects(image_data):
        results = predictor.detect_image(PROJECT_ID, PUBLISHED_NAME, image_data)
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
    print("count_occupied_tables func is running")
    people = [p for p in predictions if p.tag_name == "Person" and p.probability > 0.7]
    print(f"people: {len(people)}")
    tables = [t for t in predictions if t.tag_name == "table" and t.probability > 0.7]
    print(f"tables: {len(tables)}")

    occupied = 0
    for table in tables:
        for person in people:
            if is_overlap(table.bounding_box, person.bounding_box):
                occupied += 1
                break  # One person is enough to mark table as occupied

    total_tables = len(tables)
    return occupied, total_tables

def get_random_camera_footage(building_name):

    random_footage_path = os.path.join(f"camera_footages/{building_name}", random.choice(os.listdir(f"camera_footages/{building_name}")))
    if not os.path.exists(random_footage_path):
        print(f"Error: The file {random_footage_path} does not exist.")
        return None
    return random_footage_path

def main():
    """
    available_buildings = ["LIB", "BSN", "ENB", "MDN"]
    
    building_choice = input("Enter the building name: ")

    cur_photo = building_choice.upper()
    print(f"Current photo: {cur_photo}")

    if building_choice not in available_buildings:
        print(f"Invalid building name.")
        return

    image_path = get_random_camera_footage(building_choice)
    if not image_path:
        return
    
    cur_photo = image_path.upper()
    print(f"Current photo: {cur_photo}")
    
    """

    image_path = "camera_footages/MDN/MDN_full_ai.png"
    

    predictions = detect_objects(image_path)
    occupied, total = count_occupied_tables(predictions)
    print(f"{occupied} out of {total} tables are occupied.")

    precent_of_occupied = (occupied / total) * 100 if total > 0 else 0
    print(f"Percentage of occupied tables: {precent_of_occupied:.2f}%")

    @app.post("/api/predict-occupancy")
    async def predict_occupancy(file: UploadFile = File(...)):
        try: 
            image_data = await file.read()
            predictions = detect_objects(image_data)
            occupied, total = count_occupied_tables(predictions)
            precent_of_occupied = (occupied / total) * 100 if total > 0 else 0
            
            return JSONResponse({
                "occupied_tables": occupied,
                "total_tables": total,
                "percentage_occupied": f"{precent_of_occupied:.2f}%",
            })
        
        except Exception as e:
            return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/")
def root():
    return {"message": "Running!"}


'''
if __name__ == "__main__":
    main()
'''


