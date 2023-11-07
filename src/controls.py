from js import console, document, alert

from chat import add_history
from workflows import NewResource, MARC21toFOLIO


def clear_chat_prompt(chat_gpt_instance):
    main_chat_textarea = document.getElementById("mainChatPrompt")
    system_card = document.getElementById("system-card")
    system_card.classList.add("d-none")
    workflow_title = document.getElementById("workflow-title")
    workflow_title.innerHTML = ""
    main_chat_textarea.value = ""
    if chat_gpt_instance != None:
        chat_gpt_instance.messages = []
    _clear_vector_db()
    return None


def load_folio_default():
    folio_modal = document.getElementById("folioModal")
    folio_url = document.getElementById("folioURI")
    okapi_url = document.getElementById("okapiURI")
    tenant = document.getElementById("folioTenant")
    user = document.getElementById("folioUser")
    password = document.getElementById("folioPassword")
    folio_default = document.getElementById("folio-default")

    folio_url.value = "https://folio-nolana.dev.folio.org"
    okapi_url.value = "https://folio-nolana-okapi.dev.folio.org"
    tenant.value = "diku"
    user.value = "diku_admin"
    password.value = "admin"

    folio_default.classList.add("d-none")
    


def load_workflow(workflow_slug):
    workflow_title_h2 = document.getElementById("workflow-title")
    chat_prompt_textarea = document.getElementById("mainChatPrompt")
    folio_vector_chkbx = document.getElementById("folio-vector-db")
    sinopia_vector_chkbox = document.getElementById("sinopia-vector-db")
    lcsh_vector_chkbox = document.getElementById("lcsh-vector-db")
    examples_div = document.getElementById("prompt-examples")
    system_card = document.getElementById("system-card")
        
    system_div = document.getElementById("system-message")

    system_div.innerHTML = ""
    examples_div.innerHTML = ""
    system_card.classList.remove("d-none")
        # chat_prompt_textarea.value = prompt_base
    _clear_vector_db()
    mrc_upload_btn = document.getElementById("marc-upload-btn")
    mrc_upload_btn.classList.add("d-none")

    match workflow_slug:

        case "add-lcsh":
            msg = "Adds Library of Congress Subject Headings to Resource"
            console.log(msg)
            lcsh_vector_chkbox.checked = True
            workflow = "add_lcsh"

        case "bf-to-marc":
            msg = "Generate a MARC Record from Sinopia BIBFRAME RDF"
            console.log(msg)
            lcsh_vector_chkbox.checked = True
            sinopia_vector_chkbox.checked = True
            workflow = "bf_to_marc"

        case "marc-to-folio":
            console.log(msg)
            folio_vector_chkbx.checked = True
            mrc_upload_btn.classList.remove("d-none")
            workflow = MARC21toFOLIO
            msg = workflow.name

        case "new-resource":
            folio_vector_chkbx.checked = True
            lcsh_vector_chkbox.checked = True
            sinopia_vector_chkbox.checked = True
            workflow = NewResource
            msg = workflow.name


        case "transform-bf-folio":
            msg = "Transform Sinopia BIBFRAME to FOLIO Inventory"
            console.log(msg)
            folio_vector_chkbx.checked = True
            sinopia_vector_chkbox.checked = True
            workflow = "transform_bf_folio"

        case _:
            msg = "None selected"
            workflow = None

    workflow_title_h2.innerHTML = f"<strong>Workflow:</strong> {msg}"
    if hasattr(workflow, "system"):
        system_div.innerHTML = f"""<textarea id="system-text" class="form-control" rows=5>{workflow.system}</textarea>"""
    if hasattr(workflow, "examples"):
        for i,example in enumerate(workflow.examples):
            example_div = document.createElement("div")
            example_div.classList.add("form-check")
            example_div.innerHTML = f"""<input class="form-check-input" type="checkbox" value="" id="workflow-example-chkbox-{i}" checked></input>
                             
                               <textarea id="workflow-example-{i}" class="form-control" rows=3>{example}</textarea>"""
            examples_div.append(example_div)
    return workflow


async def run_prompt(workflow, chat_gpt_instance):
    main_chat_textarea = document.getElementById("mainChatPrompt")
    console.log(f"Workflow is {workflow}")
    if workflow is None:
        alert("Workflow is None")
        return
    prompt_examples_div = document.getElementById("prompt-examples")
    examples = []
    for check_box in prompt_examples_div.getElementsByTagName("input"):
        if check_box.checked:
            examples.append(check_box.nextElementSibling.value)
    console.log(f"Examples {examples}")
    workflow.examples = examples
    workflow_run = workflow(react=True)
    await chat_gpt_instance.set_system(workflow_run.system)
    current = main_chat_textarea.value
    if len(current) > 0:
        console.log(f"Before calling {workflow_run.run}")
        #add_history(current, "prompt")
        #chat_result = await chat_gpt_instance(current)
        #add_history(chat_result, "response")
        run_result = await workflow_run.run(chat_gpt_instance, current)
        console.log(f"Run result {run_result}")
        main_chat_textarea.value = ""

def _clear_vector_db():
    folio_vector_chkbx = document.getElementById("folio-vector-db")
    sinopia_vector_chkbox = document.getElementById("sinopia-vector-db")
    lcsh_vector_chkbox = document.getElementById("lcsh-vector-db")
    for checkbox in [folio_vector_chkbx, sinopia_vector_chkbox, lcsh_vector_chkbox]:
        checkbox.checked = False


