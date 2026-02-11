from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from urllib.parse import quote

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # 允許所有來源的跨域請求

@app.route('/api/expand-url', methods=['POST'])
def expand_url():
    """展開短連結的 API"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({
                'success': False,
                'error': '請提供 URL'
            }), 400
        
        # 發送請求展開短連結
        response = requests.get(
            url,
            allow_redirects=True,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            },
            timeout=10
        )
        
        # 返回最終的 URL
        expanded_url = response.url
        
        return jsonify({
            'success': True,
            'original_url': url,
            'expanded_url': expanded_url
        })
        
    except requests.RequestException as e:
        return jsonify({
            'success': False,
            'error': f'無法展開連結: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'發生錯誤: {str(e)}'
        }), 500

@app.route('/api/generate-tracking', methods=['POST'])
def generate_tracking():
    """生成追蹤連結的 API（完整版）"""
    try:
        data = request.get_json()
        product_url = data.get('product_url')
        base_url = data.get('base_url')
        sub_ids = data.get('sub_ids', {})
        
        if not product_url or not base_url:
            return jsonify({
                'success': False,
                'error': '請提供商品連結和 Base URL'
            }), 400
        
        # 檢查是否為短連結
        is_short_link = 'link.tw.coupang.com' in product_url
        expanded_url = product_url
        
        # 如果是短連結，先展開
        if is_short_link:
            try:
                response = requests.get(
                    product_url,
                    allow_redirects=True,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    },
                    timeout=10
                )
                expanded_url = response.url
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'無法展開短連結: {str(e)}'
                }), 500
        
        # 生成追蹤連結
        tracking_url = base_url
        
        # 處理 sub_ids
        params = []
        for key, value in sub_ids.items():
            if value:
                params.append(f"{key}={value}")
        
        # 組合最終連結
        if params:
            tracking_url += '?' + '&'.join(params)
            tracking_url += '&t=' + quote(expanded_url, safe='')
        else:
            tracking_url += '?t=' + quote(expanded_url, safe='')
        
        return jsonify({
            'success': True,
            'original_url': product_url,
            'expanded_url': expanded_url if is_short_link else None,
            'tracking_url': tracking_url,
            'is_short_link': is_short_link
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'發生錯誤: {str(e)}'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """健康檢查端點"""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
