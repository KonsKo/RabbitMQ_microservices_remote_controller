"""Config handler module."""

from typing import List, Optional

from pydantic import BaseModel

from service_framework.broker.config_route import RoutePublish


class PowerShellConfig(BaseModel):
    """Class for queue config fields determination."""

    username: str
    key_path: str
    program: str
    route_publish: Optional[List[RoutePublish]]
