# Hotel-Agent


## Environment Variables
Create a `.env` file in the project root with the following variables:
```
DB_USER=agent_user
DB_NAME=hotel_db
DB_PASS=agent_pwd
OPENAI_API_KEY=your_openai_api_key
NVIDIA_NIM_API_KEY=your_nvidia_nim_api_key
```

## Getting Started

1. Build the images
```bash
docker compose build
```

2. Start the services:
```bash
docker compose up -d
```

3. Log the containers
```bash
docker compose logs -f
```

### Service URLs
- Web Frontend: http://localhost:3000
- API Service: http://localhost:8000
- LLM Service: http://localhost:8005
- PostgreSQL Database: localhost:5432

## Services

### Database
- PostgreSQL 17
- Data is persisted using Docker volumes
- Default database name: hotel_db

### API Service
- RESTful API for hotel management
- Handles database operations
- Connects to the PostgreSQL database
- Built with a custom Dockerfile located in the `./api` directory

### LLM Service
- AI-powered natural language processing
- Integrates with OpenAI and NVIDIA NIM APIs
- Connects to the API service
- Built with a custom Dockerfile located in the `./llm` directory

### Web Frontend
- Next.js 15.2.4 web application
- Connects to both API and LLM services
- Built with a custom Dockerfile located in the `./web` directory

## Development
Each service has its own directory with source code and Dockerfile:
- `./api`: API service code
- `./llm`: LLM service code
- `./web`: Next.js web application code

## Network
All services communicate through the `agent_network` Docker network.
