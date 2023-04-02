__author__ = "Jeremy Nelson"

from pydantic import BaseModel

class AirflowConfig(BaseModel):
    is_active: bool = False
