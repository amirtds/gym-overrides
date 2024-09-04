"""
Provides application configuration for Gym Overrides.
As well as default values for running Gym Overrides along with functions to
add entries to the Django conf settings needed to run Gym Overrides.
"""

from django.apps import AppConfig
from edx_django_utils.plugins.constants import (
    PluginURLs, PluginSettings
)
from openedx.core.djangoapps.plugins.constants import (
    ProjectType, SettingsType
)


class GymOverridesConfig(AppConfig):
    """
    Provides application configuration for Gym Overrides.
    """

    name = 'gym_overrides'
    verbose_name = 'gym_overrides'

    plugin_app = {
        PluginURLs.CONFIG: {
            ProjectType.LMS: {
                PluginURLs.NAMESPACE: u'gym_overrides',
                PluginURLs.REGEX: u'^gym_overrides/',
                PluginURLs.RELATIVE_PATH: u'urls',
            }
        },
        PluginSettings.CONFIG: {
            ProjectType.LMS: {
                SettingsType.COMMON: {
                    PluginSettings.RELATIVE_PATH: u'settings.common'
                },
            }
        }
    }
