import os

MODEL_PATH = "path/to/your_model.pth"

if os.path.exists(MODEL_PATH):
    print("Model file exists:", MODEL_PATH)
else:
    print("Model file not found:", MODEL_PATH)
