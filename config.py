# Word转HTML转换器配置文件

# 服务配置
SERVER_CONFIG = {
    'host': '0.0.0.0',
    'port': 5000,
    'debug': False
}

# 文件上传配置
UPLOAD_CONFIG = {
    'upload_dir': 'uploads',
    'max_content_length': 16 * 1024 * 1024,  # 16MB
    'allowed_extensions': ['.doc', '.docx']
}

# 文件清理配置
CLEANUP_CONFIG = {
    'enabled': True,  # 是否启用自动清理
    'retention_days': 3,  # 文件保留天数
    'cleanup_interval': 24 * 60 * 60,  # 清理检查间隔（秒），默认24小时
    'cleanup_time': '02:00',  # 每天清理时间（HH:MM格式）
    'log_cleanup': True  # 是否记录清理日志
}


# 转换配置
CONVERT_CONFIG = {
    'default_maxlength': 10000,
    'min_maxlength': 1000,
    'max_maxlength': 50000
}

# API配置
API_CONFIG = {
    'base_url': '',
    'timeout': 30
}

# 日志配置
LOG_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}

# 安全配置
SECURITY_CONFIG = {
    'max_file_size': 16 * 1024 * 1024,  # 16MB
    'allowed_origins': ['*']
}