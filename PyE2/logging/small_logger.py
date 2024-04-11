from .base_logger import BaseLogger
from .logger_mixins import (_ClassInstanceMixin,
                            _ComputerVisionMixin,
                            _DateTimeMixin,
                            _DownloadMixin,
                            _GeneralSerializationMixin,
                            _JSONSerializationMixin,
                            _PickleSerializationMixin,
                            _ProcessMixin,
                            _ResourceSizeMixin,
                            _TimersMixin,
                            _UploadMixin,
                            _UtilsMixin
                            )


class Logger(
  BaseLogger,
  _ClassInstanceMixin,
  _ComputerVisionMixin,
  _DateTimeMixin,
  _DownloadMixin,
  _GeneralSerializationMixin,
  _JSONSerializationMixin,
  _PickleSerializationMixin,
  _ProcessMixin,
  _ResourceSizeMixin,
  _TimersMixin,
  _UploadMixin,
  _UtilsMixin):

  def __init__(self, lib_name="",
               lib_ver="",
               config_file="",
               config_data={},
               base_folder=None,
               app_folder=None,
               show_time=True,
               config_file_encoding=None,
               no_folders_no_save=False,
               max_lines=None,
               HTML=False,
               DEBUG=True,
               data_config_subfolder=None,
               check_additional_configs=False,
               default_color='n',
               ):

    super(Logger, self).__init__(
      lib_name=lib_name, lib_ver=lib_ver,
      config_file=config_file,
      base_folder=base_folder,
      app_folder=app_folder,
      show_time=show_time,
      config_data=config_data,
      config_file_encoding=config_file_encoding,
      no_folders_no_save=no_folders_no_save,
      max_lines=max_lines,
      HTML=HTML,
      DEBUG=DEBUG,
      data_config_subfolder=data_config_subfolder,
      check_additional_configs=check_additional_configs,
      default_color=default_color,
    )
    self.cleanup_logs(archive_older_than_days=2)

    return

  def iP(self, str_msg, results=False, show_time=False, noprefix=False, color=None):
    if self.runs_from_ipython():
      return self._logger(
        str_msg,
        show=True, results=results, show_time=show_time,
        noprefix=noprefix, color=color
      )
    return

  def __repr__(self):
    # Get the name of the class
    class_name = self.__class__.__name__

    # Get public properties (those not starting with "_")
    public_properties = {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    # Convert properties to a string representation
    properties_str = ", ".join(f"{k}={v!r}" for k, v in public_properties.items())

    return f"{class_name}({properties_str})"


if __name__ == '__main__':
  l = Logger('TEST', base_folder='Dropbox', app_folder='_libraries_testdata')
  l.P("All check", color='green')
