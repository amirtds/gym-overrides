def plugin_settings(settings):
    """
    Set of plugin settings used by the Open Edx platform.
    """
    settings.OVERRIDE_GENERATE_CERTIFICATE = 'gym_overrides.overrides.override_generate_certificate.generate_certificate'