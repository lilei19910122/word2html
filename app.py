from flask import Flask, request, jsonify, render_template_string, send_from_directory
from word_to_html_converter import word_to_html_array
import os
import time
import datetime
import threading
import logging
from config import SERVER_CONFIG, UPLOAD_CONFIG, CONVERT_CONFIG, API_CONFIG, CLEANUP_CONFIG

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert_word_to_html():
    """Word转HTML转换API接口
    
    接收参数:
    - fileurl: Word文件的URL地址
    - maxlength: 每个片段的最大长度（可选，默认10000）
    
    返回:
    - success: 是否成功
    - data: 转换后的HTML片段数组
    - error: 错误信息（如果有）
    """
    try:
        # 获取请求参数
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请求体必须为JSON格式'
            }), 400
        
        fileurl = data.get('fileurl')
        maxlength = data.get('maxlength', CONVERT_CONFIG['default_maxlength'])
        
        # 验证参数
        if not fileurl:
            return jsonify({
                'success': False,
                'error': '缺少fileurl参数'
            }), 400
        
        if not isinstance(maxlength, int) or maxlength <= 0:
            return jsonify({
                'success': False,
                'error': 'maxlength必须为正整数'
            }), 400
        
        # 调用转换函数
        result = word_to_html_array(fileurl, maxlength)
        
        # 返回结果
        return jsonify({
            'success': True,
            'data': result,
            'total_fragments': len(result),
            'maxlength': maxlength
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'转换过程中发生错误: {str(e)}'
        }), 500

@app.route('/convert-plain', methods=['POST'])
def convert_word_to_plain_text():
    """Word转纯文本分割API接口（删除所有HTML标签）
    
    接收参数:
    - fileurl: Word文件的URL地址
    - maxlength: 每个片段的最大长度（可选，默认10000）
    
    返回:
    - success: 是否成功
    - data: 转换后的纯文本片段数组（已删除HTML标签）
    - error: 错误信息（如果有）
    """
    try:
        # 获取请求参数
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请求体必须为JSON格式'
            }), 400
        
        fileurl = data.get('fileurl')
        maxlength = data.get('maxlength', CONVERT_CONFIG['default_maxlength'])
        
        # 验证参数
        if not fileurl:
            return jsonify({
                'success': False,
                'error': '缺少fileurl参数'
            }), 400
        
        if not isinstance(maxlength, int) or maxlength <= 0:
            return jsonify({
                'success': False,
                'error': 'maxlength必须为正整数'
            }), 400
        
        # 调用转换函数获取HTML片段
        html_fragments = word_to_html_array(fileurl, maxlength)
        
        # 删除所有HTML标签，转换为纯文本
        import re
        plain_fragments = []
        for fragment in html_fragments:
            # 使用正则表达式删除所有HTML标签
            plain_text = re.sub(r'<[^>]*>', '', fragment)
            # 清理多余的空白字符
            plain_text = re.sub(r'\s+', ' ', plain_text).strip()
            plain_fragments.append(plain_text)
        
        # 返回结果
        return jsonify({
            'success': True,
            'data': plain_fragments,
            'total_fragments': len(plain_fragments),
            'maxlength': maxlength
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'转换过程中发生错误: {str(e)}'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'service': 'Word转HTML转换器'
    })

