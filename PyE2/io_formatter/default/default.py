# local dependencies
from ...io_formatter.base import BaseFormatter


class DefaultFormatter(BaseFormatter):

  def __init__(self, log, **kwargs):
    super(DefaultFormatter, self).__init__(
        log=log, prefix_log='[DEFAULT-FMT]', **kwargs)
    return

  def startup(self):
    pass

  def _encode_output(self, output):
    return output

  def _decode_output(self, encoded_output):
    return encoded_output

  def _decode_streams(self, dct_config_streams):
    return dct_config_streams
