import os
import time
import streamlit as st
from dotenv import load_dotenv
from map import map_url
from crawl import start_crawl, check_crawl_status, parse_crawl_results
from batch_scrape import batch_scrape

# 加载环境变量
load_dotenv()
API_URL = os.getenv('FIRECRAWL_API_URL')
API_KEY = os.getenv('FIRECRAWL_API_KEY')

# 设置页面配置
st.set_page_config(page_title="Firecrawl工具集", layout="wide")
st.title("Firecrawl工具集")

# 创建标签页
tab1, tab2, tab3 = st.tabs(["批量抓取", "网站映射", "网站爬取"])

with tab1:
    batch_scrape(API_URL, API_KEY)

with tab2:
    # 网站映射功能
    st.subheader("网站URL映射")
    
    # 初始化session_state
    if 'mapped_links' not in st.session_state:
        st.session_state.mapped_links = []
    
    with st.form("map_form"):
        url = st.text_input(
            "输入网站URL",
            placeholder="https://example.com"
        )
        search = st.text_input(
            "搜索关键词(可选)",
            placeholder="docs"
        )
        submitted = st.form_submit_button("开始映射")
        
        if submitted:
            if not url:
                st.error("请输入网站URL")
            else:
                with st.spinner("正在映射网站URL..."):
                    result = map_url(url, search if search else None, API_URL, API_KEY)
                    if result:
                        if result.get('status') == 'success' or result.get('success'):
                            links = result.get('links', [])
                            st.success(f"找到 {len(links)} 个URL")
                            st.session_state.mapped_links = links
                            st.dataframe({"URL": links})
                        else:
                            st.error(f"映射失败: {result.get('message', '未知错误')}")
                    else:
                        st.error("API请求失败")

    if st.session_state.get('mapped_links'):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("复制URL列表"):
                import pyperclip
                pyperclip.copy("\n".join(st.session_state.mapped_links))
                st.success("已复制到剪贴板!")
        with col2:
            st.download_button(
                label="下载URL列表",
                data="\n".join(st.session_state.mapped_links),
                file_name="url_list.txt",
                mime="text/plain"
            )

with tab3:
    # 网站爬取功能
    st.subheader("网站深度爬取")
    
    # 初始化session_state
    if 'crawl_job_id' not in st.session_state:
        st.session_state.crawl_job_id = None
    if 'crawl_status' not in st.session_state:
        st.session_state.crawl_status = None
    if 'crawl_results' not in st.session_state:
        st.session_state.crawl_results = []
    
    with st.form("crawl_form"):
        url = st.text_input(
            "输入要爬取的网站URL",
            placeholder="https://example.com"
        )
        
        st.subheader("爬取选项")
        col1, col2 = st.columns(2)
        with col1:
            max_pages = st.number_input("最大页面数", min_value=1, value=100)
            only_main_content = st.checkbox("仅主要内容", value=True)
        with col2:
            include_metadata = st.checkbox("包含元数据", value=False)
            mobile = st.checkbox("移动端模式", value=False)
        
        submitted = st.form_submit_button("开始爬取")
        
        if submitted:
            if not url:
                st.error("请输入网站URL")
            else:
                with st.spinner("正在提交爬取任务..."):
                    options = {
                        "max_pages": max_pages,
                        "page_options": {
                            "onlyMainContent": only_main_content,
                            "includeMetadata": include_metadata,
                            "mobile": mobile
                        }
                    }
                    print(f"正在调用API: URL={url}, API_URL={API_URL}")
                    print(f"提交的options参数: {options}")
                    result = start_crawl(url, API_URL, API_KEY, options)
                    print(f"API调用结果: {result}")
                    if result:
                        if isinstance(result, list):
                            st.session_state.crawl_results = result
                            st.success(f"爬取完成! 共获取 {len(result)} 个页面")
                        else:
                            st.error(f"无效的API响应格式: {type(result)}")

    # 显示爬取结果
    if st.session_state.get('crawl_results'):
        st.divider()
        st.subheader("爬取结果")
        
        # 解析结果
        parsed_results = parse_crawl_results(st.session_state.crawl_results)
        st.info(f"共爬取 {len(parsed_results)} 个页面")
        
        # 下载按钮行
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="下载完整结果(JSON)",
                data=str(st.session_state.crawl_results),
                file_name="crawl_results.json",
                mime="application/json"
            )
        with col2:
            st.download_button(
                label="下载合并Markdown",
                data="\n\n---\n\n".join([r['markdown'] for r in parsed_results if r.get('markdown')]),
                file_name="combined_markdown.md",
                mime="text/markdown"
            )
        
        # 复制按钮
        if st.button("复制Markdown到剪贴板"):
            from crawl import copy_markdown
            if copy_markdown(parsed_results):
                st.success("Markdown已复制到剪贴板!")
            else:
                st.error("复制失败")
        
        # 显示结果表格
        st.dataframe({
            "URL": [r['url'] for r in parsed_results],
            "标题": [r['title'] for r in parsed_results],
            "字数": [r['word_count'] for r in parsed_results]
        })