# 目录重构说明

## 🎯 重构目标

解决当前项目目录结构的以下问题：
1. 命名不清晰和不一致
2. 功能分类混乱
3. 顶层目录过多，缺少合理分层

## 📊 重构对比

### 重构前 (19个顶层目录)
```
Spider/
├── common/
├── house_buy/
├── sport/  
├── hospital/
├── laundry-machine/
├── course_selection/
├── check_course_result/
├── check_empty_classroom/
├── bupt_second_class_ticket/
├── house_door/
├── github-oauth2/
├── gym.py
├── pdf/
├── shell/
├── io-multiplexing/
├── test/
├── byr-bbs/
├── spider_for_finance.py
└── img/
```

### 重构后 (7个主要类别)
```
Spider/
├── 🎯 core/                    # 核心框架
│   ├── common/                 # 公共模块
│   └── base/                   # 基础类
├── 🕷️ scrapers/                # 爬虫模块
│   ├── real_estate/           # 房地产
│   ├── sports/                # 体育
│   ├── finance/               # 金融
│   └── web_data/              # 网页数据
├── 🏫 campus/                  # 校园服务
│   ├── course/                # 课程
│   ├── activities/            # 活动
│   └── services/              # 服务
├── 🤖 automation/              # 自动化工具
│   ├── booking/               # 预约
│   ├── access_control/        # 门禁
│   └── auth/                  # 认证
├── 🛠️ tools/                   # 工具集
├── 👥 community/               # 社区
└── 📚 docs/                    # 文档
```

## 🔄 目录映射表

| 原目录 | 新目录 | 变化说明 |
|--------|--------|----------|
| `common/` | `core/common/` | 移入核心模块 |
| `house_buy/` | `scrapers/real_estate/house_price/` | 按功能分类+重命名 |
| `sport/` | `scrapers/sports/` | 简化命名 |
| `spider_for_finance.py` | `scrapers/finance/news/main.py` | 单文件改为模块 |
| `pdf/` | `scrapers/web_data/pdf_extract/` | 按数据类型分类 |
| `course_selection/` | `campus/course/selection/` | 校园服务分类 |
| `check_course_result/` | `campus/course/grade_check/` | 统一命名风格 |
| `check_empty_classroom/` | `campus/course/classroom/` | 简化命名 |
| `bupt_second_class_ticket/` | `campus/activities/second_class/` | 去除具体学校名 |
| `gym.py` | `campus/services/gym/main.py` | 单文件改为模块 |
| `hospital/` | `automation/booking/hospital/` | 按功能分类 |
| `laundry-machine/` | `automation/booking/laundry/` | 统一命名+分类 |
| `house_door/` | `automation/access_control/` | 功能导向命名 |
| `github-oauth2/` | `automation/auth/oauth2/` | 去除具体平台名 |
| `shell/` | `tools/text_processing/` | 功能明确命名 |
| `io-multiplexing/` | `tools/network/io_examples/` | 分类+示例定位 |
| `byr-bbs/` | `community/byr_bbs/` | 社区功能分类 |
| `test/` | `tests/` | 标准命名 |
| `img/` | `docs/images/` | 文档资源分类 |

## 📝 重构原则

### 1. 分层清晰
- **第一层**: 功能大类 (core, scrapers, campus, automation, tools, community, docs)
- **第二层**: 具体分类 (course, booking, real_estate 等)
- **第三层**: 具体功能模块

### 2. 命名规范
- **统一使用小写+下划线**: `house_price` 而非 `houseBuy`
- **功能导向**: `grade_check` 而非 `check_course_result`
- **避免冗余**: `selection` 而非 `course_selection` (已在course目录下)
- **去除具体实现**: `oauth2` 而非 `github-oauth2`

### 3. 模块化
- **单文件改模块**: `gym.py` → `gym/main.py`
- **添加__init__.py**: 所有目录都有包初始化文件
- **独立输出**: 统一的 `output/` 和 `logs/` 目录

## 🚀 使用指南

### 导入示例
```python
# 重构前
from common import get_logger
from house_buy.anjuke import AnjukeScraper

# 重构后  
from core.common import get_logger
from scrapers.real_estate.house_price.anjuke import AnjukeScraper
```

### 运行示例
```bash
# 重构前
python house_buy/anjuke.py
python gym.py

# 重构后
python scrapers/real_estate/house_price/anjuke.py  
python campus/services/gym/main.py
```

## ✅ 重构优势

1. **清晰的功能分类**: 从19个平级目录减少到7个主要类别
2. **一致的命名规范**: 统一使用小写+下划线
3. **合理的层级结构**: 2-3层目录，便于理解和维护
4. **可扩展性**: 新功能容易找到合适位置
5. **专业性**: 符合大型项目的目录组织最佳实践

## 📋 TODO

- [ ] 更新所有Python文件中的import路径
- [ ] 更新README.md中的目录结构
- [ ] 更新.gitignore中的路径
- [ ] 测试所有模块的导入和运行
- [ ] 清理旧目录结构