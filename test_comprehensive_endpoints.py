import base64
import os
import shutil
import tempfile
from unittest.mock import patch

import cv2
import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

import database as db

work_dir = tempfile.mkdtemp(prefix='exam_monitor_suite_')
db.DB_PATH = os.path.join(work_dir, 'exam_monitor.db')
db.init_db()

from app import app

app.config.update(TESTING=True, UPLOAD_FOLDER=os.path.join(work_dir, 'evidence'))
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

image = np.zeros((64, 64, 3), dtype=np.uint8)
ok, encoded_image = cv2.imencode('.png', image)
assert ok
ONE_PIXEL_PNG = 'data:image/png;base64,' + base64.b64encode(encoded_image.tobytes()).decode('ascii')


def expect(response, status, label):
    assert response.status_code == status, f'{label}: expected {status}, got {response.status_code}; {response.get_data(as_text=True)[:500]}'
    return response


class FakeAIResponse:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self):
        return b'{"choices": [{"message": {"content": "Your current integrity score is 500. Each recorded violation deducted 100 points."}}]}'


student = app.test_client()
admin = app.test_client()
anonymous = app.test_client()

# Public pages and authentication validation
expect(anonymous.get('/'), 302, 'root redirect')
expect(anonymous.get('/login'), 200, 'login page')
expect(anonymous.get('/register'), 200, 'register page')
expect(anonymous.post('/api/login', json={'email': 'missing@gmail.com', 'password': '123456'}), 401, 'unknown-user login')
expect(anonymous.post('/api/register', json={}), 400, 'invalid registration')

# Student registration and protected student flow
registration = expect(student.post('/api/register', json={
    'name': 'Comprehensive Student',
    'email': 'comprehensive.student@gmail.com',
    'password': 'a1b2c3',
    'role': 'student',
    'student_id': '8123',
    'session_id': 'EXAM26',
}), 201, 'student registration').get_json()
student_id = registration['user_id']

expect(student.get('/dashboard'), 200, 'dashboard page')
expect(student.get('/report'), 200, 'report page')
expect(student.get('/api/dashboard/student'), 200, 'dashboard before exam')
expect(student.post('/api/events', json={}), 400, 'event validation')
expect(student.post('/api/exam/start'), 200, 'start exam')

face_response = expect(student.post('/api/detect_faces', json={'image': ONE_PIXEL_PNG}), 200, 'face detection')
assert face_response.get_json()['face_count'] == 0
expect(student.post('/api/detect_faces', json={}), 400, 'face detection missing image validation')
expect(student.post('/api/detect_faces', json={'image': 'data:image/png;base64,not-valid-base64'}), 400, 'face detection invalid image validation')

# Monitoring events including screenshot evidence
for event_type, deducted, screenshot in (
    ('Face Detected', 0, None),
    ('Face Not Detected', 1, None),
    ('Browser Focus Loss', 1, ONE_PIXEL_PNG),
    ('Browser Focus Regained', 0, None),
    ('Multiple Faces', 1, None),
    ('Tab Switching', 1, None),
    ('Suspicious Activity', 1, None),
):
    payload = {'type': event_type, 'deducted': deducted}
    if screenshot:
        payload['screenshot'] = screenshot
    expect(student.post('/api/events', json=payload), 201, f'event {event_type}')

running_dashboard = expect(student.get('/api/dashboard/student'), 200, 'dashboard during exam').get_json()
assert running_dashboard['exam_running'] is True
assert running_dashboard['event_counts']['Face Not Detected'] == 1
assert running_dashboard['event_counts']['Browser Focus Loss'] == 1
assert running_dashboard['event_counts']['Multiple Faces'] == 1
assert running_dashboard['event_counts']['Tab Switching'] == 1
assert running_dashboard['event_counts']['Suspicious Activity'] == 1
assert running_dashboard['integrity_score'] == 500.0
assert running_dashboard['total_deduction'] == 500.0

expect(student.post('/api/exam/end'), 200, 'end exam')
final_dashboard = expect(student.get('/api/dashboard/student'), 200, 'dashboard after exam').get_json()
assert final_dashboard['exam_running'] is False
assert final_dashboard['final_score'] == 500.0

