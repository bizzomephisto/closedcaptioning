from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

@app.get("/")
async def get():
    return HTMLResponse("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Real-Time Captions</title>
            <style>
                body { font-family: Arial, sans-serif; }
                #captions { font-size: 24px; color: #333; padding: 20px; }
            </style>
        </head>
        <body>
            <h1>Live Captions</h1>
            <div id="captions">Waiting for captions...</div>
            <script>
                let ws = new WebSocket("ws://localhost:9000/ws/captions-web");

                ws.onmessage = function(event) {
                    document.getElementById("captions").innerText = event.data;
                };

                ws.onerror = function(event) {
                    console.log("WebSocket error:", event);
                };
            </script>
        </body>
        </html>
    """)

@app.websocket("/ws/captions-web")
async def captions_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Keep the connection alive to receive captions
            data = await websocket.receive_text()  # Receive captions from the client
            print(f"Received caption from client: {data}")  # Debugging: Print the caption received from the client
            await websocket.send_text(data)  # Send caption to the webpage
    except WebSocketDisconnect:
        pass  # Handle disconnection properly

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
