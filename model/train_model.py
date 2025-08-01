import os
import sys
import pickle
import numpy as np
from sklearn.neighbors import KNeighborsClassifier


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.extract_features import extract_features  

# Training dataset mapping
training_data = {
    'A+':   ['training_images/a1.png','training_images/a2.png','training_images/a3.png','training_images/a4.png','training_images/a5.png','training_images/a6.png'],
    'A−':   ['training_images/an1.png','training_images/an2.png','training_images/an3.png','training_images/an4.png','training_images/an5.png','training_images/an6.png'],
    'B+':   ['training_images/b1.png','training_images/b2.png','training_images/b3.png','training_images/b4.png','training_images/b5.png','training_images/b6.png',],
    'B−':   ['training_images/bn1.png','training_images/bn2.png','training_images/bn3.png','training_images/bn4.png','training_images/bn5.png','training_images/bn6.png'],
    'AB+':  ['training_images/ab1.png','training_images/ab2.png','training_images/ab3.png','training_images/ab4.png','training_images/ab5.png','training_images/ab6.png'],
    'AB−':  ['training_images/abn1.png','training_images/abn2.png','training_images/abn3.png','training_images/abn4.png','training_images/abn5.png','training_images/abn6.png'],
    'O+':   ['training_images/o1.png','training_images/o2.png','training_images/o3.png','training_images/o4.png','training_images/o5.png','training_images/o6.png'],
    'O−':   ['training_images/on1.png','training_images/on2.png','training_images/on3.png','training_images/on4.png','training_images/on5.png','training_images/on6.png']
}

X = []
y = []

for label, files in training_data.items():
    for file in files:
        if os.path.exists(file):
            features = extract_features(file, show=False)
            X.append(features[0])
            y.append(label)
        else:
            print(f"⚠️ Missing file: {file}")

X = np.array(X)

if len(X) == 0:
    print("❌ No training data found. Make sure training_images folder has fingerprint images.")
    sys.exit()

# Train KNN
model = KNeighborsClassifier(n_neighbors=1)
model.fit(X, y)

# Save model
with open('model/model.pkl', 'wb') as f:
    pickle.dump(model, f)

print("✅ Model trained and saved at model/model.pkl")
