import re

with open('frontend/templates/admin_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. CSS Updates
css_updates = """
        /* NEW DASHBOARD CARDS CSS */
        .bottom-panels {
            display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 24px; margin-top: 24px;
        }
        .bottom-panel {
            background: linear-gradient(180deg, rgba(30, 25, 75, 0.4) 0%, rgba(13, 11, 46, 0.6) 100%);
            border: 1px solid rgba(124, 77, 255, 0.3);
            border-radius: 16px; 
            padding: 24px; 
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            animation: fadeSlideUp 0.6s ease forwards;
            opacity: 0;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }
        .bottom-panel:hover {
            border-color: rgba(124,77,255,0.6);
            transform: translateY(-4px);
            box-shadow: 0 12px 40px rgba(124,77,255,0.2);
        }
        .bottom-panels .bottom-panel:nth-child(1) { animation-delay: 0.1s; }
        .bottom-panels .bottom-panel:nth-child(2) { animation-delay: 0.2s; }
        .bottom-panels .bottom-panel:nth-child(3) { animation-delay: 0.3s; }
        .bottom-panels .bottom-panel:nth-child(4) { animation-delay: 0.4s; }
        .bottom-panels .bottom-panel:nth-child(5) { animation-delay: 0.5s; }
        .bottom-panels .bottom-panel:nth-child(6) { animation-delay: 0.6s; }

        .bottom-panel h3 {
            font-size: 16px; font-weight: 600; color: #fff;
            margin-bottom: 24px; display: flex; align-items: center; gap: 10px;
        }
        .bottom-panel h3 i { color: #b8aaff; font-size: 18px; }
        .bottom-panel h3 .view-all {
            margin-left: auto; font-size: 11px; color: rgba(255,255,255,0.6);
            cursor: pointer; font-weight: 500;
            background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
            padding: 6px 12px; border-radius: 20px; transition: 0.2s;
        }
        .bottom-panel h3 .view-all:hover { color: #fff; background: rgba(255,255,255,0.1); border-color: rgba(255,255,255,0.2); }

        /* Row Items Container */
        .card-row-list { display: flex; flex-direction: column; gap: 12px; flex: 1; }

        /* Timeline Specific */
        .timeline-container { position: relative; padding-left: 100px; display: flex; flex-direction: column; gap: 20px; }
        .timeline-container::before {
            content: ''; position: absolute; left: 69px; top: 10px; bottom: 10px;
            width: 2px; background: rgba(255,255,255,0.05); z-index: 0;
        }
        .timeline-item { position: relative; display: flex; align-items: center; justify-content: space-between; z-index: 1; }
        .timeline-time { position: absolute; left: -100px; width: 60px; text-align: right; color: rgba(255,255,255,0.5); font-size: 12px; }
        .timeline-icon { 
            position: absolute; left: -39px; width: 18px; height: 18px; border-radius: 50%;
            background: #1a1545; border: 2px solid #b8aaff; display: flex; align-items: center; justify-content: center;
        }
        .timeline-icon i { font-size: 8px; color: #b8aaff; }
        .timeline-icon.green { border-color: #51cf66; } .timeline-icon.green i { color: #51cf66; }
        .timeline-icon.blue { border-color: #4dabf7; } .timeline-icon.blue i { color: #4dabf7; }
        .timeline-content { color: #fff; font-size: 13px; font-weight: 500; }
        .timeline-pill { font-size: 11px; padding: 4px 10px; border-radius: 6px; font-weight: 600; }
        .timeline-pill.info { background: rgba(77,171,247,0.15); color: #4dabf7; }
        .timeline-pill.low { background: rgba(81,207,102,0.15); color: #51cf66; }

        /* Generic Row */
        .card-row {
            display: flex; align-items: center; justify-content: space-between;
            background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.03);
            border-radius: 12px; padding: 12px 16px; transition: 0.2s;
        }
        .card-row:hover { background: rgba(0,0,0,0.3); border-color: rgba(255,255,255,0.08); }
        .card-row-left { display: flex; align-items: center; gap: 16px; }
        
        .sq-icon { width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 16px; }
        .sq-icon.green { background: rgba(81,207,102,0.15); color: #51cf66; }
        .sq-icon.blue { background: rgba(77,171,247,0.15); color: #4dabf7; }
        .sq-icon.yellow { background: rgba(252,196,25,0.15); color: #fcc419; }
        
        .row-title { font-size: 14px; font-weight: 600; color: #fff; margin-bottom: 2px; }
        .row-sub { font-size: 12px; color: rgba(255,255,255,0.5); }
        
        .row-right-text { font-size: 13px; font-weight: 600; }
        .row-right-text.green { color: #51cf66; }
        .row-right-text.blue { color: #4dabf7; }
        .row-right-text.yellow { color: #fcc419; }

        .btn-icon-purple { 
            background: rgba(124,77,255,0.15); color: #b8aaff; border: none; 
            width: 32px; height: 32px; border-radius: 8px; cursor: pointer; transition: 0.2s;
        }
        .btn-icon-purple:hover { background: rgba(124,77,255,0.3); color: #fff; }

        .rank-box { padding: 4px 8px; border-radius: 6px; font-size: 12px; font-weight: 700; }
        .rank-box.r1 { background: rgba(255,107,107,0.15); color: #ff6b6b; }
        .rank-box.r2 { background: rgba(255,107,107,0.1); color: #ff6b6b; }
        .rank-box.r3 { background: rgba(252,196,25,0.15); color: #fcc419; }
        
        .avatar-img { width: 32px; height: 32px; border-radius: 50%; object-fit: cover; border: 1px solid rgba(255,255,255,0.1); }
"""

css_start = content.find('        /* ===== BOTTOM PANELS (Quick Actions etc.) ===== */')
css_end = content.find('        .quick-actions-grid {')
if css_start != -1 and css_end != -1:
    content = content[:css_start] + css_updates + content[css_end:]
else:
    print("CSS section not found!")

new_panels_html = """
        <!-- ===== BOTTOM PANELS (Quick Actions, Recent Events, Timeline) ===== -->
        <div class="bottom-panels" id="bottomPanels">
            
            <!-- 1. Recent Suspicious Events -->
            <div class="bottom-panel" id="recentEventsPanel">
                <h3><i class="fas fa-shield-alt"></i> Recent Suspicious Events <span class="view-all" onclick="document.querySelector('[data-page=alerts]').click()">View all →</span></h3>
                <div class="card-row-list" id="recentEventsList" style="justify-content: center; align-items: center;">
                    <div style="text-align: center; margin-top: 20px;">
                        <div style="font-size: 13px; color: rgba(255,255,255,0.5);">Loading events...</div>
                    </div>
                </div>
            </div>

            <!-- 2. Today's Activity Timeline -->
            <div class="bottom-panel" id="timelinePanel">
                <h3><i class="fas fa-clock"></i> Today's Activity Timeline <span class="view-all" onclick="document.querySelector('[data-page=logs]').click()">View all →</span></h3>
                <div class="timeline-container" id="timelineList">
                    <!-- Populated by JS -->
                </div>
            </div>

            <!-- 3. System Health -->
            <div class="bottom-panel">
                <h3><i class="fas fa-wave-square"></i> System Health & AI Load</h3>
                <div class="card-row-list">
                    <div class="card-row">
                        <div class="card-row-left">
                            <div class="sq-icon green"><i class="fas fa-heartbeat"></i></div>
                            <div>
                                <div class="row-sub">Status</div>
                                <div class="row-title">All Systems Operational</div>
                            </div>
                        </div>
                        <div class="timeline-pill low" style="background: rgba(81,207,102,0.1); border: 1px solid rgba(81,207,102,0.2);">Healthy</div>
                    </div>
                    <div class="card-row">
                        <div class="card-row-left">
                            <div class="sq-icon blue"><i class="fas fa-video"></i></div>
                            <div>
                                <div class="row-sub">WebRTC</div>
                                <div class="row-title">Active Video Channels</div>
                            </div>
                        </div>
                        <div class="row-right-text blue">24 Connected</div>
                    </div>
                    <div class="card-row">
                        <div class="card-row-left">
                            <div class="sq-icon yellow"><i class="fas fa-microchip"></i></div>
                            <div>
                                <div class="row-sub">AI Load</div>
                                <div class="row-title">Vision Model Latency</div>
                            </div>
                        </div>
                        <div class="row-right-text yellow">18ms</div>
                    </div>
                </div>
            </div>

            <!-- 4. Active Exams -->
            <div class="bottom-panel">
                <h3><i class="fas fa-file-signature"></i> Active Exams Overview <span class="view-all">View all →</span></h3>
                <div class="card-row-list">
                    <div class="card-row">
                        <div class="card-row-left" style="gap:20px;">
                            <div style="display:flex;align-items:center;gap:6px;font-size:11px;font-weight:700;color:#51cf66;width:40px;"><i class="fas fa-circle" style="font-size:8px;"></i> LIVE</div>
                            <div>
                                <div class="row-title">CS101 Final Exam</div>
                                <div class="row-sub" style="color:#4dabf7;">45m remaining</div>
                            </div>
                        </div>
                        <button class="btn-icon-purple"><i class="fas fa-user-friends"></i></button>
                    </div>
                    <div class="card-row">
                        <div class="card-row-left" style="gap:20px;">
                            <div style="display:flex;align-items:center;gap:6px;font-size:11px;font-weight:700;color:#4dabf7;width:40px;"><i class="fas fa-circle" style="font-size:8px;"></i> LIVE</div>
                            <div>
                                <div class="row-title">Math 202 Midterm</div>
                                <div class="row-sub" style="color:#4dabf7;">1h 10m remaining</div>
                            </div>
                        </div>
                        <button class="btn-icon-purple"><i class="fas fa-user-friends"></i></button>
                    </div>
                    <div class="card-row">
                        <div class="card-row-left" style="gap:20px;">
                            <div style="display:flex;align-items:center;gap:6px;font-size:11px;font-weight:700;color:#fcc419;width:40px;"><i class="fas fa-circle" style="font-size:8px;"></i> SOON</div>
                            <div>
                                <div class="row-title">Physics 301</div>
                                <div class="row-sub" style="color:#fcc419;">Starts in 15m</div>
                            </div>
                        </div>
                        <button class="btn-icon-purple"><i class="fas fa-user-friends"></i></button>
                    </div>
                </div>
            </div>

            <!-- 5. Top Flagged Candidates -->
            <div class="bottom-panel">
                <h3><i class="fas fa-flag"></i> Top Flagged Candidates <span class="view-all">View all →</span></h3>
                <div class="card-row-list">
                    <div class="card-row">
                        <div class="card-row-left">
                            <div class="rank-box r1">#1</div>
                            <img src="https://ui-avatars.com/api/?name=John+Doe&background=2a2359&color=fff" class="avatar-img" />
                            <div>
                                <div class="row-title">John Doe</div>
                                <div class="row-sub" style="color:#ff6b6b;">5 Alerts</div>
                            </div>
                        </div>
                        <i class="fas fa-chevron-right" style="color:rgba(255,255,255,0.3);font-size:12px;"></i>
                    </div>
                    <div class="card-row">
                        <div class="card-row-left">
                            <div class="rank-box r2">#2</div>
                            <img src="https://ui-avatars.com/api/?name=Jane+Smith&background=2a2359&color=fff" class="avatar-img" />
                            <div>
                                <div class="row-title">Jane Smith</div>
                                <div class="row-sub" style="color:#ff6b6b;">3 Alerts</div>
                            </div>
                        </div>
                        <i class="fas fa-chevron-right" style="color:rgba(255,255,255,0.3);font-size:12px;"></i>
                    </div>
                    <div class="card-row">
                        <div class="card-row-left">
                            <div class="rank-box r3">#3</div>
                            <img src="https://ui-avatars.com/api/?name=Alex+Johnson&background=2a2359&color=fff" class="avatar-img" />
                            <div>
                                <div class="row-title">Alex Johnson</div>
                                <div class="row-sub" style="color:#fcc419;">2 Alerts</div>
                            </div>
                        </div>
                        <i class="fas fa-chevron-right" style="color:rgba(255,255,255,0.3);font-size:12px;"></i>
                    </div>
                </div>
            </div>

            <!-- 6. Help Requests -->
            <div class="bottom-panel">
                <h3><i class="fas fa-headset"></i> Live Help Requests <span class="view-all">View all →</span></h3>
                <div class="card-row-list">
                    <div class="card-row">
                        <div class="card-row-left" style="gap:20px;">
                            <div style="display:flex;align-items:center;gap:6px;font-size:11px;color:rgba(255,255,255,0.5);width:55px;"><i class="fas fa-circle" style="font-size:8px;color:#ff6b6b;"></i> 2m ago</div>
                            <div class="row-title" style="font-size:13px;">Camera disconnect issue</div>
                        </div>
                        <div class="timeline-pill" style="color:#ff6b6b;background:rgba(255,107,107,0.15);">Pending</div>
                    </div>
                    <div class="card-row">
                        <div class="card-row-left" style="gap:20px;">
                            <div style="display:flex;align-items:center;gap:6px;font-size:11px;color:rgba(255,255,255,0.5);width:55px;"><i class="fas fa-circle" style="font-size:8px;color:#fcc419;"></i> 8m ago</div>
                            <div class="row-title" style="font-size:13px;">Screen sharing permission</div>
                        </div>
                        <div class="timeline-pill" style="color:#fcc419;background:rgba(252,196,25,0.15);">Assigned</div>
                    </div>
                    <div class="card-row">
                        <div class="card-row-left" style="gap:20px;">
                            <div style="display:flex;align-items:center;gap:6px;font-size:11px;color:rgba(255,255,255,0.5);width:55px;"><i class="fas fa-circle" style="font-size:8px;color:#51cf66;"></i> 15m ago</div>
                            <div class="row-title" style="font-size:13px;">Login credential check</div>
                        </div>
                        <div class="timeline-pill" style="color:#51cf66;background:rgba(81,207,102,0.15);">Resolved</div>
                    </div>
                </div>
            </div>
        </div>
"""

start_idx = content.find('        <!-- ===== BOTTOM PANELS (Quick Actions, Recent Events, Timeline) ===== -->')
end_idx = content.find('        <!-- ===== PAGE: LIVE MONITORING ===== -->')
if start_idx != -1 and end_idx != -1:
    content = content[:start_idx] + new_panels_html + '\n' + content[end_idx:]
else:
    print("HTML section not found!")

# JS Updates
js_new = """            if (recentList && typeof window._allEvents !== 'undefined') {
                const checkToday = function(ts) {
                    const date = new Date(ts);
                    const today = new Date();
                    return date.getFullYear() === today.getFullYear() &&
                           date.getMonth() === today.getMonth() &&
                           date.getDate() === today.getDate();
                };

                const suspicious = window._allEvents
                    .filter(e => checkToday(e.timestamp) && (e.deducted > 3 || e.type === 'Multiple Faces' || e.type === 'Face Absence'))
                    .sort((a,b) => new Date(b.timestamp) - new Date(a.timestamp))
                    .slice(0, 3);

                let html = '';
                if (suspicious.length > 0) {
                    html += '<div class="card-row-list" style="justify-content: flex-start; width: 100%;">';
                    suspicious.forEach(e => {
                        const name = e.student_name || e.student_id || 'Unknown';
                        const type = e.type || 'Event';
                        const isHigh = e.deducted > 7 || type === 'Multiple Faces';
                        const timeStr = new Date(e.timestamp).toLocaleTimeString('en-US', {hour:'2-digit', minute:'2-digit'});
                        html += `
                            <div class="card-row" style="width: 100%;">
                                <div class="card-row-left" style="gap:20px;">
                                    <div style="display:flex;align-items:center;gap:6px;font-size:11px;color:rgba(255,255,255,0.5);width:60px;"><i class="fas fa-circle" style="font-size:8px;color:${isHigh ? '#ff6b6b' : '#fcc419'};"></i> ${timeStr}</div>
                                    <div>
                                        <div class="row-title" style="font-size:13px;">${name}</div>
                                        <div class="row-sub" style="color:${isHigh ? '#ff6b6b' : '#fcc419'};">${type}</div>
                                    </div>
                                </div>
                                <button class="btn-icon-purple"><i class="fas fa-eye"></i></button>
                            </div>
                        `;
                    });
                    html += '</div>';
                    recentList.style.alignItems = 'stretch';
                    recentList.innerHTML = html;
                } else {
                    recentList.style.alignItems = 'center';
                    recentList.innerHTML = `
                        <div style="text-align: center; margin-top: 20px;">
                            <div style="position: relative; display: inline-block; margin-bottom: 24px;">
                                <div style="width: 120px; height: 30px; background: radial-gradient(ellipse at center, rgba(124,77,255,0.4) 0%, transparent 70%); position: absolute; bottom: -15px; left: 50%; transform: translateX(-50%); border-radius: 50%;"></div>
                                <i class="fas fa-shield-alt" style="font-size: 80px; color: #7c4dff; filter: drop-shadow(0 10px 20px rgba(124,77,255,0.4)); background: linear-gradient(135deg, #b8aaff, #7c4dff); -webkit-background-clip: text; -webkit-text-fill-color: transparent;"></i>
                            </div>
                            <div style="font-size: 16px; font-weight: 600; color: #fff; margin-bottom: 8px;">No recent suspicious events</div>
                            <div style="font-size: 13px; color: #51cf66; display: flex; align-items: center; justify-content: center; gap: 6px;"><i class="fas fa-check-circle"></i> All clear! No suspicious activity detected.</div>
                        </div>
                    `;
                }
            }

            if (timelineList) {
                const now = new Date();
                const entries = [
                    {min: 0, text: 'Dashboard refreshed', level: 'info'},
                    {min: 5, text: 'System health checked', level: 'low'},
                    {min: 12, text: 'Monitoring session active', level: 'info'},
                    {min: 20, text: 'Data export available', level: 'low'},
                ];
                let html = '';
                entries.forEach(e => {
                    const t = new Date(now - e.min * 60000);
                    const ts = t.toLocaleTimeString('en-US', {hour:'2-digit', minute:'2-digit'});
                    
                    let iconClass = e.level === 'low' ? 'green' : 'blue';
                    let iconType = e.level === 'low' ? 'fa-check' : 'fa-bolt';
                    let pillClass = e.level === 'low' ? 'low' : 'info';
                    let pillText = e.level === 'low' ? 'Low' : 'Info';
                    
                    html += `
                        <div class="timeline-item">
                            <div class="timeline-time">${ts}</div>
                            <div class="timeline-icon ${iconClass}"><i class="fas ${iconType}"></i></div>
                            <div class="timeline-content">${e.text}</div>
                            <div class="timeline-pill ${pillClass}">${pillText}</div>
                        </div>
                    `;
                });
                timelineList.innerHTML = html;
            }
"""

js_start = content.find("            if (recentList && typeof window._allEvents !== 'undefined') {")
js_end = content.find("        };", js_start)

if js_start != -1 and js_end != -1:
    content = content[:js_start] + js_new + content[js_end:]
else:
    print("JS section not found!")

with open('frontend/templates/admin_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated completely")
