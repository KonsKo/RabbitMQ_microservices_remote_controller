"""Config module."""

from typing import Dict, Optional

from pydantic import BaseModel, validator


class ServiceConfig(BaseModel):     # noqa: WPS230
    """Class for config fields determination."""

    log_file: str
    log_level: str
    type: str = 'publisher'
    routes_file: str    # path to queue settings
    identifier: Optional[str]
    broker_config: Optional[Dict]    # Dict another broker
    handler_config: Optional[Dict]

    @validator('type')
    def _validate_type(cls, f_value):    # noqa:N805 , pydantic rule
        if f_value not in {'publisher', 'consumer', 'all'}:
            raise ValueError(
                'Wrong value. Acceptable values are: {0}'.format(
                    {'publisher', 'consumer', 'all'},
                ),
            )
        return f_value
