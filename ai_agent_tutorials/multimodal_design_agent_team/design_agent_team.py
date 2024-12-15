from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.duckduckgo import DuckDuckGo
import streamlit as st
from PIL import Image
from typing import List, Optional
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

def initialize_agents(api_key: str) -> tuple[Agent, Agent, Agent]:
    try:
        model = Gemini(id="gemini-2.0-flash-exp", api_key=api_key)
        
        vision_agent = Agent(
            model=model,
            instructions=[
                "You are a visual analysis expert that:",
                "1. Identifies design elements, patterns, and visual hierarchy",
                "2. Analyzes color schemes, typography, and layouts",
                "3. Detects UI components and their relationships",
                "4. Evaluates visual consistency and branding",
                "Be specific and technical in your analysis",
                "Please provide your analysis in Chinese (Simplified Chinese)."
            ],
            markdown=True
        )

        ux_agent = Agent(
            model=model,
            instructions=[
                "You are a UX analysis expert that:",
                "1. Evaluates user flows and interaction patterns",
                "2. Identifies usability issues and opportunities",
                "3. Suggests UX improvements based on best practices",
                "4. Analyzes accessibility and inclusive design",
                "Focus on user-centric insights and practical improvements",
                "Please provide your analysis in Chinese (Simplified Chinese)."
            ],
            markdown=True
        )

        market_agent = Agent(
            model=model,
            tools=[DuckDuckGo(search=True)],
            instructions=[
                "You are a market research expert that:",
                "1. Identifies market trends and competitor patterns",
                "2. Analyzes similar products and features",
                "3. Suggests market positioning and opportunities",
                "4. Provides industry-specific insights",
                "Focus on actionable market intelligence",
                "Please provide your analysis in Chinese (Simplified Chinese)."
            ],
            markdown=True
        )
        
        return vision_agent, ux_agent, market_agent
    except Exception as e:
        st.error(f"Error initializing agents: {str(e)}")
        return None, None, None

# Sidebar for API key input
with st.sidebar:
    st.header("🔑 API 配置")

    if "api_key_input" not in st.session_state:
        # 从环境变量获取 API key
        st.session_state.api_key_input = os.getenv("GEMINI_API_KEY", "")
        
    api_key = st.text_input(
        "输入您的 Gemini API 密钥",
        value=st.session_state.api_key_input,
        type="password",
        help="从 Google AI Studio 获取您的 API 密钥，或在 .env 文件中设置 GEMINI_API_KEY",
        key="api_key_widget"  
    )

    if api_key != st.session_state.api_key_input:
        st.session_state.api_key_input = api_key
    
    if api_key:
        st.success("API 密钥已提供! ✅")
    else:
        st.warning("请输入您的 API 密钥以继续")
        st.markdown("""
        获取 API 密钥:
        1. 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)
        """)

st.title("多模态 AI 设计助手团队")

