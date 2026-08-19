import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace imports
content = re.sub(r'import database as db', 'import backend.database as db', content)
content = re.sub(r'import export_service', 'import backend.export_service as export_service', content)
content = re.sub(r'from ai_service import', 'from backend.ai_service import', content)
content = re.sub(r'from integrity_scorer import', 'from backend.integrity_scorer import', content)

# Update HAARCASCADE path
content = re.sub(r"'haarcascade_frontalface_default\.xml'", "'backend/haarcascade_frontalface_default.xml'", content)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

with open('backend/database.py', 'r', encoding='utf-8') as f:
    db_content = f.read()
db_content = db_content.replace("'exam_monitor.db'", "'backend/exam_monitor.db'")
with open('backend/database.py', 'w', encoding='utf-8') as f:
    f.write(db_content)

print("Updated paths in app.py and backend/database.py")
