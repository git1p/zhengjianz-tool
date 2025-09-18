#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
证件照换装工具 - 代理服务器
解决CORS跨域问题，让前端可以直接调用火山引擎API
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import json
import os
import base64
from urllib.parse import urlparse

app = Flask(__name__)
CORS(app)  # 允许所有跨域请求

# 火山引擎API配置
API_CONFIG = {
    'endpoint': 'https://ark.cn-beijing.volces.com/api/v3/images/generations',
    'api_key': '70342b5a-147b-4bd0-9677-1739306b1f33',
    'model': 'doubao-seedream-4-0-250828'
}

@app.route('/')
def index():
    """主页 - 重定向到工具页面"""
    return send_from_directory('.', 'zhengjianz-tool.html')

@app.route('/zhengjianz-tool.html')
def tool_page():
    """证件照工具页面"""
    return send_from_directory('.', 'zhengjianz-tool.html')

@app.route('/api/generate', methods=['POST'])
def generate_image():
    """代理API调用 - 生成换装证件照"""
    try:
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
        
        print(f"正在调用火山引擎API...")
        print(f"请求数据: {json.dumps(api_request, indent=2, ensure_ascii=False)}")
        
        response = requests.post(
            API_CONFIG['endpoint'],
            headers=headers,
            json=api_request,
            timeout=60
        )
        
        print(f"API响应状态码: {response.status_code}")
        print(f"API响应内容: {response.text[:500]}...")
        
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

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'ok',
        'message': '代理服务器运行正常',
        'api_endpoint': API_CONFIG['endpoint']
    })

if __name__ == '__main__':
    print("=" * 50)
    print("证件照换装工具 - 代理服务器")
    print("=" * 50)
    print("正在启动服务器...")
    print("服务器地址: http://localhost:5000")
    print("工具页面: http://localhost:5000/zhengjianz-tool.html")
    print("按 Ctrl+C 停止服务器")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
