from lms.djangoapps.certificates.models import GeneratedCertificate
from lms.djangoapps.certificates.utils import get_preferred_certificate_name
from lms.djangoapps.courseware import courses
from xmodule.modulestore.django import modulestore
from common.djangoapps.student.models.user import UserProfile
from django.conf import settings

from uuid import uuid4
import logging
import requests
import json
import re
from html import unescape


log = logging.getLogger(__name__)

def strip_html(text):
    # Remove HTML tags
    text = re.sub('<[^<]+?>', '', text)
    # Unescape HTML entities
    text = unescape(text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text

def generate_accredible_certificate(user, course_id, status, course_grade):
    try:
        course = courses.get_course_by_id(course_id)
        description = get_course_description(course)
        approve = status != "generating"
        profile = UserProfile.objects.get(user=user)
        
        payload = {
            "credential": {
                "name": course.display_name or str(course_id),
                "group_name": course.display_name or str(course_id),
                "description": strip_html(description),
                "achievement_id": str(course_id),
                "course_link": f"/courses/{course_id}/about",
                "approve": approve,
                "template_name": str(course_id),
                "grade": int(float(course_grade) * 100),
                "recipient": {
                    "name": profile.name,
                    "email": user.email
                }
            }
        }

        response = requests.post(
            'https://api.accredible.com/v1/credentials',
            json=payload,
            headers={
                'Authorization': f'Token token={settings.ACCREDIBLE_API_KEY}',
                'Content-Type': 'application/json'
            }
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        log.error(f"Error generating Accredible certificate: {str(e)}")
        return {"status": "error", "message": str(e)}

def get_course_description(course):
    for section_key in ['short_description', 'description', 'overview']:
        loc = course.location.replace(category='about', name=section_key)
        try:
            item = modulestore().get_item(loc)
            if item.data:
                return item.data
        except Exception as e:
            log.warning(f"Error getting {section_key} for course {course.id}: {str(e)}")
    return "No course description available"

def _generate_certificate(prev_fn, user, course_key, status, enrollment_mode, course_grade):
    """
    Generate a certificate for this user, in this course run.

    This method takes things like grade and enrollment mode as parameters because these are used to determine if the
    user is eligible for a certificate, and they're also saved in the cert itself. We want the cert to reflect the
    values that were used when determining if it was eligible for generation.
    """
    # Retrieve the existing certificate for the learner if it exists
    existing_certificate = GeneratedCertificate.certificate_for_student(user, course_key)

    preferred_name = get_preferred_certificate_name(user)

    # Retain the `verify_uuid` from an existing certificate if possible, this will make it possible for the learner to
    # keep the existing URL to their certificate
    if existing_certificate and existing_certificate.verify_uuid:
        uuid = existing_certificate.verify_uuid
    else:
        uuid = uuid4().hex

    # Generate Accredible certificate
    accredible_result = generate_accredible_certificate(user, course_key, status, course_grade)
    
    if accredible_result.get("status") == "error":
        log.error(f"Failed to generate Accredible certificate: {accredible_result.get('message')}")
        error_reason = f"Accredible certificate generation failed: {accredible_result.get('message')}"
        status = "error"
    else:
        log.info(f"Accredible certificate generated successfully for user {user.id} in course {course_key}")
        error_reason = ""

    credential_id = accredible_result.get("credential", {}).get("id")
    private_key = accredible_result.get("private_key")

    if credential_id:
        download_url = f"https://www.credential.net/{credential_id}"
        if private_key:
            download_url += f"?key={private_key}"
    else:
        download_url = ""

    cert, created = GeneratedCertificate.objects.update_or_create(
        user=user,
        course_id=course_key,
        defaults={
            'user': user,
            'course_id': course_key,
            'mode': enrollment_mode,
            'name': preferred_name,
            'status': status,
            'grade': course_grade,
            'download_url': download_url,
            'key': credential_id or '',
            'verify_uuid': uuid,
            'error_reason': error_reason
        }
    )

    if created:
        created_msg = 'Certificate was created.'
    else:
        created_msg = 'Certificate already existed and was updated.'
    log.info(f'Generated Accredible certificate with status {cert.status}, mode {cert.mode} and grade {cert.grade} for {user.id} '
             f': {course_key}. {created_msg}')
    return cert