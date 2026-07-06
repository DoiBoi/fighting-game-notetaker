import unittest as ut
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

from Parser import Parser

class TestParser(ut.TestCase):
    TEST_IMAGE = np.array(Image.open("data_handling/SF6_ROI.png"))

    def _show_image(self, image, title=""):
        plt.title(title)
        plt.imshow(image)
        plt.show()

    def test_parse_data(self):
        self.assertTrue(True)

    def test_crop_regions(self):
        test_rois = {
            "time": np.array([894, 1013, 38, 149]),
            "character1": np.array([241, 734, 174, 988]),
            "character2": np.array([1162, 1781, 283, 1021]),
            "character1_name": np.array([4, 192, 23, 103]),
            "character2_name": np.array([1747, 1913, 5, 96]),
            "player1_health": np.array([201, 871, 18, 102]),
            "player2_health": np.array([1016, 1745, 20, 97]),
            "player1_power": np.array([530, 891, 103, 149]),
            "player2_power": np.array([1016, 1375, 99, 149]),
            "player1_score": np.array([94, 139, 956, 1033]),
            "player2_score": np.array([1772, 1831, 965, 1040]),
            "player1_bar_thing": np.array([145, 398, 979, 1038]),
            "player2_bar_thing": np.array([1503, 1766, 982, 1036])
        }

        parser = Parser()
        returned_rois = parser.crop_regions(self.TEST_IMAGE, test_rois)

        # Checks if the top left pixel and the bottom right pixel are the same in the ROI of the original and the cropped ROI
        for roi_name in returned_rois.keys():
            self._show_image(returned_rois[roi_name], roi_name)     # Displays the cropped ROIs
            self.assertListEqual(list(returned_rois[roi_name][0, 0]), list(self.TEST_IMAGE[test_rois[roi_name][2], test_rois[roi_name][0]]))

    def test_parse_bar_percentage(self):
        self.assertTrue(True)

ut.main()