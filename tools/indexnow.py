"""Tell Bing (and so ChatGPT search) about every URL in sitemap.xml.

Run after each deploy that adds or changes pages:  python tools/indexnow.py
The key file /e2ba8da7bf924ce5a9a197dcfb05084b.txt must be live on the site first.
"""
import json, os, re, urllib.request

KEY = "e2ba8da7bf924ce5a9a197dcfb05084b"
HOST = "web.wogent.in"
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
urls = re.findall(r"<loc>(https://%s/[^<]*)</loc>" % HOST, open(os.path.join(root, "sitemap.xml"), encoding="utf-8").read())
assert urls, "no URLs found in sitemap.xml"
body = json.dumps({"host": HOST, "key": KEY, "keyLocation": f"https://{HOST}/{KEY}.txt", "urlList": urls}).encode()
req = urllib.request.Request("https://api.indexnow.org/indexnow", body, {"Content-Type": "application/json; charset=utf-8"})
print(urllib.request.urlopen(req).status, "submitted", len(urls), "URLs")  # 200 or 202 = accepted
