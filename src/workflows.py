import re

from js import console, document

from chat import add_history, react_loop, prompt_base, ChatGPT

from folio import add as add_folio, load as load_folio
from sinopia import add as add_sinopia, load as load_sinopia


def construct_instance(record):
    console.log(f"Constructs a FOLIO Instance Record")
    

class WorkFlow(object):
    name: str = ""
    system: str = ""
    examples: list = []
    max_turns: int = 5



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
            
            


class MARC21toFOLIO(WorkFlow):
    name = "MARC21 to FOLIO Inventory Record"
    system = ""

    examples = []

    def __init__(self, zero_shot=False, react=False):
        self.system = system

        if zero_shot is False:
            self.system = f"""{self.system}\nExamples:\n"""
            self.system += "\n".join(MARC21toFOLIO.examples)

        if react:
            self.actions: dict = {}

            self.system = f"""{self.system}
{prompt_base}

"""
    def loop(self, chat_instance):
        pass



class NewResource(WorkFlow):
    name = "Create a New Resource"
    system = """You are an expert cataloger, return any records as FOLIO JSON encapsulated with a <record> element"""
    examples = [
        """Q: Parable of the Sower by Octiva Butler, published in 1993 by Four Walls Eight Windows in New York

           A: add_folio: <record>{ "title": "Parable of the Sower", "contributors": [{"name": "Octiva Butler", "contributorTypeText": "Author"}], 
                "publication": [{"publisher": "Four Walls Eight Windows", "dateOfPublication": "1993", "place": "New York"}] }</record>
        """
    ]
    add_folio_re = re.compile(r'add_folio: <record>(.*)</record>', re.DOTALL)

    def __init__(self, zero_shot=False, react=False):
        self.system = NewResource.system

        if zero_shot is False:
            self.system = f"""{self.system}\nExamples:\n"""
            self.system += "\n".join(NewResource.examples)
            
  
        if react:
            self.actions: dict = {
              "add_folio": add_folio,
              "construct_instance": construct_instance,
              "load_folio": load_folio,
            }
            self.system = f"""{self.system}
{prompt_base}


add_folio: 
e.g. add_folio: {{"title": "A book title" }}
Takes a constructed JSON record and adds as a FOLIO Instance
"""

    async def run(self, chat_instance: ChatGPT, initial_prompt:str):
        console.log("IN NewResource RUN")
        add_history(initial_prompt, "prompt")
        # if not self.react:
        #     chat_result = await chat_instance(initial_prompt)
        #     add_history(chat_result, "response")
        #     return

        chat_result = await chat_instance(initial_prompt)
        content = chat_result['choices'][0]['message']['content']
        action_result = NewResource.add_folio_re.search(content)
        if action_result:
            instance_url = add_folio(action_result.groups()[0])
        return f"Finished {instance_url}"
            
            

