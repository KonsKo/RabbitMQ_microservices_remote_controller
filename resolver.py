"""Resolve string PwshCommand response."""
import logging
import re
from typing import Optional

from service_framework.share_files.preferences_model import MpPreferencesModel

logger = logging.getLogger(__name__)


def get_mp_prefs_list() -> list:
    """
    Get list of preferences from schema.

    Returns:
        preferences (list): list of preferences

    Raises:
        ValueError: if could not get list

    """
    try:
        return list(
            MpPreferencesModel.schema()['properties'].keys(),
        )
    except Exception as exc_model:
        logger.exception(
            'Could not load preference from model. {0}'.format(
                exc_model,
            ),
        )
        raise ValueError


def get_status_pref_list() -> list:
    """
    Set up list of fields for MpComputerStatus.

    Returns:
        fields (list): list of chosen fields

    """
    return [
        'AntivirusSignatureLastUpdated',
        'AntivirusSignatureVersion',
        'AntivirusEnabled',
    ]


get_prefs_list = {
    'Get-MpPreference': get_mp_prefs_list,
    'Get-MpComputerStatus': get_status_pref_list,
}


def resolve_preferences(raw_prefs: str, event: str) -> Optional[list]:
    """
    Pars raw preferences and scrap values.

    Args:
        raw_prefs (str): raw string with preferences
        event (str): event name

    Returns:
        parsed_prefs (list): parsed prefs if success

    """
    parsed_prefs = []

    for pref in get_prefs_list.get(event)():
        pattern = r'{name}\s*\:\s(.+)\n'.format(name=pref)
        rslt = re.search(str(pattern), str(raw_prefs))

        if rslt:
            tmp_value = rslt.group(1).replace(
                '{', '',
            ).replace(
                '}', '',
            ).strip().rstrip()
            if tmp_value.isdigit():
                tmp_value = hex(int(tmp_value))
            parsed_prefs.append(
                {
                    'pref_name': pref,
                    'pref_val': tmp_value,
                },
            )

    return parsed_prefs
