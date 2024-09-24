import os
import bz2
import pickle

class _PickleSerializationMixin(object):
  """
  Mixin for pickle serialization functionalities that are attached to `pye2.Logger`.

  This mixin cannot be instantiated because it is built just to provide some additional
  functionalities for `pye2.Logger`

  In this mixin we can use any attribute/method of the Logger.
  """

  def __init__(self):
    super(_PickleSerializationMixin, self).__init__()
    return

  def _save_compressed_pickle(self, full_filename, myobj, locking=False):
    """
    save object to file using pickle

    @param full_filename: name of destination file
    @param myobj: object to save (has to be pickleable)
    """
    with self.managed_lock_resource(full_filename, condition=locking):
      try:
        fhandle = bz2.BZ2File(full_filename, 'wb')
        pickle.dump(myobj, fhandle, protocol=pickle.HIGHEST_PROTOCOL)
        fhandle.close()
      except:
        self.P('ERROR: File ' + full_filename + ' cannot be written!')
        return False
    # endwith conditional lock
    return True


  def _load_compressed_pickle(self, full_filename, locking=False):
    """
    Load from filename using pickle

    @param full_filename: name of file to load from
    """
    with self.managed_lock_resource(full_filename, condition=locking):
      try:
        fhandle = bz2.BZ2File(full_filename, 'rb')
        myobj = pickle.load(fhandle)
        fhandle.close()
      except:
        self.P('ERROR: File ' + full_filename + ' cannot be read!')
        return None
    # endwith conditional lock

    return myobj


  def save_pickle(self, data, fn, folder=None,
                  use_prefix=False, verbose=True,
                  compressed=False,
                  subfolder_path=None,
                  locking=True,
                  ):
    """
    compressed: True if compression is required OR you can just add '.pklz' to `fn`
    """

    def P(s):
      if verbose:
        self.P(s)
      return

    # enddef

    lfld = self.get_target_folder(target=folder)

    if lfld is None:
      P("Assuming `fn` param ({}) is a full path".format(fn))
      datafile = fn
    else:
      if use_prefix:
        fn = self.file_prefix + '_' + fn
      datafolder = lfld
      if subfolder_path is not None:
        datafolder = os.path.join(datafolder, subfolder_path.lstrip('/'))
        os.makedirs(datafolder, exist_ok=True)
      datafile = os.path.join(datafolder, fn)

    os.makedirs(os.path.split(datafile)[0], exist_ok=True)

    if compressed or '.pklz' in fn:
      if not compressed:
        P("Saving pickle with compression=True forced due to extension")
      else:
        P("Saving pickle with compression...")
      if self._save_compressed_pickle(datafile, myobj=data, locking=locking):
        P("  Compressed pickle {} saved in {}".format(fn, folder))
      else:
        P("  FAILED compressed pickle save!")
    else:
      P("Saving uncompressed pikle (lock:{}) : {} ".format(locking, datafile))
      with self.managed_lock_resource(datafile, condition=locking):
        try:
          with open(datafile, 'wb') as fhandle:
            pickle.dump(data, fhandle, protocol=pickle.HIGHEST_PROTOCOL)
        except:
          pass
    # endwith conditional lock
      if verbose:
        P("  Saved pickle '{}' in '{}' folder".format(fn, folder))
    return datafile


  def save_pickle_to_data(self, data, fn, compressed=False, verbose=True, 
                          subfolder_path=None, locking=True):
    """
    compressed: True if compression is required OR you can just add '.pklz' to `fn`
    """
    return self.save_pickle(
      data, fn,
      folder='data',
      compressed=compressed,
      subfolder_path=subfolder_path,
      verbose=verbose,
      locking=locking,
    )


  def save_pickle_to_models(self, data, fn, compressed=False, verbose=True, 
                            subfolder_path=None, locking=True):
    """
    compressed: True if compression is required OR you can just add '.pklz' to `fn`
    """
    return self.save_pickle(
      data, fn,
      folder='models',
      compressed=compressed,
      subfolder_path=subfolder_path,
      verbose=verbose,
      locking=locking,
    )


  def save_pickle_to_output(self, data, fn, compressed=False, verbose=True, 
                            subfolder_path=None, locking=True):
    """
    compressed: True if compression is required OR you can just add '.pklz' to `fn`
    """
    return self.save_pickle(
      data, fn,
      folder='output',
      compressed=compressed,
      subfolder_path=subfolder_path,
      verbose=verbose,
      locking=locking,
    )


  def load_pickle_from_models(self, fn, decompress=False, verbose=True, 
                              subfolder_path=None, locking=True):
    """
     decompressed : True if the file was saved with `compressed=True` or you can just use '.pklz'
    """
    return self.load_pickle(
      fn,
      folder='models',
      decompress=decompress,
      verbose=verbose,
      subfolder_path=subfolder_path,
      locking=locking,
    )


  def load_pickle_from_data(self, fn, decompress=False, verbose=True, 
                            subfolder_path=None, locking=True):
    """
     decompressed : True if the file was saved with `compressed=True` or you can just use '.pklz'
    """
    return self.load_pickle(
      fn,
      folder='data',
      decompress=decompress,
      verbose=verbose,
      subfolder_path=subfolder_path,
      locking=locking,
    )


  def load_pickle_from_output(self, fn, decompress=False, verbose=True, 
                              subfolder_path=None, locking=True):
    """
     decompressed : True if the file was saved with `compressed=True` or you can just use '.pklz'
    """
    return self.load_pickle(
      fn,
      folder='output',
      decompress=decompress,
      verbose=verbose,
      subfolder_path=subfolder_path,
      locking=locking,
    )


  def load_pickle(self, fn, folder=None, decompress=False, verbose=True,
                  subfolder_path=None, locking=True):
    """
     load_from: 'data', 'output', 'models'
     decompressed : True if the file was saved with `compressed=True` or you can just use '.pklz'
    """
    if verbose:
      P = self.P
    else:
      P = lambda x, color=None: x

    lfld = self.get_target_folder(target=folder)

    if lfld is None:
      P("Loading pickle ... Assuming `fn` param ({}) is a full path".format(fn))
      datafile = fn
    else:
      datafolder = lfld
      if subfolder_path is not None:
        datafolder = os.path.join(datafolder, subfolder_path.lstrip('/'))
      datafile = os.path.join(datafolder, fn)
      P("Loading pickle (locked:{}) from {}".format(locking, datafile))
    #endif full path or not
    data = None
    exc = None
    if os.path.isfile(datafile):
      if decompress or '.pklz' in datafile:
        if not decompress:
          P("Loading pickle with decompress=True forced due to extension")
        else:
          P("Loading pickle with decompression...")
        data = self._load_compressed_pickle(datafile)
      else:
        with self.managed_lock_resource(datafile, condition=locking):
          try:
            with open(datafile, "rb") as f:
              data = pickle.load(f)
          except Exception as _exc:
            data = None
            exc = _exc
        # endwith conditional lock
      #endif decompress or not
      if data is None:
        P("  {} load failed with error {}".format(datafile, exc), color='r')
      else:
        P("  Loaded: {}".format(datafile))
      #endif data is None
    else:
      P("  File not found! Pickle load failed.", color='r')
    return data
  
  
  def update_pickle_from_data(self, 
                              fn, 
                              update_callback, 
                              decompress=False, 
                              verbose=False, 
                              subfolder_path=None,
                              force_update=False):
    assert update_callback is not None, "update_callback must be defined!"
    datafile = self.get_file_path(
      fn=fn,
      folder='data',
      subfolder_path=subfolder_path,
      force=True
      )
    if datafile is None:
      self.P("update_pickle_from_data failed due to missing {}".format(datafile), color='error')
      return False

    with self.managed_lock_resource(datafile):
      result = None
      try:
        data = self.load_pickle_from_data(
          fn=fn,
          decompress=decompress,
          verbose=verbose,
          subfolder_path=subfolder_path,
          locking=False,
          )
        
        if data is not None or force_update:
          data = update_callback(data)
          
          self.save_pickle_to_data(
            data=data, 
            fn=fn,
            compressed=decompress,
            verbose=verbose,
            subfolder_path=subfolder_path,
            locking=False,
            )
          result = True
      except Exception as e:
        self.P("update_pickle_from_data failed: {}".format(e), color='error')
        result = False
    # endwith lock
    return result
      