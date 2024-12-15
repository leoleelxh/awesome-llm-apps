# 多模态 AI 设计助手团队

一个基于 Gemini API 的多模态设计分析工具，能够对UI/UX设计进行全方位的智能评估。

## ✨ 主要特性

### 🎯 多维度分析
- **视觉设计分析**：评估设计元素、色彩方案、排版和视觉层次
- **用户体验分析**：分析用户流程、交互模式和可用性
- **市场竞争分析**：评估市场定位和竞争优势

### 🔍 智能评分系统
- 10分制综合评分
- 细分领域独立评分
- 可视化评分展示
- 详细的分析报告和建议

### 💡 使用特点
- 支持多图片上传分析
- 支持竞品设计对比
- 自定义分析维度
- 中文友好界面
- 详细的使用建议

### ⚙️ 技术特性
- 基于 Streamlit 的响应式界面
- 环境变量配置（.env）支持
- API 密钥安全存储
- 智能边栏管理（配置后自动隐藏）
- 异常处理和用户提示

## 🚀 快速开始

1. 配置环境
   ```bash
   # Clone the repository
   git clone https://github.com/Shubhamsaboo/awesome-llm-apps.git
   cd ai_agent_tutorials/multimodal_design_agent_team

   # Create and activate virtual environment (optional)
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Get API Key**
   - Visit [Google AI Studio](https://aistudio.google.com/apikey)
   - Generate an API key

3. **Run the Application**
   ```bash
   streamlit run design_agent_team.py
   ```

4. **Use the Application**
   - Enter your Gemini API key in the sidebar
   - Upload design files (supported formats: JPG, JPEG, PNG)
   - Select analysis types and focus areas
   - Add context if needed
   - Click "Run Analysis" to get insights


## Technical Stack

- **Frontend**: Streamlit
- **AI Model**: Google Gemini 2.0
- **Image Processing**: Pillow
- **Market Research**: DuckDuckGo Search API
- **Framework**: Phidata for agent orchestration

## Tips for Best Results

- Upload clear, high-resolution images
- Include multiple views/screens for better context
- Add competitor designs for comparative analysis
- Provide specific context about your target audience

