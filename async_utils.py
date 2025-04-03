import aiohttp
import asyncio
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class AsyncFirecrawlClient:
    """异步Firecrawl API客户端"""
    
    def __init__(self, api_url: str, api_key: str, max_concurrency: int = 10):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.max_concurrency = max_concurrency
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def scrape(self, url: str) -> Dict:
        """异步抓取单个URL"""
        async with self.session.post(
            f"{self.api_url}/v1/scrape",
            json={"url": url}
        ) as response:
            return await self._handle_response(response)
            
    async def batch_scrape(self, urls: List[str], options: Optional[Dict] = None) -> List[Dict]:
        """异步批量抓取多个URL"""
        semaphore = asyncio.Semaphore(self.max_concurrency)
        
        async def limited_scrape(url):
            async with semaphore:
                return await self.scrape(url, options)
                
        tasks = [limited_scrape(url) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=True)
        
    async def start_crawl(self, url: str, options: Optional[Dict] = None) -> Dict:
        """异步启动爬取任务"""
        data = {
            "url": url,
            "options": options or {}
        }
        async with self.session.post(
            f"{self.api_url}/v1/crawl",
            json=data
        ) as response:
            return await self._handle_response(response)
            
    async def check_crawl_status(self, job_id: str) -> Dict:
        """异步检查爬取任务状态"""
        async with self.session.get(
            f"{self.api_url}/v1/crawl/status/{job_id}"
        ) as response:
            return await self._handle_response(response)
            
    async def _handle_response(self, response) -> Dict:
        """处理API响应"""
        if response.status == 200:
            return await response.json()
        else:
            error = await response.text()
            logger.error(f"API请求失败: {response.status} - {error}")
            return {
                "error": True,
                "status_code": response.status,
                "message": error
            }

async def run_async_tasks(tasks, progress_callback=None):
    """运行异步任务并处理进度"""
    results = []
    total = len(tasks)
    
    for i, task in enumerate(asyncio.as_completed(tasks)):
        try:
            result = await task
            results.append(result)
            if progress_callback:
                progress = (i + 1) / total * 100
                await progress_callback(progress, i + 1, total)
        except Exception as e:
            logger.error(f"任务执行失败: {str(e)}")
            results.append({"error": str(e)})
            
    return results