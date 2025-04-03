import os
import requests
import streamlit as st
from dotenv import load_dotenv
from time import sleep

# 加载环境变量
load_dotenv()
API_URL = os.getenv("FIRECRAWL_API_URL", "https://api.firecrawl.dev/v1")
API_KEY = os.getenv("FIRECRAWL_API_KEY")

# 初始化session状态
if 'job_id' not in st.session_state:
    st.session_state.job_id = None
if 'results' not in st.session_state:
    st.session_state.results = None

def submit_map_job(url, options):
    """提交URL映射任务"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "url": url,
        "ignoreSitemap": options["ignore_sitemap"],
        "sitemapOnly": options["sitemap_only"],
        "includeSubdomains": options["include_subdomains"],
        "limit": options["limit"],
    }
    
    # 可选参数
    if options["search"]:
        payload["search"] = options["search"]
    if options["timeout"]:
        payload["timeout"] = options["timeout"]

    try:
        response = requests.post(
            f"{API_URL}/map",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"提交失败: {str(e)}")
        return None

# Streamlit界面
st.title("🗺️ Firecrawl URL映射工具")

# 配置选项
with st.expander("高级映射选项"):
    col1, col2 = st.columns(2)
    with col1:
        ignore_sitemap = st.checkbox("忽略站点地图", value=True)
        sitemap_only = st.checkbox("仅站点地图", value=False)
        include_subdomains = st.checkbox("包含子域名", value=False)
        
    with col2:
        limit = st.number_input("最大链接数", min_value=1, max_value=5000, value=100)
        timeout = st.number_input("超时时间(ms)", min_value=0, value=0)
        
    search = st.text_input("搜索查询") 

# URL输入框
url = st.text_input(
    "输入要映射的URL",
    placeholder="https://example.com",
    help="输入要发现链接的起始URL"
)

# 提交按钮
if st.button("开始映射") and url:
    options = {
        "ignore_sitemap": ignore_sitemap,
        "sitemap_only": sitemap_only,
        "include_subdomains": include_subdomains,
        "limit": limit,
        "timeout": timeout if timeout > 0 else None,
        "search": search if search else None,
    }
    
    with st.spinner("提交任务中..."):
        result = submit_map_job(url.strip(), options)
        
    if not result:
        st.error("任务提交失败: 无响应")
    elif result.get("error"):
        st.error(f"任务提交失败: {result['error']}")
    elif not result.get("success"):
        st.error(f"任务提交失败: {result.get('message', '未知错误')}")
    else:
        st.session_state.results = result
        st.success("映射完成！")

# 结果显示和下载
if st.session_state.results:
    st.divider()
    st.subheader("映射结果")
    
    if not st.session_state.results.get("links"):
        st.warning("没有发现任何链接")
    else:
        links = st.session_state.results["links"]
        st.success(f"发现 {len(links)} 个链接")
        
        # 显示链接列表
        st.dataframe(links, use_container_width=True)
        
        # 下载链接按钮
        combined_links = "\n".join(links)
        st.download_button(
            label="下载链接列表",
            data=combined_links,
            file_name="discovered_links.txt",
            mime="text/plain"
        )
