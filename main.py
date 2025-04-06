from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import ApiKeyCredentials
import os
import random
import shutil

ENDPOINT = "https://tableemptypredictor.cognitiveservices.azure.com/"
PREDICTION_KEY = "ExYj2VC82WJsTbgsB5JcdfvAJArTjTXtw01JxyYfV9iUgVTAe2qdJQQJ99BDACYeBjFXJ3w3AAAIACOGOjam"
PROJECT_ID = "38320eb8-3bf2-43e2-8766-00fda8ed5144"
PUBLISHED_NAME = "Iteration1"

credentials = ApiKeyCredentials(in_headers={"Prediction-key": PREDICTION_KEY})
predictor = CustomVisionPredictionClient(ENDPOINT, credentials)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with frontend URL for better security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def detect_objects(image_path):
    with open(image_path, "rb") as image_data:
        results = predictor.detect_image(PROJECT_ID, PUBLISHED_NAME, image_data.read())
    return results.predictions

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
        return None
    return random_footage_path

    

@app.get("/api/current-occupancies")
def get_current_occupancies():
    """
    Returns the percentage of occupied tables for each building.
    """
    available_buildings = {"LIB": None, "BSN": None, "ENB": None, "MDN": None}

    for building in available_buildings.keys():
        image_path = get_random_camera_footage(building)
        if not image_path:
            continue

        predictions = detect_objects(image_path)
        occupied, total = count_occupied_tables(predictions)
        percent_of_occupied = (occupied / total) * 100 if total > 0 else None

        available_buildings[building] = percent_of_occupied

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
    Upload an image and return the prediction results.
    """
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