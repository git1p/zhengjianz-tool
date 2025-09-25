import os
import json
import requests
from flask import Flask, request, jsonify
import urllib3
from urllib3.util.retry import Retry

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# API配置
API_CONFIG = {
    'endpoint': 'https://ark.cn-beijing.volces.com/api/v3/images/generations',
    'api_key': os.getenv('API_KEY', 'your-api-key-here'),
    'model': 'doubao-seedream-4-0-250828',
    'clothingReference': 'https://img.alicdn.com/imgextra/i1/668603298/O1CN01OeNCAX1aEXJeR4rhJ_!!668603298.png'
}

def create_session_with_retry():
    """创建带重试机制的requests session"""
    session = requests.Session()
    retry_strategy = Retry(
        total=5,  # 增加重试次数
        backoff_factor=2,  # 增加重试间隔
        status_forcelist=[429, 500, 502, 503, 504, 408],  # 添加408超时错误
        raise_on_status=False
    )
    adapter = requests.adapters.HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=1,
        pool_maxsize=1
    )
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

@app.route('/')
def tool_page():
    return '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>证件照换装工具</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Microsoft YaHei', Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; background: rgba(255, 255, 255, 0.95); border-radius: 20px; padding: 2rem; box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1); }
        .header { text-align: center; margin-bottom: 2rem; }
        .header h1 { color: #333; font-size: 2.5rem; margin-bottom: 0.5rem; font-weight: 700; }
        .header p { color: #666; font-size: 1.1rem; }
        .upload-section { background: white; border-radius: 12px; padding: 2rem; margin: 2rem 0; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); text-align: center; }
        .upload-area { border: 2px dashed #ddd; border-radius: 8px; padding: 2rem; margin: 1rem 0; cursor: pointer; transition: all 0.3s ease; position: relative; }
        .upload-area:hover { border-color: #6e8efb; background-color: #f8f9ff; }
        .upload-area.dragover { border-color: #6e8efb; background-color: #f0f2ff; }
        #fileInput { display: none; }
        .upload-icon { font-size: 3rem; color: #ddd; margin-bottom: 1rem; }
        .preview-area { display: flex; justify-content: center; gap: 1.5rem; margin: 2rem 0; flex-wrap: wrap; }
        .photo-box { width: 200px; background: white; border-radius: 8px; padding: 1rem; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); text-align: center; }
        .photo-box h3 { margin-bottom: 1rem; color: #555; font-size: 1rem; }
        .photo-placeholder { width: 100%; height: 250px; background-color: #f8f9fa; display: flex; align-items: center; justify-content: center; margin-bottom: 1rem; overflow: hidden; border-radius: 4px; border: 1px solid #eee; }
        .photo-placeholder img { width: 100%; height: 100%; object-fit: cover; }
        .clothing-upload-area { border: 2px dashed #ddd; border-radius: 8px; padding: 1rem; margin: 0.5rem 0; cursor: pointer; transition: all 0.3s ease; background: #f8f9ff; }
        .clothing-upload-area:hover { border-color: #6e8efb; background-color: #f0f2ff; }
        .background-selector { background: white; border-radius: 12px; padding: 2rem; margin: 2rem 0; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); text-align: center; }
        .bg-options { display: flex; justify-content: center; gap: 1rem; margin: 1rem 0; flex-wrap: wrap; }
        .bg-option { padding: 0.8rem 1.5rem; border: 2px solid #ddd; border-radius: 50px; cursor: pointer; transition: all 0.3s ease; background: white; color: #333; }
        .bg-option:hover { border-color: #6e8efb; }
        .bg-option.selected { background: #6e8efb; color: white; border-color: #6e8efb; }
        .generate-section { text-align: center; margin: 2rem 0; }
        .generate-btn { background: linear-gradient(135deg, #6e8efb 0%, #a777e3 100%); color: white; border: none; padding: 1rem 3rem; font-size: 1.2rem; border-radius: 50px; cursor: pointer; transition: all 0.3s ease; font-weight: 600; box-shadow: 0 4px 15px rgba(110, 142, 251, 0.4); }
        .generate-btn:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(110, 142, 251, 0.6); }
        .generate-btn:disabled { background: #ccc; cursor: not-allowed; transform: none; box-shadow: none; }
        .loading { display: none; text-align: center; margin: 2rem 0; }
        .spinner { border: 4px solid #f3f3f3; border-top: 4px solid #6e8efb; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto 1rem; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .message { padding: 1rem; border-radius: 8px; margin: 1rem 0; text-align: center; font-weight: 500; }
        .error { background: #fee; color: #c33; border: 1px solid #fcc; }
        .success { background: #efe; color: #363; border: 1px solid #cfc; }
        .download-btn { background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); color: white; border: none; padding: 0.8rem 2rem; font-size: 1rem; border-radius: 25px; cursor: pointer; transition: all 0.3s ease; margin-top: 1rem; }
        .download-btn:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(76, 175, 80, 0.4); }
        .tips { background: #f8f9fa; border-left: 4px solid #6e8efb; padding: 1rem; margin: 1rem 0; border-radius: 0 8px 8px 0; }
        .tips h4 { color: #6e8efb; margin-bottom: 0.5rem; }
        .tips ul { margin-left: 1.5rem; color: #666; }
        .tips li { margin-bottom: 0.3rem; }
        .size-info { background: #e3f2fd; border: 1px solid #2196f3; border-radius: 8px; padding: 1rem; margin: 1rem 0; text-align: center; color: #1976d2; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎭 证件照换装工具</h1>
            <p>上传您的照片和服装，AI帮您生成专业证件照</p>
        </div>

        <div class="size-info">
            <strong>📐 标准证件照尺寸：3:4比例 (960×1280像素，满足API最小要求)</strong>
            <div style="margin-top: 0.5rem; font-size: 0.9rem; color: #666;">
                <label>压缩质量: </label>
                <select id="compressionQuality" style="margin-left: 0.5rem; padding: 0.2rem;">
                    <option value="0.95">高质量 (95%)</option>
                    <option value="0.85" selected>标准质量 (85%)</option>
                    <option value="0.75">压缩质量 (75%)</option>
                    <option value="0.65">高压缩 (65%)</option>
                </select>
            </div>
        </div>

        <div class="upload-section">
            <h2>📸 上传原始照片</h2>
            <div class="upload-area" onclick="document.getElementById('fileInput').click()">
                <div class="upload-icon">📷</div>
                <div id="uploadText">点击或拖拽上传照片</div>
                <input type="file" id="fileInput" accept="image/*">
            </div>
            <div class="photo-placeholder" id="originalPhoto">
                <div style="color: #999;">原始照片预览</div>
            </div>
        </div>

        <div class="upload-section">
            <h2>👔 选择服装参考</h2>
            <div class="clothing-upload-area" onclick="document.getElementById('clothingInput').click()">
                <div style="color: #666; margin-bottom: 0.5rem;">点击上传自定义服装图片</div>
                <div id="clothingText" style="color: #999; font-size: 0.9rem;">或使用默认参考服装</div>
                <input type="file" id="clothingInput" accept="image/*" style="display: none;">
            </div>
            <div class="photo-placeholder" id="clothingImage">
                <img src="https://img.alicdn.com/imgextra/i1/668603298/O1CN01OeNCAX1aEXJeR4rhJ_!!668603298.png" alt="默认参考服装" style="width: 100%; height: 100%; object-fit: cover;">
            </div>
        </div>

        <div class="background-selector">
            <h2>🎨 选择背景颜色</h2>
            <div class="bg-options">
                <div class="bg-option selected" data-bg="白底">白色背景</div>
                <div class="bg-option" data-bg="蓝底">蓝色背景</div>
                <div class="bg-option" data-bg="红底">红色背景</div>
            </div>
        </div>

        <div class="generate-section">
            <button id="generateBtn" class="generate-btn">✨ 生成证件照</button>
            <div id="loadingArea" class="loading">
                <div class="spinner"></div>
                <div>AI正在为您生成证件照，请稍候...</div>
            </div>
            <div id="errorMessage" class="message error" style="display: none;"></div>
            <div id="successMessage" class="message success" style="display: none;"></div>
        </div>

        <div class="preview-area">
            <div class="photo-box">
                <h3>📸 原始照片</h3>
                <div class="photo-placeholder" id="originalPhotoPreview">
                    <div style="color: #999; font-size: 0.9rem;">上传的照片</div>
                </div>
            </div>
            <div class="photo-box">
                <h3>👔 参考服装</h3>
                <div class="photo-placeholder" id="clothingPreview">
                    <img src="https://img.alicdn.com/imgextra/i1/668603298/O1CN01OeNCAX1aEXJeR4rhJ_!!668603298.png" alt="参考服装" style="width: 100%; height: 100%; object-fit: cover;">
                </div>
            </div>
            <div class="photo-box">
                <h3>✨ 生成结果</h3>
                <div class="photo-placeholder" id="resultPhoto">
                    <div style="color: #999; font-size: 0.9rem;">证件照将显示在这里</div>
                </div>
                <button id="downloadBtn" class="download-btn" style="display: none; font-size: 0.8rem; padding: 0.5rem 1rem;">📥 下载</button>
            </div>
        </div>

        <div class="tips">
            <h4>💡 使用提示</h4>
            <ul>
                <li>请上传清晰的人像照片，面部特征明显</li>
                <li>建议上传正面照片，效果更佳</li>
                <li>支持 JPG、PNG 格式，文件大小不超过 10MB</li>
                <li>AI会自动调整照片尺寸和压缩，确保最佳效果</li>
                <li>生成过程需要 10-30 秒，请耐心等待</li>
                <li>生成的证件照为标准3:4比例，适合各种证件使用</li>
            </ul>
        </div>
    </div>

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
        let uploadedClothingUrl = API_CONFIG.clothingReference;
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
        const clothingPreview = document.getElementById('clothingPreview');

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
            if (files.length > 0) {
                processFile(files[0]);
            }
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
            
            // 显示压缩进度
            uploadText.textContent = '正在压缩图片...';
            
            compressImage(file, function(compressedDataUrl) {
                originalPhoto.innerHTML = `<img src="${compressedDataUrl}" alt="原始照片" style="width: 100%; height: 100%; object-fit: cover;">`;
                originalPhotoPreview.innerHTML = `<img src="${compressedDataUrl}" alt="原始照片" style="width: 100%; height: 100%; object-fit: cover;">`;
                
                // 计算压缩比例
                const originalSizeKB = Math.round(file.size / 1024);
                const compressedSizeKB = Math.round((compressedDataUrl.length * 0.75) / 1024);
                const compressionRatio = Math.round((1 - compressedSizeKB / originalSizeKB) * 100);
                
                uploadText.textContent = `已选择: ${file.name} (压缩${compressionRatio}%)`;
                uploadedImageUrl = compressedDataUrl;
            });
        }

        function compressImage(file, callback) {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const img = new Image();
            
            img.onload = function() {
                let { width, height } = img;
                
                // 证件照压缩策略：保持3:4比例，最大尺寸800x1067
                const maxWidth = 800;
                const maxHeight = 1067;
                const targetRatio = 3/4;
                
                // 计算目标尺寸，保持3:4比例
                let targetWidth, targetHeight;
                if (width / height > targetRatio) {
                    // 图片太宽，以高度为准
                    targetHeight = Math.min(height, maxHeight);
                    targetWidth = targetHeight * targetRatio;
                } else {
                    // 图片太高，以宽度为准
                    targetWidth = Math.min(width, maxWidth);
                    targetHeight = targetWidth / targetRatio;
                }
                
                // 确保尺寸是整数
                targetWidth = Math.floor(targetWidth);
                targetHeight = Math.floor(targetHeight);
                
                console.log(`原始尺寸: ${width}x${height}, 压缩后: ${targetWidth}x${targetHeight}`);
                
                canvas.width = targetWidth;
                canvas.height = targetHeight;
                
                // 设置高质量渲染
                ctx.imageSmoothingEnabled = true;
                ctx.imageSmoothingQuality = 'high';
                
                // 绘制压缩后的图片
                ctx.drawImage(img, 0, 0, targetWidth, targetHeight);
                
                // 获取用户选择的压缩质量
                const quality = parseFloat(document.getElementById('compressionQuality').value);
                const compressedDataUrl = canvas.toDataURL('image/jpeg', quality);
                
                // 检查压缩后的大小
                const sizeKB = Math.round((compressedDataUrl.length * 0.75) / 1024);
                console.log(`压缩后大小: ${sizeKB}KB`);
                
                callback(compressedDataUrl);
            };
            
            img.onerror = function() {
                console.error('图片加载失败');
                showError('图片加载失败，请重试');
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
            
            // 显示压缩进度
            clothingText.textContent = '正在压缩服装图片...';
            
            compressImage(file, function(compressedDataUrl) {
                clothingImage.src = compressedDataUrl;
                clothingPreview.innerHTML = `<img src="${compressedDataUrl}" alt="自定义服装" style="width: 100%; height: 100%; object-fit: cover;">`;
                
                // 计算压缩比例
                const originalSizeKB = Math.round(file.size / 1024);
                const compressedSizeKB = Math.round((compressedDataUrl.length * 0.75) / 1024);
                const compressionRatio = Math.round((1 - compressedSizeKB / originalSizeKB) * 100);
                
                clothingText.textContent = `已选择: ${file.name} (压缩${compressionRatio}%)`;
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
                const prompt = `将图1中的人物面部长相和发型特征提取出来，调整到证件照姿势(正对镜头，头部居中，双肩在镜头内，无任何手势，表情淡然),穿上图2的衣服，保持人物长相、发型（包括头发造型、位置、头发长短和发量）与图一一致，保持性别特征一致，生成一张标准的${selectedBackground}证件照（调整人物大小和位置到证件照的合理位置）`;
                const requestBody = {
                    prompt: prompt,
                    image: [uploadedImageUrl, uploadedClothingUrl],
                    background: selectedBackground,
                    size: "960x1280",  // 3:4比例 (960/1280 = 0.75) 满足最小921600像素要求
                    face_switch: true,
                    face_image: uploadedImageUrl,
                    face_style_switch: true,
                    cfg_scale: 12,
                    seed: -1
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
                    throw new Error('生成失败，请重试');
                }
            } catch (error) {
                console.error('生成错误:', error);
                showError(`生成失败: ${error.message}`);
            } finally {
                showLoading(false);
            }
        }

        function displayResult(imageUrl) {
            resultPhoto.innerHTML = `<img src="${imageUrl}" alt="生成的证件照" style="width: 100%; height: 100%; object-fit: cover;">`;
            downloadBtn.style.display = 'inline-block';
            downloadBtn.onclick = () => {
                const link = document.createElement('a');
                link.href = imageUrl;
                link.download = `证件照_${selectedBackground}_${Date.now()}.jpg`;
                link.click();
            };
        }

        function showLoading(show) {
            loadingArea.style.display = show ? 'block' : 'none';
            generateBtn.disabled = show;
        }

        function showError(message) {
            errorMessage.textContent = message;
            errorMessage.style.display = 'block';
            successMessage.style.display = 'none';
        }

        function showSuccess(message) {
            successMessage.textContent = message;
            successMessage.style.display = 'block';
            errorMessage.style.display = 'none';
        }

        function hideMessages() {
            errorMessage.style.display = 'none';
            successMessage.style.display = 'none';
        }
    </script>
</body>
</html>
    '''

@app.route('/api/generate', methods=['POST'])
def generate_image():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': '请求数据为空'}), 400
        
        if API_CONFIG['api_key'] == 'your-api-key-here':
            return jsonify({'success': False, 'error': 'API密钥未配置，请在Vercel环境变量中设置API_KEY'}), 500
        
        request_data = {
            "model": API_CONFIG['model'],
            "prompt": data.get('prompt', ''),
            "image": data.get('image', []),
            "background": data.get('background', '白底'),
            "size": data.get('size', '960x1280'),  # 3:4比例，满足最小921600像素要求
            "face_switch": data.get('face_switch', True),
            "face_image": data.get('face_image', ''),
            "face_style_switch": data.get('face_style_switch', True),
            "hyper_switch": data.get('hyper_switch', True),
            "cfg_scale": data.get('cfg_scale', 12),
            "seed": data.get('seed', -1)
        }
        
        session = create_session_with_retry()
        
        # 增加更详细的错误处理和超时设置
        try:
            response = session.post(
                API_CONFIG['endpoint'],
                headers={
                    'Authorization': f'Bearer {API_CONFIG["api_key"]}',
                    'Content-Type': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                },
                json=request_data,
                timeout=(30, 120),  # 连接超时30秒，读取超时120秒
                verify=False
            )
        except requests.exceptions.ConnectTimeout:
            return jsonify({'success': False, 'error': '连接火山引擎API超时，请稍后重试'}), 500
        except requests.exceptions.ReadTimeout:
            return jsonify({'success': False, 'error': 'API响应超时，请稍后重试'}), 500
        except requests.exceptions.ConnectionError as e:
            return jsonify({'success': False, 'error': f'网络连接错误: {str(e)}'}), 500
        except Exception as e:
            return jsonify({'success': False, 'error': f'请求失败: {str(e)}'}), 500
        
        if response.status_code == 200:
            result = response.json()
            return jsonify({'success': True, 'data': result})
        else:
            error_msg = f'API请求失败: {response.status_code}'
            try:
                error_data = response.json()
                error_msg += f' - {error_data.get("error", "未知错误")}'
            except:
                error_msg += f' - {response.text}'
            return jsonify({'success': False, 'error': error_msg}), response.status_code
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': '证件照换装工具运行正常'})

@app.route('/api/test-connection', methods=['GET'])
def test_connection():
    """测试与火山引擎API的连接"""
    try:
        session = create_session_with_retry()
        # 发送一个简单的测试请求
        response = session.get(
            'https://ark.cn-beijing.volces.com',
            timeout=10,
            verify=False
        )
        return jsonify({
            'status': 'success', 
            'message': f'连接正常，状态码: {response.status_code}',
            'response_time': '正常'
        })
    except requests.exceptions.ConnectTimeout:
        return jsonify({
            'status': 'error', 
            'message': '连接超时 - 可能是网络问题或API服务器不可达',
            'suggestion': '请检查网络连接或稍后重试'
        }), 500
    except requests.exceptions.ConnectionError as e:
        return jsonify({
            'status': 'error', 
            'message': f'连接错误: {str(e)}',
            'suggestion': '可能是网络防火墙或DNS问题'
        }), 500
    except Exception as e:
        return jsonify({
            'status': 'error', 
            'message': f'测试失败: {str(e)}',
            'suggestion': '请检查API配置'
        }), 500

if __name__ == '__main__':
    app.run(debug=True)