"""
重构后的计算器系统 - 遵循单一职责原则和良好架构设计
"""

import math
from typing import List, Optional, Dict, Any


class Logger:
    """日志记录器 - 负责所有文件操作和日志记录"""
    
    def __init__(self, log_file: str = "calc.log"):
        self.log_file = log_file
    
    def log_operation(self, operation: str, a: float, b: float, result: float) -> None:
        """记录计算操作日志"""
        log_entry = f"{a} {operation} {b} = {result}"
        self._write_to_file(log_entry)
    
    def log_user_info(self, name: str, email: str) -> None:
        """记录用户信息日志"""
        log_entry = f"User: {name} ({email})"
        self._write_to_file(log_entry)
    
    def log_request(self, request: str, result: float) -> None:
        """记录请求日志"""
        log_entry = f"Request: {request}, Result: {result}"
        self._write_to_file(log_entry)
    
    def _write_to_file(self, content: str) -> None:
        """写入文件"""
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(content + "\n")


class HistoryManager:
    """历史记录管理器 - 负责计算历史的存储和管理"""
    
    def __init__(self):
        self.history: List[str] = []
    
    def add_entry(self, operation: str, a: float, b: float, result: float) -> None:
        """添加历史记录条目"""
        entry = f"{a} {operation} {b} = {result}"
        self.history.append(entry)
    
    def get_history(self) -> List[str]:
        """获取历史记录"""
        return self.history.copy()
    
    def clear_history(self) -> None:
        """清空历史记录"""
        self.history.clear()


class StatisticsCalculator:
    """统计计算器 - 专门负责数据统计分析"""
    
    @staticmethod
    def calculate_average(numbers: List[float]) -> float:
        """计算平均值"""
        if not numbers:
            raise ValueError("数字列表不能为空")
        return sum(numbers) / len(numbers)
    
    @staticmethod
    def calculate_max(numbers: List[float]) -> float:
        """计算最大值"""
        if not numbers:
            raise ValueError("数字列表不能为空")
        return max(numbers)
    
    @staticmethod
    def calculate_min(numbers: List[float]) -> float:
        """计算最小值"""
        if not numbers:
            raise ValueError("数字列表不能为空")
        return min(numbers)
    
    @staticmethod
    def calculate_std_dev(numbers: List[float]) -> float:
        """计算标准差"""
        if not numbers:
            raise ValueError("数字列表不能为空")
        
        avg = StatisticsCalculator.calculate_average(numbers)
        variance = sum((n - avg) ** 2 for n in numbers) / len(numbers)
        return math.sqrt(variance)
    
    def calculate_statistics(self, numbers: List[float]) -> Dict[str, float]:
        """计算完整的统计信息"""
        if not numbers:
            raise ValueError("数字列表不能为空")
        
        return {
            "average": self.calculate_average(numbers),
            "max": self.calculate_max(numbers),
            "min": self.calculate_min(numbers),
            "std_dev": self.calculate_std_dev(numbers)
        }


class UserManager:
    """用户管理器 - 负责用户信息管理"""
    
    def __init__(self, logger: Logger):
        self.user_name = ""
        self.user_email = ""
        self.logger = logger
    
    def set_user(self, name: str, email: str) -> None:
        """设置用户信息"""
        self.user_name = name
        self.user_email = email
        self.logger.log_user_info(name, email)
    
    def get_user_info(self) -> str:
        """获取用户信息"""
        return f"{self.user_name} ({self.user_email})"


