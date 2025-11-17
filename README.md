# 基于大模型的代码重构系统

基于论文 [Towards Realistic Project-Level Code Generation via Multi-Agent Collaboration](https://arxiv.org/pdf/2511.03404) 的思路，实现了一个完整的基于大模型的代码重构系统。

## 功能特性

### 核心功能

1. **SSAT (Semantic Software Architecture Tree) 提取**
   - 提取代码的语义架构信息
   - 包含类、方法、函数、导入等完整信息
   - 计算代码复杂度指标

2. **重构机会识别**
   - 基于大模型分析代码
   - 识别违反SOLID原则、DRY原则等问题
   - 评估问题严重程度

3. **重构补丁生成**
   - 根据重构机会生成实际重构代码
   - 保持功能完全一致
   - 遵循最佳实践

## 项目结构

```
refactor/
├── core/
│   └── refactor_manager.py      # 重构管理器（主入口）
├── utils/
│   ├── llm_client.py            # 大模型API客户端
│   ├── ssat_extraction.py       # SSAT提取器
│   └── refactor_engine.py       # 重构引擎（机会识别+补丁生成）
├── input/                       # 输入目录（待重构代码）
└── output/                      # 输出目录（重构后代码）
```

## 使用方法

### 1. 环境配置

设置大模型API密钥：

```bash
# Windows PowerShell
$env:DEEPSEEK="your-api-key"

# Windows CMD
set DEEPSEEK=your-api-key

# Linux/Mac
export DEEPSEEK=your-api-key
```

### 2. 基本使用

```bash
# 处理input目录下的所有Python文件
python -m core.refactor_manager

# 指定输入输出目录
python -m core.refactor_manager --input ./src --output ./refactored

# 指定API密钥和模型
python -m core.refactor_manager --api-key your-key --model deepseek-chat
```

### 3. 编程接口

```python
from core.refactor_manager import RefactorManager
from utils.llm_client import LLMClient

# 创建LLM客户端
llm_client = LLMClient(api_key="your-key")

# 创建重构管理器
manager = RefactorManager(
    input_dir="input",
    output_dir="output",
    llm_client=llm_client
)

# 处理单个文件
from pathlib import Path
result = manager.process_single_file(Path("input/messy_code.py"))

# 查看重构机会
for opp in result["opportunities"]:
    print(f"{opp['problem_type']}: {opp['description']}")

# 处理整个目录
manager.process_directory()
```

## 工作流程

1. **SSAT提取**：分析代码结构，提取语义信息
2. **重构机会识别**：使用大模型分析代码，识别重构机会
3. **重构补丁生成**：根据识别的问题生成重构后的代码
4. **结果保存**：保存重构后的代码和重构机会信息

## 输出文件

- `output/原文件名.py`：重构后的代码
- `output/原文件名_opportunities.json`：识别的重构机会详情

## 依赖要求

```bash
pip install requests urllib3
```

## 注意事项

1. 需要有效的DeepSeek API密钥（或其他兼容的API）
2. 大模型调用可能需要较长时间，请耐心等待
3. 重构后的代码建议进行测试验证
4. 对于大型项目，建议分批处理

## 技术特点

- **基于大模型**：利用LLM的代码理解能力
- **语义分析**：使用SSAT进行深度代码分析
- **完整流程**：从识别到生成的一站式解决方案
- **可扩展性**：支持不同的LLM提供商

## 参考论文

Zhao, Q., Zhang, L., Liu, F., et al. (2025). Towards Realistic Project-Level Code Generation via Multi-Agent Collaboration and Semantic Architecture Modeling. arXiv preprint.

