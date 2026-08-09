import cv2
import numpy as np
from HelperFunctions import *
from PIL import Image

SUPERTEMPLATES = {
    0: Image.open("templates/super0.jpg").convert("L"),
    1: Image.open("templates/super1.jpg").convert("L"),
    2: Image.open("templates/super2.jpg").convert("L"),
    3: Image.open("templates/super3.jpg").convert("L"),
}


class Parser:
    def __init__(self) -> None:
        self.superTemplates = SUPERTEMPLATES

    template_match_method = cv2.TM_CCOEFF_NORMED

    def parse_data(self, data: np.ndarray):
        """Takes in data and parses it into a new datatype for easy analysis
        Args:
            data (np.ndarray): the data that from Reader. We are assuming the
                file is read in 1280x720px

        Returns:
            output (Data): the parsed data with important details of that current frame
        """

        pass

    def crop_regions(
        self, data: np.ndarray, rois: dict[str, np.ndarray]
    ) -> dict[str, np.ndarray]:
        """Given data, crops the data

        Args:
            data (np.ndarray): the data provided
            rois (dict): the region of interests to be cropped out;
                Each game will have different amounts of regions so method should
                be able to handle an arbitrary amount of regions.
                The dict will have the name of the region (i.e. meter, health) with
                it's corresponding coordinates in an array in the format of [x1, x2, y1, y2]

        Returns:
            rois (dict): the dict will have named regions (np.ndarray) with its
                corresponding slice of the given data
        """
        regions = {}

        for roi_name in rois.keys():
            roi_coords = rois[roi_name]

            if len(roi_coords) == 4:  # Check if there's two pairs of coordinates
                if (
                    roi_coords[0] < roi_coords[1] and roi_coords[2] < roi_coords[3]
                ):  # Check if it's a positively sized bounding box
                    regions[roi_name] = data[
                        roi_coords[2] : roi_coords[3], roi_coords[0] : roi_coords[1]
                    ]

        return regions

    def parse_bar_percentage(self, image: np.ndarray) -> float:
        """Given a frame of image, parse the meter gauge percentage (should also be healthbar)

        Args:
            image (np.ndarray): the image to parse

        Returns:
            percentage (float): the normalized percentage of the bar
        """

        return -1.0

    def parse_super_level(self, image: np.ndarray) -> int:
        """Given an image, retrieve the super level from the text

        Args:
            image (np.ndarray): The image which the number is in.

        Returns:
            level (int): The super level number in the given image.
              Returns between [0, 3] if found or -1 if no number was found.
              This can either mean the image provided didn't contain the super level or the number was blocked by something
              (store and use previous frame values for continuous data).
        """
        threshold = 0.99

        # Check for each super level
        for i in range(len(self.superTemplates)):
            matches = self._find_first_template(
                Image.fromarray(image), self.superTemplates[i], threshold
            )
            if matches.size > 0:
                return i

        # Didn't find a valid super level number (might be blocked)
        return -1

    def parse_time(self, image: np.ndarray) -> int:
        """Given an image, retrieve the time remaining from the text.

        Args:
            image (np.ndarray): The numpy array for the B&W image which the number is in. Give the whole raw image without cropping it.

        Returns:
            time (int): The time left in the image. Can be between [99, 0] if a number was detected, or -1 if a number wasn't detected.
        """
        # Crop the image to be bounded roughly around the time section

        # Detect for a number [0-9] (go from 9 to 0 to make it faster initially)

        # If a number was detected, crop the left of the image to be from that point_x+template_w

        # Detect for a number [0-9] (go from 9 to 0 to make it faster initially)

        # If a number was detected, return the 2 digit number
        # Else return the 1 digit number from the first detection

        # A number wasn't detected. This could be due to the number being obstructed by a character.
        return -1

    def parse_character_action(self, roi: np.ndarray) -> list:
        """Given an image, check for a character action

        Args:
            roi (np.ndarray): the region (image) with the character

        Returns:
            move (list): list of flags
        """

        return []

    def parse_game_flags(self, roi: np.ndarray) -> list:
        """Given an image, detect special game specific flags (i.e. Punish Counter, Counter)

        Args:
            roi (np.ndarray): the image with the game specific flags

        Returns:
            flags (list): the detected flags
        """

        return []

    def _find_all_templates(
        self, image: Image.Image, template: Image.Image, threshold: float
    ) -> list[np.ndarray]:
        """Finds bounding boxes in the given PIL image where the given template PIL image is. False positives are filtered out by the threshold value.

        Requires the image and template to be in B&W (a 2D array)

        Args:
            image (Image.Image): The PIL image to find the template in.
            template (Image.Image): The template (a PIL image) to check for.
            threshold (float): The detection threshold.

        Returns:
            list[np.ndarray]: A list of bounding boxes where the template was found and had a similarity higher than the threshold.
        """
        template_h, template_w = np.array(template).shape[:2]

        # Taken from: https://opencv24-python-tutorials.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_template_matching/py_template_matching.html
        match_list = cv2.matchTemplate(
            np.array(image), np.array(template), self.template_match_method
        )
        # * If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
        locations = np.where(match_list >= threshold)

        matches = []
        for pt in zip(*locations[::-1]):
            matches.append(
                np.array([pt[0], pt[1], pt[0] + template_w, pt[1] + template_h])
            )

        return matches

    def _find_first_template(
        self, image: Image.Image, template: Image.Image, threshold: float
    ) -> np.ndarray:
        match_list = cv2.matchTemplate(
            np.array(image), np.array(template), self.template_match_method
        )

        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(match_list)
        # * If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
        if max_val >= threshold:
            template_h, template_w = np.array(template).shape[:2]
            return np.array(
                np.array(
                    [
                        max_loc[0],
                        max_loc[1],
                        max_loc[0] + template_w,
                        max_loc[1] + template_h,
                    ]
                )
            )

        return np.array([])
