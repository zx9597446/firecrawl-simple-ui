### Batch Scrape API

#### 提交批量任务
```bash
curl --request POST \
  --url https://api.firecrawl.dev/v1/batch/scrape \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --data '{
  "urls": [
    "<string>"
  ],
  "webhook": {
    "url": "<string>",
    "headers": {},
    "metadata": {},
    "events": [
      "completed"
    ]
  },
  "ignoreInvalidURLs": false,
  "formats": [
    "markdown"
  ],
  "onlyMainContent": true,
  "includeTags": [
    "<string>"
  ],
  "excludeTags": [
    "<string>"
  ],
  "headers": {},
  "waitFor": 0,
  "mobile": false,
  "skipTlsVerification": false,
  "timeout": 30000,
  "jsonOptions": {
    "schema": {},
    "systemPrompt": "<string>",
    "prompt": "<string>"
  },
  "removeBase64Images": true,
  "blockAds": true,
  "proxy": "basic"
}'
```

#### 响应 (返回job id)
```json
{
  "success": true,
  "id": "<string>",
  "url": "<string>",
  "invalidURLs": [
    "<string>"
  ]
}
```
Body
application/json
​
urls
string[]required
The URL to scrape

​
webhook
object
A webhook specification object.


Show child attributes

​
ignoreInvalidURLs
booleandefault:false
If invalid URLs are specified in the urls array, they will be ignored. Instead of them failing the entire request, a batch scrape using the remaining valid URLs will be created, and the invalid URLs will be returned in the invalidURLs field of the response.

​
formats
enum<string>[]
Formats to include in the output.

Available options: markdown, html, rawHtml, links, screenshot, screenshot@fullPage, json 
​
onlyMainContent
booleandefault:true
Only return the main content of the page excluding headers, navs, footers, etc.

​
includeTags
string[]
Tags to include in the output.

​
excludeTags
string[]
Tags to exclude from the output.

​
headers
object
Headers to send with the request. Can be used to send cookies, user-agent, etc.

​
waitFor
integerdefault:0
Specify a delay in milliseconds before fetching the content, allowing the page sufficient time to load.

​
mobile
booleandefault:false
Set to true if you want to emulate scraping from a mobile device. Useful for testing responsive pages and taking mobile screenshots.

​
skipTlsVerification
booleandefault:false
Skip TLS certificate verification when making requests

​
timeout
integerdefault:30000
Timeout in milliseconds for the request

​
jsonOptions
object
Extract object


Show child attributes

​
actions
object[]
Actions to perform on the page before grabbing the content

Wait
Screenshot
Click
Write text
Press a key
Scroll
Scrape
Execute JavaScript

Show child attributes

​
location
object
Location settings for the request. When specified, this will use an appropriate proxy if available and emulate the corresponding language and timezone settings. Defaults to 'US' if not specified.


Show child attributes

​
removeBase64Images
boolean
Removes all base 64 images from the output, which may be overwhelmingly long. The image's alt text remains in the output, but the URL is replaced with a placeholder.

​
blockAds
booleandefault:true
Enables ad-blocking and cookie popup blocking.

​


#### 通过job id获取结果
```bash
curl --request GET \
  --url https://api.firecrawl.dev/v1/batch/scrape/{id} \
  --header 'Authorization: Bearer <token>'
```

#### 结果响应
```json
{
  "status": "<string>",
  "total": 123,
  "completed": 123,
  "creditsUsed": 123,
  "expiresAt": "2023-11-07T05:31:56Z",
  "next": "<string>",
  "data": [
    {
      "markdown": "<string>",
      "html": "<string>",
      "rawHtml": "<string>",
      "links": [
        "<string>"
      ],
      "screenshot": "<string>",
      "metadata": {
        "title": "<string>",
        "description": "<string>",
        "language": "<string>",
        "sourceURL": "<string>",
        "<any other metadata> ": "<string>",
        "statusCode": 123,
        "error": "<string>"
      }
    }
  ]
}# Firecrawl Batch Scraper

## API Reference

### Submit Batch Job
```bash
curl --request POST \
  --url https://api.firecrawl.dev/v1/batch/scrape \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --data '{
  "urls": ["<string>"],
  "webhook": {
    "url": "<string>",
    "headers": {},
    "metadata": {},
    "events": ["completed"]
  },
  "ignoreInvalidURLs": false,
  "formats": ["markdown"],
  "onlyMainContent": true,
  "blockAds": true
}'
```

### Response (Returns job ID)
```json
{
  "success": true,
  "id": "<string>",
  "url": "<string>",
  "invalidURLs": ["<string>"]
}
```

### Get Job Results
```bash
curl --request GET \
  --url https://api.firecrawl.dev/v1/batch/scrape/{id} \
  --header 'Authorization: Bearer <token>'
```

### Results Response
```json
{
  "status": "<string>",
  "total": 123,
  "completed": 123,
  "creditsUsed": 123,
  "expiresAt": "2023-11-07T05:31:56Z",
  "next": "<string>",
  "data": [
    {
      "markdown": "<string>",
      "metadata": {
        "title": "<string>",
        "description": "<string>",
        "sourceURL": "<string>",
        "statusCode": 123,
        "error": "<string>"
      }
    }
  ]
}
```

## Usage Instructions

### Prerequisites
1. Create `.env` file:
```bash
FIRECRAWL_API_URL=https://api.firecrawl.dev/v1
FIRECRAWL_API_KEY=your_api_key_here
```

2. Install dependencies:
```bash
pip install streamlit requests python-dotenv
```

### Running the Application
```bash
streamlit run batch_scrape.py
```

### Features
- Batch URL processing
- Real-time progress tracking
- Markdown content extraction
- Error handling and validation
- Interactive results preview
- One-click downloads

### Best Practices
1. Start with small batches (5-10 URLs) to test
2. Monitor your API credit usage
3. Check the `expiresAt` field for result retention period
4. Use webhooks for large-scale processing
5. Implement retry logic for failed requests

### Troubleshooting
- **Invalid URLs**: Check the `invalidURLs` in response
- **Timeout Errors**: Increase the `timeout` parameter
- **Authentication Errors**: Verify your API key
- **Empty Results**: Try disabling `onlyMainContent`
