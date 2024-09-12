from lms.djangoapps.certificates.data import CertificateStatuses
from common.djangoapps.student.helpers import _is_certificate_earned_but_not_available, process_survey_link
from xmodule.data import CertificatesDisplayBehaviors 
from common.djangoapps.course_modes.models import CourseMode
from lms.djangoapps.instructor import access
from lms.djangoapps.certificates.api import (
    has_self_generated_certificates_enabled,
    get_certificate_url,
    has_html_certificates_enabled,
    auto_certificate_generation_enabled,
)
from common.djangoapps.student.models import LinkedInAddToProfileConfiguration
from lms.djangoapps.grades.api import CourseGradeFactory
import logging

log = logging.getLogger(__name__)

DISABLE_UNENROLL_CERT_STATES = [
    'generating',
    'downloadable',
]

def _cert_info(prev_fn, user, enrollment, cert_status):
    """
    Implements the logic for cert_info -- split out for testing.

    TODO: replace with a method that lives in the certificates app and combines this logic with
     lms.djangoapps.certificates.api.can_show_certificate_message and
     lms.djangoapps.courseware.views.get_cert_data

    Arguments:
        user (User): A user.
        enrollment (CourseEnrollment): A course enrollment.
        cert_status (dict): dictionary containing information about certificate status for the user

    Returns:
        dictionary containing:
            'status': one of 'generating', 'downloadable', 'notpassing', 'restricted', 'auditing',
                'processing', 'unverified', 'unavailable', or 'certificate_earned_but_not_available'
            'show_survey_button': bool
            'can_unenroll': if status allows for unenrollment

        The dictionary may also contain:
            'linked_in_url': url to add cert to LinkedIn profile
            'survey_url': url, only if course_overview.end_of_course_survey_url is not None
            'show_cert_web_view': bool if html web certs are enabled and there is an active web cert
            'cert_web_view_url': url if html web certs are enabled and there is an active web cert
            'download_url': url to download a cert
            'grade': if status is in 'generating', 'downloadable', 'notpassing', 'restricted',
                'auditing', or 'unverified'
    """
    # simplify the status for the template using this lookup table
    template_state = {
        CertificateStatuses.generating: 'generating',
        CertificateStatuses.downloadable: 'downloadable',
        CertificateStatuses.notpassing: 'notpassing',
        CertificateStatuses.restricted: 'restricted',
        CertificateStatuses.auditing: 'auditing',
        CertificateStatuses.audit_passing: 'auditing',
        CertificateStatuses.audit_notpassing: 'auditing',
        CertificateStatuses.unverified: 'unverified',
    }

    certificate_earned_but_not_available_status = 'certificate_earned_but_not_available'
    default_status = 'processing'

    default_info = {
        'status': default_status,
        'show_survey_button': False,
        'can_unenroll': True,
    }

    if cert_status is None or enrollment is None:
        return default_info

    course_overview = enrollment.course_overview if enrollment else None
    status = template_state.get(cert_status['status'], default_status)
    is_hidden_status = status in ('processing', 'generating', 'notpassing', 'auditing')

    if _is_certificate_earned_but_not_available(course_overview, status):
        status = certificate_earned_but_not_available_status

    if (
        course_overview.certificates_display_behavior == CertificatesDisplayBehaviors.EARLY_NO_INFO and
        is_hidden_status
    ):
        return default_info

    if not CourseMode.is_eligible_for_certificate(enrollment.mode, status=status):
        return default_info

    if course_overview and access.is_beta_tester(user, course_overview.id):
        # Beta testers are not eligible for a course certificate
        return default_info

    status_dict = {
        'status': status,
        'mode': cert_status.get('mode', None),
        'linked_in_url': None,
        'can_unenroll': status not in DISABLE_UNENROLL_CERT_STATES,
    }

    if status != default_status and course_overview.end_of_course_survey_url is not None:
        status_dict.update({
            'show_survey_button': True,
            'survey_url': process_survey_link(course_overview.end_of_course_survey_url, user)})
    else:
        status_dict['show_survey_button'] = False

    if status == 'downloadable':
        # showing the certificate web view button if certificate is downloadable state and feature flags are enabled.
        if has_html_certificates_enabled(course_overview):
            if course_overview.has_any_active_web_certificate:
                status_dict.update({
                    'show_cert_web_view': True,
                    'cert_web_view_url': get_certificate_url(user_id=user.id, course_id=course_overview.id, uuid=cert_status['uuid'])
                })
            elif cert_status['download_url']:
                status_dict['download_url'] = cert_status['download_url']
            else:
                # don't show download certificate button if we don't have an active certificate for course
                status_dict['status'] = 'unavailable'
        elif 'download_url' not in cert_status:
            log.warning(
                "User %s has a downloadable cert for %s, but no download url",
                user.username,
                course_overview.id
            )
            return default_info
        else:
            status_dict['download_url'] = cert_status['download_url']

            # If enabled, show the LinkedIn "add to profile" button
            # Clicking this button sends the user to LinkedIn where they
            # can add the certificate information to their profile.
            linkedin_config = LinkedInAddToProfileConfiguration.current()
            if linkedin_config.is_enabled():
                status_dict['linked_in_url'] = linkedin_config.add_to_profile_url(
                    course_overview.display_name, cert_status.get('mode'), cert_status['download_url'],
                )

    if status in {'generating', 'downloadable', 'notpassing', 'restricted', 'auditing', 'unverified'}:
        cert_grade_percent = -1
        persisted_grade_percent = -1
        persisted_grade = CourseGradeFactory().read(user, course=course_overview, create_if_needed=False)
        if persisted_grade is not None:
            persisted_grade_percent = persisted_grade.percent

        if 'grade' in cert_status:
            cert_grade_percent = float(cert_status['grade'])

        if cert_grade_percent == -1 and persisted_grade_percent == -1:
            # Note: as of 11/20/2012, we know there are students in this state-- cs169.1x,
            # who need to be regraded (we weren't tracking 'notpassing' at first).
            # We can add a log.warning here once we think it shouldn't happen.
            return default_info
        grades_input = [cert_grade_percent, persisted_grade_percent]
        max_grade = (
            None
            if all(grade is None for grade in grades_input)
            else max(filter(lambda x: x is not None, grades_input))
        )
        status_dict['grade'] = str(max_grade)

        # If the grade is passing, the status is one of these statuses, and request certificate
        # is enabled for a course then we need to provide the option to the learner
        cert_gen_enabled = (
            has_self_generated_certificates_enabled(course_overview.id) or
            auto_certificate_generation_enabled()
        )
        passing_grade = persisted_grade and persisted_grade.passed
        if (
            status_dict['status'] != CertificateStatuses.downloadable and
            cert_gen_enabled and
            passing_grade and
            course_overview.has_any_active_web_certificate
        ):
            status_dict['status'] = CertificateStatuses.requesting

    return status_dict