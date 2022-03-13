"""PowerShell callback handler implementation."""
import asyncio
import json
import logging
from typing import Callable, Optional

from config_handler import PowerShellConfig
from pwsh_client import PwshClient
from resolver import resolve_preferences
from service_framework.base_handler import BaseHandler
from service_framework.broker.config_route import RoutePublish
from service_framework.share_files.preferences_model import (
    BodyModel,
    get_model,
)


logger = logging.getLogger(__name__)


ERROR_CAT = '__PowerShell error'
ERROR_MSG = 'Invoke PowerShell command error. {0}'


async def get_body(raw_body: bytes) -> BodyModel:
    """
    Decode and validate broker message body.

    Args:
        raw_body (bytes): body to decode

    Returns:
        decrypted_body (BodyModel): decoded body

    """
    try:
        return BodyModel(**json.loads(raw_body))
    except Exception as exception:
        logger.exception(
            'Error: could not load json body. {0}'.format(
                exception,
            ),
        )


class PowerShellHandler(BaseHandler):     # noqa:WPS214
    """Class implements PowerShell callback handler."""

    def __init__(self):
        """Init class instance."""
        self.config = None
        self.publisher: Optional[Callable] = None
        self.loop = asyncio.get_event_loop()

    def prepare_handler(self, publisher: Callable, config: Optional[dict]):
        """
        Prepare handler to work.

        Args:
            publisher (Callable): async broker publish method
            config (Optional[dict]): PowerShell config

        """
        self.config = PowerShellConfig(**config)
        self._check_routes()
        self.publisher = publisher
        logger.info('PowerShell handler was prepared.')

    async def call_handler(self, raw_body: bytes):
        """
        Implement callback method.

        Args:
            raw_body (bytes): data from broker to work with.

        """
        decrypted_body = await get_body(raw_body)
        await self.doing_publish(
            message={'task_id': decrypted_body.task_id},
            route=self.config.route_publish[1],  # <event.notify>
        )
        for hostname in decrypted_body.hostnames:
            self.loop.create_task(
                self.process_invoking_command(
                    client=PwshClient(self.config),
                    decrypted_body=decrypted_body,
                    hostname=hostname,
                ),
            )

    async def process_invoking_command(
        self,
        client: PwshClient,
        decrypted_body: BodyModel,
        hostname: str,
    ):
        """
        Implement callback method.

        Args:
            client (PwshClient): PowerShell client instance
            decrypted_body (BodyModel): decrypted data from broker.
            hostname (str): hostname to invoke script

        Raises:
            Exception: if something went wrong

        """
        try:
            out, err = await client.invoke_command(
                hostname=hostname,
                command=decrypted_body.event,
                preferences=get_model(decrypted_body.event)(
                    **decrypted_body.preferences,
                ).dict(
                    exclude_unset=True,  # ignores not given fields
                    by_alias=True,
                ),
            )
        except Exception as exception:
            logger.exception(
                'Error: invoke PowerShell command. Body: {0}'.format(
                    exception,
                ),
            )
            await self.doing_publish(
                message={
                    'host_ip': hostname,
                    'message': ERROR_MSG.format(
                        str(exception),
                    ),
                    'category': ERROR_CAT,
                },
                route=self.config.route_publish[0],  # <event.common>
            )
            raise

        if out:
            msg = {
                'host_ip': hostname,
                'preferences': resolve_preferences(
                    raw_prefs=out,
                    event=decrypted_body.event,
                ),
            }
            if decrypted_body.event == 'Get-MpPreference':
                await self.doing_publish(
                    message=msg,
                    route=self.config.route_publish[2],  # <settings_changed>
                )
            elif decrypted_body.event == 'Get-MpComputerStatus':
                await self.doing_publish(
                    message=msg,
                    route=self.config.route_publish[3],   # <mon>
                )

        if err and len(err) > 1:
            await self.doing_publish(
                message={
                    'message': ERROR_MSG.format(
                        str(err),
                    ),
                    'host_ip': hostname,
                    'category': ERROR_CAT,
                },
                route=self.config.route_publish[0],  # <event.common>
            )

    async def stop_handler(self):
        """Process handler shutdown."""
        logger.info('PowerShell handler has been closed.')

    async def doing_publish(self, message: dict, route: RoutePublish):
        """
        Publish notify message.

        Args:
            message (dict): message to send
            route (RoutePublish): route instance to publish

        """
        await self.publisher(
            destination={
                'routing_key': route.routing_key,
                'exchange': route.exchange,
                'exchange_type': route.exchange_type,
            },
            body=message,
        )

    def _check_routes(self):
        if len(self.config.route_publish) != 4:
            logger.error('There are not all routes')
            raise ValueError('There are not all routes')
