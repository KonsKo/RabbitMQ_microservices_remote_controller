"""Route config module."""
from typing import Optional

from pydantic import BaseModel, validator

EXCHANGE_TYPES = (
    'fanout',
    'direct',
    'topic',
    'headers',
    'x-delayed-message',
    'x-consistent-hash',
)


class Route(BaseModel):
    """Class for route(queue, exchange) config fields determination."""

    exchange: str
    routing_key: Optional[str]
    exchange_type: str
    auto_ack: bool = True

    @validator('exchange_type')
    def _maps_reporting_valid(cls, f_value):     # noqa:N805
        if f_value not in EXCHANGE_TYPES:
            raise ValueError(
                'Wrong value. Acceptable values are: {0}'.format(
                    EXCHANGE_TYPES,
                ),
            )
        return f_value


class RoutePublish(Route):
    """Class for publish routes."""

    queue_name: Optional[str] = None


class RouteConsume(Route):
    """Class for publish routes."""

    queue_name: str
