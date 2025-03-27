import streamlit as st
import requests

def deep_research(api_url, api_key):
    """Handle deep research functionality"""
    st.subheader("深度网络研究")
    
    # 研究参数表单
    with st.form("research_form"):
        query = st.text_input(
            "研究主题",
            placeholder="量子计算的最新发展"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            max_depth = st.number_input("最大深度", min_value=1, max_value=10, value=3)
            max_urls = st.number_input("最大URL数", min_value=1, max_value=50, value=10)
        with col2:
            time_limit = st.number_input("时间限制(秒)", min_value=30, max_value=600, value=180)
        
        submitted = st.form_submit_button("开始研究")
        
        if submitted:
            if not query:
                st.error("请输入研究主题")
            else:
                with st.spinner("正在进行深度研究..."):
                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    }
                    payload = {
                        "query": query,
                        "maxDepth": max_depth,
                        "timeLimit": time_limit,
                        "maxUrls": max_urls
                    }
                    
                    try:
                        response = requests.post(
                            f"{api_url}/v1/deep-research",
                            headers=headers,
                            json=payload
                        )
                        result = response.json()
                        
                        if response.status_code == 200:
                            if result.get('success', False):
                                st.session_state.research_result = result
                                st.success("研究完成!")
                            else:
                                st.error(f"研究失败: {result.get('message', '未知错误')}")
                        else:
                            st.error(f"API请求失败 (状态码 {response.status_code}): {result.get('message', '无错误信息')}")
                    except Exception as e:
                        st.error(f"API请求失败: {str(e)}")

    # 显示结果和下载按钮（在表单外）
    if st.session_state.get('research_result'):
        result = st.session_state.research_result
        
        if 'data' in result and 'finalAnalysis' in result['data']:
            st.subheader("最终分析")
            st.markdown(result['data']['finalAnalysis'])
        
        if 'data' in result and 'sources' in result['data']:
            st.subheader("来源")
            for source in result['data']['sources']:
                st.markdown(f"- [{source.get('title', '无标题')}]({source.get('url', '#')})")
        
        st.download_button(
            label="下载完整报告",
            data=str(result),
            file_name="research_report.json",
            mime="application/json"
        )
