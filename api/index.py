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
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
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
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎭 证件照换装工具</h1>
            <p>上传您的照片和服装，AI帮您生成专业证件照</p>
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
                <img src="https://img.alicdn.com/imgextra/i1/668603298/O1CN01OeNCAX1aEXJeR4rhJ_!!668603298.png" alt="默认参考服装" style="max-width: 100%; max-height: 100%; object-fit: contain;">
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
                <h3>原始照片</h3>
                <div class="photo-placeholder" id="originalPhotoPreview">
                    <div style="color: #999;">原始照片</div>
                </div>
            </div>
            <div class="photo-box">
                <h3>生成结果</h3>
                <div class="photo-placeholder" id="resultPhoto">
                    <div style="color: #999;">生成的证件照将显示在这里</div>
                </div>
                <button id="downloadBtn" class="download-btn" style="display: none;">📥 下载图片</button>
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
            
            // 压缩图片
            compressImage(file, function(compressedDataUrl) {
                originalPhoto.innerHTML = `<img src="${compressedDataUrl}" alt="原始照片">`;
                uploadText.textContent = `已选择: ${file.name} (已压缩)`;
                uploadedImageUrl = compressedDataUrl;
            });
        }

        function compressImage(file, callback) {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const img = new Image();
            
            img.onload = function() {
                // 计算压缩后的尺寸，最大边不超过1024px
                let { width, height } = img;
                const maxSize = 1024;
                
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
                const prompt = `将图1中的人物面部长相和发型特征提取出来，调整到证件照姿势(正对镜头，头部居中，双肩在镜头内，无任何手势，表情淡然),穿上图2的衣服，保持人物长相、发型（包括头发造型、位置、头发长短和发量）与图一一致，保持性别特征一致，生成一张标准的${selectedBackground}证件照（调整人物大小和位置到证件照的合理位置）`;
                const requestBody = {
                    prompt: prompt,
                    image: [uploadedImageUrl, uploadedClothingUrl], // 使用用户上传的服装或默认服装
                    background: selectedBackground,
                    face_switch: true,       // 开启人脸特征学习（核心）
                    face_image: uploadedImageUrl,   // 强制绑定图1的面部与发型特征
                    face_style_switch: true, // 同步锁定发型风格
                    hyper_switch: true,      // 启用超分辨率细节保留
                    cfg_scale: 12,           // 增强约束强度（10-15效果最佳）
                    seed: -1                 // 固定随机种子确保一致性
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
            resultPhoto.innerHTML = `<img src="${imageUrl}" alt="生成的证件照" style="max-width: 100%; max-height: 100%; object-fit: contain;">`;
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
        
        # 检查API密钥
        if API_CONFIG['api_key'] == 'your-api-key-here':
            return jsonify({'success': False, 'error': 'API密钥未配置，请在Vercel环境变量中设置API_KEY'}), 500
        
        # 构建请求数据
        request_data = {
            "model": API_CONFIG['model'],
            "prompt": data.get('prompt', ''),
            "image": data.get('image', []),
            "background": data.get('background', '白底'),
            "face_switch": data.get('face_switch', True),
            "face_image": data.get('face_image', ''),
            "face_style_switch": data.get('face_style_switch', True),
            "hyper_switch": data.get('hyper_switch', True),
            "cfg_scale": data.get('cfg_scale', 12),
            "seed": data.get('seed', -1)
        }
        
        # 创建带重试机制的session
        session = create_session_with_retry()
        
        # 发送请求到火山引擎API
        response = session.post(
            API_CONFIG['endpoint'],
            headers={
                'Authorization': f'Bearer {API_CONFIG["api_key"]}',
                'Content-Type': 'application/json'
            },
            json=request_data,
            timeout=60,
            verify=False  # 禁用SSL验证以避免SSLEOFError
        )
        
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

if __name__ == '__main__':
    app.run(debug=True)
