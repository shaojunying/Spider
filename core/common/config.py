"""
全局配置管理器
统一管理项目配置，支持环境变量、配置文件等多种配置源
"""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Union

try:
    from dotenv import load_dotenv
    _dotenv_available = True
except ImportError:
    _dotenv_available = False
    def load_dotenv(*args, **kwargs):
        pass

from .logger import get_logger


@dataclass
class DatabaseConfig:
    """数据库配置"""

    host: str = "localhost"
    port: int = 3306
    username: str = ""
    password: str = ""
    database: str = ""


@dataclass
class HttpConfig:
    """HTTP请求配置"""

    timeout: int = 30
    retries: int = 3
    delay_min: float = 1.0
    delay_max: float = 3.0
    user_agent: str = "Spider-Toolkit/1.0"
    headers: Dict[str, str] = None

    def __post_init__(self):
        if self.headers is None:
            self.headers = {
                "User-Agent": self.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }


@dataclass
class SecurityConfig:
    """安全配置"""

    enable_ssl_verify: bool = True
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_domains: list = None
    blocked_domains: list = None

    def __post_init__(self):
        if self.allowed_domains is None:
            self.allowed_domains = []
        if self.blocked_domains is None:
            self.blocked_domains = []


@dataclass
class LoggingConfig:
    """日志配置"""

    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_enabled: bool = True
    console_enabled: bool = True
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5


class ConfigManager:
    """配置管理器"""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.logger = get_logger(self.__class__.__name__)
            self._config: Dict[str, Any] = {}
            self._load_config()
            ConfigManager._initialized = True

    def _load_config(self):
        """加载配置"""
        # 1. 加载环境变量
        self._load_env_config()

        # 2. 加载配置文件
        self._load_file_config()

        # 3. 初始化默认配置
        self._init_default_config()

    def _load_env_config(self):
        """加载环境变量配置"""
        # 尝试加载 .env 文件
        env_file = Path(".env")
        if env_file.exists():
            load_dotenv(env_file)
            self.logger.info(f"已加载环境配置文件: {env_file}")

    def _load_file_config(self):
        """加载配置文件"""
        config_files = [
            Path("config.json"),
            Path("config/config.json"),
            Path("settings.json"),
        ]

        for config_file in config_files:
            if config_file.exists():
                try:
                    with open(config_file, "r", encoding="utf-8") as f:
                        file_config = json.load(f)
                        self._config.update(file_config)
                        self.logger.info(f"已加载配置文件: {config_file}")
                        break
                except Exception as e:
                    self.logger.error(f"加载配置文件失败 {config_file}: {e}")

    def _init_default_config(self):
        """初始化默认配置"""
        # HTTP配置
        self._config.setdefault("http", {})
        http_config = self._config["http"]
        http_config.setdefault("timeout", int(os.getenv("HTTP_TIMEOUT", "30")))
        http_config.setdefault("retries", int(os.getenv("HTTP_RETRIES", "3")))
        http_config.setdefault("delay_min", float(os.getenv("HTTP_DELAY_MIN", "1.0")))
        http_config.setdefault("delay_max", float(os.getenv("HTTP_DELAY_MAX", "3.0")))
        http_config.setdefault(
            "user_agent", os.getenv("USER_AGENT", "Spider-Toolkit/1.0")
        )

        # 数据库配置
        self._config.setdefault("database", {})
        db_config = self._config["database"]
        db_config.setdefault("host", os.getenv("DB_HOST", "localhost"))
        db_config.setdefault("port", int(os.getenv("DB_PORT", "3306")))
        db_config.setdefault("username", os.getenv("DB_USERNAME", ""))
        db_config.setdefault("password", os.getenv("DB_PASSWORD", ""))
        db_config.setdefault("database", os.getenv("DB_DATABASE", ""))

        # 安全配置
        self._config.setdefault("security", {})
        security_config = self._config["security"]
        security_config.setdefault(
            "enable_ssl_verify", os.getenv("SSL_VERIFY", "true").lower() == "true"
        )
        security_config.setdefault(
            "max_file_size", int(os.getenv("MAX_FILE_SIZE", str(10 * 1024 * 1024)))
        )

        # 日志配置
        self._config.setdefault("logging", {})
        logging_config = self._config["logging"]
        logging_config.setdefault("level", os.getenv("LOG_LEVEL", "INFO"))
        logging_config.setdefault(
            "file_enabled", os.getenv("LOG_FILE_ENABLED", "true").lower() == "true"
        )
        logging_config.setdefault(
            "console_enabled",
            os.getenv("LOG_CONSOLE_ENABLED", "true").lower() == "true",
        )

        # 输出目录配置
        self._config.setdefault("output", {})
        output_config = self._config["output"]
        output_config.setdefault("base_dir", os.getenv("OUTPUT_DIR", "output"))
        output_config.setdefault("logs_dir", os.getenv("LOGS_DIR", "logs"))

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值，支持点分隔符路径"""
        keys = key.split(".")
        value = self._config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any) -> None:
        """设置配置值，支持点分隔符路径"""
        keys = key.split(".")
        config = self._config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def get_http_config(self) -> HttpConfig:
        """获取HTTP配置对象"""
        http_config = self._config.get("http", {})
        return HttpConfig(
            timeout=http_config.get("timeout", 30),
            retries=http_config.get("retries", 3),
            delay_min=http_config.get("delay_min", 1.0),
            delay_max=http_config.get("delay_max", 3.0),
            user_agent=http_config.get("user_agent", "Spider-Toolkit/1.0"),
            headers=http_config.get("headers"),
        )

    def get_database_config(self) -> DatabaseConfig:
        """获取数据库配置对象"""
        db_config = self._config.get("database", {})
        return DatabaseConfig(
            host=db_config.get("host", "localhost"),
            port=db_config.get("port", 3306),
            username=db_config.get("username", ""),
            password=db_config.get("password", ""),
            database=db_config.get("database", ""),
        )

    def get_security_config(self) -> SecurityConfig:
        """获取安全配置对象"""
        security_config = self._config.get("security", {})
        return SecurityConfig(
            enable_ssl_verify=security_config.get("enable_ssl_verify", True),
            max_file_size=security_config.get("max_file_size", 10 * 1024 * 1024),
            allowed_domains=security_config.get("allowed_domains", []),
            blocked_domains=security_config.get("blocked_domains", []),
        )

    def get_logging_config(self) -> LoggingConfig:
        """获取日志配置对象"""
        logging_config = self._config.get("logging", {})
        return LoggingConfig(
            level=logging_config.get("level", "INFO"),
            format=logging_config.get(
                "format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            ),
            file_enabled=logging_config.get("file_enabled", True),
            console_enabled=logging_config.get("console_enabled", True),
            max_file_size=logging_config.get("max_file_size", 10 * 1024 * 1024),
            backup_count=logging_config.get("backup_count", 5),
        )

    def save_config(self, filepath: Union[str, Path] = None) -> bool:
        """保存配置到文件"""
        if filepath is None:
            filepath = Path("config.json")

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            self.logger.info(f"配置已保存到: {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"保存配置失败: {e}")
            return False

    def reload_config(self):
        """重新加载配置"""
        self._config.clear()
        self._load_config()
        self.logger.info("配置已重新加载")

    def to_dict(self) -> Dict[str, Any]:
        """返回配置字典"""
        return self._config.copy()


# 全局配置实例
config = ConfigManager()


def get_config() -> ConfigManager:
    """获取全局配置实例"""
    return config
