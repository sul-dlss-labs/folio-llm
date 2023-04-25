import io
import json

import pymarc

from typing import Optional
from pydantic import BaseModel
from pyodide.http import pyfetch

from js import document, Headers, localStorage

class Okapi(BaseModel):
    url: str = ""
    tenant: str = ""
    token: str = ""


def services():
    modal_body = document.getElementById("folioModalBody")
    modal_body.innerHTML = ""    
    modal_label = document.getElementById("folioModalLabel")
    modal_label.innerHTML = "FOLIO Services"
    folio_services_ol = document.createElement("ol")
    auto_vendor_marc_li = document.createElement("li")
    auto_vendor_marc_li.innerHTML = "Load Vendor MARC Records"
    folio_services_ol.appendChild(auto_vendor_marc_li)
    modal_body.appendChild(folio_services_ol)
    
#    Goal 1: Automate loading of vendor MARC records                
# Goal 2: Generate Order records from brief MARC records
# Goal 3: Create Course reserves from a csv containing a faculty id, course name, course code, start date, end date, item barcode  [ Goal 4: Assist staff by generating a quick add instance, holdings, and item from barcode not in FOLIO
#Goal 5: Given a title, find all items with it's circulation status, and reserve the nearest available item



async def login(okapi: Okapi):
    okapi_url = document.getElementById("okapiURI")
    tenant = document.getElementById("folioTenant")
    user = document.getElementById("folioUser")
    password = document.getElementById("folioPassword")

    okapi.url = okapi_url.value
    okapi.tenant = tenant.value


    headers = {
        "Content-type": "application/json",
        "x-okapi-tenant": okapi.tenant
    }

    payload = { 
        "username": user.value,
        "password": password.value 
    }

    kwargs = {
       "method": "POST",
       "headers": headers,
       "mode": "cors",
       "body": json.dumps(payload)
    }
    login_response = await pyfetch(f"{okapi.url}/authn/login", **kwargs)

    login_json = await login_response.json()
    okapi.token = login_json['okapiToken']

    if login_response.ok:
        folio_button = document.getElementById("folioButton")
        folio_button.classList.remove("btn-outline-danger")
        folio_button.classList.add("btn-outline-success")
        services()

async def load_marc_record(marc_file):
    if marc_file.element.files.length > 0:
        marc_file_item = marc_file.element.files.item(0)
        marc_binary = await marc_file_item.text()
        marc_reader = pymarc.MARCReader(io.BytesIO(bytes(marc_binary, encoding='utf-8')))
        marc_record = next(marc_reader)
        return str(marc_record)

async def get_instance(okapi, uuid):
    kwargs = {
	"headers": {
            "Content-type": "application/json",
            "x-okapi-token": okapi.token,
            "x-okapi-tenant": okapi.tenant
        }
    }

    instance_response = await pyfetch(f"{okapi.url}/instance-storage/instances/{uuid}", **kwargs)

    if instance_response.ok:
        instance = await instance_response.json()
        return instance
     
