"""Main main_service module."""
import argparse
import asyncio
import json
import logging
import os
import signal
import sys
from contextlib import suppress
from logging.handlers import TimedRotatingFileHandler
from typing import TextIO, Type

from service_framework.base_broker import BaseBroker
from service_framework.base_handler import BaseHandler
from service_framework.base_service import BaseService
from service_framework.broker.rabbit_broker_async import RabbitBrokerAsync
from service_framework.config_service import ServiceConfig

os.environ['no_proxy'] = '*'

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def set_logger(log_path: str, log_name: str, log_level: str = 'DEBUG') -> None:
    """
    Set up logger according settings.

    Args:
        log_level (str): Logger level.
        log_path (str): File path to save log.
        log_name (str): File name to save log

    Raises:
        Exception: if error in logger setting up.

    """
    try:
        logger_handler = TimedRotatingFileHandler(
            os.path.join(
                log_path,
                '{0}.log'.format(log_name),
            ),
            when='W6',
        )
    except Exception:
        logger.exception('Logger has error while setting up handler.')
        raise
    try:
        logger_handler.setLevel(log_level.upper())
    except Exception:
        logger.exception('Logger has error while setting up level.')
    formatter = logging.Formatter(
        '{asctime} :: {name:22s} :: {levelname:8s} :: {message}',
        style='{',
    )
    logger_handler.setFormatter(formatter)
    logger.addHandler(logger_handler)
    logger.info('Logger has been successfully set up.')


def load_config(config_file: TextIO) -> ServiceConfig:
    """
    Load configuration from json-file and structuring into a class-notation.

    Args:
        config_file (TextIO): file with config

    Raises:
        Exception: if error while getting configuration.

    Returns:
        loaded_config (MainConfig): Config for Zabbix, Redis, Psql, logger.

    """
    try:
        loaded_config = ServiceConfig(
            **json.loads(
                config_file.read(),
            ),
        )
    except Exception:
        logger.exception('Error getting configuration')
        raise
    return loaded_config


def load_routes(routes_file: str) -> dict:
    """
    Load queues from json-file and structuring into a class-notation.

    Args:
        routes_file (str): path to queue settings file

    Raises:
        Exception: if error while getting configuration.
        FileExistsError: if queue file does not exists.

    Returns:
        loaded_routes (MainConfig): List of queues.

    """
    if os.path.exists(routes_file):
        with open(routes_file, 'r') as q_file:
            try:
                loaded_routes = json.loads(
                    q_file.read(),
                )
            except Exception:
                logger.exception('Error getting queue configuration')
                raise
    else:
        logger.error('Queue settings file does not exists.')
        raise FileExistsError
    return loaded_routes


