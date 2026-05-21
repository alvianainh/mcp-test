import pandas as pd

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from mcp.server.fastmcp import FastMCP

app = FastAPI()

mcp = FastMCP("delivery-demo-app")


EXCEL_PATH = "data_delivery.xlsx"


@mcp.tool()
def get_all_delivery_data() -> list:
    """
    Return all delivery data from Excel.
    """
    print("TOOL CALLED: get_all_delivery_data")

    df = pd.read_excel(EXCEL_PATH)

    return df.to_dict(orient="records")


@mcp.tool()
def get_delivery_by_zone(zone_id: int) -> list:
    """
    Get delivery prices for a specific zone.
    """
    print("TOOL CALLED: get_delivery_by_zone")

    df = pd.read_excel(EXCEL_PATH)

    filtered = df[df["id_zone"] == zone_id]

    return filtered.to_dict(orient="records")


@mcp.tool()
def get_delivery_by_carrier(carrier_name: str) -> list:
    """
    Get delivery rows by carrier name.
    """
    print("TOOL CALLED: get_delivery_by_carrier")

    df = pd.read_excel(EXCEL_PATH)

    filtered = df[
        df["carrier_name"].str.lower().str.contains(
            carrier_name.lower(),
            na=False
        )
    ]

    return filtered.to_dict(orient="records")


@mcp.tool()
def get_max_delivery_price() -> dict:
    """
    Get the highest delivery price.
    """
    print("TOOL CALLED: get_max_delivery_price")

    df = pd.read_excel(EXCEL_PATH)

    prices = (
        df["price"]
        .astype(str)
        .str.replace(".", "", regex=False)
        .astype(int)
    )

    max_price = prices.max()

    return {
        "max_delivery_price": int(max_price)
    }


@app.get("/")
async def root():
    return {
        "status": "ok"
    }


@app.get("/widget/hello")
async def hello_widget():
    return HTMLResponse("""
    <html>
      <body style="font-family:sans-serif;padding:20px;">
        <h1>Delivery MCP App</h1>
        <p>Excel delivery data connected successfully.</p>
      </body>
    </html>
    """)


@app.get("/ui/delivery", response_class=HTMLResponse)
def delivery_ui():
    df = pd.read_excel(EXCEL_PATH)

    html_table = df.to_html(index=False)

    return f"""
    <html>
      <head>
        <title>Delivery Dashboard</title>
      </head>
      <body style="font-family: sans-serif; padding: 20px;">
        <h1>📦 Delivery Data</h1>
        <p>Simple MCP Demo UI</p>
        {html_table}
      </body>
    </html>
    """

@app.get("/ui/zone/{zone_id}", response_class=HTMLResponse)
def ui_by_zone(zone_id: int):
    df = pd.read_excel(EXCEL_PATH)
    filtered = df[df["id_zone"] == zone_id]

    return f"""
    <html>
      <body style="font-family:sans-serif;padding:20px;">
        <h2>Zone {zone_id}</h2>
        {filtered.to_html(index=False)}
      </body>
    </html>
    """


# MCP SSE transport
app.mount("/mcp", mcp.sse_app())