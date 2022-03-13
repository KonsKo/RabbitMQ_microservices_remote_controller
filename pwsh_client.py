"""PowerShell client module."""
import asyncio
import logging
import re
from typing import Optional

import service_framework.share_files.pwsh_commands as commands
from config_handler import PowerShellConfig

logger = logging.getLogger(__name__)


bad_patterns = (
    r'__ClassMetadata[\s\S]+}}',
    r'Creating[\s\S]+remaining.',
    r'0/1 completed[\s\S]+Quick Scan',
    r'\x1b',
    r'\[\d+mA*',
    r'\~+',
    r'\|,',
)


def clean_output(source: str) -> str:
    """
    Clear response, remove garbage information.

    Args:
        source (str): string to clean

    Returns:
        cleaned (str): cleaned string.
    """
    for pattern in bad_patterns:
        source = re.sub(pattern, '', source)

    return source.replace('  ', '')


class PwshClient(object):
    """PowerShell client through subprocess."""

    def __init__(self, config: PowerShellConfig):
        """
        Create client instance.

        Args:
            config (PowerShellConfig): config fir PowerShell

        """
        self.cmd = [
            '{program}'.format(program=config.program),
            '-command',
        ]
        self.key = config.key_path
        self.username = config.username

    async def run(self, script: str) -> (str, str):
        """
        Run PowerShell script.

        Args:
            script (str): script to run.

        Returns:
            out, err (str, str): response after script running.

        Raises:
            Exception: if subprocess error

        """
        self.cmd.append(script)
        process = await asyncio.create_subprocess_exec(
            *self.cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            out, err = await process.communicate()
        except Exception as ex:
            logger.exception(
                'Subprocess communicate error. {0}'.format(
                    ex,
                ),
            )
            raise
        return clean_output(out.decode()), clean_output(err.decode())

    def create_script(
        self,
        hostname: str,
        command: str,
        preferences: Optional[dict] = None,
    ) -> str:
        """
        Create script for different parameters to run on remote PC using ssh.

        Args:
            hostname (str): host to run command
            command (str): command to run
            preferences (dict): extra preferences for script expression

        Returns:
            script (str): ready to use script
        """
        if preferences:
            for p_key, p_value in preferences.items():
                command = '{command} -{p_key} {p_value}'.format(
                    command=command,
                    p_key=p_key,
                    p_value=p_value,
                )
        return '{0}\n{1}'.format(
            commands.R_NEW_MP_SESSION.format(
                user_host='{0}@{1}'.format(
                    self.username,
                    hostname,
                ),
                key=self.key,
            ),
            commands.R_INVOKE_COMMAND.format(
                command=command,
            ),
        )

    async def invoke_command(     # noqa:WPS320 its bug
        self,
        hostname: str,
        command: str,
        preferences: Optional[dict] = None,
    ) -> (str, str):
        """
        Invoke PowerShell command.

        Args:
            hostname (str): target to use command
            command (str): command to invoke
            preferences (Optional[dict]): preferences for command if needed

        Returns:
            out, err (str, str): result of command running.
        """
        script = self.create_script(hostname, command, preferences)
        return await self.run(script=script)
