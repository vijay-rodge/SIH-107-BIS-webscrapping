from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        html = '''<!DOCTYPE html>
<html>
<head><title>BIS Intelligent Assistant</title></head>
<body style="background:#0c1524;color:#f1f5f9;font-family:sans-serif;padding:40px;text-align:center;">
  <div style="max-width:600px;margin:auto;background:#1a2333;padding:30px;border-radius:10px;border:1px solid #334155;">
    <h1 style="color:#f59e0b;">BIS AI Assistant</h1>
    <p style="color:#94a3b8;">SIH ID: 26107 - Ministry of Consumer Affairs (DoCA)</p>
    <div style="background:#0f172a;padding:15px;margin:20px 0;border-left:4px solid #f59e0b;text-align:left;font-size:0.9rem;">
      <strong>Vercel Serverless Notice:</strong><br>
      Streamlit requires continuous WebSockets and persistent server state. For the live interactive app, deploy via Streamlit Community Cloud or Render.
    </div>
  </div>
</body>
</html>'''
        self.wfile.write(html.encode('utf-8'))
