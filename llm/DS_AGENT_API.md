# Data Science Agent API Documentation

## Overview
The Data Science Agent V2 API provides educational assistance for students learning probability, statistics, machine learning, and deep learning. It supports data analysis, visualization, ML training, PDF processing, and image analysis.

## Base URL
```
/api/v2/ds-agent
```

---

## Endpoints

### 1. Chat (Non-Streaming)
**POST** `/api/v2/ds-agent/chat`

Send a message to the data science agent and receive a complete response.

#### Request

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
    "message": "Can you analyze the correlation in my dataset.csv?",
    "thread_id": "optional-thread-id-for-continuity"
}
```

**Fields:**
- `message` (string, required): Student's question or request
- `thread_id` (string, optional): Thread ID for conversation continuity. If not provided, a new thread is created.

#### Response

**Status:** `200 OK`

```json
{
    "response": "I'll analyze the correlations in your dataset. Let me load the data first...\n\n[Analysis results with interpretations]",
    "thread_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Fields:**
- `response` (string): Agent's complete response
- `thread_id` (string): Thread ID for this conversation

#### Error Response

**Status:** `500 Internal Server Error`

```json
{
    "detail": "Error processing chat request: [error details]"
}
```

---

### 2. Chat Stream (Server-Sent Events)
**POST** `/api/v2/ds-agent/chat/stream`

Stream the agent's response in real-time with thinking process, tool calls, and token-by-token output.

#### Request

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
    "message": "Train a linear regression model on houses.csv to predict prices",
    "thread_id": "optional-thread-id"
}
```

#### Response

**Content-Type:** `text/event-stream`

**Headers:**
```
Cache-Control: no-cache
Connection: keep-alive
X-Accel-Buffering: no
```

**Event Stream Format:**

The response is a stream of Server-Sent Events (SSE). Each event is in the format:
```
data: {JSON_OBJECT}\n\n
```

#### Event Types

**1. Start Event**
```json
data: {
    "type": "start",
    "thread_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**2. Thinking Event** (Model's internal reasoning)
```json
data: {
    "type": "thinking",
    "content": "I need to first load the dataset to understand its structure..."
}
```

**3. Tool Call Event** (When agent uses a tool)
```json
data: {
    "type": "tool_call",
    "step": "tools",
    "tool_calls": [
        {
            "name": "read_csv",
            "args": {
                "file_path": "houses.csv"
            }
        }
    ]
}
```

**4. Token Event** (Streaming response text)
```json
data: {
    "type": "token",
    "content": "I"
}

data: {
    "type": "token",
    "content": " analyzed"
}

data: {
    "type": "token",
    "content": " your"
}
```

**5. Thinking Stats Event** (Reasoning token usage)
```json
data: {
    "type": "thinking_stats",
    "reasoning_tokens": 1247
}
```

**6. Done Event**
```json
data: {
    "type": "done",
    "thread_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**7. Error Event**
```json
data: {
    "type": "error",
    "error": "Error message details"
}
```

---

## Example Usage

### Using cURL (Non-Streaming)

```bash
curl -X POST "http://localhost:8000/api/v2/ds-agent/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Analyze the correlation between age and salary in employees.csv",
    "thread_id": null
  }'
```

### Using cURL (Streaming)

```bash
curl -X POST "http://localhost:8000/api/v2/ds-agent/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create a histogram of the age column in employees.csv"
  }' \
  --no-buffer
```

### Using Python (Non-Streaming)

```python
import requests

url = "http://localhost:8000/api/v2/ds-agent/chat"
payload = {
    "message": "What's the distribution of grades in students.csv?",
    "thread_id": None
}

response = requests.post(url, json=payload)
result = response.json()

print(f"Response: {result['response']}")
print(f"Thread ID: {result['thread_id']}")
```

### Using Python (Streaming)

```python
import requests
import json

url = "http://localhost:8000/api/v2/ds-agent/chat/stream"
payload = {
    "message": "Train a random forest model on my data",
    "thread_id": None
}

with requests.post(url, json=payload, stream=True) as response:
    for line in response.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                event_data = json.loads(line_str[6:])

                if event_data['type'] == 'token':
                    print(event_data['content'], end='', flush=True)
                elif event_data['type'] == 'thinking':
                    print(f"\n[Thinking: {event_data['content']}]")
                elif event_data['type'] == 'tool_call':
                    print(f"\n[Tool: {event_data['tool_calls']}]")
                elif event_data['type'] == 'done':
                    print(f"\n\nConversation ID: {event_data['thread_id']}")
