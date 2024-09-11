from lms.djangoapps.certificates.data import CertificateStatuses
from lms.djangoapps.certificates.models import GeneratedCertificate

def certificate_status(prev_fn, generated_certificate):
    """
    This returns a dictionary with a key for status, and other information.

    If the status is "downloadable", the dictionary also contains
    "download_url".

    If the student has been graded, the dictionary also contains their
    grade for the course with the key "grade".
    """
    # Import here instead of top of file since this module gets imported before
    # the course_modes app is loaded, resulting in a Django deprecation warning.
    from common.djangoapps.course_modes.models import CourseMode  # pylint: disable=redefined-outer-name, reimported

    if generated_certificate:
        cert_status = {
            'status': generated_certificate.status,
            'mode': generated_certificate.mode,
            'uuid': generated_certificate.verify_uuid,
        }
        if generated_certificate.grade:
            cert_status['grade'] = generated_certificate.grade

        if generated_certificate.status == CertificateStatuses.downloadable:
            cert_status['download_url'] = generated_certificate.download_url

        return cert_status
    else:
        return {'status': CertificateStatuses.unavailable, 'mode': GeneratedCertificate.MODES.honor, 'uuid': None}
