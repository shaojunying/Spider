# 贡献指南

感谢您对 Spider Toolkit 项目的关注！本文档将指导您如何为项目做出贡献。

## 🤝 贡献方式

### 报告问题
- 使用 [Issues](https://github.com/shaojunying/Spider/issues) 报告 bug
- 提交功能请求
- 提出改进建议

### 代码贡献
- 修复 bug
- 添加新功能
- 改进现有代码
- 完善文档

## 🛠️ 开发环境设置

### 1. 克隆项目
```bash
git clone https://github.com/shaojunying/Spider.git
cd Spider
```

### 2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖
```bash
make install-dev
# 或
pip install -r requirements.txt -r requirements-dev.txt
pre-commit install
```

### 4. 验证安装
```bash
make test
make lint
```

## 📝 代码规范

### 代码风格
- 使用 [Black](https://black.readthedocs.io/) 进行代码格式化
- 使用 [isort](https://pycqa.github.io/isort/) 进行导入排序
- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 风格指南
- 最大行长度：88 字符

### 类型提示
- 所有新代码必须包含类型提示
- 使用 [mypy](http://mypy-lang.org/) 进行类型检查

### 文档字符串
- 使用 Google 风格的文档字符串
- 为所有公共函数、类和模块添加文档

示例：
```python
def scrape_data(url: str, timeout: int = 30) -> List[Dict[str, Any]]:
    """
    从指定URL爬取数据
    
    Args:
        url: 目标URL
        timeout: 请求超时时间(秒)
        
    Returns:
        爬取到的数据列表
        
    Raises:
        HttpError: HTTP请求失败
        ParseError: 数据解析失败
    """
    pass
```

## 🧪 测试规范

### 测试要求
- 所有新功能必须包含测试
- 测试覆盖率应保持在 80% 以上
- 使用有意义的测试名称

### 测试类型
- **单元测试**: 测试单个函数或方法
- **集成测试**: 测试模块间的交互
- **端到端测试**: 测试完整的工作流程

### 运行测试
```bash
# 运行所有测试
make test

# 运行快速测试
make test-fast

# 运行集成测试
make test-integration

# 运行特定测试文件
pytest tests/test_core_common.py -v
```

## 📦 提交规范

### 提交信息格式
使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### 提交类型
- `feat`: 新功能
- `fix`: bug 修复
- `docs`: 文档更新
- `style`: 代码格式化
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建工具、依赖更新等

### 示例
```
feat(scrapers): 添加新浪财经数据爬虫

- 实现股票价格数据采集
- 支持多种数据格式输出
- 添加相应的单元测试

Closes #123
```

## 🔄 Pull Request 流程

### 1. 创建分支
```bash
git checkout -b feature/your-feature-name
# 或
git checkout -b fix/your-bug-fix
```

### 2. 开发和测试
```bash
# 开发代码
# ...

# 运行测试和检查
make check-all
```

### 3. 提交代码
```bash
git add .
git commit -m "feat: your feature description"
git push origin feature/your-feature-name
```

### 4. 创建 Pull Request
- 在 GitHub 上创建 Pull Request
- 填写详细的描述
- 确保所有检查通过

### 5. 代码审查
- 响应审查意见
- 根据反馈修改代码
- 保持 PR 更新

## 🗂️ 项目结构

### 添加新的爬虫模块
1. 在相应目录下创建模块
2. 继承 `BaseScraper` 或 `SportScraper`
3. 实现必要的方法
4. 添加配置文件示例
5. 编写测试
6. 更新文档

### 目录约定
```
scrapers/
├── your_module/
│   ├── __init__.py
│   ├── main.py          # 主要爬虫逻辑
│   ├── config.py        # 配置文件
│   ├── config.py.example # 配置示例
│   └── README.md        # 模块文档
```

## 🔒 安全注意事项

### 敏感信息
- 不要提交任何密码、API 密钥或敏感数据
- 使用 `.env.example` 文件提供配置示例
- 在代码中使用占位符或环境变量

### 安全最佳实践
- 验证所有外部输入
- 使用 HTTPS 连接
- 实现适当的错误处理
- 遵循最小权限原则

## 📋 发布流程

### 版本号规范
使用 [语义化版本](https://semver.org/)：
- `MAJOR.MINOR.PATCH`
- 例如：`1.2.3`

### 发布检查清单
- [ ] 所有测试通过
- [ ] 文档已更新
- [ ] CHANGELOG.md 已更新
- [ ] 版本号已更新
- [ ] 创建 release tag

## 📞 获取帮助

### 联系方式
- GitHub Issues: [提交问题](https://github.com/shaojunying/Spider/issues)
- 讨论区: [GitHub Discussions](https://github.com/shaojunying/Spider/discussions)

### 常见问题
1. **如何添加新的爬虫？**
   - 参考现有爬虫模块
   - 继承相应的基类
   - 实现必要的方法

2. **如何配置开发环境？**
   - 按照本文档的开发环境设置步骤操作

3. **测试失败怎么办？**
   - 检查代码风格和类型提示
   - 确保所有依赖已安装
   - 查看测试输出的错误信息

## 🎉 致谢

感谢所有为项目做出贡献的开发者！您的贡献让这个项目变得更好。

---

**记住**: 好的代码不仅要能运行，还要容易理解和维护。让我们一起构建高质量的代码！