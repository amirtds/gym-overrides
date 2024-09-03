def plugin_settings(settings):
    """
    Set of plugin settings used by the Open Edx platform.
    """
    settings.OVERRIDE_GENERATE_CERTIFICATE = 'gym_overrides.overrides.override_generate_certificate.generate_certificate'
    settings.OVERRIDE_TRACK_USER_REGISTRATION = 'gym_overrides.overrides.override_track_user_registration.override_track_user_registration'
    settings.OVERRIDE_IS_ELIGIBLE_FOR_CERTIFICATE = 'gym_overrides.overrides.override_is_eligible_for_certificate.is_eligible_for_certificate'