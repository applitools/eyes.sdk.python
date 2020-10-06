from applitools.common import Configuration, logger
from applitools.common.utils.compat import basestring

_not_provided = object()


class EyesConfigurationMixin(object):
    _config_cls = Configuration

    def __init__(self):
        self._config_provider = self._config_cls()

    def get_configuration(self):
        # type:() -> Configuration
        """Returns clone of configuration instance"""
        if isinstance(self._config_provider, self._config_cls):
            return self._config_provider.clone()
        return self._config_provider.configure.clone()

    def set_configuration(self, configuration):
        # type:(Configuration) -> None
        """Clone configuration instance and set it"""
        old_configuration = self._config_provider
        if isinstance(old_configuration, self._config_cls):
            new_configuration = configuration.clone()
            if old_configuration.api_key and not configuration.api_key:
                new_configuration.api_key = old_configuration.api_key
            if old_configuration.server_url and not configuration.server_url:
                new_configuration.server_url = old_configuration.server_url
            self._config_provider = new_configuration
        else:
            self._config_provider = configuration

    @property
    def configure(self):
        # type:() -> Configuration
        if isinstance(self._config_provider, self._config_cls):
            return self._config_provider
        return self._config_provider.configure

    @property
    def configuration(self):
        logger.deprecation("`configuration` is deprecated. Use `configure` instead")
        return self.configure

    @configuration.setter
    def configuration(self, configuration):
        logger.deprecation(
            "Assign to `configuration` is deprecated. "
            "Use `set_configuration` instead"
        )
        self.set_configuration(configuration)


def merge_check_arguments(
    settings_class,
    check_settings_or_name=None,
    check_settings=_not_provided,
    name=None,
):
    """
    Merge mandatory check_settings and optional name arguments into check_settings.
    Name argument might come first.
    """
    if isinstance(check_settings_or_name, settings_class):
        if check_settings is not _not_provided:
            raise ValueError("Check settings should be provided once")
        check_settings = check_settings_or_name
    elif isinstance(check_settings_or_name, basestring):
        if name is not None:
            raise ValueError("Name might be provided only once")
        name = check_settings_or_name
    if check_settings is _not_provided:
        raise ValueError("Check settings should be provided")
    elif check_settings is None:
        check_settings = settings_class()
    if name:
        check_settings = check_settings.with_name(name)
    return check_settings
