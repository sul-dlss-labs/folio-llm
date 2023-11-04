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


class NewResource(WorkFlow):
    name = "Create a New Resource"
    system = """You are an expert cataloger, return any records as a FOLIO JSON record"""
    examples = [
        """Q: Parable of the Sower by Octiva Butler, published in 1993 by Four Walls Eight Windows in New York

           A: { "title": "Parable of the Sower", "contributors": [{"name": "Octiva Butler", "contributorTypeText": "Author"}], 
                "publication": [{"publisher": "Four Walls Eight Windows", "dateOfPublication": "1993", "place": "New York"}] }
        """
    ]

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


load_folio:
e.g. load_folio:  URL of FOLIO Inventory Record 
Loads the URL into the FOLIO Instance
"""



async def new_resource(**kwargs):
    chat_instance = kwargs.get("chat")
    prompt = kwargs.get("prompt")
    okapi = kwargs.get("okapi")
    system =  f"You are an expert cataloger, you return all results as FOLIO JSON record\n{prompt_base}"
    system =     actions = {
        "add_folio": add_folio,
        "load_folio": load_folio,
    }
    await chat_instance.set_system(system)
    system_div = document.getElementById("system-message")
    console.log(f"System DIV {system_div}")
    system_div.innerHTML = system
    react_loop(actions=actions, question=initial_prompt, chat_instance=chat_instance)
