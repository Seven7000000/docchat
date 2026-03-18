# DocChat AI

Upload any PDF and have an intelligent conversation with it. Ask questions, get accurate answers grounded in your document -- no hallucinations.

![DocChat AI Screenshot](static/screenshot.png)
<!-- Replace with actual screenshot -->

## Features

- **PDF Upload & Parsing** -- Extracts text from any PDF (up to 50,000 characters)
- **Conversational Q&A** -- Ask follow-up questions with full conversation history
- **Grounded Answers** -- Responses cite only what's in your document
- **Multi-Page Support** -- Handles PDFs of any length
- **Fast Responses** -- Powered by Claude Sonnet via OpenRouter API
- **No Database Required** -- Runs entirely in-memory, zero setup

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python) |
| AI Model | Claude Sonnet 4 via OpenRouter |
| PDF Processing | PyPDF2 |
| Frontend | HTML + TailwindCSS (CDN) |
| File Handling | python-multipart |

## Quick Start

### Prerequisites

- Python 3.10+
- OpenRouter API key ([get one here](https://openrouter.ai/keys))

### Installation

```bash
# Clone the repository
git clone https://github.com/Seven7000000/docchat.git
cd docchat

# Install dependencies
pip install -r requirements.txt

# Set your API key
export OPENROUTER_API_KEY="your-key-here"

# Run the server
uvicorn main:app --port 8001 --reload
```

Open [http://localhost:8001](http://localhost:8001) in your browser.

## API Reference

### `POST /upload`

Upload a PDF file for processing.

**Request:** `multipart/form-data` with a `file` field (PDF only)

**Response:**
```json
{
  "doc_id": "uuid-string",
  "filename": "document.pdf",
  "pages": 12,
  "chars": 45230
}
```

### `POST /chat`

Ask a question about an uploaded document.

**Request:**
```json
{
  "doc_id": "uuid-from-upload",
  "question": "What are the main findings?",
  "history": []
}
```

**Response:**
```json
{
  "answer": "Based on the document, the main findings are..."
}
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENROUTER_API_KEY` | Yes | Your OpenRouter API key |

## Project Structure

```
docchat/
  main.py             # FastAPI application
  requirements.txt    # Python dependencies
  static/
    index.html         # Single-page frontend
```

## License

MIT
