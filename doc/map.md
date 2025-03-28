### Map API

#### 请求URL发现
```bash
curl --request POST \
  --url https://api.firecrawl.dev/v1/map \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --data '{
  "url": "<string>",
  "search": "<string>",
  "ignoreSitemap": true,
  "sitemapOnly": false,
  "includeSubdomains": false,
  "limit": 5000,
  "timeout": 123
}'
```

Body
application/json
​
url
stringrequired
The base URL to start crawling from

​
search
string
Search query to use for mapping. During the Alpha phase, the 'smart' part of the search functionality is limited to 1000 search results. However, if map finds more results, there is no limit applied.

​
ignoreSitemap
booleandefault:true
Ignore the website sitemap when crawling.

​
sitemapOnly
booleandefault:false
Only return links found in the website sitemap

​
includeSubdomains
booleandefault:false
Include subdomains of the website

​
limit
integerdefault:5000
Maximum number of links to return

Required range: x <= 5000
​
timeout
integer
Timeout in milliseconds. There is no timeout by default.


#### 响应
```json
{
  "success": true,
  "links": [
    "<string>"
  ]
}