import logging

logger = logging.getLogger(__name__)

def is_eligible_for_certificate(mode_slug, status=None):
    """
    Make all modes eligible for certificates
    """
    logger.info(f"is_eligible_for_certificate called with mode_slug={mode_slug}, status={status}")
    return True