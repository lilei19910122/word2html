# Word转HTML转换器

此工具可将Word文档转换为HTML或纯文本，同时保留原始格式。转换后的内容会被拆分为数组，每个元素不超过配置的最大字符数，确保内容的完整性。

## 功能特点

- 将Word文档转换为HTML，同时保留原始格式（字体、字号、颜色、样式等）
- 支持转换为纯文本格式（删除所有HTML标签）
- 将内容拆分为数组元素，每个元素最大长度可配置
- 在拆分过程中保持内容完整性，不会破坏文本顺序
- 智能分割：避免在标题处分割，确保每个片段的完整性
- 精确分割：确保分割点不在HTML标签中间，只在标签开始前或结束后切割
- 标题保护：当标题标签（如`<p class="heading-1">`）出现在分段尾部时，自动将分割点提前，将整个标题标签移到下个片段中
- 正确处理段落和表格，表格在正确位置输出
- 支持从URL直接下载Word文件进行处理
- 提供详细的控制台调试输出
- 纯文档内容：不包含HTML头部、body等无关标签，只输出文档内容
- 配置文件统一管理：所有配置项集中在config.py中管理

## 项目结构

```
word2html/
├── app.py                    # Flask应用主文件
├── config.py                 # 配置文件
├── word_to_html_converter.py # Word转HTML核心转换器
├── requirements.txt          # 依赖包列表
├── README.md                 # 项目文档
├── test_converter.py         # 转换器测试脚本
├── test_web_api.py           # Web API测试脚本
├── simple_web_test.py        # 简单Web测试脚本
└── uploads/                  # 文件上传目录
```

## 安装

1. 安装所需依赖：

```bash
pip install -r requirements.txt
pip install beautifulsoup4
```

## 配置

所有配置项都集中在 `config.py` 文件中管理：

```python
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

# MinIO存储配置
MINIO_CONFIG = {
    'enabled': False,              # 是否启用MinIO存储
    'endpoint': 'http://localhost:9000',  # MinIO服务地址
    'access_key': 'your-access-key',      # 访问密钥
    'secret_key': 'your-secret-key',      # 秘密密钥
    'bucket_name': 'word-documents',     # 存储桶名称
    'secure': False,             # 是否使用HTTPS
    'region': 'us-east-1'       # 区域
}

# 转换配置
CONVERT_CONFIG = {
    'default_maxlength': 10000,
    'min_maxlength': 1000,
    'max_maxlength': 50000
}

# 文件清理配置
CLEANUP_CONFIG = {
    'enabled': True,           # 是否启用自动清理
    'retention_days': 3,       # 文件保留天数
    'cleanup_interval': 24,    # 清理间隔（小时）
    'cleanup_time': '02:00',   # 清理执行时间（24小时制）
    'log_cleanup': True        # 是否记录清理日志
}
```

**说明**：
- `enabled`: 设置为`True`启用MinIO存储，`False`使用本地文件存储
- `endpoint`: MinIO服务的完整地址
- `access_key`和`secret_key`: MinIO的认证凭据
- `bucket_name`: 用于存储Word文档的存储桶名称
- `secure`: 是否使用HTTPS协议连接MinIO
- `region`: MinIO服务所在的区域

**使用MinIO的步骤**：
1. 确保MinIO服务正在运行
2. 在MinIO中创建存储桶
3. 设置`MINIO_CONFIG['enabled'] = True`
4. 填写正确的MinIO连接信息
5. 重启应用服务

## Web API使用

### 启动服务

```bash
python app.py
```

服务将在 http://localhost:5000 启动

### API接口

#### 1. HTML转换接口
- **URL**: `POST /convert`
- **Content-Type**: `application/json`
- **请求参数**:
  ```json
  {
    "fileurl": "Word文件URL地址",
    "maxlength": 10000  // 可选，默认10000
  }
  ```
- **响应示例**:
  ```json
  {
    "success": true,
    "data": ["<p>HTML片段1</p>", "<p>HTML片段2</p>"],
    "total_fragments": 2,
    "maxlength": 10000
  }
  ```

#### 2. 纯文本转换接口
- **URL**: `POST /convert-plain`
- **Content-Type**: `application/json`
- **请求参数**:
  ```json
  {
    "fileurl": "Word文件URL地址",
    "maxlength": 10000  // 可选，默认10000
  }
  ```
- **响应示例**:
  ```json
  {
    "success": true,
    "data": ["纯文本片段1", "纯文本片段2"],
    "total_fragments": 2,
    "maxlength": 10000
  }
  ```

#### 3. 文件上传接口
- **URL**: `POST /upload`
- **Content-Type**: `multipart/form-data`
- **请求参数**:
  - `file`: Word文件
- **响应示例**:
  ```json
  {
    "success": true,
    "fileUrl": "http://localhost:5000/uploads/filename.docx",
    "filename": "filename.docx"
  }
  ```

#### 4. 健康检查
- **URL**: `GET /health`
- **响应示例**:
  ```json
  {
    "status": "healthy",
    "service": "Word转HTML转换器"
  }
  ```

