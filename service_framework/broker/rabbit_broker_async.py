"""Async RabbitMQ module."""
import asyncio
import json
import logging
from typing import Any, Callable, Optional

import aio_pika
from aio_pika import exceptions as aio_pika_exceptions
from service_framework.base_broker import BaseBroker
from service_framework.broker.config_broker import RabbitConfig
from service_framework.broker.config_route import RoutePublish

logger = logging.getLogger(__name__)

STR_CONNECTION_EXCEPTION = 'Connection exception: {0}'

STR_CHANNEL_EXCEPTION = 'Channel exception: {0}'

TIMEOUT_SET_UP_CONN = 5

CHANNEL_EXCEPTIONS = (
    aio_pika_exceptions.ChannelNotFoundEntity,
    aio_pika_exceptions.ChannelPreconditionFailed,
    aio_pika_exceptions.ChannelInvalidStateError,
    aio_pika_exceptions.ChannelClosed,
    aio_pika_exceptions.AMQPChannelError,
)

CONNECTION_EXCEPTIONS = (
    aio_pika_exceptions.AMQPConnectionError,
    aio_pika_exceptions.AMQPError,
    aio_pika_exceptions.AMQPException,
    aio_pika_exceptions.AuthenticationError,
    aio_pika_exceptions.ConnectionClosed,
)


class RabbitClientAsync(object):
    """Class implements RabbitMQ client."""

    def __init__(self, config: dict, loop):
        """
        Init class instance.

        Args:
            config (dict): RabbitMQ config data.
            loop: asyncio event loop

        """
        self.config = RabbitConfig(**config)
        self.loop = loop
        self.connection = None
        self.channel = None
        self.has_connection = False
        self.has_channel = False

    async def create_connection(self):
        """
        Create aio-pika connection and set up flag.

        Raises:
            NotImplementedError: if loop does not exists.

        """
        logger.info('Starting to set up new connection.')
        if self.loop:
            try:
                self.connection = await aio_pika.connect_robust(
                    host=self.config.host,
                    port=self.config.port,
                    login=self.config.username,
                    password=self.config.password,
                    timeout=10,
                    loop=self.loop,
                )
            except Exception as con_ex:
                self.has_connection = False
                logger.exception(
                    'Setting up connection was failed. {0}'.format(
                        con_ex,
                    ),
                )
                await asyncio.sleep(TIMEOUT_SET_UP_CONN)
                await self.create_connection()
            self.has_connection = True
            logger.info('Connection was set up')
        else:
            logger.error('Loop was not created.')
            raise NotImplementedError

    async def create_channel(self):
        """
        Create RabbitMQ channel and set up flag.

        Raises:
            CHANNEL_EXCEPTIONS: if aio_pika channel error
            Exception: if another error happened

        """
        if self.connection:
            logger.info('Starting to set up new channel.')
            try:
                self.channel = await self.connection.channel()
            except CHANNEL_EXCEPTIONS as ch_ex:
                self.has_connection = False
                logger.exception(
                    'Setting up channel was failed. {0}'.format(
                        ch_ex,
                    ),
                )
                raise
            except Exception as exception:
                logger.exception(
                    'Setting up channel was failed. {0}'.format(
                        exception,
                    ),
                )
                raise
            self.has_channel = True
            await self.channel.set_qos(prefetch_count=100)
            logger.info('Connection was set up.')
        else:
            await self.create_connection()

    async def check_connection(self):
        """Check for connection and channel existence."""
        if not self.has_connection:
            logger.error('Error: there is no active connection.')
            await self.create_connection()
        if not self.has_channel:
            logger.error('Error: there is no active channel.')
            await self.create_channel()