current_report = expect(student.get('/api/integrity_report'), 200, 'session-bound report').get_json()
assert current_report['user']['id'] == student_id
assert current_report['event_counts']['Face Not Detected'] == 1
assert current_report['event_counts']['Browser Focus Loss'] == 1
assert current_report['event_counts']['Multiple Faces'] == 1
assert current_report['event_counts']['Tab Switching'] == 1
assert current_report['event_counts']['Suspicious Activity'] == 1
assert current_report['score'] == 500.0
assert current_report['raw_score_from_events'] == 500.0
assert current_report['total_deduction'] == 500.0
assert len(current_report['events']) == 7
assert all(event['deducted'] == 100 for event in current_report['events'] if event['type'] in {
    'Face Not Detected', 'Browser Focus Loss', 'Multiple Faces', 'Tab Switching', 'Suspicious Activity'
})
assert all(event['deducted'] == 0 for event in current_report['events'] if event['type'] in {
    'Face Detected', 'Browser Focus Regained'
})

with patch.dict(os.environ, {'OPENROUTER_API_KEY': 'test-key'}, clear=False), patch('ai_service.request.urlopen', return_value=FakeAIResponse()):
    ai_answer = expect(student.post('/api/ai/ask', json={
        'question': 'Why is my score 500?',
        'history': [{'role': 'user', 'content': 'Explain my report.'}],
    }), 200, 'student AI Ask').get_json()
    assert '500' in ai_answer['answer']

expect(student.post('/api/ai/ask', json={}), 400, 'AI Ask question validation')
expect(student.get(f'/api/integrity_report/{student_id}'), 200, 'student id report')
legacy_report = expect(student.get(f'/api/report/{student_id}'), 200, 'legacy report').get_json()
assert legacy_report['user']['id'] == student_id

screenshot_path = next(event['screenshot_path'] for event in current_report['events'] if event['screenshot_path'])
expect(student.get('/evidence/' + screenshot_path), 200, 'student evidence access')
expect(student.get('/evidence/other-user/private.png'), 403, 'student evidence isolation')

# Admin flow and cross-candidate reporting
admin_registration = expect(admin.post('/api/register', json={
    'name': 'Comprehensive Admin',
    'email': 'comprehensive.admin@gmail.com',
    'password': 'a1b2c3',
    'role': 'admin',
}), 201, 'admin registration').get_json()
assert admin_registration['role'] == 'admin'
expect(admin.get('/admin_dashboard'), 200, 'admin page')
admin_dashboard = expect(admin.get('/api/dashboard/admin'), 200, 'admin dashboard').get_json()
assert 'stats' in admin_dashboard and 'analytics' in admin_dashboard and 'students' in admin_dashboard and 'events' in admin_dashboard
expect(admin.get('/api/dashboard/admin?candidate_id=8123&event_type=Browser%20Focus%20Loss'), 200, 'admin filters')
admin_report = expect(admin.get(f'/api/integrity_report/{student_id}'), 200, 'admin cross-candidate report').get_json()
assert admin_report['user']['id'] == student_id
with patch.dict(os.environ, {'OPENROUTER_API_KEY': 'test-key'}, clear=False), patch('ai_service.request.urlopen', return_value=FakeAIResponse()):
    admin_ai_answer = expect(admin.post('/api/ai/ask', json={'question': 'Summarize the monitoring dashboard.'}), 200, 'admin AI Ask').get_json()
    assert '500' in admin_ai_answer['answer']
expect(admin.get('/admin_logs'), 200, 'admin logs page')

# Logout and API authentication behavior
expect(student.post('/api/logout'), 200, 'student logout')
expect(student.get('/api/dashboard/student'), 401, 'dashboard unauthorized JSON')
expect(student.get('/api/integrity_report'), 401, 'report unauthorized JSON')
expect(student.post('/api/ai/ask', json={'question': 'Can I view a score?'}), 401, 'AI Ask unauthorized JSON')

print('COMPREHENSIVE_ENDPOINT_SUITE_PASS')
print('STUDENT_ID=' + str(student_id))
print('FINAL_SCORE=' + str(current_report['score']))
print('EVENT_COUNT=' + str(len(current_report['events'])))

shutil.rmtree(work_dir, ignore_errors=True)
