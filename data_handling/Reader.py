import numpy as np
from streamlink import Streamlink
import cv2

class Reader:
    def read(self):
        """Given a string, convert/parse the data for the parser to read the data

        Args:
            path (string): the path to the data (i.e. stream url or static image)

        Returns:
            frame (np.ndarray): the file
        """
        pass

    def clean(self):
        """Clears any buffer or any streams"""
        pass

class StreamReader(Reader):
    def __init__(self, url):
        self.url = url
        self.stream = Streamlink()
    
    def read(self):
        pass

    
    
class ImageReader(Reader):
    pass
    
class DesktopReader(Reader):
    pass

class VideoReader(Reader):
    pass
    
