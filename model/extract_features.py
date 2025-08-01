import cv2
import numpy as np

def is_fingerprint_like(img):
    edges = cv2.Canny(img, 50, 150)
    edge_density = np.sum(edges > 0) / edges.size
    return edge_density > 0.01  # adjust this threshold based on testing

def is_fingerprint_like(img):
    edges = cv2.Canny(img, 50, 150)
    edge_ratio = np.sum(edges > 0) / edges.size
    return edge_ratio > 0.02  # adjust threshold as needed

def extract_features(image_path, show=True):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if not is_fingerprint_like(img):
        return None  # will cause the predictor to reject it
    ...

def extract_features(image_path, show=True):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if not is_fingerprint_like(img):
        return None  # will cause the predictor to reject it

    # Resize for consistency
    img = cv2.resize(img, (256, 256))

    # Apply Gaussian blur
    blur = cv2.GaussianBlur(img, (5, 5), 0)

    # Canny Edge Detection
    edges = cv2.Canny(blur, 50, 150)

    # Thresholding to binary
    _, thresh = cv2.threshold(blur, 127, 255, cv2.THRESH_BINARY)

    # Skeletonization (thinning)
    skel = np.zeros(thresh.shape, np.uint8)
    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    temp = np.copy(thresh)
    while True:
        open_img = cv2.morphologyEx(temp, cv2.MORPH_OPEN, element)
        temp2 = cv2.subtract(temp, open_img)
        eroded = cv2.erode(temp, element)
        skel = cv2.bitwise_or(skel, temp2)
        temp = eroded.copy()
        if cv2.countNonZero(temp) == 0:
            break

    if show:
        cv2.imshow("Original", img)
        cv2.imshow("Edges", edges)
        cv2.imshow("Skeleton", skel)
        cv2.waitKey(15000)  # Show for 15 seconds
        cv2.destroyAllWindows()

   
    feature_vector = np.hstack([
        np.mean(img),
        np.std(img),
        np.mean(edges),
        np.std(edges),
        np.mean(skel),
        np.std(skel)
    ])

    return feature_vector.reshape(1, -1)


