
from django.conf import settings
import datetime
from pytz import UTC
from common.djangoapps.track import segment
import logging

logger = logging.getLogger(__name__)

def override_track_user_registration(prev_fn, user, profile, params, third_party_provider, registration, is_marketable):
    """ Track the user's registration. """
    if hasattr(settings, 'LMS_SEGMENT_KEY') and settings.LMS_SEGMENT_KEY:
        try:
            market = user.extrainfo.market
            extrainfo = {'market': market}
        except Exception as e:
            logger.exception("Exception in extrainfo_dict: %s", e)
            extrainfo = ''
        traits = {
            'email': user.email,
            'username': user.username,
            'name': profile.name,
            # Mailchimp requires the age & yearOfBirth to be integers, we send a sane integer default if falsey.
            'age': profile.age or -1,
            'yearOfBirth': profile.year_of_birth or datetime.datetime.now(UTC).year,
            'education': profile.level_of_education_display,
            'address': profile.mailing_address,
            'gender': profile.gender_display,
            'country': str(profile.country),
            'is_marketable': is_marketable,
            'extrainfo': extrainfo
        }
        if settings.MARKETING_EMAILS_OPT_IN and params.get('marketing_emails_opt_in'):
            email_subscribe = 'subscribed' if is_marketable else 'unsubscribed'
            traits['email_subscribe'] = email_subscribe

        # .. pii: Many pieces of PII are sent to Segment here. Retired directly through Segment API call in Tubular.
        # .. pii_types: email_address, username, name, birth_date, location, gender
        # .. pii_retirement: third_party
        segment.identify(user.id, traits)
        properties = {
            'category': 'conversion',
            # ..pii: Learner email is sent to Segment in following line and will be associated with analytics data.
            'email': user.email,
            'label': params.get('course_id'),
            'provider': third_party_provider.name if third_party_provider else None,
            'is_gender_selected': bool(profile.gender_display),
            'is_year_of_birth_selected': bool(profile.year_of_birth),
            'is_education_selected': bool(profile.level_of_education_display),
            'is_goal_set': bool(profile.goals),
            'total_registration_time': round(float(params.get('totalRegistrationTime', '0'))),
            'activation_key': registration.activation_key if registration else None,
            'host': params.get('host', ''),
            'utm_campaign': params.get('utm_campaign', ''),
        }
        # VAN-738 - added below properties to experiment marketing emails opt in/out events on Braze.
        if params.get('marketing_emails_opt_in') and settings.MARKETING_EMAILS_OPT_IN:
            properties['marketing_emails_opt_in'] = is_marketable

        # DENG-803: For segment events forwarded along to Hubspot, duplicate the `properties` section of
        # the event payload into the `traits` section so that they can be received. This is a temporary
        # fix until we implement this behavior outside of the LMS.
        # TODO: DENG-805: remove the properties duplication in the event traits.
        segment_traits = dict(properties)
        segment_traits['user_id'] = user.id
        segment_traits['joined_date'] = user.date_joined.strftime("%Y-%m-%d")
        segment_traits['market'] = extrainfo if extrainfo else None
        segment.track(
            user.id,
            "edx.bi.user.account.registered",
            properties=properties,
            traits=segment_traits,
        )