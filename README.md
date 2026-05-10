# ElevenLabs WebSocket Implementation Test

This project is a technical implementation test using **ElevenLabs WebSockets** for real-time text-to-speech streaming.

## Key Features & Defensive Programming

Beyond the standard API integration, this implementation focuses on **system resilience** and **data durability**:

*   **Asynchronous Streaming**: Leverages `asyncio` and `websockets` to achieve low-latency audio processing.
*   **Latency Watchdog**: A custom monitoring logic that tracks the time between chunks. If latency exceeds 15 seconds (nearing the server's 20s timeout), the system triggers an emergency save.
*   **Data Integrity (Flush & Fsync)**: Unlike standard buffered writing, this script uses `f.flush()` and `os.fsync()` during high-latency events. This ensures that received data is physically committed to the disk, preventing data loss in case of system saturation, network drops, or process crashes.

## Development Philosophy

The core structure follows the official ElevenLabs documentation. AI tools, such as Gemini and ElevenLabs AI Agent, were utilized to streamline the boilerplate and explore advanced I/O functions.

The **personal insight** added here is the "Safety First" approach: identifying potential "stalls" in the event loop and forcing disk synchronization before a potential failure occurs.
