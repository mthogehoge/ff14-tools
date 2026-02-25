import urllib.request, re
html = urllib.request.urlopen("http://localhost:8000/").read().decode("utf-8")
matches = re.findall(r"【.*?金策タスク:.*?</li>", html, re.DOTALL)
print("\n---\n".join(matches))
