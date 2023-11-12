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
    load as load_folio,
)

from sinopia import add as add_sinopia, load as load_sinopia


add_instance_sig = {
    "name": "add_instance",
    "description": "Adds an FOLIO Instance JSON record to FOLIO",
    "parameters": {
        "type": "object",
        "properties": {
            "record": {"type": "string", "description": "JSON FOLIO Instance"}
        },
    },
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

    async def run(self, chat_instance: ChatGPT, initial_prompt: str):
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
    system_prompt = """In the role as an expert cataloger, you will be given a MARC21 record and then convert
to a FOLIO Instance JSON record
"""

    examples = [
        """Q: =LDR  01071cam a2200349 i 4500
=001  a757722
=003  SIRSI
=005  19910715000000.0
=008  791017s1977\\\\onca\\\\\b\\\\001\0\eng\\
=015  \\$aC77-001233-7
=020  \\$a0070824525
=020  \\$a9780070824522
=050  0\$aHA29$b.E72
=082  \\$a519.5
=100  1\$aErickson, Bonnie H.$0(SIRSI)415236
=245  10$aUnderstanding data /$cBonnie H. Erickson, T. A. Nosanchuk.
=260  \\$aToronto ;$aNew York :$bMcGraw-Hill Ryerson,$cc1977.
=300  \\$axi, 388 p. :$bill. ;$c23 cm.
=490  1\$aMcGraw-Hill Ryerson series in Canadian sociology
=500  \\$aIncludes index.
=504  \\$aBibliography: p. 383-384.
=596  \\$a1
=650  \0$aStatistics.$0(SIRSI)1064412
=700  1\$aNosanchuk, T. A.,$d1935-$0(SIRSI)54329
=830  \0$aMcGraw-Hill Ryerson series in Canadian sociology.$0(SIRSI)1108560

           A: {
 'source': 'MARC',
 'title': 'Understanding data / Bonnie H. Erickson, T. A. Nosanchuk.',
 'indexTitle': 'Understanding data',
 'series': ['McGraw-Hill Ryerson series in Canadian sociology'],
 'identifiers': [{'identifierName': 'ISBN',
   'value': '77375092'},
  {'identifierName': 'ISBN',
   'value': '0070824525'},
  {'identifierTypeId': 'ISBN',
   'value': '9780070824522'}
  ],
 'contributors': [{'name': 'Erickson, Bonnie H',
   'primary': True},
  {,
   'name': 'Nosanchuk, T. A., 1935-',
   'contributorTypeText': None,
   'primary': False}],
 'subjects': ['Statistics'],
 'classifications': [{'classificationNumber': 'HA29 .E72',
   'classificationTypeId': 'ce176ace-a53e-4b4d-aa89-725ed7b2edac'},
  {'classificationNumber': '519.5',
   'classificationTypeId': '42471af9-7d25-4f3a-bf78-60d29dcf463b'}],
 'publication': [{'publisher': 'McGraw-Hill Ryerson',
   'place': 'Toronto New York',
   'dateOfPublication': 'c1977',
   'role': None}],
 'physicalDescriptions': ['xi, 388 p. : ill. ; 23 cm.'],
 'languages': ['eng'],
 'notes': [{
   'note': 'Includes index',
   'staffOnly': False},
  {
   'note': 'Bibliography: p. 383-384',
   'staffOnly': False}]}]
 }"""

    ]

    def __init__(self, zero_shot=False):
        super().__init__()
        self.zero_shot = zero_shot

    async def system(self):
        system_prompt = MARC21toFOLIO.system_prompt

        if self.instance_types is None:
            await self.get_types()

        
        if self.zero_shot is False:
            system_prompt = f"""{system_prompt}\nExamples\n"""
            system_prompt += "\n".join(MARC21toFOLIO.examples)
       

        return system_prompt

    async def run(self, chat_instance, initial_prompt: str):
        add_history(f"<pre>{initial_prompt}</pre>", "prompt")
        chat_result = await chat_instance(initial_prompt)
        add_history(chat_result, "response")
        


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
    functions = [
        add_instance_sig,
    ]

    def __init__(self, zero_shot=False):
        super().__init__()
        self.zero_shot = zero_shot

    async def system(self):
        system_prompt = NewResource.system_prompt
        if self.instance_types is None:
            await self.get_types()

        if self.zero_shot is False:
            system_prompt = f"""{system_prompt}\nExamples:\n"""
            system_prompt += "\n".join(NewResource.examples)

        return system_prompt

    async def run(self, chat_instance: ChatGPT, initial_prompt: str):
        add_history(initial_prompt, "prompt")
        chat_instance.functions = NewResource.functions
        chat_result = await chat_instance(initial_prompt)
        function_call = chat_result["choices"][0]["message"].get("function_call")
        if function_call:
            add_history(chat_result, "response")
            function_name = function_call.get("name")
            args = json.loads(function_call.get("arguments"))
                
            match function_name:
                case "add_instance":
                    record = json.loads(args.get("record"))
                    record["instanceTypeId"] = self.instance_types.get("text")
                    for contributor in record.get("contributors", []):
                        contributor["contributorTypeId"] = self.contributor_types.get(
                            contributor["contributorTypeText"]
                        )
                        contributor[
                            "contributorNameTypeId"
                        ] = self.contributor_name_types.get("Personal name")
                    instance_uuid = await add_instance(json.dumps(record))

                case _:
                    alert(f"Unknown function {function_name}")

        
        content = chat_result["choices"][0]["message"]["content"]
        return f"Finished {instance_url}"
