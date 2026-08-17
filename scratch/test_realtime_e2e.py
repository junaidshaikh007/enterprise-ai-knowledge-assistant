"""
End-to-end verification of Real-Time Document Ingestion and Real-Time SSE Chat Streaming.
"""
import urllib.request
import json
from urllib.parse import urlencode

def run_test():
    # 0. Register user if not exists
    reg_payload = json.dumps({
        'email': 'demo@enterprise.com',
        'password': 'DemoPassword123!',
        'full_name': 'Demo User',
        'organization_name': 'Enterprise Corp'
    }).encode()
    reg_req = urllib.request.Request('http://localhost:8000/api/v1/auth/register', data=reg_payload, headers={'Content-Type': 'application/json'})
    try:
        urllib.request.urlopen(reg_req)
    except Exception:
        pass

    # 1. Login user
    login_data = urlencode({'username': 'demo@enterprise.com', 'password': 'DemoPassword123!'}).encode()
    req = urllib.request.Request('http://localhost:8000/api/v1/auth/login', data=login_data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    with urllib.request.urlopen(req) as resp:
        token_info = json.loads(resp.read().decode())
        token = token_info['access_token']
        print("[SUCCESS] User logged in. JWT token acquired.")

    # 2. Upload document for real-time indexing
    filename = 'policy_2026.txt'
    content = b'Enterprise Policy 2026: Employees receive 28 days of paid vacation leave per year.'
    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    body = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f'Content-Type: text/plain\r\n\r\n'
    ).encode() + content + f'\r\n--{boundary}--\r\n'.encode()

    req = urllib.request.Request(
        'http://localhost:8000/api/v1/documents/upload',
        data=body,
        headers={
            'Content-Type': f'multipart/form-data; boundary={boundary}',
            'Authorization': f'Bearer {token}'
        }
    )
    try:
        with urllib.request.urlopen(req) as resp:
            upload_res = json.loads(resp.read().decode())
            print(f"[SUCCESS] Real-time Document Upload Response: {upload_res}")
    except urllib.error.HTTPError as err:
        print("[ERROR] Document Upload 500 response:", err.read().decode())
        raise err

    # 3. Stream real-time chat with document context
    chat_data = json.dumps({'message': 'How many days of paid vacation leave do employees receive?'}).encode()
    req = urllib.request.Request(
        'http://localhost:8000/api/v1/chat/',
        data=chat_data,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
    )
    print("\n--- [REAL-TIME SSE CHAT STREAMING] ---")
    with urllib.request.urlopen(req) as resp:
        for line in resp:
            line_str = line.decode().strip()
            if line_str:
                print(line_str)

if __name__ == "__main__":
    run_test()
