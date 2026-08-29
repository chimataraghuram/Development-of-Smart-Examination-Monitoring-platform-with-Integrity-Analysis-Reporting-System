import sys

with open('frontend/templates/admin_dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if '<h2><i class="fas fa-' in line and 'Welcome back' not in line:
        continue
    if '<div class="sub"' in line and 'Candidates currently' in line:
        continue
    if '<div class="sub"' in line and 'Candidates grouped' in line:
        continue
    if '<div class="sub"' in line and 'Recent high' in line:
        continue
    if '<div class="sub"' in line and 'Create examinations' in line:
        continue
    if '<div class="sub"' in line and 'All monitoring events' in line:
        continue
    new_lines.append(line)

with open('frontend/templates/admin_dashboard.html', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print('Done removing titles!')