#### 5. 文件清理接口
- **URL**: `POST /cleanup`
- **响应示例**:
  ```json
  {
    "success": true,
    "message": "文件清理任务执行完成",
    "execution_time": 0.25
  }
  ```
  
  **错误响应示例**:
  ```json
  {
    "success": false,
    "error": "清理过程中发生错误: 具体错误信息"
  }
  ```

### Web界面使用

1. 打开浏览器访问 http://localhost:5000
2. 选择Word文档文件
3. 设置片段最大长度（默认10000字符）
4. 点击以下按钮之一：
   - **上传并分割文档**：转换为HTML格式并保留标签
   - **上传并分割文档（纯文本）**：转换为纯文本格式并删除所有HTML标签
5. 查看分割结果，每个片段都会显示在独立的文本框中

### 使用示例

```python
import requests
import json

# HTML转换示例
response = requests.post(
    "http://localhost:5000/convert",
    headers={"Content-Type": "application/json"},
    data=json.dumps({
        "fileurl": "https://example.com/document.docx",
        "maxlength": 5000
    })
)

# 纯文本转换示例
response = requests.post(
    "http://localhost:5000/convert-plain",
    headers={"Content-Type": "application/json"},
    data=json.dumps({
        "fileurl": "https://example.com/document.docx",
        "maxlength": 5000
    })
)

if response.status_code == 200:
    result = response.json()
    if result["success"]:
        fragments = result["data"]
        print(f"转换成功，共{len(fragments)}个片段")
        for i, fragment in enumerate(fragments):
            print(f"片段{i+1}: {fragment[:50]}...")
    else:
        print(f"转换失败: {result['error']}")
else:
    print(f"请求失败: {response.status_code}")
```

## 测试

项目提供了多个测试脚本：

### 1. 转换器测试
```bash
python test_converter.py
```
测试核心转换功能，验证Word文档到HTML的转换。

### 2. Web API测试
```bash
python test_web_api.py
```
测试所有Web API接口，包括HTML转换、纯文本转换、文件上传等。

### 3. 简单Web测试
```bash
python simple_web_test.py
```
基础的Web接口功能测试，检查服务状态和接口可用性。

## 实现细节

该工具的工作原理：

1. **HTML转换流程**：
   - 从提供的URL下载Word文档
   - 使用临时文件处理字节数据，避免内存问题
   - 使用python-docx解析文档结构
   - 将段落和表格转换为HTML，同时保留所有样式信息
   - 智能分割HTML内容，确保不在标题处分割
   - 将分割后的片段作为数组返回
   - 提供详细的控制台输出用于调试

2. **纯文本转换流程**：
   - 先按照HTML转换流程处理文档
   - 使用正则表达式删除所有HTML标签
   - 清理多余的空白字符
   - 返回纯文本片段数组

3. **Web界面功能**：
   - 提供文件上传功能
   - 支持两种转换模式（HTML和纯文本）
   - 实时显示转换进度和结果
   - 使用textarea安全显示HTML内容，避免浏览器解析

4. **配置管理**：
   - 所有配置项集中在config.py中管理
   - 支持环境变量覆盖配置
   - 分类管理不同类型的配置（服务、上传、转换、API等）

## 依赖项

- python-docx==0.8.11：用于读取Word文档
- requests==2.28.1：用于从URL下载文件
- flask==2.3.3：Web框架
- minio==7.2.0：MinIO对象存储客户端（可选）
- beautifulsoup4==4.12.2：用于HTML处理
- lxml==4.9.3：python-docx的依赖项

**安装依赖**：
```bash
pip install -r requirements.txt
```

**可选依赖**：
如果需要使用MinIO存储功能，请确保安装minio库：
```bash
pip install minio==7.2.0
```

## 调试信息

工具运行时会输出详细的调试信息：
- 下载进度
- 解析状态
- HTML总长度
- 分割过程（每个片段的长度和剩余长度）
- 最终片段数量和验证结果

## 注意事项

- 确保提供的URL可以访问到有效的Word文档
- 分割时会自动避免在标题标签处分割
- 所有原始文本内容和顺序都会被保留
- 表格会在正确的位置输出，保持原有结构
- 配置文件修改后需要重启服务生效
- 上传文件大小限制为16MB
- 仅支持.doc和.docx格式的Word文档

### MinIO存储注意事项

- 使用MinIO存储前，请确保MinIO服务正在运行
- 需要在MinIO中创建对应的存储桶
- 确保MinIO的访问密钥和秘密密钥配置正确
- MinIO库为可选依赖，仅在启用MinIO存储时需要安装
- 启用MinIO存储后，文件将存储在MinIO服务器而非本地
- MinIO存储支持HTTP和HTTPS协议，可通过secure配置项控制

### 文件清理注意事项

- 文件清理功能默认启用，会自动删除uploads目录中超过3天的文件
- 清理任务每天凌晨2点自动执行，也可通过/cleanup接口手动触发
- 清理日志会记录在应用日志中，包含删除的文件数量和释放的空间大小
- 文件清理仅针对本地存储的文件，MinIO存储的文件不会被清理
- 修改CLEANUP_CONFIG配置后需要重启服务生效
- 确保uploads目录有正确的读写权限，否则清理可能失败