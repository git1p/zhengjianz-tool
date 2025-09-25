from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

# 火山引擎API配置
API_CONFIG = {
    'endpoint': 'https://ark.cn-beijing.volces.com/api/v3/images/generations',
    'api_key': os.getenv('API_KEY', '70342b5a-147b-4bd0-9677-1739306b1f33'),  # 使用纯密钥，不包含账号前缀
    'model': 'doubao-seedream-4-0-250828'
}

@app.route('/')
def index():
    """主页 - 重定向到工具页面"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>证件照换装工具</title>
        <meta http-equiv="refresh" content="0; url=/zhengjianz-tool.html">
    </head>
    <body>
        <p>正在跳转到工具页面...</p>
        <p><a href="/zhengjianz-tool.html">点击这里进入工具</a></p>
    </body>
    </html>
    '''

@app.route('/zhengjianz-tool.html')
def tool_page():
    """证件照工具页面 - 完全自包含版本"""
    return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>证件照换装工具 - 在线证件照服装更换</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Microsoft YaHei', sans-serif; }
        body { background-color: #f5f5f5; color: #333; line-height: 1.6; }
        header { background: linear-gradient(135deg, #6e8efb, #a777e3); color: white; text-align: center; padding: 2rem 0; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); }
        h1 { font-size: 2.5rem; margin-bottom: 1rem; }
        .container { max-width: 1200px; margin: 2rem auto; padding: 0 1rem; }
        .upload-section { background: white; border-radius: 12px; padding: 2rem; margin: 2rem 0; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); text-align: center; }
        .upload-area { border: 2px dashed #ddd; border-radius: 8px; padding: 2rem; margin: 1rem 0; cursor: pointer; transition: all 0.3s ease; position: relative; }
        .upload-area:hover { border-color: #6e8efb; background-color: #f8f9ff; }
        .upload-area.dragover { border-color: #6e8efb; background-color: #f0f2ff; }
        #fileInput { display: none; }
        .upload-icon { font-size: 3rem; color: #ddd; margin-bottom: 1rem; }
        .preview-area { display: flex; justify-content: space-around; flex-wrap: wrap; gap: 2rem; margin: 2rem 0; }
        .photo-box { flex: 1; min-width: 280px; background: white; border-radius: 8px; padding: 1rem; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); text-align: center; }
        .photo-box h3 { margin-bottom: 1rem; color: #555; }
        .photo-placeholder { width: 100%; height: 350px; background-color: #f8f9fa; display: flex; align-items: center; justify-content: center; margin-bottom: 1rem; overflow: hidden; border-radius: 4px; border: 1px solid #eee; }
        .photo-placeholder img { max-width: 100%; max-height: 100%; object-fit: contain; }
        .clothing-upload-area { border: 2px dashed #ddd; border-radius: 8px; padding: 1rem; margin: 0.5rem 0; cursor: pointer; transition: all 0.3s ease; background: #f8f9ff; }
        .clothing-upload-area:hover { border-color: #6e8efb; background-color: #f0f2ff; }
        .background-selector { background: white; border-radius: 12px; padding: 2rem; margin: 2rem 0; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); text-align: center; }
        .bg-options { display: flex; justify-content: center; gap: 1rem; margin: 1rem 0; flex-wrap: wrap; }
        .bg-option { padding: 0.8rem 1.5rem; border: 2px solid #ddd; border-radius: 50px; cursor: pointer; transition: all 0.3s ease; background: white; color: #333; }
        .bg-option:hover { border-color: #6e8efb; }
        .bg-option.selected { background: #6e8efb; color: white; border-color: #6e8efb; }
        .generate-btn { background: linear-gradient(135deg, #6e8efb, #a777e3); color: white; border: none; padding: 1rem 2.5rem; font-size: 1.2rem; border-radius: 50px; cursor: pointer; transition: all 0.3s ease; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); margin: 1rem 0; min-width: 200px; }
        .generate-btn:hover:not(:disabled) { transform: translateY(-3px); box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2); }
        .generate-btn:disabled { background: #ccc; cursor: not-allowed; transform: none; }
        .loading { display: none; text-align: center; padding: 2rem; }
        .spinner { border: 4px solid #f3f3f3; border-top: 4px solid #6e8efb; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto 1rem; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .error-message { background: #ffe6e6; color: #d32f2f; padding: 1rem; border-radius: 8px; margin: 1rem 0; display: none; }
        .success-message { background: #e8f5e8; color: #2e7d32; padding: 1rem; border-radius: 8px; margin: 1rem 0; display: none; }
        .download-btn { background: #28a745; color: white; border: none; padding: 0.8rem 2rem; font-size: 1rem; border-radius: 50px; cursor: pointer; transition: all 0.3s ease; text-decoration: none; display: inline-block; margin-top: 1rem; }
        .download-btn:hover { background: #218838; transform: translateY(-2px); }
        footer { background: #333; color: white; text-align: center; padding: 2rem 0; margin-top: 3rem; }
        @media (max-width: 768px) { .preview-area { flex-direction: column; } .bg-options { flex-direction: column; align-items: center; } }
    </style>
</head>
<body>
    <header>
        <h1>证件照换装工具</h1>
        <p>智能换装，专业证件照服务 - 一键生成符合要求的证件照</p>
    </header>
    
    <div class="container">
        <div class="upload-section">
            <h2>上传您的证件照</h2>
            <p>支持JPG、PNG格式，文件大小不超过10MB</p>
            <div class="upload-area" onclick="document.getElementById('fileInput').click()">
                <div class="upload-icon">📁</div>
                <div id="uploadText">点击这里选择文件或拖拽文件到此处</div>
                <input type="file" id="fileInput" accept="image/*">
            </div>
        </div>

        <div class="background-selector">
            <h2>选择证件照背景色</h2>
            <div class="bg-options">
                <div class="bg-option selected" data-bg="白底">白底</div>
                <div class="bg-option" data-bg="蓝底">蓝底</div>
                <div class="bg-option" data-bg="红底">红底</div>
            </div>
        </div>

        <div class="preview-area">
            <div class="photo-box">
                <h3>原始照片</h3>
                <div class="photo-placeholder" id="originalPhoto">
                    <span style="color: #999;">请先上传照片</span>
                </div>
            </div>
            
            <div class="photo-box">
                <h3>参考服装</h3>
                <div class="photo-placeholder" id="clothingPhoto">
                    <img src="https://img.alicdn.com/imgextra/i1/668603298/O1CN01OeNCAX1aEXJeR4rhJ_!!668603298.png" alt="参考服装" id="clothingImage">
                </div>
                <div class="clothing-upload-area" onclick="document.getElementById('clothingInput').click()">
                    <div class="upload-icon">👔</div>
                    <div id="clothingText">点击上传自定义服装</div>
                    <input type="file" id="clothingInput" accept="image/*" style="display: none;">
                </div>
                <p>将为您的照片更换为此款正装</p>
            </div>
            
            <div class="photo-box">
                <h3>换装结果</h3>
                <div class="photo-placeholder" id="resultPhoto">
                    <span style="color: #999;" id="resultPlaceholder">等待生成结果</span>
                </div>
                <a id="downloadBtn" class="download-btn" style="display: none;" download="证件照换装结果.png">下载结果</a>
            </div>
        </div>

        <div style="text-align: center;">
            <button class="generate-btn" id="generateBtn" disabled>请先上传照片</button>
        </div>

        <div class="loading" id="loadingArea">
            <div class="spinner"></div>
            <p>正在为您生成换装证件照，请稍候...</p>
        </div>

        <div class="error-message" id="errorMessage"></div>
        <div class="success-message" id="successMessage"></div>
    </div>
    
    <footer>
        <p>证件照换装工具 - 专业在线证件照服务 | Powered by 火山引擎豆包</p>
    </footer>

    <script>
        const API_CONFIG = {
            endpoint: '/api/generate',
            apiKey: 'your-api-key-here',
            model: 'doubao-seedream-4-0-250828',
            clothingReference: 'https://img.alicdn.com/imgextra/i1/668603298/O1CN01OeNCAX1aEXJeR4rhJ_!!668603298.png'
        };

        let uploadedFile = null;
        let uploadedImageUrl = null;
        let uploadedClothingFile = null;
        let uploadedClothingUrl = API_CONFIG.clothingReference; // 默认使用参考服装
        let selectedBackground = '白底';

        const fileInput = document.getElementById('fileInput');
        const uploadArea = document.querySelector('.upload-area');
        const uploadText = document.getElementById('uploadText');
        const originalPhoto = document.getElementById('originalPhoto');
        const resultPhoto = document.getElementById('resultPhoto');
        const generateBtn = document.getElementById('generateBtn');
        const loadingArea = document.getElementById('loadingArea');
        const errorMessage = document.getElementById('errorMessage');
        const successMessage = document.getElementById('successMessage');
        const downloadBtn = document.getElementById('downloadBtn');
        const bgOptions = document.querySelectorAll('.bg-option');
        const clothingInput = document.getElementById('clothingInput');
        const clothingText = document.getElementById('clothingText');
        const clothingImage = document.getElementById('clothingImage');

        fileInput.addEventListener('change', handleFileSelect);
        uploadArea.addEventListener('dragover', handleDragOver);
        uploadArea.addEventListener('dragleave', handleDragLeave);
        uploadArea.addEventListener('drop', handleDrop);
        clothingInput.addEventListener('change', handleClothingSelect);
        generateBtn.addEventListener('click', generatePhoto);
        
        bgOptions.forEach(option => {
            option.addEventListener('click', function() {
                bgOptions.forEach(opt => opt.classList.remove('selected'));
                this.classList.add('selected');
                selectedBackground = this.dataset.bg;
            });
        });

        function handleFileSelect(event) {
            const file = event.target.files[0];
            if (file) processFile(file);
        }

        function handleClothingSelect(event) {
            const file = event.target.files[0];
            if (file) processClothingFile(file);
        }

        function handleDragOver(event) {
            event.preventDefault();
            uploadArea.classList.add('dragover');
        }

        function handleDragLeave(event) {
            event.preventDefault();
            uploadArea.classList.remove('dragover');
        }

        function handleDrop(event) {
            event.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = event.dataTransfer.files;
            if (files.length > 0) processFile(files[0]);
        }

        function processFile(file) {
            if (!file.type.startsWith('image/')) {
                showError('请选择图片文件！');
                return;
            }
            if (file.size > 10 * 1024 * 1024) {
                showError('文件大小不能超过10MB！');
                return;
            }
            uploadedFile = file;
            
            // 压缩图片
            compressImage(file, function(compressedDataUrl) {
                originalPhoto.innerHTML = `<img src="${compressedDataUrl}" alt="上传的照片">`;
                uploadText.textContent = `已选择: ${file.name} (已压缩)`;
                generateBtn.textContent = '开始换装';
                generateBtn.disabled = false;
                uploadedImageUrl = compressedDataUrl;
            });
        }
        
        function compressImage(file, callback) {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const img = new Image();
            
            img.onload = function() {
                // 计算压缩后的尺寸
                let { width, height } = img;
                const maxSize = 1024; // 最大尺寸
                
                if (width > height) {
                    if (width > maxSize) {
                        height = (height * maxSize) / width;
                        width = maxSize;
                    }
                } else {
                    if (height > maxSize) {
                        width = (width * maxSize) / height;
                        height = maxSize;
                    }
                }
                
                canvas.width = width;
                canvas.height = height;
                
                // 绘制压缩后的图片
                ctx.drawImage(img, 0, 0, width, height);
                
                // 转换为base64，质量设置为0.8
                const compressedDataUrl = canvas.toDataURL('image/jpeg', 0.8);
                callback(compressedDataUrl);
            };
            
            img.src = URL.createObjectURL(file);
        }

        function processClothingFile(file) {
            if (!file.type.startsWith('image/')) {
                showError('请选择图片文件！');
                return;
            }
            if (file.size > 10 * 1024 * 1024) {
                showError('文件大小不能超过10MB！');
                return;
            }
            uploadedClothingFile = file;
            
            // 压缩服装图片
            compressImage(file, function(compressedDataUrl) {
                clothingImage.src = compressedDataUrl;
                clothingText.textContent = `已选择: ${file.name} (已压缩)`;
                uploadedClothingUrl = compressedDataUrl;
            });
        }

        async function generatePhoto() {
            if (!uploadedFile) {
                showError('请先上传照片！');
                return;
            }
            showLoading(true);
            hideMessages();
            try {
                const prompt = `将图1的人物穿上图2的衣服生成一个${selectedBackground}证件照`;
                const requestBody = {
                    prompt: prompt,
                    image: [uploadedImageUrl, uploadedClothingUrl], // 使用用户上传的服装或默认服装
                    background: selectedBackground
                };
                const response = await fetch(API_CONFIG.endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(requestBody)
                });
                if (!response.ok) {
                    const errorData = await response.text();
                    throw new Error(`API请求失败: ${response.status} - ${errorData}`);
                }
                const result = await response.json();
                if (result.success && result.data && result.data.data && result.data.data.length > 0) {
                    const imageUrl = result.data.data[0].url;
                    displayResult(imageUrl);
                    showSuccess('证件照换装完成！');
                } else if (result.error) {
                    throw new Error(result.error);
                } else {
                    throw new Error('API返回数据格式错误');
                }
            } catch (error) {
                console.error('生成失败:', error);
                showError(`生成失败: ${error.message}`);
            } finally {
                showLoading(false);
            }
        }

        function displayResult(imageUrl) {
            resultPhoto.innerHTML = `<img src="${imageUrl}" alt="换装结果">`;
            downloadBtn.href = imageUrl;
            downloadBtn.style.display = 'inline-block';
            const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
            downloadBtn.download = `证件照换装结果_${selectedBackground}_${timestamp}.png`;
        }

        function showLoading(show) {
            loadingArea.style.display = show ? 'block' : 'none';
            generateBtn.disabled = show;
            if (show) {
                generateBtn.textContent = '生成中...';
            } else {
                generateBtn.textContent = '开始换装';
            }
        }

        function showError(message) {
            errorMessage.textContent = message;
            errorMessage.style.display = 'block';
            setTimeout(() => { errorMessage.style.display = 'none'; }, 5000);
        }

        function showSuccess(message) {
            successMessage.textContent = message;
            successMessage.style.display = 'block';
            setTimeout(() => { successMessage.style.display = 'none'; }, 3000);
        }

        function hideMessages() {
            errorMessage.style.display = 'none';
            successMessage.style.display = 'none';
        }
    </script>
</body>
</html>'''

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'ok',
        'message': '代理服务器运行正常',
        'api_configured': API_CONFIG['api_key'] != 'your-api-key-here'
    })

@app.route('/api/generate', methods=['POST'])
def generate_image():
    """代理API调用 - 生成换装证件照"""
    try:
        if API_CONFIG['api_key'] == 'your-api-key-here':
            return jsonify({
                'success': False,
                'error': 'API密钥未配置，请联系管理员'
            }), 500
        
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据为空'}), 400
        
        required_fields = ['prompt', 'image', 'background']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必需参数: {field}'}), 400
        
        api_request = {
            'model': API_CONFIG['model'],
            'prompt': data['prompt'],
            'image': data['image'],
            'response_format': 'url',
            'size': '2K',
            'watermark': False
        }
        
        # 根据火山引擎API文档，使用正确的认证方式
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {API_CONFIG["api_key"]}'
        }
        
        # 检查API密钥格式
        print(f"API Key: {API_CONFIG['api_key'][:20]}...")  # 只打印前20个字符
        print(f"API Key length: {len(API_CONFIG['api_key'])}")
        
        # 添加SSL验证和重试机制
        import ssl
        import urllib3
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        # 创建session并配置重试策略
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # 禁用SSL警告
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        response = session.post(
            API_CONFIG['endpoint'],
            headers=headers,
            json=api_request,
            timeout=60,
            verify=True  # 保持SSL验证
        )
        
        if response.status_code == 200:
            result = response.json()
            return jsonify({
                'success': True,
                'data': result
            })
        else:
            return jsonify({
                'success': False,
                'error': f'API调用失败: {response.status_code} - {response.text}'
            }), response.status_code
            
    except requests.exceptions.Timeout:
        return jsonify({
            'success': False,
            'error': '请求超时，请稍后重试'
        }), 408
    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'error': f'网络请求失败: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'服务器内部错误: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
