from typing import Optional
from pydantic import BaseModel

from pyodide.http import pyfetch

class ChatGPT(BaseModel):
    key: str
    description: Optional[str] = None


async def login(chat_gpt: ChatGPT):
    pass
    
async def prompt():
    pass
    
    
