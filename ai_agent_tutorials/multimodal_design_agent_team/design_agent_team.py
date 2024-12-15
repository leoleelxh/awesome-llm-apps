from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.duckduckgo import DuckDuckGo
import streamlit as st
from PIL import Image
from typing import List, Optional
from dotenv import load_dotenv
import os
import re
import tempfile

# 加载环境变量
load_dotenv()

def display_score(score: float, category: str):
    """显示评分结果"""
    # 根据分数选择评价文案和表情
    if score >= 8.5:
        feedback = "非常棒的设计！ 🌟"
        color = "#2E7D32"  # 深绿色
    elif score >= 7:
        feedback = "不错的设计！ 👍"
        color = "#1976D2"  # 蓝色
    elif score >= 5:
        feedback = "一般的设计，继续努力！ 💪"
        color = "#FFA000"  # 橙色
    elif score >= 3:
        feedback = "没关系，继续加油！ 🎯"
        color = "#E64A19"  # 红橙色
    else:
        feedback = "好好修改，也许你可以的 💡"
        color = "#D32F2F"  # 红色

    # 使用HTML和CSS来美化显示
    st.markdown(f"""
        <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
            <h3 style='text-align: center; color: {color}; margin-bottom: 10px;'>{category}评分</h3>
            <div style='font-size: 48px; text-align: center; color: {color}; font-weight: bold;'>
                {score}/10
            </div>
            <div style='text-align: center; font-size: 24px; margin-top: 10px;'>
                {feedback}
            </div>
        </div>
    """, unsafe_allow_html=True)

def process_images(files):
    """处理上传的图片文件"""
    processed_images = []
    for file in files:
        try:
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, f"temp_{file.name}")
            
            with open(temp_path, "wb") as f:
                f.write(file.getvalue())
            
            processed_images.append(temp_path)
            
        except Exception as e:
            st.error(f"处理图片时出错 {file.name}: {str(e)}")
            continue
    return processed_images

def analyze_content(agent, prompt, images, analysis_type):
    """分析内容并显示结果"""
    try:
        response = agent.run(message=prompt, images=images)
        content = response.content
        
        # 提取分数
        score_match = re.search(r'SCORE:\s*(\d+\.?\d*)', content)
        score = float(score_match.group(1)) if score_match else 5.0
        
        # 提取总结
        summary_match = re.search(r'SUMMARY:(.*?)DETAILS:', content, re.DOTALL)
        summary = summary_match.group(1).strip() if summary_match else ""
        
        # 提取详细分析
        details = content.split('DETAILS:')[-1].strip()
        
        # 显示结果
        display_score(score, analysis_type)
        
        # 显示总结
        st.markdown("### 总结与建议")
        st.markdown(summary)
        
        # 显示详细分析
        st.markdown("### 详细分析")
        st.markdown(details)
        
        return score
        
    except Exception as e:
        st.error(f"分析过程中出现错误: {str(e)}")
        st.markdown(content)
        return 5.0

def initialize_agents(api_key: str) -> tuple[Agent, Agent, Agent]:
    """初始化 AI 代理"""
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
        st.error(f"初始化代理时出错: {str(e)}")
        return None, None, None

