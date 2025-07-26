"""
测试核心公共模块
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from core.common.logger import get_logger

# 可选导入 HttpClient
try:
    from core.common.http_client import HttpClient
    http_client_available = True
except ImportError:
    HttpClient = None
    http_client_available = False
from core.common.utils import (
    ensure_dir,
    save_to_csv,
    save_json,
    normalize_price_text,
    generate_timestamp_filename,
    extract_numbers,
)


class TestLogger:
    """测试日志模块"""

    def test_get_logger_default(self, temp_dir):
        """测试默认日志配置"""
        logger = get_logger("test_logger", str(temp_dir))
        assert logger.name == "test_logger"
        
        # 测试日志文件是否创建
        log_files = list(temp_dir.glob("*.log"))
        assert len(log_files) > 0

    def test_get_logger_custom_level(self, temp_dir):
        """测试自定义日志级别"""
        logger = get_logger("test_logger", str(temp_dir), level="DEBUG")
        assert logger.level == 10  # DEBUG level


@pytest.mark.skipif(not http_client_available, reason="HttpClient dependencies not available")
class TestHttpClient:
    """测试 HTTP 客户端"""

    @patch("requests.Session")
    def test_http_client_init(self, mock_session):
        """测试 HTTP 客户端初始化"""
        client = HttpClient()
        assert client.session is not None
        assert client.delay_range == (1, 3)

    @patch("requests.Session.get")
    def test_http_client_get(self, mock_get):
        """测试 GET 请求"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "test response"
        mock_get.return_value = mock_response

        client = HttpClient(delay_range=(0, 0))  # 无延迟测试
        response = client.get("https://example.com")
        
        assert response.status_code == 200
        assert response.text == "test response"
        mock_get.assert_called_once()

    @patch("requests.Session.post")
    def test_http_client_post(self, mock_post):
        """测试 POST 请求"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_post.return_value = mock_response

        client = HttpClient(delay_range=(0, 0))
        response = client.post("https://example.com", data={"key": "value"})
        
        assert response.status_code == 200
        assert response.json()["status"] == "success"

    def test_http_client_context_manager(self):
        """测试上下文管理器"""
        with HttpClient() as client:
            assert client.session is not None


class TestUtils:
    """测试工具函数"""

    def test_ensure_dir(self, temp_dir):
        """测试目录创建"""
        test_dir = temp_dir / "test_subdir"
        ensure_dir(str(test_dir))
        assert test_dir.exists()
        assert test_dir.is_dir()

    def test_ensure_dir_existing(self, temp_dir):
        """测试已存在目录"""
        ensure_dir(str(temp_dir))  # 应该不报错
        assert temp_dir.exists()

    def test_save_to_csv(self, temp_dir, sample_data):
        """测试保存 CSV 文件"""
        csv_file = temp_dir / "test.csv"
        save_to_csv(sample_data, str(csv_file))
        
        assert csv_file.exists()
        content = csv_file.read_text(encoding="utf-8")
        assert "name,value,date" in content
        assert "Test 1,100,2023-01-01" in content

    def test_save_to_json(self, temp_dir, sample_data):
        """测试保存 JSON 文件"""
        json_file = temp_dir / "test.json"
        save_json(sample_data, str(json_file))
        
        assert json_file.exists()
        with open(json_file, encoding="utf-8") as f:
            data = json.load(f)
        assert len(data) == 3
        assert data[0]["name"] == "Test 1"

    def test_normalize_price_text(self):
        """测试价格文本标准化"""
        assert normalize_price_text("￥1,234.56万") == 12345600.0
        assert normalize_price_text("1000元") == 1000.0
        assert normalize_price_text("123万") == 1230000.0
        assert normalize_price_text("no number") is None

    def test_generate_timestamp_filename(self):
        """测试时间戳文件名生成"""
        filename = generate_timestamp_filename("test", ".csv")
        assert filename.startswith("test_")
        assert filename.endswith(".csv")
        assert len(filename) > 10  # 包含时间戳

    def test_extract_numbers(self):
        """测试数字提取"""
        result = extract_numbers("价格：1,234.56元，面积：89.5平米")
        assert 1234.56 in result
        assert 89.5 in result


class TestBaseScraper:
    """测试基础爬虫类"""

    def test_base_scraper_init(self, temp_dir):
        """测试基础爬虫初始化"""
        from core.common.base_scraper import BaseScraper
        
        class TestScraper(BaseScraper):
            def scrape(self):
                return [{"test": "data"}]
        
        scraper = TestScraper("test_scraper", str(temp_dir))
        assert scraper.name == "test_scraper"
        assert scraper.output_dir == str(temp_dir)
        assert scraper.data == []

    def test_base_scraper_save_data(self, temp_dir):
        """测试数据保存"""
        from core.common.base_scraper import BaseScraper
        
        class TestScraper(BaseScraper):
            def scrape(self):
                return [{"test": "data"}]
        
        scraper = TestScraper("test_scraper", str(temp_dir))
        scraper.data = [{"name": "test", "value": 123}]
        
        # 测试保存 Excel
        file_path = scraper.save_data(format="xlsx")
        assert file_path.endswith(".xlsx")
        assert Path(file_path).exists()

    def test_base_scraper_run(self, temp_dir):
        """测试爬虫运行"""
        from core.common.base_scraper import BaseScraper
        
        class TestScraper(BaseScraper):
            def scrape(self):
                return [{"test": "data"}]
        
        scraper = TestScraper("test_scraper", str(temp_dir))
        data = scraper.run()
        
        assert len(data) == 1
        assert data[0]["test"] == "data"