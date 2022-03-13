"""Module to implement data model for Windows Defender commands."""
import datetime
from typing import Any, Dict, List, Optional, Type, Union

from pydantic import BaseModel, validator

from service_framework.share_files import pwsh_commands

VALUE_ERROR = 'Wrong value. Acceptable values are: {0}'

ScanDirection = {
    0: 'Both',
    1: 'Incoming',
    2: 'Outcoming',
}

ScanTypePref = {
    1: 'QuickScan',
    2: 'FullScan',
}

MAPSRepType = {
    0: 'Disabled',
    1: 'Basic',
    2: 'Advanced',
}

SubmitSempCons = {
    0: 'AlwaysPrompt',
    1: 'SendSafeSamples',
    2: 'NeverSend',
    3: 'SendAllSamples',
}

ThreatAction = {
    1: 'Clean',
    2: 'Quarantine',
    3: 'Remove',
    6: 'Allow',
    8: 'UserDefined',
    9: 'NoAction',
    10: 'Block',
}

PUAProtType = {
    0: 'Disabled',
    1: 'Enabled',
    2: 'AuditMode',
}


UpdatesChType = {
    0: 'NotConfigured',
    2: 'Beta',
    3: 'Preview',
    4: 'Staged',
    5: 'Broad',
}

Day = {
    0: 'Everyday',
    1: 'Sunday',
    2: 'Monday',
    3: 'Tuesday',
    4: 'Wednesday',
    5: 'Thursday',
    6: 'Friday',
    7: 'Saturday',
    8: 'Never',
}

UpdateSource = {
    0: 'InternalDefinitionUpdateServer',
    1: 'MicrosoftUpdateServer',
    2: 'MMPC',
    3: 'FileShares',
}

ScanType = {
    1: 'FullScan',
    2: 'QuickScan',
    3: 'CustomScan',
}


def to_camel(parameter: str) -> str:
    """
    Make string from snake to camel notation.

    Args:
        parameter (str): target to change

    Returns:
        changed parameter (str)

    """
    to_list = [word.capitalize() for word in parameter.split('_')]
    if '' in to_list:
        to_list = ['_' if element == '' else element for element in to_list]
    return ''.join(to_list)


class BaseParameters(BaseModel):
    """Base Preferences class."""

    cim_session: Optional[str]
    throttle_limit: Optional[int]
    as_job: Optional[Any]

    class Config(object):     # noqa:WPS431
        """Pydantic model settings."""

        alias_generator = to_camel
        extra = 'forbid'

    @validator('as_job')
    def _convert_as_job(cls, f_value):     # noqa:N805 ,pydantic requirements
        return ''

    @validator('*')
    def _convert_bool(cls, f_value):     # noqa:N805 ,pydantic requirements
        if isinstance(f_value, bool):
            f_value = '${0}'.format(f_value)     # bool format MS
        return f_value