@app.route('/cleanup', methods=['POST'])
def manual_cleanup():
    """手动触发文件清理接口"""
    try:
        if not CLEANUP_CONFIG['enabled']:
            return jsonify({
                'success': False,
                'message': '文件清理功能未启用'
            }), 400
        
        # 记录清理开始时间
        start_time = time.time()
        
        # 执行清理任务
        cleanup_old_files()
        
        # 计算执行时间
        execution_time = time.time() - start_time
        
        return jsonify({
            'success': True,
            'message': '文件清理任务执行完成',
            'execution_time': round(execution_time, 2)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'清理过程中发生错误: {str(e)}'
        }), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    """文件上传接口"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': '没有找到文件'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': '没有选择文件'
            }), 400
        
        # 检查文件扩展名
        allowed_extensions = UPLOAD_CONFIG['allowed_extensions']
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            return jsonify({
                'success': False,
                'error': f'不支持的文件格式，仅支持: {", ".join(allowed_extensions)}'
            }), 400
        
        upload_dir = UPLOAD_CONFIG['upload_dir']
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        # 生成安全的文件名
        filename = file.filename
        file_path = os.path.join(upload_dir, filename)

        # 保存文件
        file.save(file_path)

        # 返回文件URL
        file_url = f'http://localhost:5000/{upload_dir}/{filename}'

        return jsonify({
            'success': True,
            'fileUrl': file_url,
            'filename': filename,
            'storage_type': 'local'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'文件上传失败: {str(e)}'
        }), 500

@app.route('/uploads/<filename>')
def serve_uploaded_file(filename):
    """提供上传的文件"""
    try:
        return send_from_directory('uploads', filename)
    except FileNotFoundError:
        return jsonify({
            'success': False,
            'error': '文件不存在'
        }), 404

@app.route('/', methods=['GET'])
def index():
    """首页 - Word文档分割工具"""
    return render_template_string('''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Word文档分割工具</title>
    <!-- 使用原生文件上传 -->
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #555;
        }
        input[type="file"], input[type="number"] {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        button {
            background-color: #007bff;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            width: 100%;
        }
        button:hover {
            background-color: #0056b3;
        }
        button:disabled {
            background-color: #ccc;
            cursor: not-allowed;
        }
        .status {
            margin-top: 20px;
            padding: 10px;
            border-radius: 4px;
            display: none;
        }
        .status.success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .status.error {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .status.info {
            background-color: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        .result {
            margin-top: 30px;
        }
        .fragment {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 15px;
            margin-bottom: 15px;
        }
        .fragment h3 {
            margin-top: 0;
            color: #495057;
        }
        .fragment-content {
            max-height: 200px;
            overflow-y: auto;
            border: 1px solid #ced4da;
            padding: 10px;
            background: white;
        }
        .loading {
            text-align: center;
            margin: 20px 0;
        }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #007bff;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Word文档分割工具</h1>
        
        <div class="form-group">
            <label for="fileInput">选择Word文档：</label>
            <input type="file" id="fileInput" accept=".doc,.docx" required>
        </div>
        
        <div class="form-group">
            <label for="maxlength">片段最大长度（字符数）：</label>
            <input type="number" id="maxlength" value="10000" min="1000" max="50000" required>
        </div>
        
        <button id="uploadBtn" onclick="uploadAndProcess()">上传并分割文档</button>
        
        <button id="uploadBtnPlain" onclick="uploadAndProcessPlain()" style="margin-top: 10px; background-color: #28a745;">上传并分割文档（纯文本）</button>
        
        <div id="status" class="status"></div>
        
        <div id="loading" class="loading" style="display: none;">
            <div class="spinner"></div>
            <p>正在处理文档，请稍候...</p>
        </div>
        
        <div id="result" class="result"></div>
    </div>

    <script>
        // 文件上传配置
        const uploadConfig = {
            apiEndpoint: '/upload'
        };

        // API服务地址
        const API_BASE_URL = '';

        function showStatus(message, type = 'info') {
            const statusDiv = document.getElementById('status');
            statusDiv.textContent = message;
            statusDiv.className = `status ${type}`;
            statusDiv.style.display = 'block';
        }

        function hideStatus() {
            const statusDiv = document.getElementById('status');
            statusDiv.style.display = 'none';
        }

        function showLoading(show = true) {
            const loadingDiv = document.getElementById('loading');
            const uploadBtn = document.getElementById('uploadBtn');
            
            if (show) {
                loadingDiv.style.display = 'block';
                uploadBtn.disabled = true;
                uploadBtn.textContent = '处理中...';
            } else {
                loadingDiv.style.display = 'none';
                uploadBtn.disabled = false;
                uploadBtn.textContent = '上传并分割文档';
            }
        }

        function generateFileName() {
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            const random = Math.random().toString(36).substr(2, 9);
            return `word_${timestamp}_${random}.docx`;
        }

        async function uploadFile(file) {
            try {
                showStatus('正在上传文件...', 'info');
                
                // 创建FormData对象
                const formData = new FormData();
                formData.append('file', file);
                
                // 发送上传请求
                const response = await fetch(uploadConfig.apiEndpoint, {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) {
                    throw new Error('上传失败');
                }
                
                const result = await response.json();
                
                if (result.success) {
                    showStatus('文件上传成功', 'success');
                    return result.fileUrl;
                } else {
                    throw new Error(result.error || '上传失败');
                }
            } catch (error) {
                showStatus('文件上传失败: ' + error.message, 'error');
                throw error;
            }
        }

        async function convertWordToHtml(fileUrl, maxlength) {
            try {
                showStatus('正在转换文档...', 'info');
                
                const response = await fetch(`${API_BASE_URL}/convert`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        fileurl: fileUrl,
                        maxlength: parseInt(maxlength)
                    })
                });

                const result = await response.json();
                
                if (!response.ok) {
                    throw new Error(result.error || '转换失败');
                }
                
                showStatus('文档转换成功！', 'success');
                return result;
                
            } catch (error) {
                console.error('转换错误:', error);
                showStatus(`文档转换失败: ${error.message}`, 'error');
                throw error;
            }
        }

        function displayResults(result) {
            const resultDiv = document.getElementById('result');
            
            if (!result.success || !result.data || result.data.length === 0) {
                resultDiv.innerHTML = '<p style="color: red;">没有生成有效的分割结果</p>';
                return;
            }

            let html = `
                <h2>分割结果</h2>
                <p><strong>总片段数:</strong> ${result.total_fragments}</p>
                <p><strong>片段最大长度:</strong> ${result.maxlength} 字符</p>
                <hr>
            `;

            result.data.forEach((fragment, index) => {
                // 计算片段长度（去除HTML标签后的纯文本长度）
                const plainTextLength = fragment.replace(/<[^>]*>/g, '').length;
                const htmlLength = fragment.length;
                
                html += `
                    <div class="fragment">
                        <h3>片段 ${index + 1}</h3>
                        <div style="margin-bottom: 10px; color: #666; font-size: 14px;">
                            <strong>纯文本长度:</strong> ${plainTextLength} 字符 | 
                            <strong>HTML长度:</strong> ${htmlLength} 字符
                        </div>
                        <div class="fragment-content" id="editor-${index}" style="height: 200px; border: 1px solid #dee2e6; border-radius: 4px;"></div>
                    </div>
                `;
            });

            resultDiv.innerHTML = html;
            
            // 使用textarea显示HTML内容，防止浏览器解析HTML标签
            setTimeout(() => {
                result.data.forEach((fragment, index) => {
                    const editorElement = document.getElementById(`editor-${index}`);
                    if (!editorElement) {
                        console.error(`找不到编辑器容器: editor-${index}`);
                        return;
                    }
                    
                    // 创建textarea元素
                    const textarea = document.createElement('textarea');
                    textarea.value = fragment;
                    textarea.readOnly = true;
                    textarea.style.cssText = 'width: 100%; height: 200px; font-family: monospace; font-size: 12px; background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px; padding: 10px; resize: vertical; white-space: pre; overflow-wrap: normal; overflow-x: auto;';
                    
                    // 清空容器并添加textarea
                    editorElement.innerHTML = '';
                    editorElement.appendChild(textarea);
                    
                    console.log(`片段 ${index} 显示成功`);
                });
            }, 100);
        }

        async function convertWordToPlainText(fileUrl, maxlength) {
            try {
                showStatus('正在转换文档为纯文本...', 'info');
                
                const response = await fetch(`${API_BASE_URL}/convert-plain`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        fileurl: fileUrl,
                        maxlength: parseInt(maxlength)
                    })
                });

                const result = await response.json();
                
                if (!response.ok) {
                    throw new Error(result.error || '转换失败');
                }
                
                showStatus('文档转换为纯文本成功！', 'success');
                return result;
                
            } catch (error) {
                console.error('转换错误:', error);
                showStatus(`文档转换失败: ${error.message}`, 'error');
                throw error;
            }
        }

        function displayPlainResults(result) {
            const resultDiv = document.getElementById('result');
            
            if (!result.success || !result.data || result.data.length === 0) {
                resultDiv.innerHTML = '<p style="color: red;">没有生成有效的分割结果</p>';
                return;
            }

            let html = `
                <h2>分割结果（纯文本）</h2>
                <p><strong>总片段数:</strong> ${result.total_fragments}</p>
                <p><strong>片段最大长度:</strong> ${result.maxlength} 字符</p>
                <hr>
            `;

            result.data.forEach((fragment, index) => {
                const textLength = fragment.length;
                
                html += `
                    <div class="fragment">
                        <h3>片段 ${index + 1}</h3>
                        <div style="margin-bottom: 10px; color: #666; font-size: 14px;">
                            <strong>纯文本长度:</strong> ${textLength} 字符
                        </div>
                        <div class="fragment-content" id="plain-editor-${index}" style="height: 200px; border: 1px solid #dee2e6; border-radius: 4px;"></div>
                    </div>
                `;
            });

            resultDiv.innerHTML = html;
            
            // 使用textarea显示纯文本内容
            setTimeout(() => {
                result.data.forEach((fragment, index) => {
                    const editorElement = document.getElementById(`plain-editor-${index}`);
                    if (!editorElement) {
                        console.error(`找不到编辑器容器: plain-editor-${index}`);
                        return;
                    }
                    
                    // 创建textarea元素
                    const textarea = document.createElement('textarea');
                    textarea.value = fragment;
                    textarea.readOnly = true;
                    textarea.style.cssText = 'width: 100%; height: 200px; font-family: monospace; font-size: 12px; background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px; padding: 10px; resize: vertical; white-space: pre; overflow-wrap: normal; overflow-x: auto;';
                    
                    // 清空容器并添加textarea
                    editorElement.innerHTML = '';
                    editorElement.appendChild(textarea);
                    
                    console.log(`纯文本片段 ${index} 显示成功`);
                });
            }, 100);
        }

        async function uploadAndProcessPlain() {
            const fileInput = document.getElementById('fileInput');
            const maxlengthInput = document.getElementById('maxlength');
            
            // 验证输入
            if (!fileInput.files || fileInput.files.length === 0) {
                showStatus('请选择一个Word文档', 'error');
                return;
            }
            
            const file = fileInput.files[0];
            const maxlength = maxlengthInput.value;
            
            if (!maxlength || maxlength < 1000) {
                showStatus('片段长度必须大于1000字符', 'error');
                return;
            }
            
            // 重置结果区域
            document.getElementById('result').innerHTML = '';
            
            try {
                showLoading(true);
                hideStatus();
                
                // 1. 上传文件
                const fileUrl = await uploadFile(file);
                
                // 2. 调用纯文本转换接口
                const result = await convertWordToPlainText(fileUrl, maxlength);
                
                // 3. 显示结果
                displayPlainResults(result);
                
            } catch (error) {
                console.error('处理过程出错:', error);
                // 错误信息已经在各个步骤中显示
            } finally {
                showLoading(false);
            }
        }

        async function uploadAndProcess() {
            const fileInput = document.getElementById('fileInput');
            const maxlengthInput = document.getElementById('maxlength');
            
            // 验证输入
            if (!fileInput.files || fileInput.files.length === 0) {
                showStatus('请选择一个Word文档', 'error');
                return;
            }
            
            const file = fileInput.files[0];
            const maxlength = maxlengthInput.value;
            
            if (!maxlength || maxlength < 1000) {
                showStatus('片段长度必须大于1000字符', 'error');
                return;
            }
            
            // 重置结果区域
            document.getElementById('result').innerHTML = '';
            
            try {
                showLoading(true);
                hideStatus();
                
                // 1. 上传文件
                const fileUrl = await uploadFile(file);
                
                // 2. 调用转换接口
                const result = await convertWordToHtml(fileUrl, maxlength);
                
                // 3. 显示结果
                displayResults(result);
                
            } catch (error) {
                console.error('处理过程出错:', error);
                // 错误信息已经在各个步骤中显示
            } finally {
                showLoading(false);
            }
        }

        // 页面加载完成后检查API服务状态
        document.addEventListener('DOMContentLoaded', async function() {
            try {
                const response = await fetch(API_BASE_URL + '/health');
                if (response.ok) {
                    showStatus('API服务连接正常', 'success');
                    setTimeout(hideStatus, 3000);
                } else {
                    showStatus('API服务连接异常', 'error');
                }
            } catch (error) {
                showStatus('无法连接到API服务，请确保服务正在运行', 'error');
            }
        });
    </script>
</body>
</html>
    ''')

# 文件清理功能
def cleanup_old_files():
    """清理超过保留天数的文件"""
    if not CLEANUP_CONFIG['enabled']:
        return
    
    try:
        uploads_dir = UPLOAD_CONFIG['upload_dir']
        retention_days = CLEANUP_CONFIG['retention_days']
        
        if not os.path.exists(uploads_dir):
            logging.warning(f"上传目录不存在: {uploads_dir}")
            return
        
        # 计算截止时间
        cutoff_time = time.time() - (retention_days * 24 * 60 * 60)
        
        # 统计清理的文件数量
        deleted_count = 0
        total_size = 0
        
        # 遍历uploads目录
        for filename in os.listdir(uploads_dir):
            filepath = os.path.join(uploads_dir, filename)
            
            # 只处理文件，不处理目录
            if os.path.isfile(filepath):
                # 获取文件修改时间
                file_mtime = os.path.getmtime(filepath)
                
                # 如果文件超过保留天数，则删除
                if file_mtime < cutoff_time:
                    try:
                        file_size = os.path.getsize(filepath)
                        os.remove(filepath)
                        deleted_count += 1
                        total_size += file_size
                        
                        if CLEANUP_CONFIG['log_cleanup']:
                            logging.info(f"已删除过期文件: {filename} (大小: {file_size} bytes)")
                    except Exception as e:
                        logging.error(f"删除文件失败 {filename}: {str(e)}")
        
        # 记录清理结果
        if deleted_count > 0:
            logging.info(f"文件清理完成: 删除了 {deleted_count} 个文件，释放空间 {total_size} bytes")
        else:
            logging.info("没有找到需要清理的过期文件")
            
    except Exception as e:
        logging.error(f"文件清理过程中发生错误: {str(e)}")

def schedule_cleanup():
    """定时执行文件清理任务"""
    if not CLEANUP_CONFIG['enabled']:
        return
    
    def cleanup_task():
        while True:
            try:
                # 获取当前时间
                now = datetime.datetime.now()
                cleanup_time_str = CLEANUP_CONFIG['cleanup_time']
                cleanup_hour, cleanup_minute = map(int, cleanup_time_str.split(':'))
                
                # 计算下次执行时间
                next_run = now.replace(hour=cleanup_hour, minute=cleanup_minute, second=0, microsecond=0)
                
                # 如果今天的执行时间已经过了，则安排到明天
                if now >= next_run:
                    next_run += datetime.timedelta(days=1)
                
                # 计算等待时间（秒）
                wait_seconds = (next_run - now).total_seconds()
                
                logging.info(f"下次文件清理任务将在 {next_run} 执行")
                
                # 等待到执行时间
                time.sleep(wait_seconds)
                
                # 执行清理任务
                logging.info("开始执行定时文件清理任务...")
                cleanup_old_files()
                
                # 等待配置的间隔时间
                interval_hours = CLEANUP_CONFIG['cleanup_interval']
                logging.info(f"文件清理任务完成，等待 {interval_hours} 小时后再次执行")
                time.sleep(interval_hours * 60 * 60)
                
            except Exception as e:
                logging.error(f"定时清理任务发生错误: {str(e)}")
                # 发生错误时等待1小时后重试
                time.sleep(60 * 60)
    
    # 启动清理线程
    cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
    cleanup_thread.start()
    logging.info("文件清理定时任务已启动")

if __name__ == '__main__':
    # 获取环境变量中的端口，默认使用配置文件中的端口
    port = int(os.environ.get('PORT', SERVER_CONFIG['port']))
    debug = os.environ.get('FLASK_DEBUG', str(SERVER_CONFIG['debug'])).lower() == 'true'
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 启动文件清理定时任务
    schedule_cleanup()
    
    print(f"启动Word转HTML转换器API服务...")
    print(f"服务地址: http://localhost:{port}")
    print(f"API文档: http://localhost:{port}/")
    print(f"健康检查: http://localhost:{port}/health")
    
    app.run(host=SERVER_CONFIG['host'], port=port, debug=debug)