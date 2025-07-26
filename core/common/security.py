"""
安全模块
包含输入验证、URL安全检查、敏感信息处理等安全功能
"""

import re
import hashlib
import secrets
import urllib.parse
from typing import List, Optional, Dict, Any, Union
from pathlib import Path

from .exceptions import SecurityError, ValidationError
from .config import get_config


class SecurityValidator:
    """安全验证器"""
    
    # 危险的文件扩展名
    DANGEROUS_EXTENSIONS = {
        '.exe', '.bat', '.cmd', '.com', '.scr', '.pif', '.vbs', '.js',
        '.jar', '.app', '.deb', '.rpm', '.dmg', '.pkg', '.msi'
    }
    
    # 敏感信息正则模式
    SENSITIVE_PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'1[3-9]\d{9}',
        'id_card': r'\d{17}[\dXx]|\d{15}',
        'credit_card': r'\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}',
        'api_key': r'[Aa][Pp][Ii][\s_-]?[Kk][Ee][Yy][\s_-]?[:=]?\s*["\']?([A-Za-z0-9_-]{20,})["\']?',
        'password': r'[Pp][Aa][Ss][Ss][Ww][Oo][Rr][Dd][\s_-]?[:=]\s*["\']?([^"\'\s]{6,})["\']?',
        'token': r'[Tt][Oo][Kk][Ee][Nn][\s_-]?[:=]\s*["\']?([A-Za-z0-9_-]{20,})["\']?',
    }
    
    def __init__(self):
        self.config = get_config()
        self.security_config = self.config.get_security_config()
    
    def validate_url(self, url: str) -> bool:
        """验证URL是否安全"""
        try:
            parsed = urllib.parse.urlparse(url)
            
            # 检查协议
            if parsed.scheme not in ['http', 'https']:
                raise SecurityError(f"不支持的协议: {parsed.scheme}")
            
            # 检查域名白名单
            if self.security_config.allowed_domains:
                if not any(domain in parsed.netloc for domain in self.security_config.allowed_domains):
                    raise SecurityError(f"域名不在白名单中: {parsed.netloc}")
            
            # 检查域名黑名单
            if self.security_config.blocked_domains:
                if any(domain in parsed.netloc for domain in self.security_config.blocked_domains):
                    raise SecurityError(f"域名在黑名单中: {parsed.netloc}")
            
            # 检查本地网络地址
            if self._is_local_address(parsed.netloc):
                raise SecurityError(f"禁止访问本地网络地址: {parsed.netloc}")
            
            return True
            
        except Exception as e:
            if isinstance(e, SecurityError):
                raise
            raise SecurityError(f"URL验证失败: {e}")
    
    def _is_local_address(self, netloc: str) -> bool:
        """检查是否为本地网络地址"""
        local_patterns = [
            r'^localhost',
            r'^127\.',
            r'^10\.',
            r'^172\.(1[6-9]|2\d|3[01])\.',
            r'^192\.168\.',
            r'^169\.254\.',
            r'^\[::1\]',
            r'^\[::ffff:127\.',
        ]
        
        for pattern in local_patterns:
            if re.match(pattern, netloc, re.IGNORECASE):
                return True
        return False
    
    def validate_file_path(self, filepath: Union[str, Path]) -> bool:
        """验证文件路径是否安全"""
        filepath = Path(filepath)
        
        # 检查路径遍历攻击
        if '..' in str(filepath) or str(filepath).startswith('/'):
            raise SecurityError(f"检测到路径遍历攻击: {filepath}")
        
        # 检查文件扩展名
        if filepath.suffix.lower() in self.DANGEROUS_EXTENSIONS:
            raise SecurityError(f"危险的文件类型: {filepath.suffix}")
        
        # 检查文件名长度
        if len(filepath.name) > 255:
            raise SecurityError("文件名过长")
        
        return True
    
    def validate_file_size(self, size: int) -> bool:
        """验证文件大小"""
        if size > self.security_config.max_file_size:
            raise SecurityError(f"文件大小超限: {size} > {self.security_config.max_file_size}")
        return True
    
    def sanitize_input(self, text: str, max_length: int = 1000) -> str:
        """清理用户输入"""
        if not isinstance(text, str):
            raise ValidationError("输入必须是字符串")
        
        # 长度检查
        if len(text) > max_length:
            raise ValidationError(f"输入长度超限: {len(text)} > {max_length}")
        
        # 移除控制字符
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        
        # 移除JavaScript
        text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def mask_sensitive_data(self, text: str) -> str:
        """遮蔽敏感信息"""
        masked_text = text
        
        for pattern_name, pattern in self.SENSITIVE_PATTERNS.items():
            def mask_match(match):
                if pattern_name in ['email']:
                    # 邮箱只显示前缀和域名
                    email = match.group(0)
                    username, domain = email.split('@')
                    return f"{username[:2]}***@{domain}"
                elif pattern_name in ['phone']:
                    # 手机号只显示前3位和后4位
                    phone = match.group(0)
                    return f"{phone[:3]}****{phone[-4:]}"
                elif pattern_name in ['id_card']:
                    # 身份证号只显示前6位和后4位
                    id_card = match.group(0)
                    return f"{id_card[:6]}********{id_card[-4:]}"
                else:
                    # 其他敏感信息用星号替换
                    return '*' * min(len(match.group(0)), 8)
            
            masked_text = re.sub(pattern, mask_match, masked_text)
        
        return masked_text
    
    def detect_sensitive_data(self, text: str) -> Dict[str, List[str]]:
        """检测敏感数据"""
        detected = {}
        
        for pattern_name, pattern in self.SENSITIVE_PATTERNS.items():
            matches = re.findall(pattern, text)
            if matches:
                detected[pattern_name] = matches
        
        return detected
    
    def generate_secure_token(self, length: int = 32) -> str:
        """生成安全令牌"""
        return secrets.token_urlsafe(length)
    
    def hash_data(self, data: str, algorithm: str = 'sha256') -> str:
        """哈希数据"""
        if algorithm == 'md5':
            return hashlib.md5(data.encode()).hexdigest()
        elif algorithm == 'sha1':
            return hashlib.sha1(data.encode()).hexdigest()
        elif algorithm == 'sha256':
            return hashlib.sha256(data.encode()).hexdigest()
        else:
            raise ValueError(f"不支持的哈希算法: {algorithm}")


class RateLimiter:
    """请求频率限制器"""
    
    def __init__(self, max_requests: int = 100, time_window: int = 60):
        """
        初始化频率限制器
        
        Args:
            max_requests: 时间窗口内最大请求数
            time_window: 时间窗口大小(秒)
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: Dict[str, List[float]] = {}
    
    def is_allowed(self, identifier: str) -> bool:
        """检查是否允许请求"""
        import time
        
        current_time = time.time()
        
        # 初始化或清理过期记录
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        # 移除过期的请求记录
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if current_time - req_time < self.time_window
        ]
        
        # 检查是否超过限制
        if len(self.requests[identifier]) >= self.max_requests:
            return False
        
        # 记录当前请求
        self.requests[identifier].append(current_time)
        return True
    
    def get_reset_time(self, identifier: str) -> Optional[float]:
        """获取限制重置时间"""
        if identifier not in self.requests or not self.requests[identifier]:
            return None
        
        oldest_request = min(self.requests[identifier])
        return oldest_request + self.time_window


# 全局安全验证器实例
security_validator = SecurityValidator()