class MpPreferencesModel(BaseParameters):     # noqa:WPS214
    """Windows Defender preferences class."""

    exclusion_path: Optional[str]
    exclusion_extension: Optional[str]
    exclusion_process: Optional[str]
    real_time_scan_direction: Optional[Union[int, str]]
    quarantine_purge_items_after_delay: Optional[int]
    remediation_schedule_day: Optional[Union[int, str]]
    remediation_schedule_time: Optional[datetime.time]
    reporting_additional_action_time_out: Optional[int]
    reporting_critical_failure_time_out: Optional[int]
    reporting_non_critical_time_out: Optional[int]
    scan_avg_c_p_u_load_factor: Optional[int]
    check_for_signatures_before_running_scan: Optional[bool]
    scan_purge_items_after_delay: Optional[int]
    scan_only_if_idle_enabled: Optional[bool]
    scan_parameters: Optional[Union[int, str]]
    scan_schedule_day: Optional[Union[int, str]]
    scan_schedule_quick_scan_time: Optional[datetime.time]
    scan_schedule_time: Optional[datetime.time]
    signature_first_au_grace_period: Optional[int]
    signature_au_grace_period: Optional[int]
    signature_definition_update_file_shares_sources: Optional[str]
    signature_disable_update_on_startup_without_engine: Optional[bool]
    signature_fallback_order: Optional[str]
    signature_schedule_day: Optional[Union[int, str]]
    signature_schedule_time: Optional[datetime.time]
    signature_update_catchup_interval: Optional[int]
    signature_update_interval: Optional[int]
    m_a_p_s_reporting: Optional[Union[int, str]]
    submit_samples_consent: Optional[Union[int, str]]
    disable_auto_exclusions: Optional[bool]
    disable_privacy_mode: Optional[bool]
    randomize_schedule_task_times: Optional[bool]
    disable_behavior_monitoring: Optional[bool]
    disable_i_o_a_v_protection: Optional[bool]
    disable_realtime_monitoring: Optional[bool]
    disable_script_scanning: Optional[bool]
    disable_archive_scanning: Optional[bool]
    disable_catchup_full_scan: Optional[bool]
    disable_catchup_quick_scan: Optional[bool]
    disable_cpu_throttle_on_idle_scans: Optional[bool]
    disable_email_scanning: Optional[bool]
    disable_removable_drive_scanning: Optional[bool]
    disable_restore_point: Optional[bool]
    disable_scanning_mapped_network_drives_for_full_scan: Optional[bool]
    disable_scanning_network_files: Optional[bool]
    u_i_lockdown: Optional[bool]
    threat_i_d_default_action__ids: Optional[int]
    threat_i_d_default_action__actions: Optional[Union[int, str]]
    unknown_threat_default_action: Optional[Union[int, str]]
    low_threat_default_action: Optional[Union[int, str]]
    moderate_threat_default_action: Optional[Union[int, str]]
    high_threat_default_action: Optional[Union[int, str]]
    severe_threat_default_action: Optional[Union[int, str]]
    disable_block_at_first_seen: Optional[bool]
    p_u_a_protection: Optional[Union[int, str]]
    throttle_limit: Optional[int]
    definition_updates_channel: Optional[Union[int, str]]  # ex signature
    engine_updates_channel: Optional[Union[int, str]]
    platform_updates_channel: Optional[Union[int, str]]

    @validator('real_time_scan_direction')
    def _real_time_scan_direction_valid(cls, f_value):
        acceptable = set(ScanDirection.keys()) | set(ScanDirection.values())
        if f_value not in acceptable:
            raise ValueError(
                VALUE_ERROR.format(
                    ScanDirection,
                ),
            )
        return f_value

    @validator('scan_parameters')
    def _scan_parameters_valid(cls, f_value):
        acceptable = set(ScanTypePref.keys()) | set(ScanTypePref.values())
        if f_value not in acceptable:
            raise ValueError(
                VALUE_ERROR.format(
                    ScanTypePref,
                ),
            )
        return f_value

    @validator('m_a_p_s_reporting')
    def _maps_reporting_valid(cls, f_value):
        acceptable = set(MAPSRepType.keys()) | set(MAPSRepType.values())
        if f_value not in acceptable:
            raise ValueError(
                VALUE_ERROR.format(
                    MAPSRepType,
                ),
            )
        return f_value

    @validator('submit_samples_consent')
    def _submit_samples_consent_valid(cls, f_value):
        acceptable = set(SubmitSempCons.keys()) | set(SubmitSempCons.values())
        if f_value not in acceptable:
            raise ValueError(
                VALUE_ERROR.format(
                    SubmitSempCons,
                ),
            )
        return f_value

    @validator(
        'threat_i_d_default_action__actions',
        'unknown_threat_default_action',
        'low_threat_default_action',
        'moderate_threat_default_action',
        'high_threat_default_action',
        'severe_threat_default_action',
    )
    def _threat_action_valid(cls, f_value):
        acceptable = set(ThreatAction.keys()) | set(ThreatAction.values())
        if f_value not in acceptable:
            raise ValueError(
                VALUE_ERROR.format(
                    ThreatAction,
                ),
            )
        return f_value

    @validator('p_u_a_protection')
    def _pua_protection_valid(cls, f_value):
        acceptable = set(PUAProtType.keys()) | set(PUAProtType.values())
        if f_value not in acceptable:
            raise ValueError(
                VALUE_ERROR.format(
                    PUAProtType,
                ),
            )
        return f_value

    @validator(
        'engine_updates_channel',
        'platform_updates_channel',
    )
    def _updates_channel_type_valid(cls, f_value):
        acceptable = set(UpdatesChType.keys()) | set(UpdatesChType.values())
        if f_value not in acceptable:
            raise ValueError(
                VALUE_ERROR.format(
                    UpdatesChType,
                ),
            )
        return f_value

    @validator('definition_updates_channel')
    def _updates_channel_type_valid_part(cls, f_value):
        acceptable = {0, 'NotConfigured', 4, 'Staged', 5, 'Broad'}
        if f_value not in acceptable:
            raise ValueError(
                VALUE_ERROR.format(
                    acceptable,
                ),
            )
        return f_value

    @validator(
        'remediation_schedule_day',
        'scan_schedule_day',
        'signature_schedule_day',
    )
    def _day_valid(cls, f_value):
        acceptable = set(Day.keys()) | set(Day.values())
        if f_value not in acceptable:
            raise ValueError(
                VALUE_ERROR.format(
                    Day,
                ),
            )
        return f_value

    @validator(
        'signature_schedule_time',
        'remediation_schedule_time',
        'scan_schedule_quick_scan_time',
        'scan_schedule_time',
    )
    def _daytime_valid(cls, f_value):
        return f_value.strftime('%H:%M:%S')     # MS datetime format


class StartMPScanModel(BaseParameters):
    """Model for Windows Defender Scan method."""

    scan_path: Optional[str]
    scan_type_pref: Optional[Union[str, int]]

    @validator('scan_type_pref')
    def _scan_type_valid(cls, f_value):
        acceptable = set(ScanType.keys()) | set(ScanType.values())
        if f_value not in acceptable:
            raise ValueError(
                VALUE_ERROR.format(
                    ScanType,
                ),
            )
        return f_value


class UpdateMpSignatureModel(BaseParameters):
    """Model for Windows Defender Update method."""

    update_source: Optional[Union[str, int]]

    @validator('update_source')
    def _update_source_valid(cls, f_value):
        acceptable = set(UpdateSource.keys()) | set(UpdateSource.values())
        if f_value not in acceptable:
            raise ValueError(
                VALUE_ERROR.format(
                    UpdateSource,
                ),
            )
        return f_value


class BodyModel(BaseModel):
    """Model for message body."""

    hostnames: List[str]
    task_id: int
    event: str
    preferences: Dict = {}

    @validator('event')
    def _event_valid(cls, f_value):
        if f_value not in pwsh_commands.COMMANDS_IN_USE:
            raise ValueError('Wrong command.')
        return f_value


def get_model(event: str) -> Type[BaseModel]:
    """
    Take correct Model by given event.

    Args:
        event (str): event name from

    Returns:
        Type[BaseModel]: corrected Model instance

    """
    return {
        'Set-MpPreference': MpPreferencesModel,
        'Start-MpScan': StartMPScanModel,
        'Update-MpSignature': UpdateMpSignatureModel,
        'Get-MpPreference': BaseParameters,
        'Get-MpComputerStatus': BaseParameters,
    }.get(event)
