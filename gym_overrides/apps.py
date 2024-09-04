"""
App configuration for gym_overrides.
"""

from django.apps import AppConfig
from django.conf import settings
from edx_django_utils.plugins import PluginSettings, PluginURLs
try:
    from openedx.core.djangoapps.plugins.constants import ProjectType, SettingsType
    plugin_initiated = True
except ImportError:
    from django.utils.translation import gettext_noop as _
    plugin_initiated = False



EXTENSIONS_APP_NAME = 'gym_overrides'


class GymOverridesConfig(AppConfig):
    """
    gym-overrides configuration.
    """
    name = EXTENSIONS_APP_NAME
    verbose_name = 'gym-overrides'

    if plugin_initiated:
        # Class attribute that configures and enables this app as a Plugin App.
        plugin_app = {
            PluginURLs.CONFIG: {
                ProjectType.LMS: {
                    PluginURLs.NAMESPACE: EXTENSIONS_APP_NAME,
                    PluginURLs.APP_NAME: EXTENSIONS_APP_NAME,
                    PluginURLs.REGEX: r'^gym_overrides/',
                    PluginURLs.RELATIVE_PATH: 'urls',
                },
                ProjectType.CMS: {
                    PluginURLs.NAMESPACE: EXTENSIONS_APP_NAME,
                    PluginURLs.APP_NAME: EXTENSIONS_APP_NAME,
                    PluginURLs.REGEX: r'^gym_overrides/',
                    PluginURLs.RELATIVE_PATH: 'urls',
                }
            },

            PluginSettings.CONFIG: {
                ProjectType.LMS: {
                    SettingsType.COMMON: {
                        PluginSettings.RELATIVE_PATH: 'settings.common',
                    },
                    SettingsType.TEST: {
                        PluginSettings.RELATIVE_PATH: 'settings.test',
                    },
                    SettingsType.PRODUCTION: {
                        PluginSettings.RELATIVE_PATH: 'settings.production',
                    },
                },
                ProjectType.CMS: {
                    SettingsType.COMMON: {
                        PluginSettings.RELATIVE_PATH: 'settings.common',
                    },
                    SettingsType.TEST: {
                        PluginSettings.RELATIVE_PATH: 'settings.test',
                    },
                    SettingsType.PRODUCTION: {
                        PluginSettings.RELATIVE_PATH: 'settings.production',
                    },
                },
            },
        }

    def ready(self, *args, **kwargs):
        """
        Register signals on app loding.
        """
        from . import signals  # noqa: F401
