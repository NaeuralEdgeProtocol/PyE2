import os
import io
import numpy as np
import base64

from time import time as tm
from shutil import copyfile
from io import BytesIO

try:
  import cv2
except:
  pass

class _ComputerVisionMixin(object):
  """
  Mixin for computer vision functionalities that are attached to `libraries.logger.Logger`

  This mixin cannot be instantiated because it is built just to provide some additional
  functionalities for `libraries.logger.Logger`

  In this mixin we can use any attribute/method of the Logger.
  """

  def __init__(self):
    super(_ComputerVisionMixin, self).__init__()
    return

  @staticmethod
  def is_image(file):
    return any([file.endswith(tail) for tail in ('.png', '.jpg', '.jpeg')])

  @staticmethod
  def increase_brightness(img, value=30):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    lim = 255 - value
    v[v > lim] = 255
    v[v <= lim] += value

    final_hsv = cv2.merge((h, s, v))
    img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    return img

  @staticmethod
  def convert_gray(np_src, copy=False):
    np_source = np_src.copy() if copy else np_src
    if len(np_source.shape) == 3 and np_source.shape[-1] != 1:
      np_source = cv2.cvtColor(np_source, cv2.COLOR_BGR2GRAY)
    return np_source

  @staticmethod
  def scale_image(np_src, copy=False):
    np_source = np_src.copy() if copy else np_src
    if np_source.max() > 1:
      np_source = (np_source / 255).astype(np.float32)
    # endif
    return np_source

  @staticmethod
  def center_image(image, target_h, target_w, copy=False):
    image = image.copy() if copy else image
    new_h, new_w, _ = image.shape

    # determine the new size of the image
    if (float(target_w) / new_w) < (float(target_h) / new_h):
      new_h = int((new_h * target_w) / new_w)
      new_w = int(target_w)
    else:
      new_w = int((new_w * target_h) / new_h)
      new_h = int(target_h)

    # embed the image into the standard letter box
    new_image = np.ones((target_h, target_w, 3), dtype=np.uint8)
    top = int((target_h - new_h) // 2)
    bottom = int((target_h + new_h) // 2)
    left = int((target_w - new_w) // 2)
    right = int((target_w + new_w) // 2)

    resized = cv2.resize(image, dsize=(new_w, new_h))
    new_image[top:bottom, left:right, :] = resized
    return new_image

  @staticmethod
  def center_image_coordinates(src_h, src_w, target_h, target_w):
    asp_src = src_h / src_w
    asp_dst = target_h / target_w
    if asp_src > asp_dst:
      # if src_h > src_w:
      new_h = target_h
      new_w = int(target_h / (src_h / src_w))
    else:
      new_w = target_w
      new_h = int(target_w / (src_w / src_h))
    # endif

    left = target_w // 2 - new_w // 2
    top = target_h // 2 - new_h // 2
    right = left + new_w
    bottom = top + new_h
    return (top, left, bottom, right), (new_h, new_w)

  @staticmethod
  def center_image2(np_src, target_h, target_w, copy=False):
    np_source = np_src.copy() if copy else np_src
    shape = (target_h, target_w, np_src.shape[-1]) if len(np_src.shape) == 3 else (target_h, target_w)
    (top, left, bottom, right), (new_h, new_w) = _ComputerVisionMixin.center_image_coordinates(
      np_source.shape[0], np_source.shape[1],
      target_h, target_w
    )
    np_dest = np.zeros(shape).astype(np.float32 if np_src.max() <= 1 else np.uint8)
    np_src_mod = cv2.resize(np_src, dsize=(new_w, new_h))
    np_dest[top:bottom, left:right] = np_src_mod
    return np_dest

  @staticmethod
  def rescale_boxes(boxes,
                    src_h,
                    src_w,
                    target_h,
                    target_w,
                    ):
    if np.max(boxes) <= 1:
      # [0:1] to [0:model_shape]
      boxes[:, 0] *= target_h
      boxes[:, 1] *= target_w
      boxes[:, 2] *= target_h
      boxes[:, 3] *= target_w

    (top, left, bottom, right), (new_h, new_w) = _ComputerVisionMixin.center_image_coordinates(
      src_h=src_h,
      src_w=src_w,
      target_h=target_h,
      target_w=target_w
    )

    # eliminate centering
    boxes[:, 0] = boxes[:, 0] - top
    boxes[:, 1] = boxes[:, 1] - left
    boxes[:, 2] = boxes[:, 2] - top
    boxes[:, 3] = boxes[:, 3] - left

    # translate to original image scale
    boxes[:, 0] = boxes[:, 0] / new_h * src_h
    boxes[:, 1] = boxes[:, 1] / new_w * src_w
    boxes[:, 2] = boxes[:, 2] / new_h * src_h
    boxes[:, 3] = boxes[:, 3] / new_w * src_w

    # clipping between [0: max]
    boxes = boxes.astype(np.int32)
    boxes[:, 0] = np.maximum(0, boxes[:, 0])
    boxes[:, 1] = np.maximum(0, boxes[:, 1])
    boxes[:, 2] = np.minimum(src_h, boxes[:, 2])
    boxes[:, 3] = np.minimum(src_w, boxes[:, 3])
    return boxes

  @staticmethod
  def dir_visual_image_dedup(path_dir, magnify_image=None):
    """
    This method reads a folder, display every image in that folder al let's you
    decide where to move a specific image.
    Use:
      - s for skip
      - b for bad
      - g for good
      - q for quit
    """

    def close():
      cv2.waitKey(1)
      cv2.destroyAllWindows()
      for _ in range(5):
        cv2.waitKey(1)
      # endfor

    assert os.path.exists(path_dir)
    files = [x for x in os.listdir(path_dir) if x.endswith('.png') or x.endswith('.jpg')]
    path_good = os.path.join(path_dir, 'good')
    path_bad = os.path.join(path_dir, 'bad')
    for file in files:
      img_path = os.path.join(path_dir, file)
      img = cv2.imread(img_path)
      if magnify_image and magnify_image > 0:
        img = cv2.resize(img, (img.shape[1] * magnify_image, img.shape[0] * magnify_image))
      # endif
      cv2.imshow('Img', img)
      key = cv2.waitKey(0)
      if key == ord('b'):
        os.makedirs(path_bad, exist_ok=True)
        copyfile(img_path, os.path.join(path_bad, file))
      elif key == ord('g'):
        os.makedirs(path_good, exist_ok=True)
        copyfile(img_path, os.path.join(path_good, file))
      elif key == ord('q'):
        close()
        break
      elif key == ord('s'):
        pass
      # endif
    # endfor
    close()

  @staticmethod
  def to_rgb(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

  @staticmethod
  def change_brightness(img, delta):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    lim = 255 - delta
    v[v > lim] = 255
    v[v <= lim] += delta
    final_hsv = cv2.merge((h, s, v))
    img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    return img

  @staticmethod
  def rotate(image, angle, center=None, scale=1.0):
    (h, w) = image.shape[:2]
    if center is None:
      center = (w / 2, h / 2)
    # Perform the rotation
    M = cv2.getRotationMatrix2D(center, angle, scale)
    rotated = cv2.warpAffine(image, M, (w, h))
    return rotated

  @staticmethod
  def np_image_to_base64(np_image, ENCODING='utf-8', quality=95, max_height=None):
    from PIL import Image
    image = Image.fromarray(np_image)
    w, h = image.size
    if max_height is not None and h > max_height:
      ratio = max_height / h
      new_w, new_h = int(ratio * w), max_height
      image = image.resize((new_w, new_h), reducing_gap=1)
    buffered = BytesIO()
    if quality < 95:
      image.save(buffered, format='JPEG', quality=quality, optimize=True)
    else:
      image.save(buffered, format='JPEG')
    img_base64 = base64.b64encode(buffered.getvalue())
    img_str = img_base64.decode(ENCODING)
    return img_str

  @staticmethod
  def base64_to_np_image(base64_img):
    from PIL import Image
    base64_decoded = base64.b64decode(base64_img)
    image = Image.open(io.BytesIO(base64_decoded))
    np_image = np.array(image)
    return np_image

  @staticmethod
  def plt_to_base64(plt, close=True):
    figfile = BytesIO()
    plt.savefig(figfile, format='JPEG')
    figfile.seek(0)
    base64_bytes = base64.b64encode(figfile.getvalue())
    base64_string = base64_bytes.decode('utf-8')
    if close:
      plt.close()
    return base64_string
  
  @staticmethod
  def plt_to_np(plt, close=True, axis=False):
    # TODO: this method IS NOT thread-safe - needs revision
    if not axis:
      plt.axis('off')
    fig = plt.gcf()
    fig.canvas.draw()
    data = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
    w, h = fig.canvas.get_width_height()
    try:
      np_img = data.reshape((int(h), int(w), -1))
    except Exception as e:
      print(e)
      np_img = None
    if close:
      plt.close()
    return np_img    

  def time_model_forward(self, model, img_height, img_width, nr_inputs=1, lst_range=list(range(2, 33, 2))):
    from tqdm import tqdm
    lst_batches = list(range(2, 33, 2))
    self.P('Testing model {} forward time for {} iterations with batches: {}'.format(
      model.name, len(lst_batches), lst_batches)
    )
    for batch in tqdm(lst_batches):
      for i in range(2):
        data = nr_inputs * [np.random.uniform(size=(batch, img_height, img_width, 3))]
        start = tm()
        model.predict(data)
        stop = tm()
        if i == 1:
          self.P(' Forward time for bs {}: {:.3f}s. Time per obs: {:.3f}s'.format(
            batch, stop - start, (stop - start) / batch)
          )
        # endif
      # endfor
    # endfor

  @staticmethod
  def destroy_all_windows():
    cv2.waitKey(1)
    for i in range(5):
      cv2.waitKey(1)
      cv2.destroyAllWindows()
      cv2.waitKey(1)
    # endfor

  def describe_np_tensor(self, np_v):
    """
    Will take a numpy vector and will print statistics about that vector:
      - shape
      - min
      - max
      - std
      - median
      - percentiles (25 - 100)

    Parameters
    ----------
    np_v : np.ndarray
      Tensor of nD

    Returns
    -------
    None.
    """
    import pandas as pd
    assert isinstance(np_v, np.ndarray)
    lst = []
    lst.append(('Shape', np_v.shape))
    lst.append(('Dtype', np_v.dtype))
    lst.append(('Min', np.min(np_v)))
    lst.append(('Max', np.max(np_v)))
    lst.append(('Std', np.std(np_v)))
    lst.append(('Median', np.median(np_v)))
    for perc in [25, 50, 75, 100]:
      lst.append((perc, np.percentile(a=np_v, q=perc)))
    self.p('Tensor description \n{}'.format(pd.DataFrame(lst, columns=['IND', 'VAL'])))
    return

  def class_distrib(self, v):
    """
    Simple function to print the class distribution. Usefull especially for supervised classification tasks

    Parameters
    ----------
    v : list or ndarray
      Target tensor used in supervised classification problem.

    Returns
    -------
    None.

    """
    import pandas as pd
    assert isinstance(v, list) or isinstance(v, np.ndarray)
    unique, counts = np.unique(v, return_counts=True)
    self.p('Class distribution \n{}'.format(pd.DataFrame({'CLASS': unique, 'NR': counts})))
    return

  def cv_check_np_tensors(self, X, y, impose_norm=True, task='binary'):
    """
    Common pitfalls checks for input tensors of a supervised computer vision task.

    Parameters
    ----------
    X : np.ndarray
      Input tensor of a supervised computer vision task.
    y : np.ndarray
      Target tensor of a supervised computer vision task.
    impose_norm : boolean, optional
      Check if input tensor is normed. The default is True.

    Returns
    -------
    None.

    """
    assert task in ['binary', 'multiclass']
    self.p('Starting tensor sanity check')
    # check tensor lenghts are equal
    assert X.shape[0] == y.shape[0]

    # check if target is of shape (N, M)
    assert len(y.shape) == 2
    if task == 'binary': assert y.shape[-1] == 1
    if task == 'multiclass': self.p('[Info] Please ensure you have the right number of classes')

    # check if source is normed, only if impose_norm==True
    if impose_norm:
      assert X.max() <= 1.0, 'Your input tensor is not normed.'
    else:
      self.p('[Warning] Your input tensor is not normed.', color='yellow')

    # check datatypes
    if impose_norm:
      assert X.dtype == 'float32', 'Your input tensor should be of type np.float32'
    else:
      assert X.dtype == 'uint8', 'You didn\'t normed your input tensor, you should convert it to np.uint8'
    assert y.dtype == 'uint8', 'Your target tensor should be of type np.uint8'

    self.p('[Warning] RGB/BGR Please ensure that all your images are RGB', color='yellow')
    self.p('Done tensor sanity check')
    return
  
  @staticmethod
  def image_resize(image, width=None, height=None, inter=None):
    if inter is None:
      inter = cv2.INTER_AREA
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
      return image

    # check to see if the width is None
    if width is None:
      # calculate the ratio of the height and construct the
      # dimensions
      r = height / float(h)
      dim = (int(w * r), height)

    # otherwise, the height is None
    else:
      # calculate the ratio of the width and construct the
      # dimensions
      r = width / float(w)
      dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation = inter)

    # return the resized image
    return resized