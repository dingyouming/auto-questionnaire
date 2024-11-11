# 贡献指南

## 分支策略

- `main`: 主分支，用于发布
- `develop`: 开发分支，所有功能开发都基于此分支
- `feature/*`: 功能分支，用于开发新功能
- `bugfix/*`: 修复分支，用于修复bug
- `release/*`: 发布分支，用于版本发布准备

## 开发流程

1. 从 `develop` 分支创建新的功能分支
```bash
git checkout develop
git pull
git checkout -b feature/your-feature-name
```

2. 开发完成后，提交代码
```bash
git add .
git commit -m "feat: your feature description"
```

3. 推送到远程仓库
```bash
git push origin feature/your-feature-name
```

4. 创建 Pull Request 到 `develop` 分支

## 提交规范

使用规范的提交信息格式：

- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

示例：
```bash
git commit -m "feat: add answer validation"
git commit -m "fix: handle API rate limit"
git commit -m "docs: update installation guide"
```

## 代码规范

1. 使用 black 格式化代码
```bash
poetry run black .
```

2. 使用 flake8 检查代码质量
```bash
poetry run flake8
```

3. 确保所有测试通过
```bash
poetry run pytest
```

## Pull Request 流程

1. 确保你的分支与最新的 develop 分支同步
```bash
git checkout develop
git pull
git checkout your-branch
git rebase develop
```

2. 解决可能的冲突

3. 运行测试确保一切正常
```bash
poetry run pytest
```

4. 推送到远程仓库
```bash
git push origin your-branch -f
```

5. 创建 Pull Request，包含：
   - 清晰的标题和描述
   - 相关的 issue 链接
   - 测试结果截图（如果适用）
   - 新功能的使用说明（如果适用）
