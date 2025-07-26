"""
pytest 配置文件
定义全局的 fixtures 和测试配置
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Generator
import pytest

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(scope="session")
def project_root() -> Path:
    """返回项目根目录路径"""
    return Path(__file__).parent.parent


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """提供临时目录"""
    temp_path = Path(tempfile.mkdtemp())
    try:
        yield temp_path
    finally:
        shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def mock_response():
    """模拟 HTTP 响应"""
    class MockResponse:
        def __init__(self, json_data=None, text_data="", status_code=200):
            self.json_data = json_data or {}
            self.text = text_data
            self.status_code = status_code
            self.headers = {"Content-Type": "text/html"}

        def json(self):
            return self.json_data

        def raise_for_status(self):
            if self.status_code >= 400:
                raise Exception(f"HTTP {self.status_code}")

    return MockResponse


@pytest.fixture
def sample_html():
    """提供测试用的 HTML 内容"""
    return """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <div class="content">
                <h1>Sample Content</h1>
                <p>This is a test paragraph.</p>
                <ul>
                    <li>Item 1</li>
                    <li>Item 2</li>
                </ul>
            </div>
        </body>
    </html>
    """


@pytest.fixture
def sample_data():
    """提供测试用的数据"""
    return [
        {"name": "Test 1", "value": 100, "date": "2023-01-01"},
        {"name": "Test 2", "value": 200, "date": "2023-01-02"},
        {"name": "Test 3", "value": 300, "date": "2023-01-03"},
    ]


@pytest.fixture(autouse=True)
def cleanup_test_files():
    """自动清理测试文件"""
    yield
    # 清理测试过程中创建的文件
    test_patterns = ["test_*.csv", "test_*.xlsx", "test_*.json", "test_*.log"]
    for pattern in test_patterns:
        for file in Path(".").glob(pattern):
            file.unlink(missing_ok=True)