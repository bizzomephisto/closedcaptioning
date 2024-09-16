import whisper
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import wave
import io
import numpy as np

app = FastAPI()

# Allow all origins (CORS for WebSocket)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the Whisper model
print("Starting to load Whisper model...")
model = whisper.load_model("base")
print("Whisper model loaded successfully.")

@app.get("/")
def read_root():
    return {"message": "Whisper server is running"}

@app.websocket("/ws/captions")
async def captions_socket(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connection accepted")
    audio_data = b''

    try:
        while True:
            chunk = await websocket.receive_bytes()
            print(f"Received audio data chunk from client, size: {len(chunk)} bytes")
            audio_data += chunk

            # When enough audio has been accumulated, transcribe
            if len(audio_data) >= 32000:  # Transcribe after roughly 2 seconds (32 KB = 2 seconds at 16kHz)
                audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

                # Transcribe using Whisper
                result = model.transcribe(audio_np)
                print(f"Transcription: {result['text']}")

                # Send transcription to client
                await websocket.send_text(result["text"])
                
                # Clear the buffer after transcription
                audio_data = b''

    except WebSocketDisconnect:
        print("WebSocket disconnected, stopping audio reception.")
    except Exception as e:
        print(f"Error during audio reception: {e}")

# Run the FastAPI server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
