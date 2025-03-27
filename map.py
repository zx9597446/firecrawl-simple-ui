import requests

def map_url(url, search=None, api_url=None, api_key=None):
    """映射网站URL"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {"url": url}
    if search:
        data["search"] = search
    
    response = requests.post(
        f"{api_url}/v1/map",
        headers=headers,
        json=data
    )
    return response.json() if response.status_code == 200 else None