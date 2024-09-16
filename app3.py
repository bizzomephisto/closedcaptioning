import asyncio
import pyaudio
import websockets

# WebSocket URLs
TRANSCRIPTION_WS_URL = "ws://192.168.0.206:8000/ws/captions"  # Update with your main server address
LOCAL_CAPTION_WS_URL = "ws://localhost:9000/ws/captions-web"

# Audio settings (WAV format)
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024

# Initialize pyaudio
p = pyaudio.PyAudio()

# Function to send audio to the transcription server
async def send_audio_data(transcription_ws, caption_ws):
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    try:
        while True:
            audio_data = stream.read(CHUNK)
            await transcription_ws.send(audio_data)  # Send raw audio data (PCM)

            # Receive transcription from the main server and send it to the local webpage
            try:
                caption = await asyncio.wait_for(transcription_ws.recv(), timeout=0.1)
                print(f"Received caption from transcription server: {caption}")  # Debugging: Verify transcription reception
                await caption_ws.send(caption)  # Send the caption to the local caption server
                print(f"Sent caption to local webpage: {caption}")  # Debugging: Verify caption is sent to local WebSocket
            except asyncio.TimeoutError:
                pass  # Continue sending audio even if no transcription is received yet

    except websockets.ConnectionClosed:
        pass
    finally:
        stream.stop_stream()
        stream.close()

# Function to run WebSocket connections
async def run_websocket():
    async with websockets.connect(TRANSCRIPTION_WS_URL) as transcription_ws:
        async with websockets.connect(LOCAL_CAPTION_WS_URL) as caption_ws:
            await send_audio_data(transcription_ws, caption_ws)

def main():
    asyncio.run(run_websocket())

if __name__ == "__main__":
    main()