class RabbitBrokerAsync(RabbitClientAsync, BaseBroker):     # noqa:WPS214
    """Class implements async RabbitMQ broker."""

    def __init__(
        self,
        config: dict,
        loop,
        callback_handler: Optional[Callable] = None,
    ):
        """
        Init class instance.

        Args:
            config (dict): RabbitMQ config data.
            loop: asyncio event loop
            callback_handler (Optional[Awaitable]): handler to callback

        """
        super().__init__(config, loop)
        self._callback_handler = callback_handler

    async def declare_exchange(
        self,
        exchange_type: str,
        exchange_name: str,
    ) -> aio_pika.Exchange:
        """
        Declare exchange in channel.

        Args:
            exchange_type (str): type of RabbitMQ exchange
            exchange_name (str): name of exchange

        Returns:
            exchange (aio_pika.Exchange): RabbitMO exchange object

        """
        await self.check_connection()
        try:
            return await self.channel.declare_exchange(
                name=exchange_name,
                type=exchange_type,
                durable=True,
            )
        except CONNECTION_EXCEPTIONS as con_ex:
            logger.exception(
                STR_CONNECTION_EXCEPTION.format(
                    con_ex,
                ),
            )
            self.has_connection = False
            self.has_channel = False
        except CHANNEL_EXCEPTIONS as ch_ex:
            logger.exception(
                STR_CHANNEL_EXCEPTION.format(
                    ch_ex,
                ),
            )
            self.has_channel = False
        except Exception as exception:
            logger.exception(
                'Declaring exchange was failed. {0}'.format(
                    exception,
                ),
            )

    async def declare_queue(self, name: str) -> aio_pika.Queue:
        """
        Declare queue in channel.

        Args:
            name (str): name of queue

        Returns:
            queue (aio_pika.Queue): RabbitMQ queue object

        """
        await self.check_connection()
        try:
            return await self.channel.declare_queue(
                name=name,
                durable=True,
            )
        except CONNECTION_EXCEPTIONS as con_ex:
            logger.exception(
                STR_CONNECTION_EXCEPTION.format(
                    con_ex,
                ),
            )
            self.has_connection = False
            self.has_channel = False
        except CHANNEL_EXCEPTIONS as ch_ex:
            logger.exception(
                STR_CHANNEL_EXCEPTION.format(
                    ch_ex,
                ),
            )
            self.has_channel = False
        except Exception as exception:
            logger.exception(
                'Declaring queue was failed. {0}'.format(
                    exception,
                ),
            )

    async def bind_queue(
        self,
        queue_object: aio_pika.Queue,
        exchange: str,
        routing_key: Optional[str] = None,
    ):
        """
        Bind queue and exchange with given routing key.

        Args:
            queue_object (Queue): queue object to bind with
            exchange (str): name of exchange
            routing_key (Optional[str]): routing key

        """
        await self.check_connection()
        try:
            await queue_object.bind(
                exchange=exchange,
                routing_key=routing_key,
            )
        except CONNECTION_EXCEPTIONS as con_ex:
            logger.exception(
                STR_CONNECTION_EXCEPTION.format(
                    con_ex,
                ),
            )
            self.has_connection = False
            self.has_channel = False
        except CHANNEL_EXCEPTIONS as ch_ex:
            logger.exception(
                STR_CHANNEL_EXCEPTION.format(
                    ch_ex,
                ),
            )
            self.has_channel = False
        except Exception as exception:
            logger.exception(
                'Biding queue was failed. {0}'.format(
                    exception,
                ),
            )

    async def consume(self):
        """Start the consumer."""
        await self.check_connection()
        await self.declare_exchange(
            exchange_type=self.config.route_consume.exchange_type,
            exchange_name=self.config.route_consume.exchange,
        )
        queue_object = await self.declare_queue(
            name=self.config.route_consume.queue_name,
        )
        await self.bind_queue(
            queue_object=queue_object,
            exchange=self.config.route_consume.exchange,
            routing_key=self.config.route_consume.routing_key,
        )
        try:
            await queue_object.consume(self._callback)
        except CONNECTION_EXCEPTIONS as con_ex:
            logger.exception(
                STR_CONNECTION_EXCEPTION.format(
                    con_ex,
                ),
            )
            self.has_connection = False
            self.has_channel = False
        except CHANNEL_EXCEPTIONS as ch_ex:
            logger.exception(
                STR_CHANNEL_EXCEPTION.format(
                    ch_ex,
                ),
            )
            self.has_channel = False
        except Exception as exception:
            logger.exception(
                'Broker consumption is failed. {0}'.format(
                    exception,
                ),
            )

    async def publish(self, body: Any, destination: dict):
        """
        Start the publisher.

        Args:
            body (Any): message to publish
            destination (dict): address to publish

        """
        await self.check_connection()
        destination = RoutePublish(**destination)
        exchange_object = await self.declare_exchange(
            exchange_type=destination.exchange_type,
            exchange_name=destination.exchange,
        )
        body = json.dumps(body, ensure_ascii=False)
        message = aio_pika.Message(
            content_type='application/json',
            body=body.encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )
        try:
            await exchange_object.publish(
                message,
                routing_key=destination.routing_key,
            )
        except CONNECTION_EXCEPTIONS as con_ex:
            logger.exception(
                STR_CONNECTION_EXCEPTION.format(
                    con_ex,
                ),
            )
            self.has_connection = False
            self.has_channel = False
        except CHANNEL_EXCEPTIONS as ch_ex:
            logger.exception(
                STR_CHANNEL_EXCEPTION.format(
                    ch_ex,
                ),
            )
            self.has_channel = False
        except Exception as exception:
            logger.exception(
                'Broker publishing is failed. {0}'.format(
                    exception,
                ),
            )

    async def stop(self):
        """Shutdown broker."""
        if self.connection:
            await self.connection.close()
        logger.info('Connection has been closed')

    async def _callback(self, message: aio_pika.IncomingMessage):
        async with message.process():
            self.loop.create_task(self._callback_handler(message.body))
