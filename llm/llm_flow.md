# LLM Hotel Agent Workflow Documentation

## Overview
This document outlines the comprehensive workflow of the LLM-powered Hotel Agent system built with LangGraph, LangChain, and modern AI technologies. The system provides intelligent hotel management with advanced memory capabilities, contextual understanding, and seamless API integration.

## 🏗️ Architecture Overview

### Core Components
```
┌─────────────────────────────────────────────────────────────────┐
│                    Hotel Agent System                           │
├─────────────────────────────────────────────────────────────────┤
│  🧠 LLM Layer (GPT-4o/Ollama/NVIDIA)                          │
│  🔄 LangGraph Workflow Engine                                  │
│  💾 Memory Management (ChromaDB + Vector Embeddings)          │
│  🛠️ Tool Integration (Guest/Booking/Room/Payment)             │
│  🔗 API Integration Layer                                       │
│  📊 State Management                                            │
└─────────────────────────────────────────────────────────────────┘
```

## 🔄 Workflow Process

### 1. Request Initialization
```python
# Entry point: hotel_agent_service.py:181
async def handle_conversation(message, thread_id, context)
```

**Flow:**
1. **Thread Management**: Creates or retrieves conversation thread
2. **State Initialization**: Sets up `HotelAgentState` with messages and context
3. **Configuration**: Prepares LangGraph execution config
4. **Graph Invocation**: Triggers the workflow graph

### 2. LangGraph Workflow Nodes

#### Node Flow Sequence:
```
START → prepare_context → load_memories → agent → [tools/END] → process_response → agent
```

#### A. **Prepare Context Node** (`_prepare_context`)
**Location:** `hotel_agent_service.py:390`

**Purpose:** Identify and link guests to conversation threads

**Process:**
- Extract thread ID from configuration
- Check existing guest-thread associations via `memory_service.get_thread_guest()`
- **Email Detection:** Use regex to find email in message content
- **Guest Lookup:** Query API for guest by email
- **Auto-Linking:** Link identified guest to current thread
- Update context with guest_id and thread_id

**Key Features:**
- Automatic guest identification from conversation
- Cross-thread memory persistence
- Context enrichment for personalization

#### B. **Load Memories Node** (`_load_memories`)
**Location:** `hotel_agent_service.py:443`

**Purpose:** Retrieve relevant memories for context-aware responses

**Memory Types Retrieved:**
1. **Interaction History:** Previous conversations via similarity search
2. **Guest Preferences:** Stored preferences (room type, view, etc.)
3. **Booking History:** Recent bookings and stays
4. **Cross-thread Memories:** Memories that persist across conversations

**Process:**
```python
memories = await self.memory_service.recall_memories(
    query=query,
    guest_id=guest_id, 
    thread_id=thread_id,
    limit=5
)
```

#### C. **Agent Node** (`_call_model`)
**Location:** `hotel_agent_service.py:230`

**Purpose:** Process input with LLM and generate responses

**Enhanced Context Building:**
- **Hotel Information:** Fetches current hotel details via `HotelUtils.get_all_hotel_name()`
- **Tool Descriptions:** Formats available tools for LLM
- **Memory Integration:** Includes recalled memories in prompt
- **Prompt Engineering:** Uses `Prompt.prompt_agent()` with contextual information

**LLM Configuration:**
```python
self.llm = ChatOpenAI(
    model="gpt-4o-2024-08-06",
    temperature=0.4
).bind_tools(self.tools)
```

**Response Types:**
- Direct text responses (END workflow)
- Tool calls (continue to tools node)

#### D. **Tools Node** (LangChain ToolNode)
**Purpose:** Execute requested tool operations

**Available Tool Categories:**
- **Guest Tools:** `search_guest`, `create_guest`, `update_guest`
- **Room Tools:** `get_all_rooms`
- **Booking Tools:** `create_booking`, `check_booking_status`, `get_guest_bookings`, `list_bookings`
- **Invoice Tools:** `generate_invoice`

#### E. **Process Response Node** (`_process_tool_results`)
**Location:** `hotel_agent_service.py:502`

**Purpose:** Extract context and save memories from tool responses

**Context Extraction:**
- **Guest Identification:** Parse guest IDs from search/create responses
- **Booking Information:** Extract booking details for memory storage
- **Preference Detection:** Identify room preferences from user messages
- **Thread Linking:** Link newly identified guests to conversation threads

**Memory Storage Triggers:**
- **Guest Creation/Search:** Link guest to thread
- **Booking Operations:** Save booking memories
- **Preference Detection:** Store guest preferences
- **Interaction Logging:** Save user-assistant exchanges

### 3. Memory Management System

#### Memory Service Architecture
**Location:** `app/services/memory_service.py`

**Storage Backend:** ChromaDB with vector embeddings

#### Memory Types:

##### A. **Guest Preferences** (`save_guest_preference`)
```python
await memory_service.save_guest_preference(
    guest_id=guest_id,
    preference_type="room_type", 
    value="deluxe",
    thread_id=thread_id
)
```

**Stored Preferences:**
- Room types (suite, deluxe, standard, etc.)
- View preferences (ocean, mountain, garden, etc.)
- Special requirements
- Service preferences

##### B. **Booking Memories** (`save_booking_memory`)
```python
await memory_service.save_booking_memory(
    guest_id=guest_id,
    booking_id=booking_id,
    hotel_id=hotel_id,
    check_in=check_in_date,
    check_out=check_out_date
)
```

**Booking Context:**
- Booking IDs and details
- Date ranges and duration
- Room and hotel associations
- Guest count and special requests

