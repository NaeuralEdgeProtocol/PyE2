import base64
import io
from collections import UserDict

import numpy as np


class Payload(UserDict):
  """
  This class enriches the default python dict, providing
  helpful methods to process the payloads received from Naeural edge nodes.
  """

  def get_images_as_np(self, key='IMG') -> list:
    """
    Extract the image from the payload.
    The image is returned as a numpy array.

    Parameters
    ----------
    key : str, optional
        The key from which to extract the image, by default 'IMG'.
        Can be modified if the user wants to extract an image from a different key

    Returns
    -------
    NDArray[Any] | None
        The image if it was found or None otherwise.
    """
    images = self.get_images_as_PIL(key)
    images = [np.array(image) if image is not None else None for image in images]
    return images

  def get_images_as_PIL(self, key='IMG') -> list:
    """
    Extract the image from the payload.
    The image is returned as a PIL image.

    Parameters
    ----------
    key : str, optional
        The key from which to extract the image, by default 'IMG'.
        Can be modified if the user wants to extract an image from a different key

    Returns
    -------
    List[Image] | None
        A list of images if there were any or None otherwise.
    """
    base64_img = self.data.get(key, None)
    if base64_img is None:
      return [None]
    if isinstance(base64_img, list):
      return [self._image_from_b64(b64) if b64 is not None else None for b64 in base64_img]
    return [self._image_from_b64(base64_img)]

  def _image_from_b64(self, base64_img):
    image = None
    try:
      from PIL import Image

      base64_decoded = base64.b64decode(base64_img)
      image = Image.open(io.BytesIO(base64_decoded))
    except ModuleNotFoundError:
      raise "This functionality requires the PIL library. To use this feature, please install it using 'pip install pillow'"
    return image
