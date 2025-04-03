### Extract API

#### 提交提取任务 (POST)
```bash
curl --request POST \
  --url https://api.firecrawl.dev/v1/extract \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --data '{
  "urls": [
    "<string>"
  ],
  "prompt": "<string>",
  "schema": {
    "property1": "<string>",
    "property2": 123
  },
  "enableWebSearch": false,
  "ignoreSitemap": false,
  "includeSubdomains": true,
  "showSources": false,
  "scrapeOptions": {
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
    "actions": [
      {
        "type": "wait",
        "milliseconds": 2,
        "selector": "#my-element"
      }
    ],
    "location": {
      "country": "US",
      "languages": [
        "en-US"
      ]
    },
    "removeBase64Images": true,
    "blockAds": true,
    "proxy": "basic"
  }
}'
```

Body
application/json
​
urls
string[]required
The URLs to extract data from. URLs should be in glob format.

​
prompt
string
Prompt to guide the extraction process

​
schema
object
Schema to define the structure of the extracted data


Hide child attributes

​
enableWebSearch
booleandefault:false
When true, the extraction will use web search to find additional data

​
ignoreSitemap
booleandefault:false
When true, sitemap.xml files will be ignored during website scanning

​
includeSubdomains
booleandefault:true
When true, subdomains of the provided URLs will also be scanned

​
showSources
booleandefault:false
When true, the sources used to extract the data will be included in the response as sources key

​
scrapeOptions
object

Hide child attributes

​
scrapeOptions.formats
enum<string>[]
Formats to include in the output.

Available options: markdown, html, rawHtml, links, screenshot, screenshot@fullPage, json 
​
scrapeOptions.onlyMainContent
booleandefault:true
Only return the main content of the page excluding headers, navs, footers, etc.

​
scrapeOptions.includeTags
string[]
Tags to include in the output.

​
scrapeOptions.excludeTags
string[]
Tags to exclude from the output.

​
scrapeOptions.headers
object
Headers to send with the request. Can be used to send cookies, user-agent, etc.

​
scrapeOptions.waitFor
integerdefault:0
Specify a delay in milliseconds before fetching the content, allowing the page sufficient time to load.

​
scrapeOptions.mobile
booleandefault:false
Set to true if you want to emulate scraping from a mobile device. Useful for testing responsive pages and taking mobile screenshots.

​
scrapeOptions.skipTlsVerification
booleandefault:false
Skip TLS certificate verification when making requests

​
scrapeOptions.timeout
integerdefault:30000
Timeout in milliseconds for the request

​
scrapeOptions.jsonOptions
object
Extract object


Show child attributes

​
scrapeOptions.actions
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
scrapeOptions.location
object
Location settings for the request. When specified, this will use an appropriate proxy if available and emulate the corresponding language and timezone settings. Defaults to 'US' if not specified.


Show child attributes

​
scrapeOptions.removeBase64Images
boolean
Removes all base 64 images from the output, which may be overwhelmingly long. The image's alt text remains in the output, but the URL is replaced with a placeholder.

​
scrapeOptions.blockAds
booleandefault:true
Enables ad-blocking and cookie popup blocking.

​

#### 响应 (返回job id)
```json
{
  "success": true,
  "id": "<string>"
}
```

#### 通过job id获取提取结果 (GET)
```bash
curl --request GET \
  --url https://api.firecrawl.dev/v1/extract/{id} \
  --header 'Authorization: Bearer <token>'
```

#### 结果响应
```json
{
  "success": true,
  "data": {},
  "status": "completed",
  "expiresAt": "2023-11-07T05:31:56Z"
}