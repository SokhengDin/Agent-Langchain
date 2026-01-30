# Data Science Agent

## Project Overview
This is a **Data Science Educational Agent**. It's an AI-powered teaching assistant that helps students learn and apply concepts in mathematics, probability theory, statistics, machine learning, and deep learning.

**Demo Video**: [Watch on YouTube](https://www.youtube.com/watch?v=uVgpjIIOgZ4)

---

## Architecture

### Multi-Service Microservices Architecture

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   Web Frontend  │─────▶│   LLM Service   │─────▶│   API Service   │
│   (Next.js)     │      │  (FastAPI/AI)   │      │  (FastAPI/DB)   │
│   Port 3000     │      │   Port 8005     │      │   Port 8000     │
└─────────────────┘      └─────────────────┘      └─────────────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │   PostgreSQL    │
                         │   Database      │
                         │   Port 5432     │
                         └─────────────────┘
```

**Services:**
1. **Web Frontend** (Next.js 15.2.4) - User interface for interacting with the agent
2. **LLM Service** (Python/FastAPI) - Core AI engine with LangGraph orchestration
3. **API Service** (FastAPI) - Database operations and business logic
4. **PostgreSQL Database** - Data persistence and conversation checkpointing

---

## Core Agent Capabilities

**Example Interaction:**
```
Student: "What is a normal distribution?"
Agent: "The normal distribution is defined by two parameters:

1. Mean μ - center of the distribution
2. Standard deviation σ - spread of the distribution

The PDF is given by:
$$
f(x) = \frac{1}{\sigma\sqrt{2\pi}} \exp\left[-\frac{(x-\mu)^2}{2\sigma^2}\right]
$$"
```

### 1. **Data Analysis & Exploratory Data Analysis (EDA)**
The agent can perform comprehensive data analysis including:
- Loading and exploring datasets (CSV, Excel)
- Descriptive statistics (mean, median, std, quartiles)
- Correlation analysis with heatmaps
- Distribution analysis (histograms, normality tests)
- Outlier detection (box plots, IQR method)
- Missing value analysis
- Feature relationships visualization

**Example Workflow:**
```python
Student: "Analyze this dataset"
Agent:
1. Loads the CSV file
2. Shows dataset shape, column types, missing values
3. Computes descriptive statistics
4. Creates correlation heatmap
5. Generates distribution plots
6. Detects outliers
7. Provides key insights and recommendations
```

### 2. **Statistical Analysis**
- Hypothesis testing (t-tests, chi-squared tests)
- Correlation analysis (Pearson, Spearman)
- Distribution fitting and testing
- Probability calculations
- Statistical inference
- A/B testing analysis

### 3. **Machine Learning**
The agent supports full ML workflows:
- Data preprocessing and feature engineering
- Model training (regression, classification, clustering)
- Cross-validation and hyperparameter tuning
- Model evaluation with proper metrics
- Feature importance analysis
- Model persistence with metadata

**Supported Algorithms:**
- Linear/Logistic Regression
- Random Forests
- XGBoost, LightGBM
- Support Vector Machines
- K-Means Clustering
- Neural Networks (TensorFlow/PyTorch)

### 4. **Data Visualization**
Comprehensive plotting capabilities:
- Histograms and distribution plots
- Scatter plots and correlation matrices
- Box plots for outlier detection
- Heatmaps for correlation analysis
- Time series plots
- Custom matplotlib/seaborn visualizations
- Interactive Plotly charts

### 5. **Code Execution & Generation**
- **Full Python code execution** with scientific computing libraries
- **Pre-imported libraries**: NumPy, Pandas, Matplotlib, Seaborn, SciPy, scikit-learn, Plotly, SymPy
- Code generation using specialized coding model (Qwen3-coder:30b)
- Real-time error handling and automatic code fixing
- Support for custom figure sizes and high-resolution exports

### 6. **Document Processing & RAG**
- PDF document processing and storage in vector database
- Semantic search across uploaded documents
- Text extraction from PDFs
- Context-aware question answering from documents

### 7. **Image Analysis (Vision)**
- Analyze images containing math problems
- Extract mathematical equations from images
- Analyze charts and graphs in images
- Solve problems from uploaded exercise images

---

## Example Use Cases

### Use Case 1: Dataset Analysis
```
Student: "I uploaded grades.csv, analyze it"

Agent Actions:
1. Loads CSV → Shows 100 rows, 3 columns (student_id, math, science)
2. Computes correlation → r=0.85 between math and science
3. Creates correlation heatmap
4. Generates distribution plots
5. Detects outliers

Response: "I analyzed your grades dataset with 100 students:
- Strong positive correlation (r=0.85) between math and science scores
- This suggests students who perform well in math tend to excel in science
- 3 outliers detected in the lower range
[displays visualizations]"
```

### Use Case 2: Machine Learning
```
Student: "Train a model to predict house prices"

Agent Actions:
1. Loads houses.csv
2. Performs EDA → distribution analysis
3. Trains Random Forest regression
4. Evaluates with cross-validation
5. Shows feature importance

Response: "I trained a Random Forest model:
- R² Score: 0.89 (explains 89% of variance)
- RMSE: $45,000
- Most important features: sqft (45%), location (30%), bedrooms (25%)
[displays feature importance plot]"
```

### Use Case 3: Theoretical Explanation
```
Student: "Explain the Central Limit Theorem"

Agent Response: "The Central Limit Theorem states that for a large
sample size n, the sampling distribution of the mean approaches a
normal distribution, regardless of the population's distribution:

$$\bar{X} \sim N\left(\mu, \frac{\sigma^2}{n}\right)$$

where:
- μ is the population mean
- σ² is the population variance
- n is the sample size

This is why the normal distribution is so prevalent in statistics."
```

### Use Case 4: Image Analysis
```
Student: [uploads image of math problem]
"Can you solve this?"

Agent Actions:
1. Analyzes image with vision tool
2. Extracts problem text and equations
3. Solves step-by-step
4. Explains the approach

Response: "I analyzed your image. The problem asks:
'Find the eigenvalues of matrix A = [[2,1],[1,2]]'

Solution:
1. Compute characteristic polynomial: det(A - λI) = 0
2. (2-λ)² - 1 = 0
3. λ² - 4λ + 3 = 0
4. Eigenvalues: λ₁ = 3, λ₂ = 1"
```

---

## API Endpoints

### Chat Endpoint
**POST** `/api/v2/ds/chat`

Request:
```json
{
  "message": "Analyze this dataset and create visualizations",
  "thread_id": "optional-thread-id",
  "uploaded_files": ["uploads/data/dataset.csv"]
}
```

Response:
```json
{
  "response": "Agent's complete response with analysis",
  "thread_id": "conversation-thread-uuid"
}
```

### Streaming Chat Endpoint
**POST** `/api/v2/ds/chat/stream`

Provides real-time streaming of:
- Thinking/reasoning steps
- Tool calls and executions
- Token-by-token response generation
- Error handling

---

## Deployment

### Docker Compose Architecture
All services run in containerized environments:

```yaml
services:
  web:      # Next.js frontend (port 3000)
  llm:      # LLM service (port 8005)
  api:      # API service (port 8000)
  postgres: # Database (port 5432)
```

### Quick Start
```bash
# 1. Set environment variables in .env
DB_USER=agent_user
DB_NAME=hotel_db
DB_PASS=agent_pwd
OPENAI_API_KEY=your_key
NVIDIA_NIM_API_KEY=your_key

# 2. Build and start services
docker compose build
docker compose up -d

# 3. Access the application
# Frontend: http://localhost:3000
# LLM API: http://localhost:8005
# API: http://localhost:8000
```

---