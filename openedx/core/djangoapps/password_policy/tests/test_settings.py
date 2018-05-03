"""
Test password policy settings
"""

from dateutil.parser import parse as parse_date
from django.test import TestCase
from mock import patch

from ..settings import parse_dates


class TestSettings(TestCase):
    """
    Tests plugin settings
    """

    @patch('openedx.core.djangoapps.password_policy.settings.log')
    def test_get_compliance_deadline_for_user_misconfiguration(self, mock_log):
        """
        Test that we gracefully handle misconfigurations
        """
        config = parse_dates({
            'STAFF_USER_COMPLIANCE_DEADLINE': 'foo',
            'GENERAL_USER_COMPLIANCE_DEADLINE': '2018-03-03 00:00:00+00:00'
        })
        self.assertEqual(mock_log.exception.call_count, 1)
        self.assertIsNone(config['STAFF_USER_COMPLIANCE_DEADLINE'])
        self.assertEqual(parse_date('2018-03-03 00:00:00+00:00'), config['GENERAL_USER_COMPLIANCE_DEADLINE'])
