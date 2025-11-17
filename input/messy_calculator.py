"""
一个混乱的计算器类 - 包含多种代码坏味道
用于测试代码重构系统
"""

class Calculator:
    """一个做了太多事情的计算器类"""
    
    def __init__(self):
        self.history = []
        self.result = 0
        self.user_name = ""
        self.user_email = ""
        self.log_file = "calc.log"
    
    # 计算功能
    def add(self, a, b):
        """加法"""
        result = a + b
        self.result = result
        self.history.append(f"{a} + {b} = {result}")
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"{a} + {b} = {result}\n")
        return result
    
    def subtract(self, a, b):
        """减法"""
        result = a - b
        self.result = result
        self.history.append(f"{a} - {b} = {result}")
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"{a} - {b} = {result}\n")
        return result
    
    def multiply(self, a, b):
        """乘法"""
        result = a * b
        self.result = result
        self.history.append(f"{a} * {b} = {result}")
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"{a} * {b} = {result}\n")
        return result
    
    def divide(self, a, b):
        """除法"""
        if b == 0:
            print("错误：除数不能为0")
            return None
        result = a / b
        self.result = result
        self.history.append(f"{a} / {b} = {result}")
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"{a} / {b} = {result}\n")
        return result
    
    # 用户管理功能（不应该在这里）
    def set_user(self, name, email):
        """设置用户信息"""
        self.user_name = name
        self.user_email = email
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"User: {name} ({email})\n")
    
    def get_user_info(self):
        """获取用户信息"""
        return f"{self.user_name} ({self.user_email})"
    
    # 数据统计功能（不应该在这里）
    def calculate_statistics(self, numbers):
        """计算统计信息"""
        if not numbers:
            return None
        
        # 计算平均值
        total = 0
        for n in numbers:
            total += n
        avg = total / len(numbers)
        
        # 计算最大值
        max_val = numbers[0]
        for n in numbers:
            if n > max_val:
                max_val = n
        
        # 计算最小值
        min_val = numbers[0]
        for n in numbers:
            if n < min_val:
                min_val = n
        
        # 计算标准差
        variance = 0
        for n in numbers:
            variance += (n - avg) ** 2
        variance = variance / len(numbers)
        std_dev = variance ** 0.5
        
        return {
            "average": avg,
            "max": max_val,
            "min": min_val,
            "std_dev": std_dev
        }
    
    # 文件操作功能（不应该在这里）
    def save_to_file(self, filename):
        """保存历史记录到文件"""
        with open(filename, "w", encoding="utf-8") as f:
            for item in self.history:
                f.write(item + "\n")
    
    def load_from_file(self, filename):
        """从文件加载历史记录"""
        try:
            with open(filename, "r", encoding="utf-8") as f:
                lines = f.readlines()
                self.history = [line.strip() for line in lines]
        except FileNotFoundError:
            print(f"文件 {filename} 不存在")
    
    # 格式化输出功能（不应该在这里）
    def print_history(self):
        """打印历史记录"""
        print("=" * 50)
        print("计算历史:")
        print("=" * 50)
        for i, item in enumerate(self.history, 1):
            print(f"{i}. {item}")
        print("=" * 50)
    
    def export_to_html(self, filename):
        """导出历史记录为HTML"""
        html = "<html><head><title>计算历史</title></head><body>"
        html += "<h1>计算历史</h1><ul>"
        for item in self.history:
            html += f"<li>{item}</li>"
        html += "</ul></body></html>"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)
    
    # 复杂的业务逻辑（函数过长）
    def process_calculation_request(self, request):
        """处理计算请求 - 一个做了太多事情的函数"""
        # 解析请求
        parts = request.split()
        if len(parts) != 3:
            print("格式错误：应为 '数字 操作符 数字'")
            return None
        
        try:
            a = float(parts[0])
            op = parts[1]
            b = float(parts[2])
        except ValueError:
            print("数字格式错误")
            return None
        
        # 执行计算
        if op == "+":
            result = self.add(a, b)
        elif op == "-":
            result = self.subtract(a, b)
        elif op == "*":
            result = self.multiply(a, b)
        elif op == "/":
            result = self.divide(a, b)
        else:
            print(f"不支持的操作符: {op}")
            return None
        
        # 记录日志
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"Request: {request}, Result: {result}\n")
        
        # 检查结果是否异常
        if result is not None:
            if result > 1000:
                print("警告：结果很大")
            if result < -1000:
                print("警告：结果很小")
            if abs(result) < 0.0001:
                print("警告：结果接近0")
        
        return result


# 使用示例
if __name__ == "__main__":
    calc = Calculator()
    
    # 设置用户（不应该在计算器里）
    calc.set_user("张三", "zhangsan@example.com")
    
    # 基本计算
    calc.add(10, 20)
    calc.subtract(50, 30)
    calc.multiply(5, 6)
    calc.divide(100, 4)
    
    # 处理字符串请求
    calc.process_calculation_request("15 * 3")
    
    # 计算统计信息（不应该在计算器里）
    stats = calc.calculate_statistics([10, 20, 30, 40, 50])
    print(f"统计信息: {stats}")
    
    # 打印历史
    calc.print_history()
    
    # 导出HTML（不应该在计算器里）
    calc.export_to_html("history.html")

