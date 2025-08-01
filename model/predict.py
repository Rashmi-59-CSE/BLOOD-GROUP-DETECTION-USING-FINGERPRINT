import pickle
from .extract_features import extract_features
import numpy as np

def predict_blood_group(image_path):
    with open('model/model.pkl', 'rb') as f:
        model = pickle.load(f)

    features = extract_features(image_path, show=True)

   

    prediction = model.predict(features)
    return prediction[0]
