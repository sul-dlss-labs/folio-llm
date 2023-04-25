"""
ChatGPT React-Action

Inspired by this blog post https://til.simonwillison.net/llms/python-react-pattern
"""
import json
import re

from typing import Optional
from js import document, localStorage

from pyodide.http import pyfetch


async def login():
    bearer_key_element = document.getElementById("chatApiKey")
    chat_gpt = ChatGPT(key=bearer_key_element.value)
    chatgpt_button = document.getElementById("chatGPTButton")
    chatgpt_button.classList.remove("btn-outline-danger")
    chatgpt_button.classList.add("btn-outline-success")
    chat_prompts_div = document.getElementById("chat-gpt-prompts")
    chat_prompts_div.classList.remove("d-none")
    return chat_gpt


class ChatGPT(object):
    def __init__(self, key, model="text-davinci-003"):
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}"
        }
        self.openai_url = "https://api.openai.com/v1/completions"
        self.system = None 
        self.model = model
        self.messages = []

                    
    async def __call__(self, message):
        self.messages.append(message)
        result = await self.execute()
        self.messages.append(result)
        return result


    async def set_system(self, system):
        self.system = system
        self.messages.insert(0, system)

    
    async def execute(self):
        kwargs = {
            "method": "POST",
            "headers": self.headers,
            "body": json.dumps({
                "model": self.model,
                "prompt": self.messages,
                "temperature": 0.9,
                "max_tokens": 250,
                "stop": [" Human:", " AI:"]

            })
        }
        completion = await pyfetch(self.openai_url, **kwargs)
        if completion.ok:
            result = await completion.json()
        else:
            result = { "error": completion.status,
                       "message": completion.status_text }
        return result


action_re = re.compile(r"^Action: (\w+): (.*)$")


prompt_base = """
You run in a loop of Thought, Action, PAUSE, Observation.
At the end of the loop you output an Answer
Use Thought to describe your thoughts about the question you have been asked.
Use Action to run one of the actions available to you - then return PAUSE.
Observation will be the result of running those actions.

Your available actions are:

retrieve_instance:
e.g. folio_instance: 529056f1-d1a2-5dd6-b074-311847ab362a


assign_lchs:
e.g. lcsh: 
"""

marc2folio_prompt = """
In the role as an expert cataloger, you will be given a MARC21 record and then convert
to a FOLIO Instance JSON record

MARC21 record:
"""

marc2folio_prompt2 = """
In the role as an expert cataloger, you will be given a MARC21 record and then convert
to a FOLIO Instance JSON record

Example session:

Question: Convert this MARC21 record to a FOLIO Instance
=LDR  00704cam a22002051  4500
=001  a3044621
=003  SIRSI
=008  850513q19401949enkab\\\\\\\\\000\0\eng\d
=035  \\$a(OCoLC-M)12030243
=035  \\$a(OCoLC-I)275077884
=040  \\$aCSJ$cCSJ$dCSt-H$dOrLoB
=049  \\$aHINA
=100  1\$aKearsey, A.$q(Alexander Horace Cyril),$d1877-
=245  14$aThe operations in Egypt and Palestine: August, 1914, to June, 1917;$billustrating the field service regulations /$cby A. Kearsey.
=250  \\$a3d ed.
=260  \\$aAldershot,$bGale & Polden$c[194-?]
=300  \\$axvii, 154 p.$bmaps, fold. diagr.$c22 cm.
=596  \\$a25
=650  \0$aWorld War, 1914-1918$xCampaigns$zTurkey and the Near East.
=918  \\$a3044621

Observation:
{'id': 'e52f84b1-027a-5905-a00d-0bdeff370caa',
 '_version': 1,
 'hrid': 'a3044621',
 'source': 'MARC',
 'title': 'The operations in Egypt and Palestine: August, 1914, to June, 1917; illustrating the field service regulations / by A. Kearsey.',
 'indexTitle': 'Operations in egypt and palestine: august, 1914, to june, 1917; illustrating the field service regulations',
 'alternativeTitles': [],
 'editions': ['3d ed'],
 'series': [],
 'identifiers': [{'value': '(OCoLC-M)12030243',
   'identifierTypeId': '7e591197-f335-4afb-bc6d-a6d76ca3bace'},
  {'value': '(OCoLC-I)275077884',
   'identifierTypeId': '7e591197-f335-4afb-bc6d-a6d76ca3bace'}],
 'contributors': [{'name': 'Kearsey, A. (Alexander Horace Cyril), 1877-',
   'contributorTypeId': '9f0a2cf0-7a9b-45a2-a403-f68d2850d07c',
   'contributorTypeText': 'Contributor',
   'contributorNameTypeId': '2b94c631-fca9-4892-a730-03ee529ffe2a',
   'primary': True}],
 'subjects': ['World War, 1914-1918 Campaigns Turkey and the Near East'],
 'classifications': [],
 'publication': [{'publisher': 'Gale & Polden',
   'place': 'Aldershot',
   'dateOfPublication': '[194-?]'}],
 'publicationFrequency': [],
 'publicationRange': [],
 'electronicAccess': [],
 'instanceTypeId': '30fffe0e-e985-4144-b2e2-1e8179bdb41f',
 'instanceFormatIds': [],
 'instanceFormats': [],
 'physicalDescriptions': ['xvii, 154 p. maps, fold. diagr. 22 cm.'],
 'languages': ['eng'],
 'notes': [],
 'administrativeNotes': ['Identifier(s) from previous system: a3044621'],
 'modeOfIssuanceId': '9d18a02f-5897-4c31-9106-c9abb5c7ae8b',
 'catalogedDate': '1995-08-21',
 'previouslyHeld': False,
 'staffSuppress': False,
 'discoverySuppress': False,
 'statisticalCodeIds': [],
 'statusUpdatedDate': '2023-02-11T16:45:56.888+0000',
 'holdingsRecords2': [],
 'natureOfContentTermIds': []}
"""

lcsh_prompt = f"""
Create Library of Congress Subject Headings (LCSH) for the following subjects:

"""

prompt_action = """
You run in a loop of Thought, Action, PAUSE, Observation.
At the end of the loop you output an Answer
Use Thought to describe your thoughts about the question you have been asked.
Use Action to run one of the actions available to you - then return PAUSE.
Observation will be the result of running those actions.

Your available actions are:

marc2folio:
e.g. marc2folio:   

Example session:

Question: Generate a FOLIO Instance record from this MARC record
=LDR \n=001 

"""