```

### Using JavaScript (Fetch API + SSE)

```javascript
// Non-streaming
async function chatWithDSAgent(message, threadId = null) {
    const response = await fetch('/api/v2/ds-agent/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            message: message,
            thread_id: threadId
        })
    });

    const result = await response.json();
    console.log('Response:', result.response);
    console.log('Thread ID:', result.thread_id);
    return result;
}

// Streaming
function streamChatWithDSAgent(message, threadId = null) {
    fetch('/api/v2/ds-agent/chat/stream', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            message: message,
            thread_id: threadId
        })
    }).then(response => {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        function readStream() {
            reader.read().then(({ done, value }) => {
                if (done) {
                    console.log('Stream complete');
                    return;
                }

                const chunk = decoder.decode(value);
                const lines = chunk.split('\n\n');

                lines.forEach(line => {
                    if (line.startsWith('data: ')) {
                        const event = JSON.parse(line.slice(6));

                        switch(event.type) {
                            case 'start':
                                console.log('Started:', event.thread_id);
                                break;
                            case 'thinking':
                                console.log('[Thinking]:', event.content);
                                break;
                            case 'tool_call':
                                console.log('[Tool]:', event.tool_calls);
                                break;
                            case 'token':
                                process.stdout.write(event.content);
                                break;
                            case 'done':
                                console.log('\nDone:', event.thread_id);
                                break;
                            case 'error':
                                console.error('Error:', event.error);
                                break;
                        }
                    }
                });

                readStream();
            });
        }

        readStream();
    });
}

// Usage
chatWithDSAgent("Analyze correlations in my dataset.csv");
streamChatWithDSAgent("Create a scatter plot of X vs Y");
```

---

## Common Use Cases

### 1. Data Analysis
```json
{
    "message": "Load data.csv and show me summary statistics",
    "thread_id": null
}
```

### 2. Statistical Testing
```json
{
    "message": "Perform a t-test on the 'scores' column against a mean of 75",
    "thread_id": "existing-thread-id"
}
```

### 3. Visualization
```json
{
    "message": "Create a correlation heatmap for all numeric columns in dataset.csv",
    "thread_id": null
}
```

### 4. Machine Learning
```json
{
    "message": "Train a random forest classifier to predict 'outcome' using features X1, X2, X3",
    "thread_id": null
}
```

### 5. PDF Exercise Processing
```json
{
    "message": "Process the PDF exercise sheet I uploaded: /path/to/exercise.pdf",
    "thread_id": null
}
```

### 6. Image Analysis
```json
{
    "message": "Analyze the math problem in this image: /path/to/problem.jpg",
    "thread_id": null
}
```

---

## Available Tools (Auto-Used by Agent)

The agent automatically selects and uses these tools based on your request:

### Data Loading
- `read_csv` - Load and summarize CSV files
- `read_excel` - Load and summarize Excel files
- `get_column_info` - Get detailed column statistics

### Statistical Analysis
- `correlation_analysis` - Calculate correlation matrices
- `hypothesis_test` - Perform t-tests and normality tests
- `distribution_analysis` - Analyze distributions

### Visualization
- `create_histogram` - Generate histograms
- `create_scatter_plot` - Create scatter plots
- `create_correlation_heatmap` - Visualize correlations
- `create_box_plot` - Box plots for outlier detection

### Machine Learning
- `train_linear_regression` - Train linear models
- `train_random_forest` - Train random forests
- `make_prediction` - Make predictions with models

### Document Processing
- `process_pdf_document` - Process PDF exercises
- `search_document_content` - Search PDFs
- `extract_pdf_text` - Extract PDF text

### Image Analysis
- `analyze_exercise_image` - Analyze math problems
- `extract_math_equations` - Extract equations
- `analyze_graph_chart` - Analyze charts/graphs

---

## Thread Management

**Thread ID** allows conversation continuity:
- First request: Don't provide `thread_id` (or set to `null`)
- Subsequent requests: Use the `thread_id` from the first response
- This allows the agent to remember context and previous analyses

Example flow:
```python
# First message
response1 = chat("Load dataset.csv")
thread = response1['thread_id']

# Follow-up (remembers previous context)
response2 = chat("Now create a histogram of age", thread_id=thread)
response3 = chat("What's the correlation with salary?", thread_id=thread)
```

---

## Error Handling

All errors return HTTP 500 with details:
```json
{
    "detail": "Error processing chat request: File not found"
}
```

Common errors:
- File not found
- Invalid data format
- Missing required columns
- Model training failures
- Tool execution errors

The agent handles errors gracefully and provides guidance.
