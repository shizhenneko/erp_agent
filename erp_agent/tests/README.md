# ERP Agent 测试套件

完整的测试套件，包含单元测试和集成测试。

## 测试结构

```
tests/
├── test_agent.py       # 主测试文件，包含所有测试
├── test_questions.py   # 10个测试问题定义
├── test_config.py      # 配置测试（已有）
└── README.md          # 本文件
```

## 测试内容

### 1. 单元测试

测试所有核心组件的功能：

#### 时间工具测试 (`TestDateUtils`)
- ✓ 获取当前时间信息
- ✓ 计算日期偏移
- ✓ 获取时期日期范围
- ✓ 计算天数差
- ✓ 获取月份/季度起止
- ✓ 格式化日期为SQL格式

#### 数据库配置测试 (`TestDatabaseConfig`)
- ✓ 配置创建和验证
- ✓ 从字典创建配置
- ✓ 获取连接字符串
- ✓ 配置验证逻辑

#### LLM配置测试 (`TestLLMConfig`)
- ✓ LLM配置创建
- ✓ 配置验证
- ✓ API请求头生成

#### Agent配置测试 (`TestAgentConfig`)
- ✓ Agent配置创建
- ✓ 配置转换为字典

#### SQL执行器测试 (`TestSQLExecutor`)
- ✓ 安全SQL验证（SELECT允许）
- ✓ 危险SQL检测（DROP/DELETE/UPDATE/INSERT禁止）
- ✓ 多语句SQL检测

#### Prompt构建器测试 (`TestPromptBuilder`)
- ✓ 初始化和文件加载
- ✓ Schema加载
- ✓ Few-shot示例加载
- ✓ 系统Prompt模板加载
- ✓ 占位符提取
- ✓ 构建SQL生成Prompt
- ✓ 构建带上下文的Prompt

#### 日志系统测试 (`TestLogger`)
- ✓ 日志设置
- ✓ 获取日志记录器
- ✓ 日志记录功能

#### 测试问题测试 (`TestQuestions`)
- ✓ 所有10个问题存在
- ✓ 问题结构完整性

### 2. 集成测试 (`TestIntegration`)

测试实际系统交互：

- ✓ 数据库连接测试
- ✓ SQL执行器真实查询
- ✓ Agent简单查询测试

### 3. 问题测试

对10个测试问题进行完整测试：

1. **平均每个员工在公司在职多久？** [中等 - 统计分析]
2. **公司目前有多少在职员工？** [简单 - 简单统计]
3. **每个部门分别有多少在职员工？** [简单 - 分组统计]
4. **每个部门今年和去年各新入职了多少人？** [中等 - 时间分析]
5. **在职员工中职级最高的5位员工是谁？** [简单 - 排序查询]
6. **工资最高的前10名在职员工是谁？** [简单 - 排序查询]
7. **去年A部门的平均工资是多少？** [中等 - 时间分析]
8. **从前年3月到去年5月，A部门的平均工资是多少？** [困难 - 时间分析]
9. **从去年到今年涨薪幅度最大的10位员工是谁？** [困难 - 复杂分析]
10. **有没有出现过拖欠员工工资的情况？如果有，是哪些员工？** [困难 - 复杂分析]

## 运行测试

### 前置条件

1. **安装依赖**
```bash
pip install -r requirements.txt
```

2. **配置环境变量**

复制 `.env.example` 为 `.env` 并配置：
```
MOONSHOT_API_KEY=sk-xxxxx
DB_HOST=localhost
DB_PORT=5432
DB_NAME=erp_agent_db
DB_USER=erp_user
DB_PASSWORD=your_password
```

### 运行方式

#### 方式1: 交互式运行

```bash
cd erp_agent/tests
python test_agent.py
```

然后选择测试模式：
- `1` - 运行单元测试（快速，不需要API）
- `2` - 运行10个测试问题（需要API和数据库）
- `3` - 运行所有测试
- `0` - 退出

#### 方式2: 命令行参数

```bash
# 仅运行单元测试
python test_agent.py unit

# 仅运行问题测试
python test_agent.py questions

# 运行所有测试
python test_agent.py all
```

#### 方式3: 使用 unittest

```bash
# 运行所有测试
python -m unittest test_agent

# 运行特定测试类
python -m unittest test_agent.TestDateUtils

# 运行特定测试方法
python -m unittest test_agent.TestDateUtils.test_get_current_datetime
```

## 测试输出

### 单元测试输出

```
======================================================================
运行单元测试套件
======================================================================
test_agent_config_creation (test_agent.TestAgentConfig) ... ok
test_agent_config_to_dict (test_agent.TestAgentConfig) ... ok
test_calculate_date_offset (test_agent.TestDateUtils) ... ok
...

----------------------------------------------------------------------
Ran 35 tests in 2.456s

OK (skipped=1)

======================================================================
测试统计:
  总测试数: 35
  成功: 34
  失败: 0
  错误: 0
  跳过: 1
======================================================================
```

### 问题测试输出

```
======================================================================
问题 1/10: 平均每个员工在公司在职多久？
======================================================================

✓ 成功
答案: 根据查询结果，在职员工平均在公司工作约 4.5 年。
迭代次数: 2
耗时: 3.45秒

======================================================================
测试问题总结
======================================================================
总问题数: 10
成功: 8
失败: 2
成功率: 80.0%

详细结果:
✓ 问题1: 平均每个员工在公司在职多久？
   迭代: 2次, 耗时: 3.45秒
✓ 问题2: 公司目前有多少在职员工？
   迭代: 1次, 耗时: 2.12秒
...
```

## 注意事项

### 跳过的测试

某些集成测试可能会被跳过，如果：
- 缺少必需的环境变量
- 数据库连接不可用
- API密钥无效

### 测试失败排查

1. **单元测试失败**
   - 检查代码是否有语法错误
   - 确认所有依赖已安装
   - 查看具体的错误信息

2. **数据库连接失败**
   - 确认数据库服务正在运行
   - 检查 `.env` 中的数据库配置
   - 测试能否手动连接数据库

3. **API调用失败**
   - 确认 `MOONSHOT_API_KEY` 是否正确
   - 检查网络连接
   - 查看API配额是否用完

4. **问题测试失败**
   - 查看具体的错误信息
   - 检查生成的SQL是否正确
   - 确认数据库中有测试数据

## 测试数据

测试使用的是实际的 ERP 数据库，包含：
- employees 表：员工信息
- salary_history 表：工资历史记录
- departments 表（如果存在）：部门信息

确保数据库中有足够的测试数据才能获得准确的测试结果。

## 持续集成

可以将测试集成到 CI/CD 流程中：

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run unit tests
        run: |
          cd erp_agent/tests
          python test_agent.py unit
```

## 扩展测试

如果需要添加新的测试：

1. 在 `test_agent.py` 中添加新的测试类或测试方法
2. 遵循命名规范：`test_xxx` 
3. 使用 `self.assertEqual`, `self.assertTrue` 等断言方法
4. 添加清晰的文档字符串

示例：
```python
class TestNewComponent(unittest.TestCase):
    """测试新组件"""
    
    def test_new_feature(self):
        """测试新功能"""
        # 测试代码
        result = new_function()
        self.assertEqual(result, expected_value)
```

## 问题反馈

如果遇到测试相关的问题，请提供：
1. 完整的错误信息
2. 运行环境（Python版本、操作系统）
3. 相关的配置信息（隐藏敏感信息）
4. 复现步骤
