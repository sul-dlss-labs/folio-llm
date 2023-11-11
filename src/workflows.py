import asyncio
import json
import sys
import time

from js import console, document

from chat import add_history, react_loop, prompt_base, ChatGPT

from folio import (
    add_instance,
    get_contributor_types,
    get_contributor_name_types,
    get_identifier_types,
    get_instance_types, 
    load as load_folio
)

from sinopia import add as add_sinopia, load as load_sinopia



add_instance_sig = {
  "name": "add_instance",
  "description": "Adds an FOLIO Instance JSON record to FOLIO",
  "parameters": {
    "type": "object",
    "properties": {
      "record": {
        "type": "string",
        "description": "JSON FOLIO Instance"
      }
    }
  }
}


class WorkFlow(object):
    name: str = ""
    system: str = ""
    examples: list = []
    max_turns: int = 5


class FOLIOWorkFlow(WorkFlow):

    def __init__(self):
        self.contributor_types = None
        self.contributor_name_types = None
        self.identifier_types = None
        self.instance_types = None
        

    async def get_types(self):
        if self.contributor_types is None: 
            self.contributor_types = await get_contributor_types()

        if self.contributor_name_types is None:
            self.contributor_name_types = await get_contributor_name_types()

        if self.identifier_types is None:
            self.identifier_types = await get_identifier_types()

        if self.instance_types is None:
            self.instance_types = await get_instance_types()



class AssignLCSH(WorkFlow):
    name = "Assign Library of Congress Subject Heading to record"
    system = ""

    examples = []

    def __init__(self, zero_shot=False, react=False):
        self.system = system
        self.react = react

        if zero_shot is False:
            self.system = f"""{self.system}\nExamples:\n"""
            self.system += "\n".join(MARC21toFOLIO.examples)

        if self.react:
            self.actions: dict = {}

            self.system = f"""{self.system}
{prompt_base}

"""

    async def run(self, chat_instance: ChatGPT, initial_prompt:str):
        add_history(initial_prompt, "prompt")
        if not self.react:
            chat_result = await chat_instance(initial_prompt)
            add_history(chat_result, "response")
            return
        count = 0
        while count < AssignLCSH.max_turns:
            count += 1
            
            


class MARC21toFOLIO(FOLIOWorkFlow):
    name = "MARC21 to FOLIO Inventory Record"
    system = ""

    examples = []

    def __init__(self, zero_shot=False, react=False):
        self.system = MARC21toFOLIO.system

        if zero_shot is False:
            self.system = f"""{self.system}\nExamples:\n"""
            self.system += "\n".join(MARC21toFOLIO.examples)

    
    def loop(self, chat_instance):
        pass


class NewResource(FOLIOWorkFlow):
    name = "Create a New Resource"
    system_prompt = """You are an expert cataloger, return any records as FOLIO JSON"""
    examples = [
        """Q: Parable of the Sower by Octiva Butler, published in 1993 by Four Walls Eight Windows in New York

           A: {"title": "Parable of the Sower", "source": "ChatGPT", 
                 "contributors": [{"name": "Octiva Butler", "contributorTypeText": "Author"}], 
                "publication": [{"publisher": "Four Walls Eight Windows", "dateOfPublication": "1993", "place": "New York"}] }}
        """
    ]
    functions = [add_instance_sig,]


    def __init__(self, zero_shot=False):
        super().__init__()
        self.zero_shot = zero_shot 
        
           
    async def system(self):
        system_prompt = NewResource.system_prompt
        if self.instance_types is None:
            await self.get_types()
        
        #system_prompt = f"""{system_prompt} The FOLIO Record needs an instanceTypeId from this hash of \n\n{self.instance_types}\n\n
        #if a match cannot be found, use txt as the default\n"""

        #system_prompt = f"""{system_prompt} For any contributors, set a contributorTypeId by lookup with contributorTypeText of this
        #hash \n\n
        #{self.contributor_types}.\n\nIf a match cannot be found, use "Author" as the default"""

        if self.zero_shot is False:
            system_prompt = f"""{system_prompt}\nExamples:\n"""
            #NewResource.examples[0] = NewResource.examples[0].format(
            #                              instance_type_id=self.instance_types.get("text"),
            #                              contributor_type_id=self.contributor_types.get("Author"))
            system_prompt += "\n".join(NewResource.examples)

        return system_prompt
 


    async def run(self, chat_instance: ChatGPT, initial_prompt: str):
        add_history(initial_prompt, "prompt")
        chat_instance.functions = NewResource.functions
        chat_result = await chat_instance(initial_prompt)
        function_call = chat_result['choices'][0]['message'].get("function_call")
        if function_call:
            function_name = function_call.get("name")
            args = json.loads(function_call.get("arguments"))
            match function_name:

                case "add_instance":
                    record = json.loads(args.get("record"))
                    record["instanceTypeId"] = self.instance_types.get("text")
                    for contributor in record.get("contributors", []):
                        contributor["contributorTypeId"] = self.contributor_types.get(contributor["contributorTypeText"])
                        contributor["contributorNameTypeId"] = self.contributor_name_types.get("Personal name")
                    instance_uuid = await add_instance(json.dumps(record))

                case _:
                    alert(f"Unknown function {function_name}")

            
        add_history(chat_result, "response")
        content = chat_result['choices'][0]['message']['content']
        return f"Finished {instance_url}"
            
            

