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
    settings.OVERRIDE_CERTIFICATE_STATUS = 'gym_overrides.overrides.override_certificate_status.certificate_status'
    settings.OVERRIDE_GET_CERTIFICATE_URL = 'gym_overrides.overrides.override_get_certificate_url.get_certificate_url'
    settings.OVERRIDE_CERT_INFO = 'gym_overrides.overrides.override_cert_info._cert_info'