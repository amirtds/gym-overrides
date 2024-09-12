from lms.djangoapps.certificates import api as certs_api
from lms.djangoapps.courseware.views.views import (
    _downloadable_cert_data,
    GENERATING_CERT_DATA,
    INVALID_CERT_DATA,
    REQUESTING_CERT_DATA,
    _earned_but_not_available_cert_data,
    _missing_required_verification,
    _unverified_cert_data,
)


def _downloadable_certificate_message(prev_fn, student, course, cert_downloadable_status):  # lint-amnesty, pylint: disable=missing-function-docstring
    if certs_api.has_html_certificates_enabled(course):
        if certs_api.get_active_web_certificate(course) is not None:
            return _downloadable_cert_data(
                download_url=None,
                cert_web_view_url=certs_api.get_certificate_url(
                    user_id=student.id, 
                    course_id=course.id, 
                    uuid=cert_downloadable_status['uuid']
                )
            )
        elif not cert_downloadable_status['is_pdf_certificate']:
            return GENERATING_CERT_DATA

    return _downloadable_cert_data(download_url=cert_downloadable_status['download_url'])

def _certificate_message(prev_fn, student, course, enrollment_mode):  # lint-amnesty, pylint: disable=missing-function-docstring
    if certs_api.is_certificate_invalidated(student, course.id):
        return INVALID_CERT_DATA

    cert_downloadable_status = certs_api.certificate_downloadable_status(student, course.id)

    if cert_downloadable_status.get('earned_but_not_available'):
        return _earned_but_not_available_cert_data(cert_downloadable_status)

    if cert_downloadable_status['is_generating']:
        return GENERATING_CERT_DATA

    if cert_downloadable_status['is_unverified'] or _missing_required_verification(student, enrollment_mode):
        return _unverified_cert_data()

    if cert_downloadable_status['is_downloadable']:
        return _downloadable_certificate_message(prev_fn, student, course, cert_downloadable_status)

    return REQUESTING_CERT_DATA