# SHL Assessment Recommendation System

An intelligent AI-powered system for recommending SHL assessments based on job descriptions and natural language queries using LangGraph, O, and RAG architecture.

## Deployment

### FastAPI Backend
The FastAPI backend is deployed and accessible at:
[https://shl-fastapi-y933.onrender.com/docs](https://shl-fastapi-y933.onrender.com/docs)


## API Endpoints

| Feature | Endpoint | Method | Description |
|---------|----------|--------|-------------|
| **Health Check** | `/api/health` | GET | Checks if the API is running and healthy. |
| **Recommendations** | `/api/recommend` | POST | Generates SHL assessment recommendations based on input. |
| **Chat** | `/api/chat` | POST | Chat-based interaction with the model. |
| **Session Management** | `/api/session/{session_id}` | GET | Retrieve a specific session and its data. |
| **Session Management** | `/api/session/{session_id}` | DELETE | Delete a specific session and clear its history. |
| **Session Management** | `/api/session/{session_id}/stats` | GET | Get statistics and metrics for a specific session. |
| **Assessment Search** | `/api/assessments/search` | GET | Search assessments by keyword or filters. |
| **Assessment Details** | `/api/assessments/{assessment_id}` | GET | Get detailed information about a specific assessment. |
| **Assessment Overview** | `/api/assessments/stats/overview` | GET | Get overview statistics of all available assessments. |
| **Test Types** | `/api/test-types` | GET | Retrieve the full list of SHL test types. |
| **Job Description Extraction** | `/api/extract-jd` | POST | Extract structured details from job descriptions. |
| **Refresh Data** | `/api/refresh` | POST | Refreshes vector embeddings and cached data. |
| **Refresh Status** | `/api/refresh/status` | GET | Check the status of the data refresh operation. |
| **Root** | `/` | GET | Root endpoint providing API information. |
| **API Info** | `/api` | GET | Get API metadata and version information. |
---

### Chainlit Frontend 
The Chainlit frontend interface is deployed at:
[https://shl-chainlit.onrender.com/](https://shl-chainlit.onrender.com/)

## Frontend Screenshots:


### Home Page
![Frontend Screenshot 1](images/1.png)

### Query containing  JD link
![Frontend Screenshot 2](images/2.png)

![Frontend Screenshot 2](images/3.png)

### JD in Query
![Frontend Screenshot 2](images/4.png)
![Frontend Screenshot 2](images/5.png)

### General Question
![Frontend Screenshot 2](images/10.png)

### FASTAPI Endpoints
![Frontend Screenshot 2](images/8.png)

![Frontend Screenshot 2](images/9.png)

---

## Architecture

### LangGraph Workflow

The complete orchestration flow showing how queries are processed through different agents and decision points:

```mermaid
graph TD
    Start([User Input via Chainlit]) --> InitState[Initialize Graph State]
   
    InitState --> SupervisorNode[Supervisor Node<br/>classify_intent]
   
    SupervisorNode --> SupervisorEdge{route_by_intent}
   
    SupervisorEdge -->|intent=jd_query| InputCheckNode[Input Check Node<br/>check for URL]
    SupervisorEdge -->|intent=general| GeneralNode[General Query Node<br/>answer_question]
    SupervisorEdge -->|intent=out_of_context| EndNode[End Node<br/>redirect_message]
   
    InputCheckNode --> URLCheckEdge{has_url?}
   
    URLCheckEdge -->|has_url=True| ExtractorNode[JD Extractor Node<br/>extract_url_and_fetch]
    URLCheckEdge -->|has_url=False| ProcessorNode[JD Processor Node]
   
    ExtractorNode --> ProcessorNode
   
    ProcessorNode --> EnhanceNode[Query Enhancement]
   
    EnhanceNode --> RAGNode[RAG Agent Node<br/>retrieve_and_rank]
   
    RAGNode --> RAGSubgraph[RAG Processing]
   
    subgraph RAGSubgraph[RAG Subgraph]
        direction TB
        EmbedStep[Embed Requirements] --> VectorSearchStep[ChromaDB Vector Search]
        VectorSearchStep --> RetrieveStep[Retrieve Top 15]
        RetrieveStep --> RerankDecision{RAG_ENABLE_LLM_RERANKING?}
        RerankDecision -->|True| LLMRerankStep[LLM Reranking]
        RerankDecision -->|False| ScoreRankStep[Score-Based Ranking]
        LLMRerankStep --> SelectStep[Select Top 5-10]
        ScoreRankStep --> SelectStep
    end
   
    RAGSubgraph --> FormatNode[Format Output Node<br/>create_table]
   
    FormatNode --> OutputNode([Return to Chainlit])
   
    GeneralNode --> GeneralSubgraph[General Query Processing]
   
    subgraph GeneralSubgraph[General Query Subgraph]
        direction TB
        EmbedQuery[Embed Query] --> SearchKB[Search Knowledge Base]
        SearchKB --> GenerateAns[Generate Answer]
    end
   
    GeneralSubgraph --> FormatGeneral[Format General Response]
    FormatGeneral --> OutputNode
   
    EndNode --> OutputNode
   
    style SupervisorNode fill:#ff9999,stroke:#cc0000,stroke-width:3px
    style RAGNode fill:#99ccff,stroke:#0066cc,stroke-width:3px
    style GeneralNode fill:#99ff99,stroke:#00cc00,stroke-width:3px
    style ExtractorNode fill:#ffcc99,stroke:#ff9900,stroke-width:3px
    style OutputNode fill:#cc99ff,stroke:#9900cc,stroke-width:3px
    style RAGSubgraph fill:#e6f3ff,stroke:#0066cc,stroke-width:2px
    style GeneralSubgraph fill:#e6ffe6,stroke:#00cc00,stroke-width:2px
    style LLMRerankStep fill:#ffeb99,stroke:#ffb300,stroke-width:2px
    style ScoreRankStep fill:#99ffeb,stroke:#00b38f,stroke-width:2px
    style RerankDecision fill:#ffffcc,stroke:#ffcc00,stroke-width:2px
```


---

## System Components

### Agents

The system uses 5 specialized AI agents orchestrated by LangGraph:

#### 1. **Supervisor Agent** (`app/agents/supervisor_agent.py`)
**Purpose:** Classifies user intent to route queries appropriately

**Key Functions:**
- Intent classification (jd_query, general, out_of_context)
- Confidence scoring
- Fallback keyword matching
- Query validation

**Technology:** 
- Gemini LLM with structured output
- Pydantic schema validation
- Pattern matching fallback

**Input:** Raw user query
**Output:** Intent classification with confidence score

---

#### 2. **JD Extractor Agent** (`app/agents/jd_extractor_agent.py`)
**Purpose:** Extracts URLs and fetches job descriptions from web pages

**Key Functions:**
- URL detection (regex + LLM)
- Web page fetching
- HTML parsing
- Job description extraction

**Technology:**
- BeautifulSoup4 for HTML parsing


**Input:** Query with potential URL
**Output:** Extracted job description text

---

#### 3. **JD Processor Agent** (`app/agents/jd_processor_agent.py`)
**Purpose:** Analyzes and enhances job descriptions

**Key Functions:**
- Skill extraction (technical & soft)
- Duration constraint detection
- Job level identification
- Test type inference
- Key requirement extraction

**Technology:**
- Gemini LLM for deep analysis
- Rule-based extraction as fallback
- Pydantic EnhancedQuery schema

**Input:** Job description or query text
**Output:** Structured requirements (EnhancedQuery)

---

#### 4. **RAG Agent** (`app/agents/rag_agent.py`)
**Purpose:** Retrieves and ranks relevant assessments using RAG

**Key Functions:**
- Vector similarity search
- LLM-based reranking
- Duration filtering
- Top-K selection (5-10 assessments)

**Technology:**
- ChromaDB vector search
- Gemini embeddings
- LLM reranking
- Custom balance algorithm

**Input:** Enhanced query with requirements
**Output:** 5-10 ranked assessments

**RAG Process (6 Steps):**
1. Embed requirements using Gemini
2. Vector search in ChromaDB (top 15-20)
3. Retrieve candidate assessments
4. LLM reranking for relevance
5. Select final 5-10 recommendations

---

#### 5. **General Query Agent** (`app/agents/general_query_agent.py`)
**Purpose:** Handles questions about assessments and the system

**Key Functions:**
- Answer FAQ questions
- Provide assessment details
- Explain system functionality
- Search knowledge base

**Technology:**
- Gemini LLM for generation
- ChromaDB for context retrieval
- Pre-defined FAQ responses

**Input:** General question
**Output:** Informative answer with optional related assessments

---

### Services

#### **LLM Service** (`app/services/llm_service.py`)
- Gemini API integration
- Structured output generation
- Intent classification
- Reranking

#### **Embedding Service** (`app/services/embedding_service.py`)
- Generate embeddings using Gemini
- Batch processing
- Query vs document embeddings
- Similarity computation

#### **Vector Store Service** (`app/services/vector_store_service.py`)
- ChromaDB operations
- Assessment indexing
- Vector search
- Collection management

#### **Scraper Service** (`app/services/scraper_service.py`)
- Web scraping SHL catalog
- Pagination handling
- Data extraction
- JSON storage

#### **Session Service** (`app/services/session_service.py`)
- Session management
- Interaction tracking
- Statistics calculation
- Database persistence

---

##  API Endpoints

### Core Endpoints

#### `POST /api/recommend`
**Purpose:** Get assessment recommendations for a job description

**Request:**
```json
{
  "query": "I need assessments for Java developers who can collaborate with teams"
}
```

**Response:**
```json
{
  "recommended_assessments": [
    {
      "url": "https://www.shl.com/products/...",
      "name": "Java Programming",
      "adaptive_support": "No",
      "description": "Multi-choice test measuring Java knowledge...",
      "duration": 30,
      "remote_support": "Yes",
      "test_type": ["Knowledge & Skills"]
    }
  ]
}
```

**Features:**
- 5-10 assessments returned
- Balanced test type distribution
- Respects duration constraints
- Ranked by score and llm ranking

---

#### `POST /api/chat`
**Purpose:** General chat interface for queries and recommendations

**Request:**
```json
{
  "query": "What is the Python assessment?",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "response": "The Python assessment is a multi-choice test...",
  "session_id": "abc-123",
  "assessments": null
}
```

**Features:**
- Handles both JD queries and questions
- Session management
- Contextual responses

---

#### `GET /api/health`
**Purpose:** Health check endpoint

**Response:**
```json
{
  "status": "healthy"
}
```

**Checks:**
- Database connectivity
- ChromaDB status
- LLM service availability

---

### Search & Discovery

#### `GET /api/assessments/search`
**Purpose:** Direct search in assessment catalog

**Parameters:**
- `search_term` (required): Search keyword
- `test_type` (optional): Filter by test type
- `duration_max` (optional): Maximum duration in minutes
- `remote_only` (optional): Only remote assessments
- `limit` (optional): Number of results (1-50)

**Example:**
```
GET /api/assessments/search?search_term=python&duration_max=30&limit=5
```

---

#### `GET /api/assessments/{assessment_id}`
**Purpose:** Get specific assessment details

**Example:**
```
GET /api/assessments/https://www.shl.com/products/product-catalog/view/automata-selenium/
```

---

#### `GET /api/test-types`
**Purpose:** Get available test types

**Response:**
```json
{
  "test_types": [
    {
      "code": "K",
      "name": "Knowledge & Skills",
      "description": "Tests that assess technical knowledge..."
    }
  ]
}
```

---

### Utility Endpoints

#### `POST /api/extract-jd`
**Purpose:** Extract job description from URL

**Request:**
```json
{
  "url": "https://example.com/job/12345"
}
```

**Response:**
```json
{
  "success": true,
  "url": "https://example.com/job/12345",
  "jd_text": "We are looking for...",
  "text_length": 1250,
  "metadata": {
    "title": "Software Engineer - Java",
    "page_heading": "Join Our Team"
  }
}
```

---

### Session Management

#### `GET /api/session/{session_id}`
**Purpose:** Get session history and interactions

**Response:**
```json
{
  "session_id": "abc-123",
  "created_at": "2024-01-15T10:00:00",
  "interaction_count": 5,
  "interactions": [...]
}
```

---

#### `DELETE /api/session/{session_id}`
**Purpose:** Delete session and all data

**Response:**
```json
{
  "message": "Session abc-123 deleted successfully",
  "session_id": "abc-123"
}
```

---

#### `GET /api/session/{session_id}/stats`
**Purpose:** Get session statistics

**Response:**
```json
{
  "session_id": "abc-123",
  "created_at": "2024-01-15T10:00:00",
  "total_interactions": 5,
  "successful_interactions": 4,
  "success_rate": 0.8
}
```

---

### Admin Endpoints

#### `POST /api/refresh` 
**Purpose:** Refresh assessment catalog (requires API key)

**Headers:**
```
X-API-Key: shl-refresh-key
```

**Parameters:**
- `force` (optional): Force refresh even if recently updated

**Response:**
```json
{
  "status": "started",
  "message": "Refresh started in background",
  "assessments_count": 0,
  "timestamp": "2024-01-15T10:00:00Z"
}
```

**Features:**
- Automatic refresh every 7 days
- Scrapes latest assessments
- Updates ChromaDB embeddings
- Replaces old data

---

#### `GET /api/refresh/status` 
**Purpose:** Get refresh status

**Response:**
```json
{
  "refresh_in_progress": false,
  "last_refresh_time": "2024-01-08T10:00:00Z",
  "last_refresh_db": "2024-01-08T10:00:00Z",
  "assessments_count": 215,
  "next_auto_refresh": "2024-01-15T10:00:00Z",
  "auto_refresh_enabled": true,
  "refresh_interval_days": 7
}
```

---

## Project Structure

```
shl/
│
├── .env                              # Environment configuration
├── requirements.txt                 
├── README.md                         
├── run.py                            # FastAPI runner
├── predictions.csv                   # for test-set prediction using fastapi
│
├── app/                              # Main application 
│   ├── __init__.py
│   ├── main.py                       # FastAPI application entry
│   ├── config.py                     # Configuration management
│   │
│   ├── agents/                       # Agents
│   │   ├── __init__.py
│   │   ├── base_agent.py            # Base agent class
│   │   ├── supervisor_agent.py      # Intent classification
│   │   ├── jd_extractor_agent.py    # URL extraction & fetching
│   │   ├── jd_processor_agent.py    # JD parsing & enhancement
│   │   ├── rag_agent.py             # RAG retrieval & ranking
│   │   └── general_query_agent.py   # General questions handler
│   │
│   ├── api/                          # FastAPI routes
│   │   ├── __init__.py
│   │   ├── dependencies.py          
│   │   ├── middleware.py           
│   │   │
│   │   └── routes/                   # API endpoints
│   │       ├── __init__.py
│   │       ├── health.py            # Health check
│   │       ├── recommend.py         # Main recommendations
│   │       ├── chat.py              # Chat interface
│   │       ├── session.py           # Session management
│   │       ├── assessments.py       # Assessment search
│   │       ├── extract_jd.py        # JD extraction utility
│   │       ├── test_types.py        # Test types info
│   │       └── refresh.py           # Auto-refresh system
│   │
│   ├── database/                    
│   │   ├── __init__.py
│   │   ├── sqlite_db.py             # SQLite connection
│   │   ├── chroma_db.py             # ChromaDB connection
│   │   │
│   │   └── migrations/               # Database migrations
│   │       └── init_db.sql
│   │
│   ├── graph/                        # LangGraph 
│   │   ├── __init__.py
│   │   ├── state.py                 # Graph state definitions
│   │   ├── nodes.py                 # Graph node implementations
│   │   ├── edges.py                 # Conditional edge logic
│   │   ├── workflow.py              # Main workflow orchestration
│   │   └── utils.py                 # Graph utilities
│   │
│   ├── models/                      
│   │   ├── __init__.py
│   │   ├── schemas.py               # Pydantic API schemas
│   │   ├── database_models.py       # SQLAlchemy ORM models
│   │   └── assessment.py            # Assessment data models
│   │
│   ├── prompts/                     
│   │   ├── __init__.py
│   │   ├── supervisor_prompts.py    # Supervisor agent prompts
│   │   ├── jd_extraction_prompts.py # JD extraction prompts
│   │   ├── rag_prompts.py           # RAG & reranking prompts
│   │   └── general_query_prompts.py # General query prompts
│   │
│   ├── services/                     
│   │   ├── __init__.py
│   │   ├── llm_service.py           # Gemini LLM integration
│   │   ├── embedding_service.py     # Gemini embeddings
│   │   ├── vector_store_service.py  # ChromaDB operations
│   │   ├── scraper_service.py       # Web scraping
│   │   ├── jd_fetcher_service.py    # JD fetching from URLs
│   │   └── session_service.py       # Session management
│   │
│   └── utils/                        # Utility functions
│       ├── __init__.py
│       ├── logger.py                # Logging configuration
│       ├── validators.py            # Input validation
│       ├── formatters.py            # Output formatting
│       └── helpers.py               # General helpers
│
│
├── data/                            
│   ├── shl_assessments.json         # Scraped  377 assessments data
│   ├── labeled_train_set.json       # data
│   └── Test-Set.json                # Test queries
│
├── storage/                          # Database storage
│   ├── sqlite/
│   │   └── sessions.db              # SQLite database
│   │
│   └── chroma/                      # ChromaDB storage
│       └── assessments/             # Vector collections
│
├── scripts/                          
│   ├── __init__.py
│   ├── scrape_catalog.py            #scraper    
│
└── logs/                             # Application logs
    ├── app.log                       # Main application log
```

### Key Directories Explained

- **`app/agents/`** - Contains all 5 AI agents with their logic
- **`app/api/routes/`** - All FastAPI endpoint implementations
- **`app/graph/`** - LangGraph workflow orchestration
- **`app/prompts/`** - LLM prompts for each agent (fully written, no truncation)
- **`app/services/`** - Business logic and external service integrations
- **`chainlit_app/`** - Complete Chainlit frontend application
- **`scripts/`** - Standalone script for scraping SHL test assesments
- **`data/`** - Assessment data and training sets
- **`storage/`** - Persistent storage for databases

---

## Getting Started

### Prerequisites

- Python 3.11
- Google Gemini API Key 

### Installation

```bash
# 1. Clone repository
git clone https://github.com/vinu0404/SHL.git
cd shl

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create .env file and add your Gemini API key
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```


### Running the Application

**Terminal 1 - FastAPI Backend:**
```bash
python run.py
# Access at: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

**Terminal 2 - Chainlit Frontend:**
```bash
python run_chainlit.py
# Access at: http://localhost:8001
```

---

##  Usage Examples

### Example 1: Job Description Query

**Input:**
```
I'm hiring for a Senior Java Developer who needs to collaborate 
with business teams. Looking for assessments under 60 minutes.
```

**Process:**
1. Supervisor classifies as `jd_query`
2. JD Processor extracts: Java, collaboration, senior level, 60 min
3. RAG retrieves Knowledge & Skills + Personality & Behavior tests
4. Returns balanced 5-10 assessments

**Output:**
- Java Programming Test
- Interpersonal Communication
- Team Collaboration Assessment
- Technical Problem Solving
- [More balanced recommendations...]

### Example 2: URL-Based Query

**Input:**
```
Here's the job posting: https://example.com/jobs/data-scientist
```

**Process:**
1. Supervisor classifies as `jd_query`
2. JD Extractor fetches and parses the URL
3. JD Processor analyzes full job description
4. RAG recommends relevant assessments

### Example 3: General Question

**Input:**
```
What is the .net assessment and how long does it take?
```

**Process:**
1. Supervisor classifies as `general`
2. General Query Agent searches knowledge base
3. Returns detailed information about Python assessment

**Output:**
```
The .NET (New) assessment is a multi-choice test that measures 
knowledge of programming, modules and libraries.

Duration: 11 minutes
Test Type: Knowledge & Skills
Remote Support: Yes
Adaptive: No
```

---
## Auto-Refresh System

The system automatically refreshes assessment data every 7 days:

**Features:**
- Scrapes latest assessments from SHL website
- Generates new embeddings
- Updates ChromaDB collection
- Tracks last update time

**Manual Trigger:**
```bash
curl -X POST http://localhost:8000/api/refresh \
  -H "X-API-Key: shl-refresh-key"
```

