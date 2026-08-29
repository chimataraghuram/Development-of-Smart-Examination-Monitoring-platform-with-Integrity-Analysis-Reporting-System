import re

with open('frontend/templates/admin_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

new_header = """        <!-- ===== PAGE: DASHBOARD ===== -->
        <div class="page active" id="page-dashboard">
            <!-- New Modern Welcome Banner -->
            <div class="welcome-banner" style="background: rgba(13,11,46,0.6); border: 1px solid rgba(255,255,255,0.05); border-radius: 20px; padding: 24px 32px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; box-shadow: 0 8px 32px rgba(0,0,0,0.2); backdrop-filter: blur(10px); flex-wrap: wrap; gap: 20px;">
                <div class="welcome-text">
                    <div style="color: #b8aaff; font-size: 13px; font-weight: 600; margin-bottom: 8px;">Dashboard</div>
                    <h2 style="margin: 0 0 8px 0; font-size: 28px; font-weight: 700; color: #fff;">Welcome back, Admin 👋</h2>
                    <div style="color: rgba(255,255,255,0.6); font-size: 14px;">Here's what's happening with your examinations today.</div>
                </div>
                <div class="welcome-actions" style="display: flex; gap: 16px; flex-wrap: wrap;">
                    <button id="systemHealthBtn" class="welcome-action-btn" style="background: rgba(124,77,255,0.05); border: 1px solid rgba(124,77,255,0.15); border-radius: 12px; padding: 16px 20px; display: flex; align-items: center; gap: 16px; cursor: pointer; transition: 0.2s; text-align: left; min-width: 240px;" onmouseover="this.style.background='rgba(124,77,255,0.15)'" onmouseout="this.style.background='rgba(124,77,255,0.05)'">
                        <div style="background: rgba(124,77,255,0.15); width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: #b8aaff; font-size: 18px;"><i class="fas fa-heartbeat"></i></div>
                        <div style="flex: 1;">
                            <div style="color: #fff; font-weight: 600; font-size: 14px; margin-bottom: 4px;">System Diagnosis</div>
                            <div style="color: rgba(255,255,255,0.5); font-size: 12px;">Check system health & status</div>
                        </div>
                        <i class="fas fa-chevron-right" style="color: rgba(255,255,255,0.3);"></i>
                    </button>
                    <button id="exportAllCsv" class="welcome-action-btn" style="background: rgba(81,207,102,0.05); border: 1px solid rgba(81,207,102,0.15); border-radius: 12px; padding: 16px 20px; display: flex; align-items: center; gap: 16px; cursor: pointer; transition: 0.2s; text-align: left; min-width: 240px;" onmouseover="this.style.background='rgba(81,207,102,0.15)'" onmouseout="this.style.background='rgba(81,207,102,0.05)'">
                        <div style="background: rgba(81,207,102,0.15); width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: #51cf66; font-size: 18px;"><i class="fas fa-file-csv"></i></div>
                        <div style="flex: 1;">
                            <div style="color: #fff; font-weight: 600; font-size: 14px; margin-bottom: 4px;">Export Reports</div>
                            <div style="color: rgba(255,255,255,0.5); font-size: 12px;">Download reports & insights</div>
                        </div>
                        <i class="fas fa-chevron-right" style="color: rgba(255,255,255,0.3);"></i>
                    </button>
                </div>
            </div>

            <!-- Redesigned Stats Grid -->
            <div class="stats-grid" id="statsGrid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px;">
                <!-- Total Candidates -->
                <div class="stat-card" style="background: rgba(13,11,46,0.5); border: 1px solid rgba(255,255,255,0.05); border-radius: 16px; padding: 20px; position: relative; overflow: hidden; display: flex; flex-direction: column; justify-content: space-between; min-height: 140px;">
                    <div style="display: flex; gap: 12px; align-items: flex-start;">
                        <div style="background: rgba(124,77,255,0.15); color: #b8aaff; width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 16px; flex-shrink: 0;"><i class="fas fa-user-friends"></i></div>
                        <div>
                            <div style="color: rgba(255,255,255,0.5); font-size: 11px; font-weight: 600; margin-bottom: 4px;">Total Candidates</div>
                            <div style="color: #fff; font-size: 24px; font-weight: 700;" id="totalCandidates">0</div>
                            <div style="color: rgba(255,255,255,0.4); font-size: 11px; margin-top: 4px;">All registered</div>
                        </div>
                    </div>
                    <div style="height: 20px; width: 100%; border-bottom: 2px solid #b8aaff; border-radius: 50% 50% 0 0 / 20px 20px 0 0; position: relative; margin-top: 16px;"><div style="position: absolute; bottom: -2px; left: 0; width: 100%; height: 2px; background: linear-gradient(90deg, transparent, #b8aaff, transparent);"></div></div>
                </div>

                <!-- Examinations -->
                <div class="stat-card" style="background: rgba(13,11,46,0.5); border: 1px solid rgba(255,255,255,0.05); border-radius: 16px; padding: 20px; position: relative; overflow: hidden; display: flex; flex-direction: column; justify-content: space-between; min-height: 140px;">
                    <div style="display: flex; gap: 12px; align-items: flex-start;">
                        <div style="background: rgba(81,207,102,0.15); color: #51cf66; width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 16px; flex-shrink: 0;"><i class="fas fa-calendar-check"></i></div>
                        <div>
                            <div style="color: rgba(255,255,255,0.5); font-size: 11px; font-weight: 600; margin-bottom: 4px;">Examinations</div>
                            <div style="color: #fff; font-size: 24px; font-weight: 700;" id="completedSessions">0</div>
                            <div style="color: rgba(255,255,255,0.4); font-size: 11px; margin-top: 4px;">Total conducted</div>
                        </div>
                    </div>
                    <div style="height: 20px; width: 100%; border-bottom: 2px solid #51cf66; border-radius: 50% 50% 0 0 / 20px 20px 0 0; position: relative; margin-top: 16px;"><div style="position: absolute; bottom: -2px; left: 0; width: 100%; height: 2px; background: linear-gradient(90deg, transparent, #51cf66, transparent);"></div></div>
                </div>

                <!-- Live Sessions -->
                <div class="stat-card" style="background: rgba(13,11,46,0.5); border: 1px solid rgba(255,255,255,0.05); border-radius: 16px; padding: 20px; position: relative; overflow: hidden; display: flex; flex-direction: column; justify-content: space-between; min-height: 140px;">
                    <div style="display: flex; gap: 12px; align-items: flex-start;">
                        <div style="background: rgba(77,171,247,0.15); color: #4dabf7; width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 16px; flex-shrink: 0;"><i class="fas fa-eye"></i></div>
                        <div>
                            <div style="color: rgba(255,255,255,0.5); font-size: 11px; font-weight: 600; margin-bottom: 4px;">Live Sessions</div>
                            <div style="color: #fff; font-size: 24px; font-weight: 700;" id="activeSessions">0</div>
                            <div style="color: rgba(255,255,255,0.4); font-size: 11px; margin-top: 4px;">Ongoing now</div>
                        </div>
                    </div>
                    <div style="height: 20px; width: 100%; border-bottom: 2px solid #4dabf7; border-radius: 50% 50% 0 0 / 20px 20px 0 0; position: relative; margin-top: 16px;"><div style="position: absolute; bottom: -2px; left: 0; width: 100%; height: 2px; background: linear-gradient(90deg, transparent, #4dabf7, transparent);"></div></div>
                </div>

                <!-- Suspicious Alerts -->
                <div class="stat-card" style="background: rgba(13,11,46,0.5); border: 1px solid rgba(255,255,255,0.05); border-radius: 16px; padding: 20px; position: relative; overflow: hidden; display: flex; flex-direction: column; justify-content: space-between; min-height: 140px;">
                    <div style="display: flex; gap: 12px; align-items: flex-start;">
                        <div style="background: rgba(252,196,25,0.15); color: #fcc419; width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 16px; flex-shrink: 0;"><i class="fas fa-shield-alt"></i></div>
                        <div>
                            <div style="color: rgba(255,255,255,0.5); font-size: 11px; font-weight: 600; margin-bottom: 4px;">Suspicious Alerts</div>
                            <div style="color: #fff; font-size: 24px; font-weight: 700;" id="totalSuspiciousEvents">0</div>
                            <div style="color: rgba(255,255,255,0.4); font-size: 11px; margin-top: 4px;">Requires attention</div>
                        </div>
                    </div>
                    <div style="height: 20px; width: 100%; border-bottom: 2px solid #fcc419; border-radius: 50% 50% 0 0 / 20px 20px 0 0; position: relative; margin-top: 16px;"><div style="position: absolute; bottom: -2px; left: 0; width: 100%; height: 2px; background: linear-gradient(90deg, transparent, #fcc419, transparent);"></div></div>
                </div>
                
                <!-- Reports Generated -->
                <div class="stat-card" style="background: rgba(13,11,46,0.5); border: 1px solid rgba(255,255,255,0.05); border-radius: 16px; padding: 20px; position: relative; overflow: hidden; display: flex; flex-direction: column; justify-content: space-between; min-height: 140px;">
                    <div style="display: flex; gap: 12px; align-items: flex-start;">
                        <div style="background: rgba(124,77,255,0.15); color: #b8aaff; width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 16px; flex-shrink: 0;"><i class="fas fa-file-alt"></i></div>
                        <div>
                            <div style="color: rgba(255,255,255,0.5); font-size: 11px; font-weight: 600; margin-bottom: 4px;">Reports Generated</div>
                            <div style="color: #fff; font-size: 24px; font-weight: 700;">36</div>
                            <div style="color: rgba(255,255,255,0.4); font-size: 11px; margin-top: 4px;">This month</div>
                        </div>
                    </div>
                    <div style="height: 20px; width: 100%; border-bottom: 2px solid #b8aaff; border-radius: 50% 50% 0 0 / 20px 20px 0 0; position: relative; margin-top: 16px;"><div style="position: absolute; bottom: -2px; left: 0; width: 100%; height: 2px; background: linear-gradient(90deg, transparent, #b8aaff, transparent);"></div></div>
                </div>

                <!-- System Health -->
                <div class="stat-card" style="background: rgba(13,11,46,0.5); border: 1px solid rgba(255,255,255,0.05); border-radius: 16px; padding: 20px; position: relative; overflow: hidden; display: flex; flex-direction: column; justify-content: space-between; min-height: 140px;">
                    <div style="display: flex; gap: 12px; align-items: flex-start;">
                        <div style="background: rgba(81,207,102,0.15); color: #51cf66; width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 16px; flex-shrink: 0;"><i class="fas fa-heartbeat"></i></div>
                        <div>
                            <div style="color: rgba(255,255,255,0.5); font-size: 11px; font-weight: 600; margin-bottom: 4px;">System Health</div>
                            <div style="color: #fff; font-size: 24px; font-weight: 700;">98%</div>
                            <div style="color: rgba(255,255,255,0.4); font-size: 11px; margin-top: 4px;">All systems active</div>
                        </div>
                    </div>
                    <div style="height: 20px; width: 100%; border-bottom: 2px solid #51cf66; border-radius: 50% 50% 0 0 / 20px 20px 0 0; position: relative; margin-top: 16px;"><div style="position: absolute; bottom: -2px; left: 0; width: 100%; height: 2px; background: linear-gradient(90deg, transparent, #51cf66, transparent);"></div></div>
                </div>
            </div>"""

old_header_regex = re.compile(
    r'        <!-- ===== PAGE: DASHBOARD \(unchanged\) ===== -->\n'
    r'        <div class="page active" id="page-dashboard">\n'
    r'            <h2><i class="fas fa-chart-pie" style="color:#7c4dff;margin-right:12px;"></i>Dashboard</h2>\n'
    r'            <div class="sub">Overview of all candidates and overall statistics</div>\n'
    r'            <div class="stats-grid" id="statsGrid">\n'
    r'                <div class="stat-card"><div class="label">Total Candidates</div><div class="value blue" id="totalCandidates">0</div></div>\n'
    r'                <div class="stat-card"><div class="label">Active Sessions</div><div class="value green" id="activeSessions">0</div></div>\n'
    r'                <div class="stat-card"><div class="label">Completed Sessions</div><div class="value purple" id="completedSessions">0</div></div>\n'
    r'                <div class="stat-card"><div class="label">Average Integrity Score</div><div class="value orange" id="avgIntegrity">0</div></div>\n'
    r'                <div class="stat-card"><div class="label">Total Suspicious Events</div><div class="value red" id="totalSuspiciousEvents">0</div></div>\n'
    r'            </div>'
)

new_content = old_header_regex.sub(new_header, content)

old_buttons_regex = re.compile(
    r'            <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">\n'
    r'                <button class="btn-health" id="systemHealthBtn"><i class="fas fa-heartbeat"></i> System Health</button>\n'
    r'                                <button class="btn-export" id="exportAllCsv"><i class="fas fa-file-csv"></i> Export Reports</button>\n'
    r'\n'
    r'            </div>'
)

new_content = old_buttons_regex.sub('', new_content)

allEvents_regex = re.compile(
    r'                        allStudents = data\.students \|\| \[\];\n'
    r'                        allEvents = data\.events \|\| \[\];'
)
new_allEvents = """                        allStudents = data.students || [];
                        allEvents = data.events || [];
                        // Expose globally for bottom panels
                        window._allEvents = allEvents;"""
new_content = allEvents_regex.sub(new_allEvents, new_content)

bottom_panels_regex = re.compile(
    r'            if \(recentList && typeof allEvents !== \'undefined\'\) {\n'
    r'                const suspicious = allEvents'
)
new_bottom_panels = """            if (recentList && typeof window._allEvents !== 'undefined') {
                const suspicious = window._allEvents"""
new_content = bottom_panels_regex.sub(new_bottom_panels, new_content)

with open('frontend/templates/admin_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(new_content)
    
print("Updated HTML.")
