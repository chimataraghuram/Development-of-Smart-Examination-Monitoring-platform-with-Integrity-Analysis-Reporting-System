import io
import openpyxl
from datetime import datetime

try:
    from . import database as db
except ImportError:
    import database as db

def generate_excel_export(export_type: str) -> io.BytesIO:
    """Generate an Excel file for the requested export type."""
    
    dashboard = db.get_admin_dashboard_data()
    wb = openpyxl.Workbook()
    ws = wb.active
    
    if export_type == 'candidates':
        ws.title = "All Candidates"
        headers = ['Name', 'Candidate ID', 'Session ID', 'Integrity Score', 'Risk Level', 'Session Status', 'Event Count']
        ws.append(headers)
        
        for student in dashboard.get('students', []):
            ws.append([
                student.get('name', ''),
                student.get('student_id', ''),
                student.get('session_id', ''),
                student.get('integrity_score', ''),
                student.get('risk_label', ''),
                student.get('session_status', ''),
                student.get('event_count', 0)
            ])
            
    elif export_type == 'average_students':
        ws.title = "Average Students"
        headers = ['Name', 'Candidate ID', 'Session ID', 'Integrity Score', 'Risk Level', 'Session Status', 'Event Count']
        ws.append(headers)
        
        avg_score = dashboard.get('stats', {}).get('average_integrity', 0)
        
        # Sort all students by how close they are to the average score
        sorted_students = sorted(
            dashboard.get('students', []),
            key=lambda s: abs(s.get('integrity_score', 0) - avg_score)
        )
        
        for student in sorted_students:
            ws.append([
                student.get('name', ''),
                student.get('student_id', ''),
                student.get('session_id', ''),
                student.get('integrity_score', ''),
                student.get('risk_label', ''),
                student.get('session_status', ''),
                student.get('event_count', 0)
            ])
                
    elif export_type == 'high_risk':
        ws.title = "High Risk Candidates"
        headers = ['Name', 'Candidate ID', 'Session ID', 'Integrity Score', 'Risk Level', 'Session Status', 'Event Count']
        ws.append(headers)
        
        for student in dashboard.get('students', []):
            if student.get('risk_label') == 'High Risk':
                ws.append([
                    student.get('name', ''),
                    student.get('student_id', ''),
                    student.get('session_id', ''),
                    student.get('integrity_score', ''),
                    student.get('risk_label', ''),
                    student.get('session_status', ''),
                    student.get('event_count', 0)
                ])

    elif export_type == 'suspicious_events':
        ws.title = "Suspicious Events"
        headers = ['Candidate', 'Candidate ID', 'Event Type', 'Timestamp', 'Score Deducted']
        ws.append(headers)
        
        for event in dashboard.get('events', []):
            # Only suspicious if deducted > 0
            if int(event.get('deducted', 0)) > 0:
                ws.append([
                    event.get('student_name', ''),
                    event.get('student_id', ''),
                    event.get('type', ''),
                    str(event.get('timestamp', '')),
                    event.get('deducted', 0)
                ])
    else:
        # Fallback empty
        ws.title = "Export"
        ws.append(['Unknown export type'])

    # Format headers
    for cell in ws[1]:
        cell.font = openpyxl.styles.Font(bold=True)

    # Save to BytesIO
    excel_file = io.BytesIO()
    wb.save(excel_file)
    excel_file.seek(0)
    
    return excel_file
