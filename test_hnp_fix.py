"""
Local test: verify HNP fix and that app still works.
Run from visionscript-fix dir: python test_hnp_fix.py
"""
import os
import sys

# Use local package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Ensure env not set so API_URL is ""
for key in ("VISIONSCRIPT_BASE_URL", "API_URL"):
    os.environ.pop(key, None)

def test_notebook_app():
    from visionscript.notebook import app
    client = app.test_client()
    # 1) Without Host header: response should have API_URL = ""
    r = client.get("/notebook")
    assert r.status_code == 200, r.status_code
    html = r.data.decode("utf-8")
    assert 'const API_URL = "";' in html or 'const API_URL = ""' in html, (
        "Expected API_URL empty in HTML when env unset. Got: " + html[html.find("API_URL"):html.find("API_URL")+80]
    )
    print("[PASS] GET /notebook without Host: API_URL is empty in HTML")
    # 2) With forged Host header: still API_URL = "" (not poisoned)
    r2 = client.get("/notebook", headers={"Host": "evil.example.com"})
    assert r2.status_code == 200, r2.status_code
    html2 = r2.data.decode("utf-8")
    assert "evil.example.com" not in html2 or 'const API_URL = ""' in html2, (
        "Host header should not poison API_URL. Found evil.example.com in: " + html2[html2.find("API_URL"):html2.find("API_URL")+100]
    )
    assert 'const API_URL = "";' in html2 or 'const API_URL = ""' in html2
    print("[PASS] GET /notebook with Host: evil.example.com: API_URL still empty (not poisoned)")
    # 3) Basic behaviour: GET / redirects to /notebook
    r_root = client.get("/")
    assert r_root.status_code in (200, 302), r_root.status_code
    print("[PASS] GET / returns 200 or 302 (redirect to /notebook)")
    print("All HNP fix and sanity checks passed.")

if __name__ == "__main__":
    test_notebook_app()
