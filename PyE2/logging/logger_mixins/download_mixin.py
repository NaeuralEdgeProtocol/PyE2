import os
import sys
import zipfile
from time import time


class _DownloadMixin(object):
  """
  Mixin for download functionalities that are attached to `pye2.Logger`.

  This mixin cannot be instantiated because it is built just to provide some additional
  functionalities for `pye2.Logger`

  In this mixin we can use any attribute/method of the Logger.
  """

  def __init__(self):
    super(_DownloadMixin, self).__init__()
    return

  def maybe_download_model(self,
                           url,
                           model_file,
                           force_download=False,
                           url_model_cfg=None,
                           **kwargs,
                           ):
    """
    url11 = 'https://www.dropbox.com/s/t6qfxiopcr8yvlq/60_xomv_employee01_002_e142_acc0.985.pb?dl=1'
    url12 = 'https://www.dropbox.com/s/akzyk9vcuqluzup/60_xomv_employee01_002_e142_acc0.985.pb.txt?dl=1'
    # use maybe_download_model
    log.maybe_download_model(url11, 'model1_dup.pb',
                             force_download=False,
                             url_model_cfg=url12)
    """
    urls = [url]
    fn = [model_file]
    if url_model_cfg is not None:
      urls += [url_model_cfg]
      fn += [model_file + '.txt']

    return self.maybe_download(
      url=urls,
      fn=fn,
      force_download=force_download,
      target='models',
      **kwargs,
    )

  def maybe_download(self,
                     url,
                     fn=None,
                     force_download=False,
                     target=None,
                     print_progress=True,
                     publish_func=None,
                     publish_only_value=False,
                     verbose=True,
                     unzip=False,
                     **kwargs
                     ):
    """
    NEW VERSION: if url starts with 'minio:' the function will retrieve minio conn
                 params from **kwargs and use minio_download (if needed or forced)

    will (maybe) download a from a given (full) url a file and save to
    target folder in `model_file`.

    The parameter named `publish_func` is a function that publish a message
    through a channel. We do not want to parametrize more than necessary this
    method, so the `publish_func` function should be already charged with
    the channel via a partial.

    The `unzip` parameter comes in when the url(s) is/are zipped folder(s).
    In this case, put `fn` as the name of the local folder, not as the name of the local zip file

    Examples:

    url11 = 'https://www.dropbox.com/s/t6qfxiopcr8yvlq/60_xomv_employee01_002_e142_acc0.985.pb?dl=1'
    fn1 = 'model1.pb'
    url12 = 'https://www.dropbox.com/s/akzyk9vcuqluzup/60_xomv_employee01_002_e142_acc0.985.pb.txt?dl=1'
    fn2 = 'model1.txt'
    url21 = 'https://www.dropbox.com/s/tuywpfzv6ueknj6/70_xfgc03_007_e092_acc0.9413.pb?dl=1'
    fn3 = 'model2.pb'
    url22 = 'https://www.dropbox.com/s/5wrvohffl14qfd3/70_xfgc03_007_e092_acc0.9413.pb.txt?dl=1'
    fn4 = 'model2.txt'
    log = Logger(lib_name='MDL',  config_file='config/duplex_config.txt',  TF_KERAS=False)

    # download two files in output
    log.maybe_download(url=[url11, url12],
                       fn=[fn1,fn2],
                       target='output'
                       )

    # download a txt in data
    log.maybe_download(url=url12,
                       fn='model1_dup.txt',
                       target='data'
                       )

    # download another two files in models with other signature
    log.maybe_download(url={
                        fn3 : url21,
                        fn4 : url22
                        },
                       force_download=True,
                       target='models'
                       )

    # use maybe_download_model
    log.maybe_download_model(url11, 'model1_dup.pb',
                             force_download=False,
                             url_model_cfg=url12)

    """
    import urllib.request
    assert target in ['models', 'data', 'output', None], "target must be either 'models', 'data', 'output' or None"

    if type(url) is dict:
      urls = [v for k, v in url.items()]
      fns = [k for k in url]
    else:
      if fn is None:
        self.raise_error("fn must be a string or a list if url param does not have file:url dict")
      urls = url
      fns = fn
      if type(urls) is str:
        urls = [urls]
      if type(fns) is str:
        fns = [fns]
      if len(fns) != len(urls):
        self.raise_error("must provided same nr of urls and file names")

    if verbose:
      str_log = "Maybe dl '{}' to '{}' from '{}'".format(fns, target, urls)
      self.P(str_log)
    # endif

    def _print_download_progress(count, block_size, total_size):
      """
      Function used for printing the download progress.
      Used as a call-back function in maybe_download_and_extract().
      """

      # Percentage completion.
      pct_complete = float(count * block_size) / total_size

      # Limit it because rounding errors may cause it to exceed 100%.
      pct_complete = min(1.0, pct_complete)

      if publish_func is not None:
        if publish_only_value:
          publish_func(round(pct_complete * 100, 2))
        else:
          publish_func("progress:{:.1%}".format(pct_complete))

      if print_progress:
        # Status-message. Note the \r which means the line should overwrite itself.
        msg = "\r- Download progress: {0:.1%}".format(pct_complete)

        # Print it.
        sys.stdout.write(msg)
        sys.stdout.flush()
      return

    def _copy_to_target(src, dst):
      import shutil
      if os.path.isfile(src):
        shutil.copy(src, dst)
      elif os.path.isdir(src):
        if not os.path.exists(dst):
          shutil.copytree(src, dst)
      else:
        self.P("ERROR: unknown source type: {}".format(src), color='error')
      return

    # Path for local file.
    if target is not None:
      download_dir = self.get_target_folder(target=target)
    else:
      download_dir = ''

    saved_files = []
    msgs = []
    for _fn, _url in zip(fns, urls):
      if _fn is None or _url is None:
        msg = "Cannot download '{}' from '{}'".format(_fn, _url)
        msgs.append(msg)
        saved_files.append(None)
        self.P(msg, color='error')
        continue
      # useful if _fn is a hierarchy not a filename
      _append_to_download_dir, _fn = os.path.split(_fn)
      _crt_download_dir = os.path.join(download_dir, _append_to_download_dir)
      save_path = os.path.join(_crt_download_dir, _fn)

      # Check if the file already exists, otherwise we need to download it now.
      has_file = os.path.exists(save_path)
      if not has_file or force_download:
        file_path = None
        # handle http standard download
        # automatically add .zip in this corner case
        if unzip and not save_path.endswith('.zip'):
          save_path += '.zip'

        # Check if the download directory exists, otherwise create it.
        if not os.path.exists(_crt_download_dir):
          if verbose:
            self.P("Download folder not found - creating")
          os.makedirs(_crt_download_dir)
        if has_file:
          if verbose:
            self.P("Forced download: removing ...{}".format(save_path[-40:]))
          os.remove(save_path)

        if _url.startswith('minio:'):
          # handle MinIO url
          _url = _url.replace('minio:', '')
          file_path = self.minio_download(
            local_file_path=save_path,
            object_name=_url,
            **kwargs,
          )

        elif _url.startswith('http'):
          # Download the file from the internet.
          if verbose:
            self.P("Downloading {} from {}...".format(_fn, _url[:40]))
          reporthook = _print_download_progress
          import ssl
          ssl._create_default_https_context = ssl._create_unverified_context
          file_path, msg = urllib.request.urlretrieve(  # this has errors!!! if this fails, the path is none
            url=_url,
            filename=save_path,
            reporthook=reporthook
          )

          msgs.append(msg)
          print("", flush=True)
          if verbose:
            self.P("Download done and saved in ...{}".format(file_path[-40:]))
          # endif
        elif os.path.exists(_url):
          if verbose:
            self.P("Found file in local file system at {}".format(_url))
          _copy_to_target(_url, save_path)
          file_path = save_path

          if verbose:
            self.P("Copied file from given location to {}".format(save_path))
        else:
          self.P("ERROR: unknown url type: {}".format(_url), color='error')

        if file_path is not None:
          if unzip:
            _directory_to_extract_to = os.path.splitext(save_path)[0]
            if verbose:
              self.P("Unzipping '...{}' ...".format(file_path[-40:]))
            if not os.path.exists(_directory_to_extract_to):
              os.makedirs(_directory_to_extract_to)

            with zipfile.ZipFile(file_path, 'r') as zip_ref:
              zip_ref.extractall(_directory_to_extract_to)

            # remove the downloaded zip file as it was already extracted, so it occupies space without any use
            os.remove(file_path)
            saved_files.append(_directory_to_extract_to)
          else:
            saved_files.append(file_path)

      else:
        if verbose:
          self.P("File {} found. Skipping.".format(_fn))
        saved_files.append(save_path)
        msgs.append("'{}' already downloaded.".format(save_path))
    # endfor

    return saved_files, msgs

  def minio_get_dowload_url(self,
                            endpoint,
                            access_key,
                            secret_key,
                            bucket_name,
                            object_name,
                            ):
    """
    Retreives a 7 day url for a particular bucket/object

    Parameters
    ----------
    endpoint : str
      address of the MinIO server.
    access_key : str
      user.
    secret_key : str
      password.
    bucket_name : str
      preconfigureg bucket name.
    object_name : str
      the existing Minio object name

    Returns
    -------
     URL

    """
    from minio import Minio

    try:
      client = Minio(
        endpoint=endpoint,
        access_key=access_key,
        secret_key=secret_key,
        secure=False,
      )

      url = client.presigned_get_object(
        bucket_name=bucket_name,
        object_name=object_name,
      )
    except Exception as e:
      self.P(str(e), color='error')
      return None

    return url

  def minio_download(self,
                     local_file_path,
                     endpoint,
                     access_key,
                     secret_key,
                     bucket_name,
                     object_name,
                     secure=False,
                     SSL_CERT_FILE=None,
                     **kwargs,
                     ):
    """


    Parameters
    ----------
    local_file_path : str
      relative or full path to the (future) local file.
    endpoint : str
      address of the MinIO server.
    access_key : str
      user.
    secret_key : str
      password.
    bucket_name : str
      preconfigureg bucket name.
    object_name : str
      a object name - can be None and will be auto-generated

    Returns
    -------
      saved file name

    """
    from minio import Minio
    import urllib3
    from datetime import timedelta

    try:
      start_up = time()

      # if SSL_CERT_FILE is not None:
      #   os.environ['SSL_CERT_FILE'] = SSL_CERT_FILE
      cert_reqs = None
      http_client = None
      if secure:
        if SSL_CERT_FILE is not None:
          if not os.path.isfile(SSL_CERT_FILE):
            raise ValueError("Invalid SSL_CERT_FILE in config")
          else:
            cert_reqs = 'CERT_REQUIRED'
        else:
          cert_reqs = 'CERT_NONE'

        timeout = timedelta(minutes=5).seconds
        http_client = urllib3.PoolManager(
          timeout=urllib3.util.Timeout(connect=timeout, read=timeout),
          maxsize=10,
          cert_reqs=cert_reqs,
          ca_certs=SSL_CERT_FILE,
          retries=urllib3.Retry(
            total=5,
            backoff_factor=0.2,
            status_forcelist=[500, 502, 503, 504]
          )
        )
      self.P("Downloading from Minio: <{} {} @{}>, secure:{}, SSL_CERT_FILE:'{}', cert_reqs:'{}' using http_client: {}...".format(
        access_key, secret_key, endpoint, secure, SSL_CERT_FILE,
        cert_reqs,
        http_client,
      )
      )
      client = Minio(
        endpoint=endpoint,
        access_key=access_key,
        secret_key=secret_key,
        secure=secure,
        http_client=http_client,
      )

      res = client.fget_object(
        bucket_name=bucket_name,
        object_name=object_name,
        file_path=local_file_path,
      )

      self.P("Downloaded '{}' from {}/{}/{} in {:.2f}s".format(
        local_file_path, endpoint, bucket_name, object_name,
        time() - start_up), color='y')
    except Exception as e:
      self.P(str(e), color='error')
      return None

    return local_file_path
