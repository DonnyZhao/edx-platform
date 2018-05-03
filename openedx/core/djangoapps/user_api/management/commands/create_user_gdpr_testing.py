from __future__ import unicode_literals

from datetime import datetime
from pytz import UTC

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from enterprise.models import EnterpriseCourseEnrollment, EnterpriseCustomerUser, PendingEnterpriseCustomerUser
from integrated_channels.sap_success_factors.models import SapSuccessFactorsLearnerDataTransmissionAudit

from consent.models import DataSharingConsent
from entitlements.models import CourseEntitlement, CourseEntitlementSupportDetail
from lms.djangoapps.verify_student.models import SoftwareSecurePhotoVerification
from openedx.core.djangoapps.course_groups.models import UnregisteredLearnerCohortAssignments
from student.models import (
    PendingEmailChange,
    UserProfile,
    CourseEnrollmentAllowed
)

from ..models import RetirementState, RetirementStateError, UserOrgTag, UserRetirementStatus


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '-u', '--username',
            nargs=1,
            required=False,
            help='Username'
        )

    def handle(self, *args, **options):
        """
        Execute the command.
        """

        username = options['username'] if options['username'] else 'gdpr_test_user'
        user = User.objects.create(
            user=username,
            email='gdpr_test_user@example.com'
        )

        # clear_pii_from_userprofile
        profile_image_uploaded_date = datetime.datetime(2018, 5, 3, tzinfo=UTC)
        UserProfile.objects.create(
            user=user,
            name='gdpr test name',
            meta='gdpr test meta',
            location='gdpr test location',
            year_of_birth='gdpr test year',
            gender='gdpr test gender',
            mailing_address='gdpr test mailing address',
            city='Boston',
            country='United States',
            bio='gdpr test bio',
            profile_image_uploaded_at=profile_image_uploaded_date,
            first_name="GDPR",
            last_name="Test",
            is_active=True,
        )

        # delete_users_profile_images
        # Need a way to upload a profile image?

        # retire_users_data_sharing_consent
        DataSharingConsent.objects.create(
            username=username,
        )

        # retire_sapsf_data_transmission
        enterprise_user = EnterpriseCustomerUser.objects.create(
            user_id=user.id
        )
        audit = EnterpriseCourseEnrollment.objects.create(
            enterprise_customer_user=enterprise_user
        )
        SapSuccessFactorsLearnerDataTransmissionAudit.objects.create(
            enterprise_course_enrollment_id=audit.id
        )

        # retire_user_from_pending_enterprise_customer_user
        PendingEnterpriseCustomerUser.objects.create(
            user_email=user.email
        )

        # retire_entitlement_support_detail
        CourseEntitlement.objects.create(
            user_id=user.id,

        )
        CourseEntitlementSupportDetail.objects.create(
            support_user=user,
            comments='bla bla test comments bla bla'
        )

        # Retire misc. models that may contain PII of this user
        SoftwareSecurePhotoVerification.objects.create(
            user=user,
            name='gdpr test',
            face_image_url='gdpr_test',
            photo_id_image_url='gdpr_test',
            photo_id_key='gdpr_test'
        )
        PendingEmailChange.objects.create(
            user=user
        )
        UserOrgTag.objects.create(
            email=user.email
        )

        # Retire any objects linked to the user via their original email
        CourseEnrollmentAllowed.objects.create(
            email=user.email
        )
        UnregisteredLearnerCohortAssignments.objects.create(
            email=user.email
        )