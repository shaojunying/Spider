"""
统一的HTTP请求处理模块

提供项目中所有爬虫脚本的统一HTTP请求处理
"""

import requests
import time
import random
from typing import Dict, Optional, Any, Union
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging

from .exceptions import HttpError, SecurityError, NetworkError, TimeoutError
from .security import security_validator


class HttpClient:
    """统一的HTTP客户端"""
    
    def __init__(
        self,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        retry_times: int = 3,
        retry_backoff_factor: float = 0.3,
        delay_range: tuple = (1, 3),
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化HTTP客户端
        
        Args:
            headers: 默认请求头
            timeout: 请求超时时间
            retry_times: 重试次数
            retry_backoff_factor: 重试退避因子
            delay_range: 请求间隔范围(秒)
            logger: 日志记录器
        """
        self.session = requests.Session()
        self.timeout = timeout
        self.delay_range = delay_range
        self.logger = logger or logging.getLogger(__name__)
        
        # 设置默认请求头
        default_headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }
        
        if headers:
            default_headers.update(headers)
        
        self.session.headers.update(default_headers)
        
        # 设置重试策略
        retry_strategy = Retry(
            total=retry_times,
            backoff_factor=retry_backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def _delay(self):
        """随机延迟"""
        if self.delay_range:
            delay = random.uniform(*self.delay_range)
            time.sleep(delay)
    
    def get(
        self,
        url: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> requests.Response:
        """GET请求"""
        # 安全验证
        try:
            security_validator.validate_url(url)
        except SecurityError as e:
            self.logger.error(f"URL安全验证失败: {e}")
            raise
        
        self._delay()
        
        try:
            response = self.session.get(
                url,
                params=params,
                headers=headers,
                timeout=self.timeout,
                **kwargs
            )
            
            self.logger.debug(f"GET {url} -> {response.status_code}")
            response.raise_for_status()
            return response
            
        except requests.exceptions.Timeout as e:
            self.logger.error(f"GET请求超时 {url}: {e}")
            raise TimeoutError(f"请求超时: {url}", timeout_seconds=self.timeout)
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"GET连接错误 {url}: {e}")
            raise NetworkError(f"网络连接失败: {url}")
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"GET HTTP错误 {url}: {e}")
            raise HttpError(f"HTTP错误: {e}", status_code=e.response.status_code, url=url)
        except requests.exceptions.RequestException as e:
            self.logger.error(f"GET请求失败 {url}: {e}")
            raise HttpError(f"请求失败: {e}", url=url)
    
    def post(
        self,
        url: str,
        data: Optional[Union[Dict, str]] = None,
        json: Optional[Dict] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> requests.Response:
        """POST请求"""
        self._delay()
        
        try:
            response = self.session.post(
                url,
                data=data,
                json=json,
                headers=headers,
                timeout=self.timeout,
                **kwargs
            )
            
            self.logger.debug(f"POST {url} -> {response.status_code}")
            response.raise_for_status()
            return response
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"POST请求失败 {url}: {e}")
            raise
    
    def get_json(self, url: str, **kwargs) -> Dict[str, Any]:
        """GET请求并返回JSON数据"""
        response = self.get(url, **kwargs)
        try:
            return response.json()
        except ValueError as e:
            self.logger.error(f"JSON解析失败: {e}")
            raise
    
    def post_json(self, url: str, **kwargs) -> Dict[str, Any]:
        """POST请求并返回JSON数据"""
        response = self.post(url, **kwargs)
        try:
            return response.json()
        except ValueError as e:
            self.logger.error(f"JSON解析失败: {e}")
            raise
    
    def set_cookies(self, cookies: Union[Dict, requests.cookies.RequestsCookieJar]):
        """设置cookies"""
        if isinstance(cookies, dict):
            self.session.cookies.update(cookies)
        else:
            self.session.cookies = cookies
    
    def get_cookies(self) -> requests.cookies.RequestsCookieJar:
        """获取当前cookies"""
        return self.session.cookies
    
    def close(self):
        """关闭会话"""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# 便捷函数
def create_spider_client(
    headers: Optional[Dict[str, str]] = None,
    delay_range: tuple = (1, 3),
    logger: Optional[logging.Logger] = None
) -> HttpClient:
    """创建适用于爬虫的HTTP客户端"""
    return HttpClient(
        headers=headers,
        delay_range=delay_range,
        logger=logger
    )