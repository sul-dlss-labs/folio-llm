from chat import add_history, react_loop

from folio import add as add_folio, load as load_folio
from sinopia import add as add_sinopia, load as load_sinopia

async def new_resource(**kwargs):
    chat_instance = kwargs.get("chat")
    prompt = kwargs.get("prompt")
    okapi = kwargs.get("okapi")
    system =  f"You are an expert cataloger, you return all results as FOLIO JSON record\n{prompt_base}"
    system = f"""{system}

Your available actions are:

add_folio:
e.g. add_folio: JSON record
Takes a JSON record and adds to the FOLIO Instance

add_sinopia:
e.g. add_sinopia: JSON-LD Record
Takes a JSON-LD Record and adds to the Sinopia Linked Data Record

load_folio:
e.g. load_folio:  URL of FOLIO Inventory Record 
Loads the URL into the FOLIO Instance

load_sinopia: 
e.g. load_sinopia: URL of the Sinopia Record
Loads the URL into the Sinopia environment
"""
    actions = {
        "add_folio": add_folio,
        "add_sinopia": add_sinopia,
        "load_folio": load_folio,
        "load_sinopia": load_sinopia
    }
    await chat_instance.set_system(system)
    await react_loop(actions=actions, question=initial_prompt, chat_instance=chat_instance)
