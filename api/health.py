#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
健康检查API
"""

import json
import os

def handler(request):
    """健康检查函数"""
    api_key = os.getenv('API_KEY', 'your-api-key-here')
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'status': 'ok',
            'message': '代理服务器运行正常',
            'api_configured': api_key != 'your-api-key-here'
        })
    }
