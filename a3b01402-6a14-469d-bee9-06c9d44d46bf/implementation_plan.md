# Scam Detection & Honeypot System - Implementation Plan

## Goal
Build a Python-based system that implements the "Elite Scam Detection & Honeypot Extraction" logic defined by the user. The system will process incoming messages, detect scams using Regex and (simulated) LLM analysis, and if a scam is detected, engage using the "Deepak Sharma" persona.

## Proposed Changes

### Project Structure
`scamsafe_bot/`
- `main.py`: Entry point CLI.
- `prompts.py`: Stores the system prompts (Phase 1 & Phase 2).
- `detector.py`: Handles Phase 1 logic (Regex patterns + LLM stub).
- `persona.py`: Handles Phase 2 logic (Persona management + Intel extraction).
- `session_manager.py`: Manages state and JSON logging.
- `utils.py`: Helper functions for JSON parsing and simulated latency.

### Detailed Component Logic

#### `prompts.py`
- Will contain `PHASE_1_SYSTEM_PROMPT` and `PHASE_2_PERSONA_PROMPT` as raw strings, copied exactly from the user's specification.

#### `detector.py`
- **Regex Engine**: Implement the Critical Pattern Recognition (UPI, Bank, Phishing, Keywords).
- **LLM Classifier**: A function `assess_threat(message)` that constructs the prompt and returns the JSON verdict. *Note: We will mock the actual LLM API call for this demonstration unless configured otherwise, or use a placeholder that returns logical responses based on keywords.*

#### `persona.py`
- **Persona Engine**: Manages the conversation history.
- **Intel Extraction**: Parses the "extracted_intel" from the LLM response.
- **Turn Management**: Tracks the turn count to escalate the persona's behavior (Confusion -> Leakage -> Commitment -> Max Extraction).

#### `main.py`
- A `while True` loop to accept user input (simulating a scammer).
- Prints the "Backend logs" (JSON) and the "Public response" (Text) as specified.

## Verification Plan
### Manual Verification
- Run `python main.py`.
- Paste a sample scam message (e.g., "Urgent! Your SBI account blocked. Click bit.ly/123 to verify").
- Verify the system outputs the detection JSON.
- Verify the system switches to "Deepak" and responds.
- Continue the conversation for 3-4 turns to verify state updates.
