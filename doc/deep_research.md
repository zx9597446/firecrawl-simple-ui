### Deep Research API (Alpha)

#### 提交深度研究任务
```bash
curl -X POST "https://api.firecrawl.dev/v1/deep-research" \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the latest developments in quantum computing?",
    "maxDepth": 5,
    "timeLimit": 180,
    "maxUrls": 15
  }'
```

query: The research topic or question you want to investigate
maxDepth (Optional): Maximum number of research iterations (1-10, default: 7)
timeLimit (Optional): Time limit in seconds (30-300, default: 270)
maxUrls (Optional): Maximum number of URLs to analyze (1-1000, default: 20)

### 响应
{
  "success": true,
  "id": "a0c3e196-0a0f-46da-8fc7-03fe13443677"
}

### check
curl --request GET \
  --url http://localhost:3002/v1/deep-research/{id} \
  --header 'Authorization: Bearer 0xFirecrawl'

### in progress
{
  "success": true,
  "status": "processing",
  "data": {
    "activities": [
      {
        "type": "search",
        "status": "completed",
        "message": "Initial research on quantum computing trends",
        "timestamp": "2024-03-15T10:30:00Z",
        "depth": 1
      },
      {
        "type": "analyze",
        "status": "in_progress",
        "message": "Analyzing quantum error correction advances",
        "timestamp": "2024-03-15T10:31:00Z",
        "depth": 2
      }
    ],
    "sources": [
      {
        "url": "https://example.com/quantum-computing-2024",
        "title": "Latest Quantum Computing Breakthroughs",
        "description": "Overview of recent advances in quantum computing technology"
        }
      ],
    },
  "currentDepth": 2,
  "maxDepth": 5,
  "expiresAt": "2024-03-16T10:30:00Z"
}

#### complete
```json
{
  "success": true,
  "data": {
    "finalAnalysis": "Recent developments in quantum computing show significant progress in several key areas:\n\n1. Error Correction: Improved quantum error correction techniques have increased qubit stability\n2. Quantum Supremacy: Multiple demonstrations of quantum advantage in specific computational tasks\n3. Hardware Advances: New architectures using superconducting circuits and trapped ions\n4. Commercial Applications: Growing industry adoption in optimization and cryptography",
    "activities": [
      {
        "type": "search",
        "status": "completed",
        "message": "Analyzing quantum computing breakthroughs in 2024",
        "timestamp": "2024-03-15T10:30:00Z",
        "depth": 1
      }
    ],
    "sources": [
      {
        "url": "https://example.com/quantum-computing-2024",
        "title": "Latest Quantum Computing Breakthroughs",
        "description": "Overview of recent advances in quantum computing technology"
      }
    ]
  },
  "status": "completed",
  "currentDepth": 5,
  "maxDepth": 5,
  "expiresAt": "2024-03-16T10:30:00Z"
}
```