##### C. **Interaction Memories** (`save_interaction_memory`)
```python
await memory_service.save_interaction_memory(
    thread_id=thread_id,
    content="User: ... Assistant: ...",
    guest_id=guest_id
)
```

**Conversation Context:**
- User-assistant exchanges
- Problem resolution history
- Service interactions
- Cross-thread accessibility

##### D. **Thread Linking** (`link_guest_to_thread`)
**Purpose:** Enable cross-conversation continuity
```python
await memory_service.link_guest_to_thread(
    guest_id=guest_id,
    thread_id=thread_id
)
```

### 4. Tool Integration System

#### Tool Architecture
**Location:** `app/tools/`

Each tool follows LangChain tool pattern:
```python
@tool("tool_name", args_schema=SchemaClass)
async def tool_function(param1, param2):
    # API integration via APIUtils
    response = await APIUtils.post("/endpoint", data)
    return response
```

#### Guest Management Tools (`guest_tools.py`)
- **`search_guest`:** Find guests by name, email, or phone
- **`create_guest`:** Register new guests with full profile
- **`update_guest`:** Modify existing guest information

#### Booking Management Tools (`booking_tools.py`)
- **`create_booking`:** New reservation creation
- **`check_booking_status`:** Retrieve booking information
- **`get_guest_bookings`:** List all guest reservations
- **`list_bookings`:** Filter bookings by criteria

#### Room Management Tools (`room_tools.py`)
- **`get_all_rooms`:** Available room inventory
- **`check_room_availability`:** Date-based availability

### 5. State Management

#### HotelAgentState Structure
**Location:** `app/states/hotel_agent_state.py`

```python
class HotelAgentState(TypedDict):
    messages: Annotated[list, add_messages]  # LangGraph message handling
    current_tool: Optional[str]              # Active tool tracking
    recall_memories: List[str]               # Retrieved memories
    context: Dict[str, Optional[UUID]]       # Guest/hotel/room IDs
    thread_id: Optional[str]                 # Conversation ID
```

**State Evolution:**
1. **Initial:** Basic message and context
2. **Context Enrichment:** Guest identification and linking
3. **Memory Loading:** Historical context retrieval
4. **Tool Processing:** Context updates from tool responses
5. **Response Generation:** Final state with complete context

### 6. Prompt Engineering

#### System Prompt Structure
**Location:** `app/prompts/prompt_v2.py`

**Components:**
1. **Role Definition:** Hotel assistant with memory capabilities
2. **Hotel Profile:** Dynamic hotel information injection
3. **Available Tools:** Tool descriptions and usage guidelines
4. **Memory Context:** Recalled memories for personalization
5. **Instruction Guidelines:** Behavior and response patterns

**Key Prompt Features:**
- Memory-aware response generation
- Tool usage requirements
- Personalization guidelines
- Natural conversation flow
- Context-aware recommendations

## 🚀 Key Workflow Advantages

### 1. **Intelligent Context Building**
- Automatic guest identification from conversations
- Cross-thread memory persistence
- Dynamic context enrichment

### 2. **Advanced Memory Management**
- Vector-based similarity search for relevant memories
- Multi-type memory storage (preferences, bookings, interactions)
- Cross-conversation continuity

### 3. **Seamless Tool Integration**
- Automatic tool selection based on user intent
- Context extraction from tool responses
- Memory updates from tool operations

### 4. **Personalized Interactions**
- Guest preference awareness
- Booking history consideration
- Tailored recommendations

### 5. **Robust State Management**
- Persistent conversation tracking
- Context preservation across tool calls
- Error recovery and graceful handling

## 🔧 Configuration Options

### LLM Providers
```python
# OpenAI (Default)
self.llm = ChatOpenAI(model="gpt-4o-2024-08-06", temperature=0.4)

# Ollama (Local)
self.llm = ChatOllama(model="gemma3:12b", temperature=0.4)

# NVIDIA NIM
self.llm = ChatNVIDIA(model="deepseek-ai/deepseek-r1", temperature=0.2)
```

### Embedding Models
```python
# OpenAI (Default)
self.embeddings = OpenAIEmbeddings()

# HuggingFace (Local)
self.embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Ollama (Local)
self.embeddings = OllamaEmbeddings(model="llama3.1")
```

### Memory Configuration
```python
# ChromaDB Setup
self.memory_store = Chroma(
    collection_name="hotel_memories",
    embedding_function=self.embeddings,
    persist_directory="output/chromadb"
)
```

## 📈 Performance Features

### 1. **Efficient Memory Retrieval**
- Vector similarity search for relevant memories
- Metadata filtering for targeted queries
- Configurable memory limits

### 2. **Context Optimization**
- Token limit management with tiktoken
- Selective memory inclusion
- Dynamic prompt sizing

### 3. **Error Handling**
- Graceful degradation on tool failures
- Memory operation fallbacks
- Comprehensive logging

### 4. **Scalable Architecture**
- Stateless workflow design
- Persistent memory storage
- Multi-conversation support

## 🎯 Best Practices for Implementation

### 1. **Memory Management**
- Regularly monitor ChromaDB size
- Implement memory cleanup strategies
- Use appropriate embedding models for domain

### 2. **Tool Development**
- Follow LangChain tool patterns
- Include comprehensive error handling
- Validate input schemas thoroughly

### 3. **Prompt Engineering**
- Test prompts with various conversation scenarios
- Include clear tool usage instructions
- Balance context length with relevance

### 4. **State Management**
- Keep state updates atomic
- Handle concurrent conversation scenarios
- Implement proper error recovery

This workflow creates a sophisticated, memory-aware hotel management assistant that provides personalized service while maintaining conversation continuity across multiple interactions.