"""
重构管理器 - 集成完整的基于大模型的重构流程
"""
import os
import sys
from pathlib import Path
import json
from typing import List, Dict, Any, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.ssat_extraction import SSATExtractorAST
from utils.llm_client import LLMClient
from utils.refactor_engine import RefactorEngine


class RefactorManager:
    """
    重构管理器 - 基于大模型的代码重构系统
    实现完整的重构流程：SSAT提取 -> 重构机会识别 -> 重构补丁生成
    """
    
    def __init__(
        self, 
        input_dir: str = "input", 
        output_dir: str = "output",
        llm_client: Optional[LLMClient] = None
    ):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.input_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
        # 初始化重构引擎
        self.llm_client = llm_client or LLMClient()
        self.refactor_engine = RefactorEngine(self.llm_client)
        
    def process_directory(self, verbose: bool = True):
        """
        处理输入目录中的所有Python文件
        
        Args:
            verbose: 是否显示详细输出
        """
        python_files = list(self.input_dir.glob("*.py"))
        
        if not python_files:
            if verbose:
                print(f"在 {self.input_dir} 中没有找到Python文件")
            return
        
        for py_file in python_files:
            if verbose:
                print(f"\n{'='*60}")
                print(f"处理文件: {py_file.name}")
                print(f"{'='*60}")
            self.process_single_file(py_file, verbose=verbose)
    
    def process_single_file(self, file_path: Path, verbose: bool = True) -> Dict[str, Any]:
        """
        处理单个Python文件 - 完整的重构流程
        
        Args:
            file_path: 文件路径
            verbose: 是否显示详细输出
        
        Returns:
            处理结果字典，包含：
            - opportunities: 识别的重构机会
            - refactored_code: 重构后的代码
            - output_path: 输出文件路径
        """
        try:
            # 步骤1: 提取SSAT结构
            if verbose:
                print("\n[1/3] 提取代码结构 (SSAT)...")
            extractor = SSATExtractorAST(str(file_path))
            ssat = extractor.extract()
            if verbose:
                print(f"  ✓ 提取完成: {len(ssat.get('classes', {}))} 个类")
            
            # 步骤2: 识别重构机会
            if verbose:
                print("\n[2/3] 识别重构机会...")
            opportunities = self.refactor_engine.detect_opportunities(str(file_path))
            if verbose:
                print(f"  ✓ 识别到 {len(opportunities)} 个重构机会")
                for i, opp in enumerate(opportunities, 1):
                    print(f"    {i}. [{opp.get('severity', 'medium').upper()}] {opp.get('problem_type')} - {opp.get('location')}")
            
            # 步骤3: 生成重构补丁
            if verbose:
                print("\n[3/3] 生成重构代码...")
            with open(file_path, 'r', encoding='utf-8') as f:
                original_code = f.read()
            
            refactored_code = self.refactor_engine.generate_patch(
                original_code=original_code,
                opportunities=opportunities
            )
            
            # 步骤4: 保存结果
            output_file = self.output_dir / file_path.name
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(refactored_code)
            
            if verbose:
                print(f"  ✓ 重构完成，输出文件: {output_file}")
            
            # 保存重构机会信息（可选）
            opportunities_file = self.output_dir / f"{file_path.stem}_opportunities.json"
            with open(opportunities_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "file": str(file_path),
                    "opportunities": opportunities,
                    "ssat": ssat
                }, f, indent=2, ensure_ascii=False)
            
            return {
                "opportunities": opportunities,
                "refactored_code": refactored_code,
                "output_path": str(output_file),
                "ssat": ssat
            }
            
        except Exception as e:
            if verbose:
                print(f"  ✗ 处理文件 {file_path.name} 时出错: {e}")
            import traceback
            if verbose:
                traceback.print_exc()
            raise
    
    def refactor_code_string(
        self, 
        code: str, 
        code_name: str = "code.py"
    ) -> Dict[str, Any]:
        """
        直接重构代码字符串（不涉及文件）
        
        Args:
            code: 代码字符串
            code_name: 代码名称（用于上下文）
        
        Returns:
            处理结果字典
        """
        # 创建临时文件
        temp_file = self.input_dir / f"_temp_{code_name}"
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            return self.process_single_file(temp_file, verbose=False)
        finally:
            # 清理临时文件
            if temp_file.exists():
                temp_file.unlink()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='基于大模型的代码重构工具')
    parser.add_argument('--input', '-i', default='input', help='输入目录路径 (默认: input)')
    parser.add_argument('--output', '-o', default='output', help='输出目录路径 (默认: output)')
    parser.add_argument('--api-key', help='大模型API密钥（可选，默认从环境变量DEEPSEEK读取）')
    parser.add_argument('--model', default='deepseek-chat', help='模型名称 (默认: deepseek-chat)')
    
    args = parser.parse_args()
    
    # 创建LLM客户端
    llm_client = None
    if args.api_key or os.getenv("DEEPSEEK"):
        llm_client = LLMClient(api_key=args.api_key, model=args.model)
    
    # 创建管理器并处理
    manager = RefactorManager(args.input, args.output, llm_client=llm_client)
    manager.process_directory()


if __name__ == "__main__":
    main()