if st.session_state.api_key_input:
    vision_agent, ux_agent, market_agent = initialize_agents(st.session_state.api_key_input)
    
    if all([vision_agent, ux_agent, market_agent]):
        # File Upload Section
        st.header("📤 上传内容")
        col1, space, col2 = st.columns([1, 0.1, 1])
        
        with col1:
            design_files = st.file_uploader(
                "上传 UI/UX 设计图",
                type=["jpg", "jpeg", "png"],
                accept_multiple_files=True,
                key="designs",
                help="将文件拖放到此处 • 每个文件限制200MB • 支持JPG、JPEG、PNG格式",
                label_visibility="visible"
            )
            
            if design_files:
                for file in design_files:
                    try:
                        image = Image.open(file)
                        st.image(
                            image, 
                            caption=file.name, 
                            use_column_width=True
                        )
                    except Exception as e:
                        st.error(f"无法打开图片 {file.name}: {str(e)}")

        with col2:
            competitor_files = st.file_uploader(
                "上传竞品设计图（可选）",
                type=["jpg", "jpeg", "png"],
                accept_multiple_files=True,
                key="competitors",
                help="将文件拖放到此处 • 每个文件限制200MB • 支持JPG、JPEG、PNG格式",
                label_visibility="visible"
            )
            
            if competitor_files:
                for file in competitor_files:
                    try:
                        image = Image.open(file)
                        st.image(
                            image, 
                            caption=f"竞品: {file.name}", 
                            use_column_width=True
                        )
                    except Exception as e:
                        st.error(f"无法打开图片 {file.name}: {str(e)}")

        # Analysis Configuration
        st.header("🎯 分析配置")

        analysis_types = st.multiselect(
            "选择分析类型",
            ["视觉设计", "用户体验", "市场分析"],
            default=["视觉设计"]
        )

        specific_elements = st.multiselect(
            "关注领域",
            ["配色方案", "字体排版", "布局设计", "导航结构", 
             "交互设计", "无障碍性", "品牌设计", "市场契合度"],
            default=[],
            placeholder="请选择关注的设计领域..."
        )

        context = st.text_area(
            "补充说明",
            placeholder="描述您的产品、目标用户或特定关注点...",
            help="提供更多上下文信息以获得更准确的分析结果"
        )

        # Analysis Process
        if st.button("🚀 开始分析", type="primary"):
            if design_files:
                try:
                    st.header("📊 分析结果")
                    
                    # Process images once
                    def process_images(files):
                        processed_images = []
                        for file in files:
                            try:
                                # Create a temporary file path for the image
                                import tempfile
                                import os

                                temp_dir = tempfile.gettempdir()
                                temp_path = os.path.join(temp_dir, f"temp_{file.name}")
                                
                                # Save the uploaded file to temp location
                                with open(temp_path, "wb") as f:
                                    f.write(file.getvalue())
                                
                                # Add the path to processed images
                                processed_images.append(temp_path)
                                
                            except Exception as e:
                                st.error(f"Error processing image {file.name}: {str(e)}")
                                continue
                        return processed_images
                    
                    design_images = process_images(design_files)
                    competitor_images = process_images(competitor_files) if competitor_files else []
                    all_images = design_images + competitor_images
                    
                    # Visual Design Analysis
                    if "视觉设计" in analysis_types and design_files:
                        with st.spinner("🎨 正在分析视觉设计..."):
                            if all_images:
                                vision_prompt = f"""
                                Analyze these designs focusing on: {', '.join(specific_elements)}
                                Additional context: {context}
                                Provide specific insights about visual design elements.
                                
                                Please format your response with clear headers and bullet points.
                                Focus on concrete observations and actionable insights.
                                Please provide your analysis in Chinese (Simplified Chinese).
                                """
                                
                                response = vision_agent.run(
                                    message=vision_prompt,
                                    images=all_images
                                )
                                
                                st.subheader("🎨 视觉设计分析")
                                st.markdown(response.content)
                    
                    # UX Analysis
                    if "用户体验" in analysis_types:
                        with st.spinner("🔄 正在分析用户体验..."):
                            if all_images:
                                ux_prompt = f"""
                                Evaluate the user experience considering: {', '.join(specific_elements)}
                                Additional context: {context}
                                Focus on user flows, interactions, and accessibility.
                                
                                Please format your response with clear headers and bullet points.
                                Focus on concrete observations and actionable improvements.
                                Please provide your analysis in Chinese (Simplified Chinese).
                                """
                                
                                response = ux_agent.run(
                                    message=ux_prompt,
                                    images=all_images
                                )
                                
                                st.subheader("🔄 用户体验分析")
                                st.markdown(response.content)
                    
                    # Market Analysis
                    if "市场分析" in analysis_types:
                        with st.spinner("📊 正在进行市场分析..."):
                            market_prompt = f"""
                            Analyze market positioning and trends based on these designs.
                            Context: {context}
                            Compare with competitor designs if provided.
                            Suggest market opportunities and positioning.
                            
                            Please format your response with clear headers and bullet points.
                            Focus on concrete market insights and actionable recommendations.
                            Please provide your analysis in Chinese (Simplified Chinese).
                            """
                            
                            response = market_agent.run(
                                message=market_prompt,
                                images=all_images
                            )
                            
                            st.subheader("📊 市场分析")
                            st.markdown(response.content)
                    
                    # Combined Insights
                    if len(analysis_types) > 1:
                        st.subheader("🎯 关键发现")
                        st.info("""
                        以上是来自多个专业 AI 助手的详细分析，每个助手都专注于其专业领域：
                        - 视觉设计助手：分析设计元素和模式
                        - 用户体验助手：评估用户体验和交互
                        - 市场研究助手：提供市场背景和机会
                        """)
                
                except Exception as e:
                    st.error(f"分析过程中出现错误: {str(e)}")
                    st.error("请检查您的 API 密钥并重试。")
            else:
                st.warning("请至少上传一张设计图进行分析。")
    else:
        st.info("👈 请在侧边栏输入您的 API 密钥以开始")
else:
    st.info("👈 请在侧边栏输入您的 API 密钥以开始")

# Footer with usage tips
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <h4>使用技巧</h4>
    <p>
    • 上传清晰的高分辨率图片<br>
    • 包含多个视图/界面以提供更好的上下文<br>
    • 添加竞品设计以进行对比分析<br>
    • 提供具体的目标用户群体信息
    </p>
</div>
""", unsafe_allow_html=True) 