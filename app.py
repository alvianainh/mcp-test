import pandas as pd

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from mcp.server.fastmcp import FastMCP
import os
import requests
import json

from dotenv import load_dotenv

load_dotenv()

HUBSPOT_TOKEN = os.getenv("HUBSPOT_TOKEN")

app = FastAPI()

mcp = FastMCP("hubspot-demo-app")

BASE_URL = "https://api.hubapi.com"

def hubspot_get(endpoint: str, params: dict = None):
    headers = {
        "Authorization": f"Bearer {HUBSPOT_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.get(
        f"{BASE_URL}{endpoint}",
        headers=headers,
        params=params
    )

    response.raise_for_status()

    return response.json()

@app.post("/hubspot/webhook")
async def hubspot_webhook(req: Request):

    print("===== HUBSPOT WEBHOOK RECEIVED =====")

    body = await req.body()

    print(body)

    return {"status": "received"}


@mcp.tool()
def get_all_contacts() -> list:
    """
    Get all HubSpot contacts.
    """

    print("TOOL CALLED: get_all_contacts")

    data = hubspot_get(
        "/crm/v3/objects/contacts",
        {
            "limit": 100,
            "properties": "firstname,lastname,email"
        }
    )

    return data.get("results", [])

@mcp.tool()
def get_all_deals() -> list:
    """
    Get all HubSpot deals.
    """

    print("TOOL CALLED: get_all_deals")

    data = hubspot_get(
        "/crm/v3/objects/deals",
        {
            "limit": 100,
            "properties": "dealname,amount,dealstage"
        }
    )

    return data.get("results", [])

@mcp.tool()
def search_contact_by_email(email: str) -> list:
    """
    Search HubSpot contact by email.
    """

    print("TOOL CALLED: search_contact_by_email")

    headers = {
        "Authorization": f"Bearer {HUBSPOT_TOKEN}",
        "Content-Type": "application/json"
    }

    body = {
        "filterGroups": [
            {
                "filters": [
                    {
                        "propertyName": "email",
                        "operator": "EQ",
                        "value": email
                    }
                ]
            }
        ],
        "properties": [
            "firstname",
            "lastname",
            "email"
        ],
        "limit": 10
    }

    response = requests.post(
        f"{BASE_URL}/crm/v3/objects/contacts/search",
        headers=headers,
        json=body
    )

    response.raise_for_status()

    data = response.json()

    return data.get("results", [])



@app.get("/")
async def root():
    return {
        "status": "ok"
    }

@app.get("/test")
def test():
    return get_all_contacts()


# MCP SSE transport
app.mount("/mcp", mcp.sse_app())