import streamlit as st
import pyperclip
import asyncio
from async_utils import AsyncFirecrawlClient

async def batch_scrape(api_url, api_key):
    # 初始化session_state
    if 'combined_markdown' not in st.session_state:
        st.session_state.combined_markdown = ""

    # 创建表单
    with st.form("scrape_form"):
        # 多URL输入
        urls = st.text_area(
            "输入要抓取的URL列表(每行一个URL)", 
            placeholder="https://example.com\nhttps://another.com",
            height=150
        )
        
        # 抓取选项
        st.subheader("抓取选项")
        col1, col2 = st.columns(2)
        with col1:
            only_main_content = st.checkbox("仅主要内容", value=True)
            include_metadata = st.checkbox("包含元数据", value=False)
        with col2:
            wait_for = st.number_input("等待时间(毫秒)", min_value=0, value=0)
            mobile = st.checkbox("移动端模式", value=False)
        
        submitted = st.form_submit_button("开始批量抓取")

        if submitted:
            if not urls:
                st.error("请输入至少一个URL")
            else:
                url_list = [url.strip() for url in urls.split('\n') if url.strip()]
                all_markdown = []
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # 准备抓取选项
                options = {
                    "pageOptions": {
                        "onlyMainContent": only_main_content,
                        "includeMetadata": include_metadata,
                        "waitFor": wait_for,
                        "mobile": mobile
                    }
                }
                
                # 异步处理所有URL
                async with AsyncFirecrawlClient(api_url, api_key) as client:
                    tasks = [client.scrape(url, options) for url in url_list]
                    
                    for i, task in enumerate(asyncio.as_completed(tasks)):
                        try:
                            result = await task
                            status_text.text(f"正在处理: {i+1}/{len(url_list)}")
                            progress_bar.progress((i+1)/len(url_list))
                            
                            if isinstance(result, dict) and not result.get('error'):
                                if 'markdown' in result.get('data', {}):
                                    url = result['data'].get('url', url_list[i])
                                    all_markdown.append(f"# {url}\n\n{result['data']['markdown']}\n\n---\n")
                                else:
                                    st.warning(f"URL {i+1}: 未返回markdown内容")
                            else:
                                st.error(f"URL {i+1}: 请求失败 - {result.get('message', '未知错误')}")
                                
                        except Exception as e:
                            st.error(f"URL {i+1}: 发生错误 - {str(e)}")
                
                if all_markdown:
                    st.session_state.combined_markdown = "\n".join(all_markdown)

    # 显示结果和操作按钮
    if st.session_state.combined_markdown:
        # 下载和复制按钮（放在结果上方）
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="下载Markdown",
                data=st.session_state.combined_markdown,
                file_name="firecrawl_results.md",
                mime="text/markdown"
            )
        with col2:
            if st.button("复制到剪贴板"):
                pyperclip.copy(st.session_state.combined_markdown)
                st.success("已复制到剪贴板!")
        
        st.markdown("### 合并后的抓取结果")
        st.markdown(st.session_state.combined_markdown)