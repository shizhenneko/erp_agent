# 测试指南

ERP Agent 项目的完整测试套件使用说明。

## 快速开始

### 最简单的方式

```bash
# 在项目根目录运行
python run_tests.py
```

会显示交互式菜单，选择你需要的测试类型。

### 命令行方式

```bash
# 仅运行单元测试（快速，不需要API）
python run_tests.py unit

# 仅运行10个测试问题（需要API）
python run_tests.py questions

# 运行所有测试
python run_tests.py all
```

## 测试内容

### 1. 单元测试 (35+ 测试)

测试所有核心组件：
- ✅ 配置模块 (DatabaseConfig, LLMConfig, AgentConfig)
- ✅ 时间工具 (8个日期处理函数)
- ✅ SQL执行器 (安全验证、执行)
- ✅ Prompt构建器 (模板加载、构建)
- ✅ 日志系统 (日志记录)

**特点：**
- 快速执行（2-5秒）
- 不需要API密钥
- 不需要数据库连接
- 适合开发时快速验证

### 2. 测试问题 (10个业务场景)

测试完整的查询流程：

| ID | 问题 | 难度 |
|----|------|------|
| 1 | 平均每个员工在公司在职多久？ | 中等 |
| 2 | 公司目前有多少在职员工？ | 简单 |
| 3 | 每个部门分别有多少在职员工？ | 简单 |
| 4 | 每个部门今年和去年各新入职了多少人？ | 中等 |
| 5 | 在职员工中职级最高的5位员工是谁？ | 简单 |
| 6 | 工资最高的前10名在职员工是谁？ | 简单 |
| 7 | 去年A部门的平均工资是多少？ | 中等 |
| 8 | 从前年3月到去年5月，A部门的平均工资是多少？ | 困难 |
| 9 | 从去年到今年涨薪幅度最大的10位员工是谁？ | 困难 |
| 10 | 有没有出现过拖欠员工工资的情况？ | 困难 |

**特点：**
- 需要API密钥和数据库
- 测试完整的ReAct流程
- 每个问题2-5秒
- 总计约30-50秒

## 环境准备

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量（问题测试需要）

复制 `.env.example` 为 `.env` 并配置：

```env
# LLM配置
MOONSHOT_API_KEY=sk-xxxxx

# 数据库配置
DB_HOST=localhost
DB_PORT=5432
DB_NAME=erp_agent_db
DB_USER=erp_user
DB_PASSWORD=your_password
```

## 运行选项

### 选项A: 交互式运行 (推荐)

```bash
python run_tests.py
```

### 选项B: 命令行参数

```bash
python run_tests.py unit       # 单元测试
python run_tests.py questions  # 问题测试
python run_tests.py all        # 所有测试
```

### 选项C: 直接运行测试文件

```bash
cd erp_agent/tests
python test_agent.py
```

### 选项D: 使用 unittest

```bash
# 运行所有测试
python -m unittest erp_agent.tests.test_agent

# 运行特定测试类
python -m unittest erp_agent.tests.test_agent.TestDateUtils

# 运行特定测试方法
python -m unittest erp_agent.tests.test_agent.TestDateUtils.test_get_current_datetime
```

## 测试输出

### 成功的单元测试

```
======================================================================
运行单元测试套件
======================================================================
test_calculate_date_offset (test_agent.TestDateUtils) ... ok
test_database_config_creation (test_agent.TestDatabaseConfig) ... ok
...
----------------------------------------------------------------------
Ran 35 tests in 2.456s

OK (skipped=1)

测试统计:
  总测试数: 35
  成功: 34
  失败: 0
  错误: 0
  跳过: 1
```

### 成功的问题测试

```
======================================================================
问题 1/10: 平均每个员工在公司在职多久？
======================================================================

✓ 成功
答案: 根据查询结果，在职员工平均在公司工作约 4.5 年。
迭代次数: 2
耗时: 3.45秒

...

测试问题总结
总问题数: 10
成功: 9
失败: 1
成功率: 90.0%
```

## 故障排查

### 单元测试失败

1. **检查依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **检查Python版本**
   ```bash
   python --version  # 需要 3.8+
   ```

3. **查看错误信息**
   - 单元测试失败通常是代码问题
   - 查看详细的错误堆栈

### 问题测试失败

1. **环境变量未配置**
   ```
   ⚠️  缺少必需的环境变量: MOONSHOT_API_KEY
   ```
   **解决**: 配置 `.env` 文件

2. **数据库连接失败**
   ```
   ❌ 数据库连接失败: connection refused
   ```
   **解决**: 
   - 检查数据库是否运行
   - 验证 `.env` 中的数据库配置
   - 测试手动连接

3. **API调用失败**
   ```
   ✗ API调用失败: 401 Unauthorized
   ```
   **解决**:
   - 检查 `MOONSHOT_API_KEY` 是否正确
   - 确认API配额未用完
   - 检查网络连接

4. **某些问题失败**
   - 这可能是正常的（困难问题可能不稳定）
   - 查看具体的错误信息
   - 成功率 ≥ 80% 即可

## 目录结构

```
ppt_generator/
├── run_tests.py              # 快速测试脚本 (新)
├── TEST_GUIDE.md            # 快速入门指南 (新)
├── TESTING.md               # 本文件 (新)
├── COMPLETION_SUMMARY.md    # 完成总结 (新)
└── erp_agent/
    └── tests/
        ├── test_agent.py         # 主测试文件 (完善)
        ├── test_questions.py     # 测试问题 (增强)
        ├── README.md            # 详细文档 (新)
        └── TESTING_SUMMARY.md   # 测试总结 (新)
```

## 更多文档

- **TEST_GUIDE.md** - 快速入门指南，适合首次使用
- **erp_agent/tests/README.md** - 详细的测试文档
- **erp_agent/tests/TESTING_SUMMARY.md** - 完整的测试总结
- **COMPLETION_SUMMARY.md** - 开发完成总结

## 开发建议

### 开发流程

1. **修改代码前** - 运行单元测试确保基准
2. **修改代码后** - 运行相关测试验证
3. **提交代码前** - 运行所有测试确保质量

### 添加新测试

如果需要测试新功能：

```python
# 在 test_agent.py 中添加
class TestNewFeature(unittest.TestCase):
    """测试新功能"""
    
    def test_basic_functionality(self):
        """测试基础功能"""
        result = new_function()
        self.assertEqual(result, expected)
```

### CI/CD 集成

可以在CI/CD流程中使用：

```yaml
# GitHub Actions 示例
- name: Run tests
  run: |
    pip install -r requirements.txt
    python run_tests.py unit
```

## 性能指标

- **单元测试**: 2-5秒
- **问题测试**: 30-50秒
- **总测试**: 35-60秒

## 支持

如遇问题，请提供：
1. 完整的错误输出
2. Python版本和操作系统
3. 是否配置了环境变量
4. 具体的复现步骤

---

**测试版本**: 1.0.0
**最后更新**: 2026-01-25
