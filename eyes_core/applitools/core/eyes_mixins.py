from typing import TYPE_CHECKING

from applitools.common import Configuration, MatchResult, logger
from applitools.core.fluent import CheckSettings

if TYPE_CHECKING:
    from typing import Optional


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


class EyesCheckMixin(object):
    _check_settings_cls = CheckSettings

    def check(self, name=None, check_settings=None, *args):
        checks = []
        if name and not isinstance(name, ("".__class__, u"".__class__)):
            checks.append(name)
            name = None
        if check_settings:
            checks.append(check_settings)
        if args:
            checks.extend(a for a in args if a)
        if not checks:
            checks = [self._check_settings_cls()]
        if name:
            checks[0] = checks[0].with_name(name)
        for check_settings in checks:
            res = self._check(check_settings)
        if len(checks) == 1:
            return res

    def _check(self, check_settings):
        # type: (*CheckSettings) -> Optional[MatchResult]
        pass
