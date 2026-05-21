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

    df = pd.read_excel(EXCEL_PATH)

    return df.to_dict(orient="records")


@mcp.tool()
def get_delivery_by_zone(zone_id: int) -> list:
    """
    Get delivery prices for a specific zone.
    """

    df = pd.read_excel(EXCEL_PATH)

    filtered = df[df["id_zone"] == zone_id]

    return filtered.to_dict(orient="records")


@mcp.tool()
def get_delivery_by_carrier(carrier_name: str) -> list:
    """
    Get delivery rows by carrier name.
    """

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


# MCP SSE transport
app.mount("/mcp", mcp.sse_app())