def launch_service(callback_handler: Type[BaseHandler], *args, **kwargs):
    """
    Make preparation and start service.

    Init argument parser and parse command line.
    Load config and add extra data to it.
    Set logger.
    Create, init and start service.

    Args:
        callback_handler (Type[BaseHandler]): handler instance  to callback
        args: extra arguments for handler constructor
        kwargs: extra key arguments for handler constructor

    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-C',
        '--config',
        help='Required. Path to file with configurations',
        required=True,
        type=argparse.FileType('r'),
        dest='config_file',
    )
    parser.add_argument(
        '-s',
        '--service',
        help='Required. Service name to identify it',
        required=True,
        type=str,
        dest='service_name',
    )
    parsed_args = parser.parse_args()

    config = load_config(config_file=parsed_args.config_file)
    config.identifier = parsed_args.service_name

    set_logger(
        log_path=config.log_file,
        log_name=parsed_args.service_name,
        log_level=config.log_level,
    )

    new_service = ServiceFramework(
        config=config,
        callback_handler=callback_handler,
    )
    new_service.prepare_to_run(*args, **kwargs)
    new_service.service_run()


# noinspection PyArgumentList
class AsyncService(object):
    """Async service class implementation."""

    def __init__(
        self,
        config: ServiceConfig,
        callback_handler: Type[BaseHandler],
    ):
        """
        Init service instance.

        Args:
            config (ServiceConfig): configuration data
            callback_handler (Type[BaseHandler]r): handler to run callback

        """
        self.loop = self._create_loop()
        self.config = config
        self.broker: Type[BaseBroker] = RabbitBrokerAsync
        self.callback_handler: Type[BaseHandler] = callback_handler

    def _create_loop(self):
        """
        Create event loop and set up signal handlers.

        Returns:
            loop: asyncio event loop
        """
        loop = asyncio.get_event_loop()
        signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
        for sig in signals:
            loop.add_signal_handler(
                sig,
                self._process_sig_callback_sync,
            )
        return loop

    def _process_sig_callback_sync(self):
        """Convert async callback function to sync."""
        self.loop.create_task(self._process_sig_callback())

    async def _process_sig_callback(self):
        tasks = [
            task for task in asyncio.Task.all_tasks() if task is not
            asyncio.tasks.Task.current_task()
        ]
        with suppress(asyncio.exceptions.CancelledError):
            list(
                map(
                    lambda task: task.cancel(),
                    tasks,
                ),
            )
        pending_tasks = await asyncio.gather(
            *tasks,
            return_exceptions=True,
        )
        logger.info(
            'Finished pending tasks: {0}'.format(
                pending_tasks,
            ),
        )
        await self.broker.stop()
        await self.callback_handler.stop_handler()
        self.loop.stop()
        logger.info('Service has benn stopped.')


class ServiceFramework(AsyncService, BaseService):
    """Service-framework class implementation."""

    def prepare_to_run(self, *args, **kwargs):
        """
        Do preparation before service start.

        Args:
            args: extra arguments for handler constructor
            kwargs: extra key arguments for handler constructor

        """
        self._take_routes()
        self._create_callback_handler(*args, **kwargs)
        self._create_broker()
        self.callback_handler.prepare_handler(
            config=self.config.handler_config,
            publisher=self.broker.publish,
        )
        logger.info(
            'Init main_service: success. Identifier: "{0}"'.format(
                self.config.identifier,
            ),
        )

    def service_run(self):
        """
        Start service running.

        If service type publisher than run handler as main process.
        """
        if self.config.type == 'publisher':
            self.loop.create_task(self.callback_handler.call_handler())
        else:
            self.loop.create_task(self.broker.consume())
        try:
            self.loop.run_forever()
        except Exception as exception:
            logger.exception(
                'Could not to start service. {0}'.format(
                    exception,
                ),
            )
            sys.exit(1)
        finally:
            self.loop.close()

    def _create_broker(self):
        try:
            self.broker = self.broker(
                config=self.config.broker_config,
                callback_handler=self.callback_handler.call_handler,
                loop=self.loop,
            )
        except Exception as exception:
            logger.exception(
                'Init main_service: broker did not created. {0}'.format(
                    exception,
                ),
            )
            raise NotImplementedError('Broker did not set up.')
        logger.info('Broker has been created successfully.')

    def _create_callback_handler(self, *args, **kwargs):
        try:
            self.callback_handler = self.callback_handler(*args, **kwargs)
        except Exception as exception:
            logger.exception(
                'Init main_service: handler did not created. {0}'.format(
                    exception,
                ),
            )
            raise NotImplementedError('Handler did not set up.')
        logger.info('Handler has been created successfully.')

    def _take_routes(self):
        try:
            routes = list(
                filter(
                    lambda route: route['service'] == self.config.identifier,
                    load_routes(routes_file=self.config.routes_file),
                ),
            )[0]['routes']
        except Exception:
            logger.exception('Routes was not provided.')
            raise ValueError('Routes was not provided.')
        if self.config.type in {'consumer', 'all'}:
            try:
                self.config.broker_config['route_consume'] = routes['consume']
            except Exception as exception:
                logger.exception(
                    'Error getting consume route. {0}'.format(
                        exception,
                    ),
                )
                raise
        if self.config.type in {'publisher', 'all'}:
            try:
                self.config.handler_config['route_publish'] = routes['publish']
            except Exception as excptn:
                logger.exception(
                    'Error while filtering publish queues. {0}'.format(
                        excptn,
                    ),
                )
                raise