def get_prompts(specific_elements, context):
    """获取分析提示语"""
    vision_prompt = f"""
    Analyze these designs focusing on: {', '.join(specific_elements)}
    Additional context: {context}

    Please provide your analysis in the following format:
    1. Score (0-10) based on visual design principles
    2. Brief summary and key suggestions (2-3 sentences)
    3. Detailed analysis with the following aspects:
       - Design elements and patterns
       - Color schemes and typography
       - Layout and visual hierarchy
       - Brand consistency

    Please format your response with clear headers and bullet points.
    Focus on concrete observations and actionable insights.
    Please provide your analysis in Chinese (Simplified Chinese).

    Response format:
    SCORE: [number]
    SUMMARY: [brief summary and suggestions]
    DETAILS: [detailed analysis]
    """

    ux_prompt = f"""
    Analyze these designs focusing on: {', '.join(specific_elements)}
    Additional context: {context}

    Please provide your analysis in the following format:
    1. Score (0-10) based on user experience principles
    2. Brief summary and key suggestions (2-3 sentences)
    3. Detailed analysis with the following aspects:
       - User flows and navigation
       - Interaction patterns
       - Accessibility and usability
       - Areas for improvement

    Please format your response with clear headers and bullet points.
    Focus on concrete observations and actionable improvements.
    Please provide your analysis in Chinese (Simplified Chinese).

    Response format:
    SCORE: [number]
    SUMMARY: [brief summary and suggestions]
    DETAILS: [detailed analysis]
    """

    market_prompt = f"""
    Analyze market positioning and trends based on these designs.
    Context: {context}

    Please provide your analysis in the following format:
    1. Score (0-10) based on market competitiveness
    2. Brief summary and key suggestions (2-3 sentences)
    3. Detailed analysis with the following aspects:
       - Market positioning
       - Competitive advantages
       - Industry trends
       - Growth opportunities

    Please format your response with clear headers and bullet points.
    Focus on concrete market insights and actionable recommendations.
    Please provide your analysis in Chinese (Simplified Chinese).

    Response format:
    SCORE: [number]
    SUMMARY: [brief summary and suggestions]
    DETAILS: [detailed analysis]
    """

    return vision_prompt, ux_prompt, market_prompt

def main():
    st.title("多模态 AI 设计助手团队")
    
    # Sidebar - API 配置
    with st.sidebar:
        st.header("🔑 API 配置")

        if "api_key_input" not in st.session_state:
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

    # 主界面逻辑
    if st.session_state.api_key_input:
        vision_agent, ux_agent, market_agent = initialize_agents(st.session_state.api_key_input)
        
        if all([vision_agent, ux_agent, market_agent]):
            # 文件上传部分
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

            # 分析配置
            st.header("🎯 分析配置")

            analysis_types = st.multiselect(
                "选择分析类型",
                ["视觉设计", "用户体验", "市场分析"],
                default=["视觉设计"],
                placeholder="请选择分析类型..."
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

            # 分析过程
            if st.button("🚀 开始分析", type="primary"):
                if design_files:
                    try:
                        st.header("📊 分析结果")
                        
                        # 处理图片
                        design_images = process_images(design_files)
                        competitor_images = process_images(competitor_files) if competitor_files else []
                        all_images = design_images + competitor_images
                        
                        # 获取提示语
                        vision_prompt, ux_prompt, market_prompt = get_prompts(specific_elements, context)
                        
                        # 执行分析
                        scores = {}
                        
                        if "视觉设计" in analysis_types:
                            st.subheader("🎨 视觉设计分析")
                            with st.spinner("正在分析视觉设计..."):
                                scores['视觉设计'] = analyze_content(
                                    vision_agent, vision_prompt, all_images, "视觉设计"
                                )
                        
                        if "用户体验" in analysis_types:
                            st.subheader("🔄 用户体验分析")
                            with st.spinner("正在分析用户体验..."):
                                scores['用户体验'] = analyze_content(
                                    ux_agent, ux_prompt, all_images, "用户体验"
                                )
                        
                        if "市场分析" in analysis_types:
                            st.subheader("📊 市场分析")
                            with st.spinner("正在进行市场分析..."):
                                scores['市场分析'] = analyze_content(
                                    market_agent, market_prompt, all_images, "市场竞争力"
                                )
                        
                        # 显示综合评分
                        if len(scores) > 1:
                            st.subheader("🎯 综合评估")
                            avg_score = sum(scores.values()) / len(scores)
                            display_score(avg_score, "综合")
                            
                    except Exception as e:
                        st.error(f"分析过程中出现错误: {str(e)}")
                else:
                    st.warning("请至少上传一张设计图进行分析。")
    else:
        st.info("👈 请在侧边栏输入您的 API 密钥以开始")

    # Footer
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

if __name__ == "__main__":
    main() 