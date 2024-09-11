from openedx.core.djangoapps.content.course_overviews.api import get_course_overview_or_none
from lms.djangoapps.certificates.utils import _safe_course_key, _certificate_download_url

def get_certificate_url(prev_fn, user_id=None, course_id=None, uuid=None, user_certificate=None):
    """
    Returns the certificate URL
    """
    url = ''

    course_overview = get_course_overview_or_none(_safe_course_key(course_id))
    if not course_overview:
        return url
    url = _certificate_download_url(user_id, course_id, user_certificate=user_certificate)
    return url