import unittest as ut
import numpy as np
from PIL import Image

from HelperFunctions import *

class TestHelperFunctions(ut.TestCase):
    TEST_IMAGE = Image.open("data_handling/test_images/BlankTestImage.jpg")

    def test_show_image(self):
        show_image(np.array(self.TEST_IMAGE))
        self.assertTrue(True)

    def test_display_bounding_boxes(self):
        test_boxes = [
            np.array([894, 38, 1013, 149]),
            np.array([4, 23, 192, 103]),
            np.array([1747, 5, 1913, 96]),
            np.array([201, 18, 871, 102]),
            np.array([1016, 20, 1745, 97]),
            np.array([530, 103, 891, 149]),
            np.array([1016, 99, 1375, 149]),
            np.array([94, 956, 139, 1033]),
            np.array([1772, 965, 1831, 1040]),
            np.array([145, 979, 398, 1038]),
            np.array([1503, 982, 1766, 1036])
        ]

        display_bounding_boxes(self.TEST_IMAGE, test_boxes)
        self.assertTrue(True)

ut.main()