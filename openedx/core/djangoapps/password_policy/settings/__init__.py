"""
Helper functions for settings
"""

import logging
from dateutil.parser import parse as parse_date

log = logging.getLogger(__name__)


def parse_dates(config_in):
    """
    Convert the string dates in a config file to datetime.datetime versions, logging any issues.
    """
    config = dict(config_in)
    _update_date_safely(config, 'STAFF_USER_COMPLIANCE_DEADLINE')
    _update_date_safely(config, 'ELEVATED_PRIVILEGE_USER_COMPLIANCE_DEADLINE')
    _update_date_safely(config, 'GENERAL_USER_COMPLIANCE_DEADLINE')
    return config


def _update_date_safely(config, setting):
    """
    Updates a parsed datetime.datetime object for a given config setting name.
    """
    deadline = config.get(setting)
    try:
        if deadline:
            config[setting] = parse_date(deadline)
    except (ValueError, OverflowError):
        log.exception("Could not parse %s password policy rollout value of '%s'.", setting, deadline)
        config[setting] = None
