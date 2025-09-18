from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

# 火山引擎API配置
API_CONFIG = {
    'endpoint': 'https://ark.cn-beijing.volces.com/api/v3/images/generations',
    'api_key': os.getenv('API_KEY', 'your-api-key-here'),
    'model': 'doubao-seedream-4-0-250828'
}

@app.route('/')
def index():
    """主页 - 重定向到工具页面"""
    return app.send_static_file('zhengjianz-tool.html')

@app.route('/zhengjianz-tool.html')
def tool_page():
    """证件照工具页面"""
    return app.send_static_file('zhengjianz-tool.html')

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
        # 检查API密钥
        if API_CONFIG['api_key'] == 'your-api-key-here':
            return jsonify({
                'success': False,
                'error': 'API密钥未配置，请联系管理员'
            }), 500
        
        # 获取请求数据
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据为空'}), 400
        
        # 验证必需参数
        required_fields = ['prompt', 'image', 'background']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必需参数: {field}'}), 400
        
        # 构建火山引擎API请求
        api_request = {
            'model': API_CONFIG['model'],
            'prompt': data['prompt'],
            'image': data['image'],
            'response_format': 'url',
            'size': '2K',
            'watermark': False
        }
        
        # 调用火山引擎API
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {API_CONFIG["api_key"]}'
        }
        
        response = requests.post(
            API_CONFIG['endpoint'],
            headers=headers,
            json=api_request,
            timeout=60
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
