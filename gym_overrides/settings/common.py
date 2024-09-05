import logging

log = logging.getLogger(__name__)

def plugin_settings(settings):
    """
    Set of plugin settings used by the Open Edx platform.
    """
    log.info("Gym Overrides plugin settings loaded")
    settings.OVERRIDE_IS_PASSING_STATUS = 'gym_overrides.overrides.override_is_passing_status.is_passing_status'
    settings.OVERRIDE_GENERATE_CERTIFICATE = 'gym_overrides.overrides.override_generate_certificate._generate_certificate'
    settings.OVERRIDE_TRACK_USER_REGISTRATION = 'gym_overrides.overrides.override_track_user_registration.override_track_user_registration'
    settings.OVERRIDE_IS_ELIGIBLE_FOR_CERTIFICATE = 'gym_overrides.overrides.override_is_eligible_for_certificate.is_eligible_for_certificate'