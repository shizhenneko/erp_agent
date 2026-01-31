# ERP Agent Frontend

基于 Vue 3 + Element Plus + WebSocket 的 ERP Agent 前端界面。

## 技术栈

- **Vue 3** - 渐进式 JavaScript 框架
- **Element Plus** - 基于 Vue 3 的组件库
- **Vite** - 下一代前端构建工具
- **WebSocket** - 实时双向通信
- **Pinia** - Vue 状态管理

## 功能特性

- ✨ 自然语言查询输入
- 📊 实时流式输出展示
- 🗃️ SQL 语句查看器
- 📋 数据结果表格展示
- 💾 CSV 数据导出
- 🔄 自动重连机制
- 🎨 现代化 UI 设计

## 项目结构

```
frontend/
├── src/
│   ├── components/          # 组件
│   │   ├── QueryInput.vue          # 查询输入组件
│   │   │   ├── StreamOutput.vue        # 流式输出组件
│   │   │   ├── ResultTable.vue         # 结果表格组件
│   │   │   └── SQLViewer.vue           # SQL查看器组件
│   ├── composables/         # Composable
│   │   └── useWebSocket.js  # WebSocket封装
│   ├── views/               # 页面
│   │   └── Dashboard.vue    # 主页面
│   ├── styles/              # 样式
│   │   └── main.css         # 全局样式
│   ├── App.vue
│   └── main.js
├── package.json
├── vite.config.js
└── .env
```

## 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 配置环境变量

编辑 `.env` 文件：

```env
VITE_WS_URL=ws://localhost:8000/ws
VITE_API_BASE_URL=http://localhost:8000
```

### 3. 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:3000

### 4. 构建生产版本

```bash
npm run build
```

### 5. 预览生产构建

```bash
npm run preview
```

## 使用说明

### 查询示例

- 有多少在职员工？
- 每个部门有多少人？
- 工资最高的前10名员工是谁？
- 今年新入职了多少人？
- 从去年到今年涨薪幅度最大的10位员工是谁？

### 快捷键

- `Ctrl + Enter` - 提交查询

### 功能说明

1. **自然语言查询**
   - 在输入框中输入问题
   - 点击"提交查询"按钮或按 `Ctrl + Enter` 提交

2. **流式输出**
   - 实时显示 Agent 的思考过程
   - 包括：思考、SQL 执行、查询结果、最终答案

3. **SQL 查看器**
   - 查看生成的 SQL 语句
   - 支持一键复制
   - 支持折叠/展开

4. **结果表格**
   - 表格形式展示查询结果
   - 支持分页、排序
   - 支持导出 CSV

## WebSocket 协议

### 前端发送

```json
{
  "action": "query",
  "question": "有多少在职员工？"
}
```

### 后端推送

后端会推送多种类型的消息：

- `iteration_start` - 迭代开始
- `thought` - 思考过程
- `sql_executing` - SQL 执行
- `sql_result` - SQL 结果
- `answer` - 最终答案
- `final` - 查询完成
- `error` - 错误信息

详细协议说明请参考 [开发文档.md](./开发文档.md)

## 浏览器支持

- Chrome >= 90
- Firefox >= 88
- Safari >= 14
- Edge >= 90

## 开发

### 添加新组件

1. 在 `src/components/` 创建新组件
2. 在需要的地方导入使用

### 添加新页面

1. 在 `src/views/` 创建新页面
2. 在 `App.vue` 中配置路由

### 调试

- 打开浏览器开发者工具
- 查看 Console 日志
- 查看 Network 中的 WebSocket 连接

## 问题排查

### 连接失败

1. 检查后端服务是否启动
2. 检查 `.env` 中的 WebSocket 地址是否正确
3. 检查浏览器控制台的错误信息

### 样式问题

1. 清除浏览器缓存
2. 重新启动开发服务器

### 其他问题

1. 删除 `node_modules` 和 `package-lock.json`
2. 重新运行 `npm install`

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT

## 联系方式

如有问题，请联系项目维护者。

---

**版本**: 1.0.0  
**最后更新**: 2026-01-31
