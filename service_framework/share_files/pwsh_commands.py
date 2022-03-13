"""Constants: PowerShell commands related to Windows Defender."""

# Creates a persistent connection to a local or remote computer.
# https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/new-pssession?view=powershell-7.1
R_NEW_MP_SESSION = """
    $session = New-PSSession -HostName {user_host} -KeyFilePath {key}
"""

# Runs commands on local and remote computers.
# https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/invoke-command?view=powershell-7.1
R_INVOKE_COMMAND = """
    Invoke-Command -Session $session -ScriptBlock {{{command}}}
"""

# Gets events from event logs and event tracing log files.
# https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.diagnostics/get-winevent?view=powershell-7.1
GET_EVENT_LOG = 'Get-WinEvent -LogName *defe* | Select-Object -First 5'

# Gets preferences for the Windows Defender scans and updates.
# https://docs.microsoft.com/en-us/powershell/module/defender/get-mppreference?view=windowsserver2019-ps
GET_MP_PREFERENCE = 'Get-MpPreference'

# Gets the status of antimalware software on the computer.
# https://docs.microsoft.com/en-us/powershell/module/defender/get-mpcomputerstatus?view=windowsserver2019-ps
GET_MP_COMPUTER_STATUS = 'Get-MpComputerStatus'

# Gets the history of threats detected on the computer.
# https://docs.microsoft.com/en-us/powershell/module/defender/get-mpthreat?view=windowsserver2019-ps
GET_MP_THREAT = 'Get-MpThreat'

# Gets active and past malware threats that Windows Defender detected.
# https://docs.microsoft.com/en-us/powershell/module/defender/get-mpthreatdetection?view=windowsserver2019-ps
GET_MP_THREAT_DETECTION = 'Get-MpThreatDetection'

# Starts a scan on a computer.
# https://docs.microsoft.com/en-us/powershell/module/defender/start-mpscan?view=windowsserver2019-ps
R_START_MP_SCAN = 'Start-MpScan'

# Starts a Windows Defender offline scan.
# https://docs.microsoft.com/en-us/powershell/module/defender/start-mpwdoscan?view=windowsserver2019-ps
R_START_MP_WDO_SCAN = 'Start-MpScan'

# Modifies settings for Windows Defender.
# https://docs.microsoft.com/en-us/powershell/module/defender/add-mppreference?view=windowsserver2019-ps
E_ADD_MP_PREFERENCE = 'Add-MpPreference'

# Removes exclusions or default actions.
# https://docs.microsoft.com/en-us/powershell/module/defender/remove-mppreference?view=windowsserver2019-ps
E_REMOVE_MP_PREFERENCE = 'Remove-MpPreference'

# Configures preferences for Windows Defender scans and updates.
# https://docs.microsoft.com/en-us/powershell/module/defender/set-mppreference?view=windowsserver2019-ps
E_SET_MP_PREFERENCE = 'Set-MpPreference'

# Updates the antimalware definitions on a computer.
# https://docs.microsoft.com/en-us/powershell/module/defender/update-mpsignature?view=windowsserver2019-ps
E_UPDATE_MP_SIGNATURE = 'Update-MpSignature'


COMMANDS_IN_USE = (
    E_SET_MP_PREFERENCE,
    R_START_MP_SCAN,
    E_UPDATE_MP_SIGNATURE,
    GET_MP_PREFERENCE,
    GET_MP_COMPUTER_STATUS,
)
