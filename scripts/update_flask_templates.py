import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("app = Flask(__name__)", "app = Flask(__name__, template_folder='frontend/templates')")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated Flask template_folder.")
