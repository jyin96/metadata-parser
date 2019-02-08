import cv2

def get_first_frame(url):
    vidcap = cv2.VideoCapture(url)
    success, image = vidcap.read()
    if (success):
        return image
