import json

from typing import Optional
from pydantic import BaseModel
from pyodide.http import pyfetch

from js import document, Headers

class Okapi(BaseModel):
    url: str = ""
    tenent: str = ""
    token: str = ""


def services():
    modal_body = document.getElementById("folioModalBody")
    modal_body.innerHTML = ""    
    modal_label = document.getElementById("folioModalLabel")
    modal_label.innerHTML = "FOLIO Services"



async def login(okapi: Okapi):
    okapi_url = document.getElementById("okapiURI")
    tenant = document.getElementById("folioTenant")
    user = document.getElementById("folioUser")
    password = document.getElementById("folioPassword")

    okapi.url = okapi_url.value
    okapi.tenent = tenant.value


    headers = {
        "Content-type": "application/json",
        "x-okapi-tenant": okapi.tenent
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
                     
     
    
