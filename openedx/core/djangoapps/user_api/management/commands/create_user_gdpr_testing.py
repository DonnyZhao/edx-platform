from __future__ import unicode_literals

from datetime import datetime
from pytz import UTC

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from consent.models import DataSharingConsent
from enterprise.models import (
    EnterpriseCourseEnrollment,
    EnterpriseCustomer,
    EnterpriseCustomerUser,
    PendingEnterpriseCustomerUser,
)
from entitlements.models import CourseEntitlement, CourseEntitlementSupportDetail
from integrated_channels.sap_success_factors.models import SapSuccessFactorsLearnerDataTransmissionAudit
from lms.djangoapps.verify_student.models import SoftwareSecurePhotoVerification
from openedx.core.djangoapps.course_groups.models import UnregisteredLearnerCohortAssignments
from openedx.core.djangoapps.profile_images.images import create_profile_images
from openedx.core.djangoapps.profile_images.tests.helpers import make_image_file
from student.models import (
    PendingEmailChange,
    UserProfile,
    CourseEnrollmentAllowed
)

from ...models import UserOrgTag


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '-u', '--username',
            nargs=1,
            required=False,
            help='Username'
        )
        parser.add_argument(
            '-e', '--email',
            nargs=1,
            required=False,
            help='Email'
        )

    def handle(self, *args, **options):
        """
        Execute the command.
        """

        username = options['username'] if options['username'] else 'gdpr_test_user_bla'
        email = options['email'] if options['email'] else 'gdpr_test_user_bla@example.com'

        user, __ = User.objects.get_or_create(
            username=username,
            email=email,
            first_name="GDPR",
            last_name="Test",
            is_active=True,
            password='gdpr test password'
        )

        # UserProfile
        profile_image_uploaded_date = datetime(2018, 5, 3, tzinfo=UTC)
        UserProfile.objects.get_or_create(
            user=user,
            name='gdpr test name',
            meta='gdpr test meta',
            location='gdpr test location',
            year_of_birth=1950,
            gender='gdpr test gender',
            mailing_address='gdpr test mailing address',
            city='Boston',
            country='United States',
            bio='gdpr test bio',
            profile_image_uploaded_at=profile_image_uploaded_date,
        )

        # Profile images
        with make_image_file() as image_file:
            create_profile_images(
                image_file,
                {10: "ten.jpg"}
            )

        # DataSharingConsent
        enterprise_customer = EnterpriseCustomer.objects.get_or_create(
            name='test gdpr enterprise customer',
            #enforce_data_sharing_consent='At Enrollment',
        )
        DataSharingConsent.objects.get_or_create(
            username=username,
            enterprise_customer_id=enterprise_customer.uuid
        )

        # Sapsf data transmission
        enterprise_customer_user = EnterpriseCustomerUser.objects.get_or_create(
            user_id=user.id
        )
        audit = EnterpriseCourseEnrollment.objects.get_or_create(
            enterprise_customer_user=enterprise_customer_user
        )
        SapSuccessFactorsLearnerDataTransmissionAudit.objects.get_or_create(
            enterprise_course_enrollment_id=audit.id
        )

        # PendingEnterpriseCustomerUser
        PendingEnterpriseCustomerUser.objects.get_or_create(
            user_email=user.email
        )

        # EntitlementSupportDetail
        CourseEntitlement.objects.get_or_create(
            user_id=user.id,

        )
        CourseEntitlementSupportDetail.objects.get_or_create(
            support_user=user,
            comments='bla bla test comments bla bla'
        )

        # Misc. models that may contain PII of this user
        SoftwareSecurePhotoVerification.objects.get_or_create(
            user=user,
            name='gdpr test',
            face_image_url='gdpr_test',
            photo_id_image_url='gdpr_test',
            photo_id_key='gdpr_test'
        )
        PendingEmailChange.objects.get_or_create(
            user=user
        )
        UserOrgTag.objects.get_or_create(
            email=user.email
        )

        # Objects linked to the user via their original email
        CourseEnrollmentAllowed.objects.get_or_create(
            email=user.email
        )
        UnregisteredLearnerCohortAssignments.objects.get_or_create(
            email=user.email
        )