#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
证件照换装工具 - Vercel API函数
"""

from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

# 火山引擎API配置 - 使用环境变量
API_CONFIG = {
    'endpoint': 'https://ark.cn-beijing.volces.com/api/v3/images/generations',
    'api_key': os.getenv('API_KEY', 'your-api-key-here'),
    'model': 'doubao-seedream-4-0-250828'
}

def handler(request):
    """Vercel函数入口点"""
    try:
        # 检查API密钥
        if API_CONFIG['api_key'] == 'your-api-key-here':
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'API密钥未配置，请联系管理员'
                })
            }
        
        # 获取请求数据
        if request.method != 'POST':
            return {
                'statusCode': 405,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Method not allowed'})
            }
        
        data = request.get_json()
        
        if not data:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': '请求数据为空'})
            }
        
        # 验证必需参数
        required_fields = ['prompt', 'image', 'background']
        for field in required_fields:
            if field not in data:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': f'缺少必需参数: {field}'})
                }
        
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
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': True,
                    'data': result
                })
            }
        else:
            return {
                'statusCode': response.status_code,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': f'API调用失败: {response.status_code} - {response.text}'
                })
            }
            
    except requests.exceptions.Timeout:
        return {
            'statusCode': 408,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'error': '请求超时，请稍后重试'
            })
        }
    except requests.exceptions.RequestException as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'error': f'网络请求失败: {str(e)}'
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'error': f'服务器内部错误: {str(e)}'
            })
        }
