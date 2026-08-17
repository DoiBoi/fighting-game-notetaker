import unittest as ut

import numpy as np
from HelperFunctions import *
from Parser import Parser
from PIL import Image


class TestParser(ut.TestCase):
    TEST_IMAGE_1 = Image.open("data_handling/test_images/BoundedTestImage.png")
    TEST_IMAGE_2 = Image.open("data_handling/test_images/BlankTestImage.jpg")
    TEST_IMAGE_3 = Image.open("data_handling/test_images/BlankTestImage2.jpg")
    TEST_IMAGE_4 = Image.open("data_handling/test_images/BlankTestImage3.jpg")
    TEST_IMAGE_5 = Image.open("data_handling/test_images/BlankTestImage4.jpg")
    TEST_IMAGE_6 = Image.open("data_handling/test_images/superImage.jpg")
    TEST_TEMPLATE = Image.open("data_handling/test_images/TestTemplate.jpg")
    TEST_TEMPLATE2 = Image.open("data_handling/test_images/TestTemplate2.jpg")


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
        returned_rois = parser.crop_regions(np.array(self.TEST_IMAGE_1), test_rois)

        # Checks if the top left pixel and the bottom right pixel are the same in the ROI of the original and the cropped ROI
        for roi_name in returned_rois.keys():
            # show_image(returned_rois[roi_name], roi_name)     # Displays the cropped ROIs
            self.assertListEqual(list(returned_rois[roi_name][0, 0]), list(np.array(self.TEST_IMAGE_1)[test_rois[roi_name][2], test_rois[roi_name][0]]))

    def test_parse_character(self):
        parser = Parser()
        characters = parser.parse_characters(np.array(self.TEST_IMAGE_2.convert("L")))
        self.assertEqual(characters[0], "Jamie")
        self.assertEqual(characters[1], "Ingrid")

        characters = parser.parse_characters(np.array(self.TEST_IMAGE_6.convert("L")))
        self.assertEqual(characters[0], "JP")
        self.assertEqual(characters[1], "Ed")

        characters = parser.parse_characters(np.array(self.TEST_IMAGE_4.convert("L")))
        self.assertEqual(characters[0], "JP")
        self.assertEqual(characters[1], "Ed")

        characters = parser.parse_characters(np.array(self.TEST_IMAGE_5.convert("L")))
        self.assertEqual(characters[0], "Alex")
        self.assertEqual(characters[1], "Ingrid")



    def test_parse_super_level(self):
        parser = Parser()

        super_level = parser.parse_super_level(np.array(self.TEST_IMAGE_2.convert("L")))
        self.assertEqual(super_level, 0)

        super_level = parser.parse_super_level(np.array(self.TEST_IMAGE_3.convert("L")))
        self.assertNotEqual(super_level, 1)

        super_level = parser.parse_super_level(np.array(self.TEST_IMAGE_6.convert("L")))
        self.assertEqual(super_level, 0)

    def test_find_all_templates(self):
        threshold = 0.99
        parser = Parser()

        matches = parser._find_all_templates(self.TEST_IMAGE_2.convert("L"), self.TEST_TEMPLATE.convert("L"), threshold)
        # display_bounding_boxes(self.TEST_IMAGE_2, matches)

        matches = parser._find_all_templates(self.TEST_IMAGE_4.convert("L"), self.TEST_TEMPLATE.convert("L"), 0.75)
        # display_bounding_boxes(self.TEST_IMAGE_4, matches)

        matches = parser._find_all_templates(self.TEST_IMAGE_3.convert("L"), self.TEST_TEMPLATE.convert("L"), threshold)
        # display_bounding_boxes(self.TEST_IMAGE_3, matches)

        self.assertTrue(True)

    def test_find_first_template(self):
        threshold = 0.99
        parser = Parser()

        match = parser._find_first_template(self.TEST_IMAGE_2.convert("L"), self.TEST_TEMPLATE.convert("L"), threshold)
        # display_bounding_boxes(self.TEST_IMAGE_2, [match])

        match = parser._find_first_template(self.TEST_IMAGE_3.convert("L"), self.TEST_TEMPLATE.convert("L"), threshold)
        # display_bounding_boxes(self.TEST_IMAGE_3, [match])

        self.assertTrue(True)

    def test_parse_bar_percentage(self):
        self.assertTrue(True)

ut.main()
