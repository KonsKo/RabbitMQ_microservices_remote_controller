"""Config module."""
from typing import Optional

from pydantic import BaseModel
from service_framework.broker.config_route import RouteConsume


class RabbitConfig(BaseModel):     # noqa: WPS230
    """Class for config fields determination."""

    host: str
    port: int
    username: str
    password: str
    route_consume: Optional[RouteConsume]
