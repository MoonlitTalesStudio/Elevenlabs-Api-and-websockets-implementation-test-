import base64
import json
import asyncio
import time
import os
from dotenv import load_dotenv
from pathlib import Path
import websockets

async def write_to_local(audio_stream):
    """
    Receive the stream as an input, check latency and write to disk .
    Implements the 'Resume Download' logic with flush e fsync.
    """
    last_time = time.perf_counter()
    
    with open('./web_socket_test_latency.mp3', "wb") as f:
        async for chunk in audio_stream:
            if chunk:
                # 1. Calculate latency (Like newtorks congestions)
                current_time = time.perf_counter()
                if (current_time - last_time) > 15:
                    # If we are dangerous close to the timedout (20s), we write everything we got on disk (we dont know if it is internet latency or system latency prior to a crash)
                    f.flush()
                    os.fsync(f.fileno())
                    print(f"\n[WATCHDOG] High latency: {(current_time - last_time):.2f}s. Emergency saving executed.")
                
                last_time = current_time

                # 2. Direct disk writing
                f.write(chunk)
                
        # 3. Transaction closure (Final flush before break/close)
        f.flush()
        os.fsync(f.fileno())
        print("\n[FINISH] Stream completed. File finalized on disk.")

async def listen(websocket):
    while True:
        try:
            message = await websocket.recv()
            data = json.loads(message)
            
            if data.get("audio"):
                yield base64.b64decode(data["audio"])
            
            elif data.get('isFinal'):
                break
        except websockets.exceptions.ConnectionClosed:
            print("Connessione chiusa.")
            break

async def voice_websocket(voice_id: str, text: str):
    load_dotenv(".env")
    api_key = os.getenv("ELEVENLABS_API_KEY")
    model_id = 'eleven_flash_v2_5'
    uri = f"wss://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream-input?model_id={model_id}"
    
    async with websockets.connect(uri) as websocket:
        listen_task = asyncio.create_task(write_to_local(listen(websocket)))
        
        await websocket.send(json.dumps({
            "text": " ",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.8, "use_speaker_boost": False},
            "xi_api_key": api_key,
        }))
        
        await websocket.send(json.dumps({"text": text}))
        
        await websocket.send(json.dumps({"text": ""}))
        
        await listen_task
        
if __name__ == "__main__":
    VOICE_ID = "JsGvsyDJpK0DdmEORFDa"
    SAMPLE_TEXT = "Today is a beautiful day for a walk in the woods... Look the sunrise is so beautiful today. Don't you agree?"

    asyncio.run(voice_websocket(VOICE_ID, SAMPLE_TEXT))

#The code was implemeted with official elevenlabs documentation and AI boilerplate generation, while the possibile problems and possible solution that they could not being really needed but they add for this test some personal insight