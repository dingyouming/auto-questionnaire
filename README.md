# Auto Questionnaire

自动问卷填写工具，基于Python 3.12开发，使用AI技术辅助问卷填写和分析。

## 项目结构

```plaintext
auto-questionnaire/
├── data/                  # 数据文件
│   ├── context_db.json    # 上下文数据库
│   ├── screenshots/       # 截图存储
│   └── templates/         # 模板文件
├── docs/                  # 文档
│   ├── API.md            # API文档
│   ├── CHANGELOG.md      # 变更日志
│   ├── CONTRIBUTING.md   # 贡献指南
│   ├── DEPLOYMENT.md     # 部署文档
│   └── DEVELOPMENT.md    # 开发指南
├── src/                  # 源代码
│   └── auto_questionnaire/
│       ├── ai/           # AI相关功能
│       ├── config/       # 配置管理
│       ├── monitoring/   # 监控功能
│       ├── parser/       # 解析器
│       └── utils/        # 工具函数
└── tests/                # 测试代码
    ├── unit/            # 单元测试
    ├── integration/     # 集成测试
    └── performance/     # 性能测试
```

## 功能特性

- AI辅助问卷填写
- 自动化表单解析
- 性能监控和报告
- 截图和日志记录
- 可配置的问答模板

## 环境要求

- Python 3.12+
- Poetry 依赖管理
- Groq API 密钥（用于AI功能）

## 快速开始

1. 克隆项目
```bash
git clone https://github.com/dingyouming/auto-questionnaire.git
cd auto-questionnaire
```

2. 安装依赖
```bash
poetry install
```

3. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填入必要的配置信息
```

4. 运行程序
```bash
poetry run python src/auto_questionnaire/main.py
```

## 使用说明

### 基础使用

1. **准备问卷**
   - 打开目标问卷网页
   - 确保问卷在可见区域内

2. **启动程序**
```bash
poetry run python src/auto_questionnaire/main.py
```

3. **配置选项**
   - 在 `config/settings.yaml` 中设置：
```yaml
ai:
  model: "groq-large"
  temperature: 0.7
  max_tokens: 1000

performance:
  max_concurrent: 5
  rate_limit: 100
  timeout: 30
```

### 高级功能

1. **自定义模板**
   - 在 `data/templates/` 创建回答模板：
```json
{
    "education": {
        "pattern": "学历|教育",
        "answers": ["本科", "硕士", "博士"]
    },
    "experience": {
        "pattern": "工作经验|工作年限",
        "answers": ["1-3年", "3-5年", "5年以上"]
    }
}
```

2. **批量处理**
```bash
poetry run python src/auto_questionnaire/batch_processor.py --input urls.txt
```

3. **性能监控**
   - 访问 `http://localhost:8080` 查看实时性能指标
   - 性能报告位于 `tests/reports/`

### 常见问题

1. **API限流处理**
   - 默认限制：每分钟100次请求
   - 超出限制时自动等待
   - 可在配置文件调整限制

2. **答案质量控制**
   - 使用内置验证器检查答案质量
   - 质量分数低于0.6时自动重试
   - 支持自定义质量评估规则

3. **错误处理**
   - 自动重试失败的请求（最多3次）
   - 详细错误日志在 `logs/error.log`
   - 关键错误通过邮件通知

### 使用建议

1. **性能优化**
   - 启用缓存减少API调用
   - 合理设置并发数
   - 定期清理缓存文件

2. **答案定制**
   - 使用上下文数据库提供领域知识
   - 调整模型参数影响答案风格
   - 创建自定义答案模板

3. **监控告警**
   - 设置性能基准阈值
   - 配置告警通知方式
   - 定期检查性能报告

### 扩展功能

1. **自定义解析器**
```python
from auto_questionnaire.parser import CustomParser

parser = CustomParser(
    element_types=['radio', 'checkbox', 'text'],
    custom_rules={...}
)
```

2. **集成其他AI模型**
```python
from auto_questionnaire.ai import CustomModelHandler

handler = CustomModelHandler(
    model_name="custom-model",
    api_key="your-api-key"
)
```

3. **数据导出**
```bash
poetry run python src/auto_questionnaire/exporter.py --format csv
```

## 开发指南

### 安装开发依赖
```bash
poetry install --with dev
```

### 运行测试
```bash
# 运行所有测试
poetry run pytest

# 运行特定类型的测试
poetry run pytest tests/unit/
poetry run pytest tests/integration/
poetry run pytest tests/performance/
```

### 代码风格
项目使用 black 进行代码格式化，使用 flake8 进行代码检查：
```bash
poetry run black .
poetry run flake8
```

## 主要模块说明

- **ai/**: AI模型交互和提示词构建
- **config/**: 配置文件管理
- **monitoring/**: 性能监控和告警
- **parser/**: 问卷解析和元素定位
- **utils/**: 通用工具函数

## 测试报告

性能测试报告位于 `tests/reports/` 目录，包含：
- API延迟测试
- 压力测试结果
- 集成测试报告

## 文档

详细文档请参考 `docs/` 目录：
- [API文档](docs/API.md)
- [开发指南](docs/DEVELOPMENT.md)
- [部署文档](docs/DEPLOYMENT.md)
- [贡献指南](docs/CONTRIBUTING.md)
- [变更日志](docs/CHANGELOG.md)

## 贡献

欢迎贡献代码！请阅读 [贡献指南](docs/CONTRIBUTING.md) 了解详情。

## 许可证

[选择合适的许可证]

## 作者

[你的名字或组织名称]

## 致谢

- Groq API 提供AI支持
- [其他致谢对象]