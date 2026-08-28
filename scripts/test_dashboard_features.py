import base64
import os
import shutil
import sys
import tempfile
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))

from Backend import database as db

work_dir = Path(tempfile.mkdtemp(prefix='dashboard_feature_check_'))
db.DB_PATH = str(work_dir / 'exam_monitor.db')
db.init_db()

from app import app

app.config.update(TESTING=True, UPLOAD_FOLDER=str(work_dir / 'evidence'))
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

client = app.test_client()

def expect(response, status, label):
    assert response.status_code == status, f'{label}: expected {status}, got {response.status_code}'
    return response


def check(condition, label):
    assert condition, label


image = np.zeros((64, 64, 3), dtype=np.uint8)
ok, encoded = cv2.imencode('.png', image)
check(ok, 'test image encoding')
one_pixel_png = 'data:image/png;base64,' + base64.b64encode(encoded.tobytes()).decode('ascii')

# Public and authenticated dashboard delivery.
expect(client.get('/login'), 200, 'login page')
registration = expect(client.post('/api/register', json={
    'name': 'Dashboard Feature Student',
    'email': 'dashboard.feature.student@gmail.com',
    'password': 'a1b2c3d4',
    'role': 'student',
    'student_id': '8456',
    'session_id': 'EXAM26',
}), 201, 'student registration').get_json()

html_response = expect(client.get('/dashboard'), 200, 'dashboard page')
html = html_response.get_data(as_text=True)
check(html_response.headers.get('Cache-Control', '').startswith('no-store'), 'dashboard no-cache header')

# Profile redesign and preserved data hooks.
for marker in (
    'class="panel active profile-panel"',
    'class="profile-hero"',
    'class="profile-identity-card"',
    'class="profile-result-card"',
    'class="profile-facts-grid"',
    'id="candId"', 'id="candName"', 'id="candSession"',
    'id="candScore"', 'id="candRemark"', 'id="faceRatio"',
    'id="candidateExamSections"', 'id="examControls"',
    'id="integrityScoreSection"',
):
    check(marker in html, f'Profile marker missing: {marker}')
for element_id in ('candId', 'candName', 'candSession', 'candScore', 'candRemark', 'faceRatio', 'examControls', 'integrityScoreSection'):
    check(html.count(f'id="{element_id}"') == 1, f'duplicate ID: {element_id}')

# Navigation, Activity, Stats, Report, and evidence preview hooks.
for marker in (
    'data-panel="candidate"', 'data-panel="session"', 'data-panel="stats"',
    'Profile', 'Activity', 'Stats', 'Report',
        '<div class="panel" id="panelSession">',
  'Session Information'
,
    'id="eventLogBody"', 'id="timeline"',     'id="eventLogBody"',

    'class="panel stats-panel"', 'id="panelReport"',
    'class="evidence-modal"', 'id="closeEvidenceTop"',
    'function openEvidencePreview', 'function closeEvidencePreview',
    "document.getElementById('inlineReportEvents').addEventListener('click'",
    'function setActiveNav(panelName)', "setActiveNav('report');", 'setActiveNav(panel);',
):
    check(marker in html, f'dashboard hook missing: {marker}')
check('class="evidence-view-btn"' in html and 'data-evidence-url' in html, 'evidence preview button missing')
check("const evidence = event.screenshot_path ? `<a href=" not in html, 'evidence still renders as a new-tab anchor')

# Dashboard APIs and network verification endpoint.
expect(client.get('/api/check_verification'), 200, 'network verification check')
initial_dashboard = expect(client.get('/api/dashboard/student'), 200, 'initial student dashboard API').get_json()
check(initial_dashboard['user']['email'] == 'dashboard.feature.student@gmail.com', 'dashboard user identity')
check(initial_dashboard['integrity_score'] == 100.0, 'initial integrity score')

# Exam lifecycle, monitoring event, report, and evidence access.
expect(client.post('/api/exam/start'), 200, 'start exam')
expect(client.post('/api/exam/pause'), 200, 'pause exam')
expect(client.post('/api/exam/resume'), 200, 'resume exam')
expect(client.post('/api/events', json={'type': 'Suspicious Activity', 'screenshot': one_pixel_png}), 201, 'evidence event')
active_dashboard = expect(client.get('/api/dashboard/student'), 200, 'active dashboard API').get_json()
check(active_dashboard['integrity_score'] == 95.0, 'event score deduction')
check(active_dashboard['event_counts']['Suspicious Activity'] == 1, 'event count')
report = expect(client.get('/api/integrity_report'), 200, 'integrity report API').get_json()
check(report['score'] == 95.0, 'report score')
check(len(report['events']) == 1, 'report event count')
evidence_path = report['events'][0]['screenshot_path']
expect(client.get('/evidence/' + evidence_path), 200, 'evidence image access')
expect(client.post('/api/exam/end'), 200, 'end exam')
final_dashboard = expect(client.get('/api/dashboard/student'), 200, 'final dashboard API').get_json()
check(final_dashboard['exam_running'] is False, 'exam ended state')
check(final_dashboard['final_score'] == 95.0, 'final score')

# Logout and protected-route behavior.
expect(client.post('/api/logout'), 200, 'logout')
expect(client.get('/api/dashboard/student'), 401, 'dashboard protection after logout')

print('DASHBOARD_FEATURE_SUITE_PASS')
print('PROFILE_REDESIGN_MARKERS_PASS')
print('FEATURES_CHECKED=Profile, Activity, Stats, Report, network, exam lifecycle, integrity scoring, evidence preview, logout')
print('FINAL_SCORE=' + str(final_dashboard['final_score']))

shutil.rmtree(work_dir, ignore_errors=True)
