from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from app.stocks import Stocks

app = FastAPI()
stocks = Stocks()

# Allow front-end app which runs at 3000 to send requests to our backend
origins = ["http://localhost:3000", "localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/stock/{ticket_name}/{start}/{end}")
async def handle_df(ticket_name: str, start: str, end: str):
    graph_image = stocks.plot_by_stock(name = ticket_name, start=start, end=end)

    # TODO: Drop down for ticker data

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>displayDF</title>
        </head>
        <body>
        <h2>Support Resistance Level:</h2>
            {graph_image}
        </body>
    </html>
    """

    return HTMLResponse(content=html_content, status_code=200)

@app.get("/")
async def root():
    return {"message":"Hello World"}