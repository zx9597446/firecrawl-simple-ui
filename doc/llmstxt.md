### LLMs.txt API (Alpha)


# Start LLMs.txt generation
curl -X POST "https://api.firecrawl.dev/v1/llmstxt" \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "maxUrls": 2,
    "showFullText": true
  }'

# Check generation status
curl -X GET "https://api.firecrawl.dev/v1/llmstxt/job_id" \
  -H "Authorization: Bearer your_api_key"

# in progress
  {
  "success": true,
  "data": {
    "llmstxt": "# Firecrawl.dev llms.txt\n\n- [Web Data Extraction Tool](https://www.firecrawl.dev/)...",
    "llmsfulltxt": "# Firecrawl.dev llms-full.txt\n\n"
  },
  "status": "processing",
  "expiresAt": "2025-03-03T23:19:18.000Z"
}

# completed
{
  "success": true,
  "data": {
    "llmstxt": "# http://firecrawl.dev llms.txt\n\n- [Web Data Extraction Tool](https://www.firecrawl.dev/): Transform websites into clean, LLM-ready data effortlessly.\n- [Flexible Web Scraping Pricing](https://www.firecrawl.dev/pricing): Flexible pricing plans for web scraping and data extraction.\n- [Web Scraping and AI](https://www.firecrawl.dev/blog): Explore tutorials and articles on web scraping and AI...",
    "llmsfulltxt": "# http://firecrawl.dev llms-full.txt\n\n## Web Data Extraction Tool\nIntroducing /extract - Get web data with a prompt [Try now](https://www.firecrawl.dev/extract)\n\n[💥Get 2 months free with yearly plan](https://www.firecrawl.dev/pricing)..."
  },
  "status": "completed",
  "expiresAt": "2025-03-03T22:45:50.000Z"
}