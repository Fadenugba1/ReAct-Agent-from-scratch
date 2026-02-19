from enum import Enum,auto
from typing import Union, Callable
from pydantic import BaseModel, Field
import logging
class Name(Enum):
    '''Enumeration tool defining the names available for the agent to use'''
    WIKIPEDIA = auto()
    GOOGLE = auto()
    NONE = auto()
    def __str__(self) -> str:
        return self.name.lower()
    
Observation = Union[str,Exception]



class Message(BaseModel):
    role: str = Field(...,description = "role of message sender")
    content: str = Field(...,description="The content of the message")

class Choice(BaseModel):
    name: Name = Field(...,description="The name of the tool chosen.")
    reason: str = Field(...,description="The reason for choosing this tool.")


class Tool:
    def __init__(self, name:Name, func:Callable[[str], str]):
        self.name = name
        self.func = func


    def use(self, query: str) -> Observation:
        try:
            return self.func(query)
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Error executing tool {self.name}: {e}")
            return str(e)


class Agent:
    def __init__(self, model: GenerativeModel) -> None:
        self.model = model 
        self.tools : Dict[Name,Tool] = {}
        self.messages: List[Message] = []
        self.query = ""
        self.max_iterations = 5
        self.current_iteration = 0
        self.template = self.load_template()

    def load_template(self)-> str:
        ...
    
    def register(self, name, func: Callable[[str], str]) -> None:...

    def trace(self, role: str, content: str) -> None: ...

    def get_history(self) -> str: ...

    def think(self) -> None: ...

    def decide(self, response: str) -> None: ...

    def act(self, tool_name: Name, query: str) -> None: ...

    def execute(self, query: str) -> str: ...

    def ask_gemini(self, prompt: str) -> str: ...
