import numpy as np

class Parser:
    def parse_data(self, data: np.ndarray):
        """Takes in data and parses it into a new datatype for easy analysis
        Args:
            data (np.ndarray): the data that from Reader. We are assuming the
                file is read in 1280x720px

        Returns:
            output (Data): the parsed data with important details of that current frame
        """

        pass

    def crop_regions(self, data: np.ndarray, rois: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
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

            if len(roi_coords) == 4:    # Check if there's two pairs of coordinates
                if roi_coords[0] < roi_coords[1] and roi_coords[2] < roi_coords[3]: # Check if it's a positively sized bounding box
                    regions[roi_name] = data[roi_coords[2]:roi_coords[3], roi_coords[0]:roi_coords[1]]

        return regions

    def parse_bar_percentage(self, roi: np.ndarray) -> float:
        """Given a frame of image, parse the meter gauge percentage (should also be healthbar)

        Args:
            roi (np.ndarray): the region of interest

        Returns:
            percentage (float): the normalized percentage of the bar
        """

        return -1.0

    def parse_super_level(self, roi: np.ndarray) -> int:
        """Given an image, retrieve the super level from the text

        Args:
            roi (np.ndarray): the region (image) which the number resides in

        Returns:
            percentage (int): the number in the image
        """

        return -1

    def parse_time(self, roi: np.ndarray) -> int:
        """Given an image, retrieve the time remaining from the text

        Args:
            roi (np.ndarray): the region (image) which the number resides in

        Returns:
            percentage (int): the number in the image
        """

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