import streamlit as st
import requests
import pyperclip

def search_content(api_url, api_key):
    # 初始化session_state
    if 'search_results' not in st.session_state:
        st.session_state.search_results = []
    if 'combined_markdown' not in st.session_state:
        st.session_state.combined_markdown = ""

    # 创建表单
    with st.form("search_form"):
        query = st.text_input(
            "搜索关键词",
            placeholder="输入要搜索的内容"
        )
        
        # 搜索选项
        st.subheader("搜索选项")
        col1, col2 = st.columns(2)
        with col1:
            limit = st.number_input("结果数量", min_value=1, max_value=10, value=5)
            lang = st.text_input("语言代码", value="en")
        with col2:
            country = st.text_input("国家代码", value="us")
            scrape_markdown = st.checkbox("获取完整Markdown", value=True)
        
        submitted = st.form_submit_button("开始搜索")

        if submitted:
            if not query:
                st.error("请输入搜索关键词")
            else:
                try:
                    # 准备请求数据
                    data = {
                        "query": query,
                        "limit": limit,
                        "lang": lang,
                        "country": country,
                        "scrapeOptions": {
                            "formats": ["markdown"] if scrape_markdown else []
                        }
                    }
                    
                    # 调用Firecrawl API
                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    }
                    
                    response = requests.post(
                        f"{api_url}/v1/search",
                        headers=headers,
                        json=data
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get('success'):
                            st.session_state.search_results = result.get('data', [])
                            if scrape_markdown:
                                markdowns = []
                                for item in st.session_state.search_results:
                                    if 'markdown' in item:
                                        markdowns.append(f"# {item.get('title', item['url'])}\n\n{item['markdown']}\n\n---\n")
                                st.session_state.combined_markdown = "\n".join(markdowns)
                            st.success(f"找到 {len(st.session_state.search_results)} 个结果")
                        else:
                            st.error(f"搜索失败: {result.get('message', '未知错误')}")
                    else:
                        st.error(f"API请求失败 - {response.status_code}")
                        
                except Exception as e:
                    st.error(f"发生错误 - {str(e)}")

    # 显示结果和操作按钮
    if st.session_state.search_results:
        # 下载和复制按钮
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="下载JSON",
                data=str(st.session_state.search_results),
                file_name="search_results.json",
                mime="application/json"
            )
        with col2:
            if st.session_state.combined_markdown:
                if st.button("复制Markdown到剪贴板"):
                    pyperclip.copy(st.session_state.combined_markdown)
                    st.success("已复制到剪贴板!")

        if st.session_state.combined_markdown:
            st.download_button(
                label="下载Markdown",
                data=st.session_state.combined_markdown,
                file_name="search_results.md",
                mime="text/markdown"
            )
        
        st.markdown("### 搜索结果")
        if st.session_state.combined_markdown:
            st.markdown(st.session_state.combined_markdown)
        else:
            for result in st.session_state.search_results:
                st.markdown(f"### [{result.get('title', '无标题')}]({result['url']})")
                st.markdown(result.get('description', '无描述'))
                st.divider()
