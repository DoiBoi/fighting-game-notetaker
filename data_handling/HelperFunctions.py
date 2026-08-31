import math

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw
from scipy import signal


def show_image(image: np.ndarray, title: str = ""):
    """Displays the given image using your device's default image viewer.

    Args:
        image (np.ndarray): The image to display.
    """
    if title != "":
        plt.title(title)
        plt.imshow(image)
        plt.show()
    else:
        Image.fromarray(image).show()

def display_bounding_boxes(image: Image.Image, bounding_boxes: list[np.ndarray], thickness: int = 5):
    """Draws the given bounding boxes on a copy of the given image.

    Adapted from https://stackoverflow.com/a/43486239 and UBC's CPSC 425 course.

    Args:
        image (Image.Image): The PIL image to draw onto. This will make a copy of the original image.
        bounding_boxes (np.ndarray): The list of 4-tuples that define a bounding box in the format [x0, y0, x1, y1].
        thickness (int, optional): The thickness of the lines when drawing the bounding boxes. Defaults to 5.
    """
    image_copy = image.copy()
    image_draw = ImageDraw.Draw(image_copy)

    # Draw bounding boxes
    for box in bounding_boxes:
        x0, y0, x1, y1 = box

        image_draw.line([(x0, y0), (x1, y0)], fill="red", width=thickness)
        image_draw.line([(x1, y0), (x1, y1)], fill="red", width=thickness)
        image_draw.line([(x1, y1), (x0, y1)], fill="red", width=thickness)
        image_draw.line([(x0, y1), (x0, y0)], fill="red", width=thickness)

    image_copy.show()

def _normxcorr2D(image: Image.Image, template: Image.Image):
    """Normalized cross-correlation for 2D PIL images.
    Wherever the search space has zero variance under the template, normalized cross-correlation is undefined.
    An extremely slow, but mathematically-correct method.
    It's advised to use OpenCV's `cv2.matchTemplate` function instead.

    Adapted from UBC's CPSC 425 course.

    Args:
        image (Image.Image): The PIL image to template match against.
        template (Image.Image): The template PIL image to match with in the given image.

    Returns:
        nxcorr (np.ndarray): Array of cross-correlation coefficients, in the range [-1.0, 1.0].
    """

    # (one-time) normalization of template
    t = np.asarray(template, dtype=np.float64)
    t = t - np.mean(t)
    norm = math.sqrt(np.sum(np.square(t)))
    t = t / norm

    # create filter to sum values under template
    sum_filter = np.ones(np.shape(t))

    # get image
    a = np.asarray(image, dtype=np.float64)
    #also want squared values
    aa = np.square(a)

    # compute sums of values and sums of values squared under template
    a_sum = signal.correlate2d(a, sum_filter, 'same')
    aa_sum = signal.correlate2d(aa, sum_filter, 'same')
    # Note:  The above two lines could be made more efficient by
    #        exploiting the fact that sum_filter is separable.
    #        Even better would be to take advantage of integral images

    # compute correlation, 't' is normalized, 'a' is not (yet)
    numer = signal.correlate2d(a, t, 'same')
    # (each time) normalization of the window under the template
    denom = np.sqrt(aa_sum - np.square(a_sum)/np.size(t))

    # wherever the denominator is near zero, this must be because the image
    # window is near constant (and therefore the normalized cross correlation
    # is undefined). Set nxcorr to zero in these regions
    tol = np.sqrt(np.finfo(denom.dtype).eps)
    nxcorr = np.where(denom < tol, 0, numer/denom)

    # if any of the coefficients are outside the range [-1 1], they will be
    # unstable to small variance in a or t, so set them to zero to reflect
    # the undefined 0/0 condition
    nxcorr = np.where(np.abs(nxcorr-1.) > np.sqrt(np.finfo(nxcorr.dtype).eps),nxcorr,0)

    return nxcorr
