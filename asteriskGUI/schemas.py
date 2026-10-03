
# schemas.py
from pydantic import BaseModel, Field
from typing import Dict, Any

class HangupRequest(BaseModel):
    # Field validation ensures the incoming value is a valid string handle
    channel: str = Field(..., description="Unique Asterisk channel identifier to drop")
    
class AMICommandRequest(BaseModel):
    # {"dc":"N","command":{"Action": "show_endpoints","Param":{} }}
    # dc for command 
    # command for command or script
    command: Dict[str, Any]
    dc: str

class ExtensionCreateRequest(BaseModel):
    numStart: str = Field(..., description="Extension number start range to create")
    numEnd: str = Field(..., description="Extension number end range to create")
    dept: str = Field(..., description="Department grouping")
    callerid: str = Field(..., description="Caller ID")
    passwd: str = Field(..., description="SIP Password")


class ExtensionModifyRequest(BaseModel):
    numStart: str = Field(..., description="Extension number start range to create")
    numEnd: str = Field(..., description="Extension number end range to create")
    dept: str = Field(..., description="Department grouping")
    callerid: str = Field(..., description="Caller ID")
    passwd: str = Field(..., description="SIP Password")

class ExtensionDeleteRequest(BaseModel):
    numStart: str = Field(..., description="Extension number delete start")
    numEnd: str = Field(..., description="Extension number delete start")    
    dept: str = Field(..., description="Updated department")
