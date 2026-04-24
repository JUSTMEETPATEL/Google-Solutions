import urllib.request, json, uuid
from time import sleep

def build_multipart(files):
    boundary = uuid.uuid4().hex
    parts = []
    for field, (filename, data, mime) in files.items():
        parts.append(f'--{boundary}\r\n'.encode())
        parts.append(f'Content-Disposition: form-data; name="{field}"; filename="{filename}"\r\n'.encode())
        parts.append(f'Content-Type: {mime}\r\n\r\n'.encode())
        parts.append(data)
        parts.append(b'\r\n')
    parts.append(f'--{boundary}--\r\n'.encode())
    return b''.join(parts), boundary

with open('samples/insurance_claims_model.pkl', 'rb') as f:
    m = f.read()
with open('samples/insurance_claims_data.csv', 'rb') as f:
    d = f.read()

body, bound = build_multipart({'model': ('m.pkl', m, 'application/octet-stream'), 'dataset': ('d.csv', d, 'text/csv')})
req = urllib.request.Request('http://127.0.0.1:57530/api/v1/scan/', data=body, headers={'Content-Type': f'multipart/form-data; boundary={bound}'}, method='POST')
resp = urllib.request.urlopen(req)
scan_data = json.loads(resp.read())
session_id = scan_data['session_id']
print('Scan session:', session_id)

mitigate_req = urllib.request.Request('http://127.0.0.1:57530/api/v1/mitigate/', data=json.dumps({'session_id': session_id, 'algorithm': 'reweighing'}).encode(), headers={'Content-Type': 'application/json'}, method='POST')
try:
    mitigate_resp = urllib.request.urlopen(mitigate_req)
    print(json.loads(mitigate_resp.read()))
except Exception as e:
    print('Failed:', e, e.read().decode() if hasattr(e, "read") else "")
