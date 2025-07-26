"""
测试爬虫模块
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from core.common.base_scraper import SportScraper


class TestSportScraper:
    """测试体育爬虫基类"""

    def test_sport_scraper_init(self, temp_dir):
        """测试体育爬虫初始化"""
        class TestSportScraper(SportScraper):
            def scrape(self):
                return []
        
        scraper = TestSportScraper("Basketball", output_dir=str(temp_dir))
        assert scraper.sport_name == "Basketball"
        assert scraper.sport_id == "basketball"
        assert scraper.name == "basketball"

    def test_sport_scraper_custom_id(self, temp_dir):
        """测试自定义体育项目ID"""
        class TestSportScraper(SportScraper):
            def scrape(self):
                return []
        
        scraper = TestSportScraper("Basketball", sport_id="bball", output_dir=str(temp_dir))
        assert scraper.sport_id == "bball"
        assert scraper.name == "bball"

    @patch("core.common.base_scraper.HttpClient")
    def test_sport_scraper_default_scrape(self, mock_http_client, temp_dir):
        """测试默认爬取流程"""
        mock_client_instance = MagicMock()
        mock_response = Mock()
        mock_response.text = "<html><body>Test</body></html>"
        mock_client_instance.get.return_value = mock_response
        mock_http_client.return_value = mock_client_instance
        
        class TestSportScraper(SportScraper):
            def get_competition_urls(self):
                return ["http://example.com/test"]
            
            def parse_competition_data(self, html_content):
                return [{"url": "test", "content": html_content[:20]}]
        
        scraper = TestSportScraper("Test Sport", output_dir=str(temp_dir))
        data = scraper.scrape()
        
        assert len(data) == 1
        assert data[0]["url"] == "test"


class TestScrapersIntegration:
    """测试爬虫集成功能"""

    @pytest.mark.integration
    def test_house_price_scraper_structure(self):
        """测试房价爬虫结构"""
        from pathlib import Path
        house_price_dir = Path("scrapers/house_price")
        
        assert (house_price_dir / "__init__.py").exists()
        assert (house_price_dir / "config.py").exists()

    @pytest.mark.integration
    def test_sports_data_scraper_structure(self):
        """测试体育数据爬虫结构"""
        from pathlib import Path
        sports_dir = Path("scrapers/sports_data")
        
        assert (sports_dir / "__init__.py").exists()
        assert (sports_dir / "config.py").exists()
        assert (sports_dir / "py").exists()