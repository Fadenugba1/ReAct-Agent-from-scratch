from enum import Enum,auto
from typing import Union, Callable
from pydantic import BaseModel, Field
import logging
import json
class Name(Enum):
    '''Enumeration tool defining the names available for the agent to use'''
    WIKIPEDIA = auto()
    GOOGLE = auto()
    NONE = auto()
    def __str__(self) -> str:
        return self.name.lower()
    
Observation = Union[str,Exception]
logger = logging.getLogger(__name__)


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

    def think(self) -> None: 
        self.current_iteration +=1
        if self.current_iteration>self.max_iterations:
            logger.warning("reached maximum iterations. Stopping")
            return
        
        prompt = self.prompt_template.format(
        query=self.query, 
        history=self.get_history(),
        tools=', '.join([str(tool.name) for tool in self.tools.values()])
    )
        response = self.ask_gemini(prompt)
        self.trace("assistant", f"Thought: {response}")
        self.decide(response)


    def decide(self, response: str) -> None: 
        try:
            parsed_response = json.loads(response.strip().strip('`').strip())
            if "action" in parsed_response:
                action = parsed_response["action"]
                tool_name = Name[action["name"].upper()]
                self.act(tool_name, action.get("input", self.query))
            elif "answer" in parsed_response:
                self.trace("assistant", f"Final Answer: {parsed_response['answer']}")
            else:
                raise ValueError("Invalid Response Format")

        except Exception as e:
            logger.error(f"Errors with api {str(e)}")
            self.think()

    def act(self, tool_name: Name, query: str) -> None:
        tool = self.tools.get(tool_name)
        if tool:
            result = tool.use(query)
            observation = f"Observation from {tool_name}: {result}"
            self.trace("system", observation)
            self.think()
        
        else:
            logger.error(f"No tool registered for choice: {tool_name}")
            self.think()

    def execute(self, query: str) -> str: ...

    def ask_gemini(self, prompt: str) -> str: ...
