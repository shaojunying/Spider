# Spider项目重构指南

## 优化概述

本次重构主要解决了以下问题：
1. **代码重复严重** - 13个文件重复日志配置，47个文件重复HTTP请求代码
2. **缺少统一架构** - sport目录下46个相似脚本没有统一基类
3. **项目管理混乱** - 缺少依赖管理、.gitignore等基础设施

## 新增公共模块结构

```
common/
├── __init__.py          # 模块初始化，导出常用组件
├── logger.py           # 统一日志配置
├── http_client.py      # 统一HTTP请求处理
├── utils.py            # 通用工具函数
└── base_scraper.py     # 基础爬虫类
```

## 使用方式

### 1. 基础使用

```python
# 导入公共组件
from common import get_logger, HttpClient, save_to_csv

# 使用统一日志
logger = get_logger('my_scraper', 'output')

# 使用HTTP客户端
with HttpClient(delay_range=(1, 3)) as client:
    response = client.get('https://example.com')
    data = response.json()

# 保存数据
save_to_csv(data, 'output/data.csv')
```

### 2. 继承基础爬虫类

对于sport模块等，可以继承`SportScraper`基类：

```python
from common.base_scraper import SportScraper

class MySportScraper(SportScraper):
    def __init__(self):
        super().__init__(
            sport_name="Mysport", 
            sport_id="my_sport"
        )
    
    def scrape(self):
        # 实现具体爬虫逻辑
        return []

# 使用
scraper = MySportScraper()
data = scraper.run(save_format='xlsx')
```

## 重构示例

### house_buy模块重构

原始代码问题：
- 重复的日志配置代码
- 手动处理HTTP请求和重试
- 文件操作代码重复

重构后：
- `house_buy/anjuke_refactored.py` - 使用公共组件的版本
- 统一日志配置
- 使用HttpClient处理请求
- 使用公共工具函数处理文件操作

### sport模块重构

原始代码问题：
- 46个脚本结构高度相似
- 每个脚本都重复相同的框架代码

重构后：
- `sport/py/1.gymnastics_refactored.py` - 重构示例
- 继承`SportScraper`基类
- 专注于业务逻辑实现
- 统一的数据保存和日志处理

## 新增项目基础设施

### 1. requirements.txt
管理项目依赖，运行：
```bash
pip install -r requirements.txt
```

### 2. .gitignore
完善的Git忽略规则，包括：
- Python临时文件
- 输出数据文件
- 配置文件
- 日志文件

## 迁移建议

### 现有脚本迁移步骤：

1. **导入公共模块**
   ```python
   from common import get_logger, HttpClient, save_to_csv
   ```

2. **替换日志配置**
   ```python
   # 替换原有的logging.basicConfig
   logger = get_logger('script_name', 'output')
   ```

3. **使用HttpClient**
   ```python
   # 替换requests.get/post
   client = HttpClient(delay_range=(1, 3))
   response = client.get(url)
   ```

4. **使用工具函数**
   ```python
   # 替换手动文件操作
   save_to_csv(data, filename)
   ```

### sport脚本迁移：

1. **继承基类**
   ```python
   from common.base_scraper import SportScraper
   
   class MyScraper(SportScraper):
       def scrape(self):
           # 实现具体逻辑
           return data
   ```

2. **简化主函数**
   ```python
   if __name__ == "__main__":
       scraper = MyScraper()
       scraper.run()
   ```

## 优势

### 1. 减少代码重复
- 日志配置：从13个文件减少到1个公共模块
- HTTP请求：统一处理重试、延迟、错误处理
- 文件操作：统一的保存格式和错误处理

### 2. 提高可维护性
- 统一的错误处理和日志格式
- 修改一个地方影响所有脚本
- 更容易添加新功能（如监控、统计等）

### 3. 标准化项目结构
- 统一的输出目录和文件命名
- 标准的依赖管理
- 完善的版本控制忽略规则

## 未来扩展

基于这个架构，可以很容易地添加：
1. **数据库支持** - 在base_scraper中添加数据库保存方法
2. **监控告警** - 在logger中集成告警功能
3. **分布式爬取** - 在HttpClient中添加代理池支持
4. **配置管理** - 添加统一的配置文件管理

## 注意事项

1. 现有脚本仍然可以正常运行，重构是渐进式的
2. 配置文件（config.py等）需要各模块自行维护
3. 建议优先重构使用频率高的脚本
4. 新开发的脚本建议直接使用新架构