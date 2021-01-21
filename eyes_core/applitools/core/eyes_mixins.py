from applitools.common import Configuration, deprecated


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
    @deprecated.attribute("use `configure` instead")
    def configuration(self):
        return self.configure

    @configuration.setter
    @deprecated.attribute("use `set_configuration` instead")
    def configuration(self, configuration):
        self.set_configuration(configuration)
