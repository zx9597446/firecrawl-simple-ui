curl --request POST \
  --url https://api.firecrawl.dev/v1/search \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --data '{
  "query": "<string>",
  "limit": 5,
  "tbs": "<string>",
  "lang": "en",
  "country": "us",
  "location": "<string>",
  "timeout": 60000,
  "scrapeOptions": {}
}'

The search endpoint combines web search (SERP) with Firecrawl’s scraping capabilities to return full page content for any query.

Include `scrapeOptions` with `formats: ["markdown"]` to get complete markdown content for each search result otherwise you will default to getting the SERP results (url, title, description).

#### Authorizations

Bearer authentication header of the form `Bearer <token>`, where `<token>` is your auth token.

#### Body

Maximum number of results to return

Required range: `1 <= x <= 10`

Time-based search parameter

Language code for search results

Country code for search results

Location parameter for search results

Options for scraping search results

#### Response

Successful response

Warning message if any issues occurred

{
  "success": true,
  "data": [
    {
      "title": "<string>",
      "description": "<string>",
      "url": "<string>",
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
        "sourceURL": "<string>",
        "statusCode": 123,
        "error": "<string>"
      }
    }
  ],
  "warning": "<string>"
}