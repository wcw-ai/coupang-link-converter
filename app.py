from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from urllib.parse import quote
import re

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # 允許所有來源的跨域請求

def expand_with_requests(short_url):
    """使用 requests 展開短連結"""
    try:
        # 嘗試多種方法
        methods = [
            # 方法1: HEAD 請求
            lambda: requests.head(
                short_url,
                allow_redirects=False,
                headers={
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'
                },
                timeout=15
            ),
            # 方法2: GET 請求（模擬手機瀏覽器）
            lambda: requests.get(
                short_url,
                allow_redirects=True,
                headers={
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'zh-TW,zh;q=0.9',
                },
                timeout=15
            ),
            # 方法3: GET 請求（模擬桌面瀏覽器）
            lambda: requests.get(
                short_url,
                allow_redirects=True,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                },
                timeout=15
            ),
        ]
        
        for i, method in enumerate(methods):
            try:
                response = method()
                
                # 檢查 Location header
                if response.status_code in [301, 302, 303, 307, 308]:
                    location = response.headers.get('Location')
                    if location and 'link.tw.coupang.com' not in location:
                        return location
                
                # 檢查最終 URL（最重要的部分！）
                if hasattr(response, 'url') and response.url:
                    final_url = response.url
                    # 只要不是短連結網域，就視為成功展開
                    if 'link.tw.coupang.com' not in final_url:
                        return final_url
                
                # 從 HTML 中尋找真實連結
                if hasattr(response, 'text'):
                    # 尋找 tw.coupang.com 或 coupang.com.tw 的連結
                    patterns = [
                        r'https?://(?:www\.)?tw\.coupang\.com/products/[^\s"\'<>]+',
                        r'https?://(?:www\.)?coupang\.com\.tw/vp/products/[^\s"\'<>]+',
                        r'https?://(?:www\.)?tw\.coupang\.com[^\s"\'<>]+',
                        r'https?://(?:www\.)?coupang\.com\.tw[^\s"\'<>]+',
                        r'window\.location\.href\s*=\s*["\']([^"\']+)["\']',
                        r'<meta[^>]+http-equiv=["\']refresh["\'][^>]+url=([^"\'>\s]+)',
                    ]
                    
                    for pattern in patterns:
                        matches = re.findall(pattern, response.text, re.IGNORECASE)
                        if matches:
                            url = matches[0]
                            if 'coupang.com' in url:
                                return url
                
            except Exception as e:
                print(f"方法 {i+1} 失敗: {e}")
                continue
        
        return None
        
    except Exception as e:
        print(f"展開失敗: {e}")
        return None

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
        
        expanded = expand_with_requests(url)
        
        if expanded:
            return jsonify({
                'success': True,
                'original_url': url,
                'expanded_url': expanded
            })
        else:
            return jsonify({
                'success': False,
                'error': '無法展開連結，請手動複製完整網址'
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
            expanded = expand_with_requests(product_url)
            if expanded:
                expanded_url = expanded
            else:
                # 展開失敗，但仍然繼續生成追蹤連結（使用原始短連結）
                return jsonify({
                    'success': False,
                    'error': '無法自動展開短連結。請手動開啟此連結，複製完整網址後再試一次。',
                    'manual_expand_url': product_url
                }), 400
        
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
