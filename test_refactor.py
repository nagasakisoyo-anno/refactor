"""
快速测试脚本 - 验证重构系统是否正常工作
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from utils.llm_client import LLMClient
from utils.refactor_engine import RefactorEngine
from core.refactor_manager import RefactorManager


def test_llm_connection():
    """测试LLM连接"""
    print("=" * 60)
    print("测试1: LLM连接")
    print("=" * 60)
    
    try:
        client = LLMClient()
        response = client.call("请用一句话回答：Python是什么？", max_tokens=50)
        print(f"✓ LLM连接成功")
        print(f"  响应: {response[:100]}...")
        return True
    except Exception as e:
        print(f"✗ LLM连接失败: {e}")
        print("  请检查环境变量DEEPSEEK是否设置正确")
        return False


def test_ssat_extraction():
    """测试SSAT提取"""
    print("\n" + "=" * 60)
    print("测试2: SSAT提取")
    print("=" * 60)
    
    try:
        from utils.ssat_extraction import SSATExtractorAST
        
        input_file = Path("input/messy_calculator.py")
        if not input_file.exists():
            print(f"✗ 测试文件不存在: {input_file}")
            return False
        
        extractor = SSATExtractorAST(str(input_file))
        ssat = extractor.extract()
        
        print(f"✓ SSAT提取成功")
        print(f"  文件: {ssat['file_name']}")
        print(f"  类数量: {len(ssat.get('classes', {}))}")
        print(f"  函数数量: {len(ssat.get('functions', []))}")
        print(f"  导入数量: {len(ssat.get('imports', []))}")
        
        # 显示第一个类的信息
        if ssat.get('classes'):
            first_class = list(ssat['classes'].values())[0]
            print(f"  第一个类的方法数: {len(first_class.get('methods', []))}")
        
        return True
    except Exception as e:
        print(f"✗ SSAT提取失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_refactor_opportunity_detection():
    """测试重构机会识别"""
    print("\n" + "=" * 60)
    print("测试3: 重构机会识别")
    print("=" * 60)
    
    try:
        input_file = Path("input/messy_calculator.py")
        if not input_file.exists():
            print(f"✗ 测试文件不存在: {input_file}")
            return False
        
        engine = RefactorEngine()
        opportunities = engine.detect_opportunities(str(input_file))
        
        print(f"✓ 重构机会识别成功")
        print(f"  识别到 {len(opportunities)} 个重构机会:")
        for i, opp in enumerate(opportunities[:3], 1):  # 只显示前3个
            print(f"    {i}. [{opp.get('severity', 'medium').upper()}] {opp.get('problem_type')}")
            print(f"       位置: {opp.get('location')}")
        
        return True
    except Exception as e:
        print(f"✗ 重构机会识别失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_refactor():
    """测试完整重构流程"""
    print("\n" + "=" * 60)
    print("测试4: 完整重构流程")
    print("=" * 60)
    
    try:
        manager = RefactorManager(input_dir="input", output_dir="output")
        
        input_file = Path("input/messy_calculator.py")
        if not input_file.exists():
            print(f"✗ 测试文件不存在: {input_file}")
            return False
        
        result = manager.process_single_file(input_file, verbose=False)
        
        print(f"✓ 完整重构流程成功")
        print(f"  重构机会数: {len(result.get('opportunities', []))}")
        print(f"  输出文件: {result.get('output_path')}")
        
        # 检查输出文件是否存在
        output_file = Path(result.get('output_path', ''))
        if output_file.exists():
            size = output_file.stat().st_size
            print(f"  输出文件大小: {size} 字节")
        
        return True
    except Exception as e:
        print(f"✗ 完整重构流程失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("代码重构系统 - 功能测试")
    print("=" * 60)
    
    # 检查环境变量
    if not os.getenv("DEEPSEEK"):
        print("\n⚠ 警告: 未设置环境变量DEEPSEEK")
        print("  某些测试可能会失败")
        print("  设置方法: export DEEPSEEK=your-api-key")
    
    results = []
    
    # 运行测试
    results.append(("LLM连接", test_llm_connection()))
    results.append(("SSAT提取", test_ssat_extraction()))
    
    # 只有LLM连接成功才测试需要API的功能
    if results[0][1]:
        results.append(("重构机会识别", test_refactor_opportunity_detection()))
        results.append(("完整重构流程", test_full_refactor()))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {name}: {status}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！系统可以正常使用。")
    else:
        print("\n⚠ 部分测试失败，请检查配置和依赖。")


if __name__ == "__main__":
    main()