class FileExporter:
    """文件导出器 - 负责不同格式的文件导出"""
    
    @staticmethod
    def save_history_to_file(history: List[str], filename: str) -> None:
        """保存历史记录到文本文件"""
        with open(filename, "w", encoding="utf-8") as f:
            for item in history:
                f.write(item + "\n")
    
    @staticmethod
    def export_to_html(history: List[str], filename: str) -> None:
        """导出历史记录为HTML格式"""
        html = "<html><head><title>计算历史</title></head><body>"
        html += "<h1>计算历史</h1><ul>"
        for item in history:
            html += f"<li>{item}</li>"
        html += "</ul></body></html>"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)
    
    @staticmethod
    def load_history_from_file(filename: str) -> List[str]:
        """从文件加载历史记录"""
        try:
            with open(filename, "r", encoding="utf-8") as f:
                lines = f.readlines()
                return [line.strip() for line in lines]
        except FileNotFoundError:
            print(f"文件 {filename} 不存在")
            return []


class Formatter:
    """格式化器 - 负责不同格式的输出显示"""
    
    @staticmethod
    def format_history(history: List[str]) -> str:
        """格式化历史记录为可读字符串"""
        if not history:
            return "暂无历史记录"
        
        output = ["=" * 50, "计算历史:", "=" * 50]
        for i, item in enumerate(history, 1):
            output.append(f"{i}. {item}")
        output.append("=" * 50)
        
        return "\n".join(output)
    
    @staticmethod
    def print_history(history: List[str]) -> None:
        """打印历史记录"""
        print(Formatter.format_history(history))


class CalculatorCore:
    """计算器核心 - 专门负责数学计算"""
    
    def __init__(self, history_manager: HistoryManager, logger: Logger):
        self.history_manager = history_manager
        self.logger = logger
        self.result = 0
    
    def _log_operation(self, operation: str, a: float, b: float, result: float) -> None:
        """记录操作日志和历史"""
        self.history_manager.add_entry(operation, a, b, result)
        self.logger.log_operation(operation, a, b, result)
        self.result = result
    
    def add(self, a: float, b: float) -> float:
        """加法"""
        result = a + b
        self._log_operation("+", a, b, result)
        return result
    
    def subtract(self, a: float, b: float) -> float:
        """减法"""
        result = a - b
        self._log_operation("-", a, b, result)
        return result
    
    def multiply(self, a: float, b: float) -> float:
        """乘法"""
        result = a * b
        self._log_operation("*", a, b, result)
        return result
    
    def divide(self, a: float, b: float) -> Optional[float]:
        """除法"""
        if b == 0:
            print("错误：除数不能为0")
            return None
        
        result = a / b
        self._log_operation("/", a, b, result)
        return result


class Calculator:
    """主计算器类 - 协调各个组件的工作"""
    
    def __init__(self, log_file: str = "calc.log"):
        self.logger = Logger(log_file)
        self.history_manager = HistoryManager()
        self.calculator_core = CalculatorCore(self.history_manager, self.logger)
        self.user_manager = UserManager(self.logger)
        self.statistics_calculator = StatisticsCalculator()
        self.file_exporter = FileExporter()
        self.formatter = Formatter()
    
    # 计算功能委托
    def add(self, a: float, b: float) -> float:
        return self.calculator_core.add(a, b)
    
    def subtract(self, a: float, b: float) -> float:
        return self.calculator_core.subtract(a, b)
    
    def multiply(self, a: float, b: float) -> float:
        return self.calculator_core.multiply(a, b)
    
    def divide(self, a: float, b: float) -> Optional[float]:
        return self.calculator_core.divide(a, b)
    
    # 用户管理功能委托
    def set_user(self, name: str, email: str) -> None:
        self.user_manager.set_user(name, email)
    
    def get_user_info(self) -> str:
        return self.user_manager.get_user_info()
    
    # 统计功能委托
    def calculate_statistics(self, numbers: List[float]) -> Dict[str, float]:
        return self.statistics_calculator.calculate_statistics(numbers)
    
    # 文件操作功能委托
    def save_to_file(self, filename: str) -> None:
        self.file_exporter.save_history_to_file(
            self.history_manager.get_history(), filename
        )
    
    def load_from_file(self, filename: str) -> None:
        history = self.file_exporter.load_history