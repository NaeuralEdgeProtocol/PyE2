import os
import pickle
import numpy as np
import zlib
import base64

class _GeneralSerializationMixin(object):
  """
  Mixin for general serialization functionalities that are attached to `pye2.Logger`:
    - zip
    - csr
    - numpy
    - xml


  This mixin cannot be instantiated because it is built just to provide some additional
  functionalities for `pye2.Logger`

  In this mixin we can use any attribute/method of the Logger.
  """

  def __init__(self):
    super(_GeneralSerializationMixin, self).__init__()
    return

  def unzip(self, path_source, path_dest):
    import zipfile
    if not zipfile.is_zipfile(path_source):
      self.P('File provided is not a .zip file!', color='r')
      return

    with zipfile.ZipFile(path_source, 'r') as zip_ref:
      zip_ref.extractall(path_dest)
    return

  def save_csr(self, fn, csr_matrix, folder='data', use_prefix=True, verbose=True):
    from scipy import sparse
    lfld = self.get_target_folder(target=folder)

    if lfld is None:
      raise ValueError("Uknown save folder '{}' - valid options are `data`, `output`, `models`".format(
        folder))
    if use_prefix:
      fn = self.file_prefix + '_' + fn
    datafile = os.path.join(lfld, fn)
    sparse.save_npz(datafile, csr_matrix)
    if verbose:
      self.P("Saved sparse csr matrix '{}' in '{}' folder".format(
        fn, folder))
    return

  def load_csr(self, fn, folder='data'):
    """
     load_from: 'data', 'output', 'models'
    """
    from scipy import sparse
    lfld = self.get_target_folder(target=folder)

    if lfld is None:
      raise ValueError("Uknown load folder '{}' - valid options are data, output, models".format(
        folder))
    datafile = os.path.join(lfld, fn)
    self.verbose_log("Loading csr sparse matrix '{}' from '{}'".format(fn, folder))
    data = None
    if os.path.isfile(datafile):
      data = sparse.load_npz(datafile)
    else:
      self.P("  File not found!", color='r')
    return data

  def save_np(self, fn, arr_or_arrs, folder='data', use_prefix=True, verbose=True):
    lfld = self.get_target_folder(target=folder)

    if lfld is None:
      raise ValueError("Uknown save folder '{}' - valid options are `data`, `output`, `models`".format(
        folder))
    if use_prefix:
      fn = self.file_prefix + '_' + fn
    datafile = os.path.join(lfld, fn)
    if type(arr_or_arrs) == list:
      np.savez(datafile, arr_or_arrs)
    elif type(arr_or_arrs) == np.ndarray:
      np.save(datafile, arr_or_arrs)
    else:
      raise ValueError("Unknown `arr_or_arrs` - must provide either list of ndarrays or a single ndarray")
    if verbose:
      self.P("Saved sparse numpy data '{}' in '{}' folder".format(
        fn, folder)
      )
    return

  def load_np(self, fn, folder='data'):
    """
     `folder`: 'data', 'output', 'models'
    """
    lfld = self.get_target_folder(target=folder)

    if lfld is None:
      raise ValueError("Uknown load folder '{}' - valid options are data, output, models".format(
        folder))
    datafile = os.path.join(lfld, fn)
    self.verbose_log("Loading numpy data '{}' from '{}'".format(fn, folder))
    data = None
    if os.path.isfile(datafile):
      data = np.load(datafile)
    else:
      self.P("  File not found!", color='r')
    return data

  @staticmethod
  def load_xml(fn):
    import xml.etree.ElementTree as ET
    doc = ET.parse(fn)
    root = doc.getroot()
    return doc, root

  def read_from_path(self, path):
    import pandas as pd
    from os.path import splitext
    file_name, extension = splitext(path)
    if extension == '.csv':
      self.P('Reading from {}'.format(path))
      df = pd.read_csv(path)
      self.P('Done reading from {}'.format(path), show_time=True)
      return df
    elif extension == '.xls' or extension == '.xlsx':
      self.P('Reading from {}'.format(path))
      df = pd.read_excel(path)
      self.P('Done reading from {}'.format(path), show_time=True)
      return df
    elif extension == '.pkl':
      self.P('Reading from {}'.format(path))
      with open(path, 'rb') as handle:
        df = pickle.load(handle)
      self.P('Done reading from {}'.format(path), show_time=True)
      return df
    raise ValueError('Extension {} not understood!'.format(extension))

  @staticmethod
  def write_to_path(path, data):
    import pandas as pd
    from os.path import splitext
    file_name, extension = splitext(path)
    if extension == '.csv':
      if isinstance(data, np.ndarray):
        data = pd.DataFrame(data)
      data.to_csv(path, index=False)
    elif extension == '.xls' or extension == '.xlsx':
      if isinstance(data, np.ndarray):
        data = pd.DataFrame(data)
      data.to_excel(path, index=False)
    elif extension == '.pkl':
      with open(path, 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
  
  
  def add_file_to_zip(self, path_zip, path_file):
    try:
      from zipfile import ZipFile, ZIP_DEFLATED
      if not os.path.isfile(path_file):
        self.P("Adding to zip '{}' failed: missing '{}' ".format(path_zip, path_file), color='r')
        return
      zip = ZipFile(
        file=path_zip, 
        mode='a', 
        compression=ZIP_DEFLATED
      )
      self.P("Archiving (zip) '{}' => {}".format(path_file, path_zip), color='y')
      zip.write(path_file, arcname=os.path.basename(path_file))
      zip.close()
    except Exception as e:
      self.P("Exception occured while archiving '{}' in '{}': {}".format(
        path_file, path_zip, e), color='r'
      )
      return
    return path_zip
    
  def add_files_to_zip(self, path_zip, files):
    try:
      from zipfile import ZipFile, ZIP_DEFLATED
      zip = ZipFile(
        file=path_zip, 
        mode='a', 
        compression=ZIP_DEFLATED
      )
      self.P("  Adding {} files to archive (zip) {}".format(
        len(files),
        path_zip, 
        ), color='y'
      )
      written = 0
      for path_file in files:
        if not os.path.isfile(path_file):
          self.P("    Adding to zip '{}' failed: missing '{}' ".format(path_zip, path_file), color='r')
          continue        
        zip.write(path_file, arcname=os.path.basename(path_file))
        print(".",  flush=True, end='')
        written += 1
      zip.close()
      self.P("    Added {} files.".format(written), color='y')
    except Exception as e:
      self.P("Exception occured while archiving {} files in '{}': {}".format(
        len(files), path_zip, e), color='r'
      )
      return
    return path_zip
  
  
  def compress_bytes(self, data):
    if not isinstance(data, bytes):
      data = bytes(str(data), 'utf-8')
    zip_data = zlib.compress(data)
    return zip_data
  
  def decompress_bytes(self, zip_data):
    if not isinstance(zip_data, bytes):
      raise ValueError('`decompress_bytes` input must be bytes type')
    data = zlib.decompress(zip_data)
    return data
  
  
  def compress_text(self, text):
    b_text = bytes(text, 'utf-8')    
    b_code = zlib.compress(b_text, level=9)
    b_encoded = base64.b64encode(b_code)
    str_encoded = b_encoded.decode('utf-8')
    return str_encoded


  def decompress_text(self, b64text):
    decoded = None
    try:
      b_decoded = base64.b64decode(b64text)
      b_decoded = zlib.decompress(b_decoded)
      s_decoded = b_decoded.decode('utf-8')
      decoded = s_decoded
    except:
      pass
    return decoded
    
    
    