
        (function() {
            'use strict';

            // ----- DOM refs (existing) -----
            const userNameDisplay = document.getElementById('userNameDisplay');
            const candId = document.getElementById('candId');
            const candName = document.getElementById('candName');
            const candSession = document.getElementById('candSession');
            const candScore = document.getElementById('candScore');
            const candRemark = document.getElementById('candRemark');
            const faceRatioEl = document.getElementById('faceRatio');
            const sessionDurationEl = document.getElementById('sessionDuration');
            const totalDeductedEl = document.getElementById('totalDeducted');
            const statsDurationEl = document.getElementById('statsDuration');
            const eventLogBody = document.getElementById('eventLogBody');
            const faceAbsenceCountEl = document.getElementById('faceAbsenceCount');
            const multipleFacesCountEl = document.getElementById('multipleFacesCount');
            const totalSuspiciousEl = document.getElementById('totalSuspicious');
            const scoreValue = document.getElementById('scoreValue');
            const scoreBar = document.getElementById('scoreBar');
            const riskLabel = document.getElementById('riskLabel');
            const startBtn = document.getElementById('startExamBtn');
            const togglePauseBtn = document.getElementById('togglePauseBtn');
            const endBtn = document.getElementById('endExamBtn');
            const dropdownToggle = document.getElementById('dropdownToggle');
            const dropdownMenu = document.getElementById('dropdownMenu');
            const generateReportBtn = document.getElementById('generateReportBtn');
            const logoutBtn = document.getElementById('logoutBtn');
            const toast = document.getElementById('toast');
            const toastMsg = document.getElementById('toastMsg');
            const pieCanvas = document.getElementById('pieChart');
                        const timeline = document.getElementById('timeline');

            // ----- Live network status refs -----
            const networkModal = document.getElementById('networkModal');
            const networkStatusButtons = [
                document.getElementById('connectionStatusButton'),
                document.getElementById('connectionStatusButtonTop')
            ].filter(Boolean);
            const networkHeaderState = document.getElementById('headerConnectionState');
            const networkState = document.getElementById('connectionState');
            const networkModalIcon = document.getElementById('networkModalIcon');
            const networkModalTitle = document.getElementById('networkModalTitle');
            const networkHeaderClock = document.getElementById('networkHeaderClock');
            const networkModalDescription = document.getElementById('networkModalDescription');
            const networkRefreshButton = document.getElementById('networkRefreshButton');
            const networkCloseButton = document.getElementById('networkCloseButton');
            const networkCloseButtonSecondary = document.getElementById('networkCloseButtonSecondary');
            const networkLastChecked = document.getElementById('networkLastChecked');
            const networkSpeedCanvas = document.getElementById('networkSpeedChart');
            const networkSpeedValue = document.getElementById('networkSpeedValue');
            const offlineCacheCard = document.getElementById('offlineCacheCard');
            const offlineCacheState = document.getElementById('offlineCacheState');
            const offlineCacheDetail = document.getElementById('offlineCacheDetail');
            const offlineCacheBadge = document.getElementById('offlineCacheBadge');
            const profileModal = document.getElementById('profileModal');
            const profileButton = document.getElementById('profileButton');
            const profileCloseButton = document.getElementById('profileCloseButton');
            const profileDoneButton = document.getElementById('profileDoneButton');
            const profileAvatarImage = document.getElementById('profileAvatarImage');
            const profileTriggerAvatar = document.getElementById('profileTriggerAvatar');
            const openSettingsButton = document.getElementById('openSettingsButton');
            const settingsModal = document.getElementById('settingsModal');
            const settingsForm = document.getElementById('settingsForm');
            const settingsName = document.getElementById('settingsName');
            const settingsEmail = document.getElementById('settingsEmail');
            const settingsStudentId = document.getElementById('settingsStudentId');
            const settingsAvatarInput = document.getElementById('settingsAvatarInput');
            const settingsAvatarPreview = document.getElementById('settingsAvatarPreview');
            const settingsFormMessage = document.getElementById('settingsFormMessage');
            const settingsSaveButton = document.getElementById('settingsSaveButton');
            const settingsCloseButton = document.getElementById('settingsCloseButton');
            const settingsCancelButton = document.getElementById('settingsCancelButton');
            const DEFAULT_PROFILE_IMAGE = "{{ url_for('static', filename='student-profile-default.png') }}";
            let networkCheckInFlight = false;
            let networkCheckComplete = false;

            // ----- Wizard DOM refs -----

            const wizardOverlay = document.getElementById('wizardOverlay');
            const wizardVideo = document.getElementById('wizardVideo');
            const wizardCanvas = document.getElementById('wizardOverlayCanvas');
            const wCtx = wizardCanvas.getContext('2d');
            const captureBtn = document.getElementById('captureBtn');
            const submitPhotoBtn = document.getElementById('submitPhotoBtn');
            const nextStep1Btn = document.getElementById('nextStep1Btn');
            const nextStep2Btn = document.getElementById('nextStep2Btn');
            const startExamFinalBtn = document.getElementById('startExamFinalBtn');
            const consentCheck = document.getElementById('consentCheck');
            const capturedPreview = document.getElementById('capturedPreview');
            const capturedImg = document.getElementById('capturedImg');
            const attemptDisplay = document.getElementById('attemptDisplay');
            const checkList = document.getElementById('checkList');
            const step1 = document.getElementById('step1');
            const step2 = document.getElementById('step2');
            const step3 = document.getElementById('step3');
            const dot1 = document.getElementById('dot1');
            const dot2 = document.getElementById('dot2');
            const dot3 = document.getElementById('dot3');
            const step1Label = document.getElementById('step1Label');
            const checksVideo = document.getElementById('checksVideo');
            const checksOverlayCanvas = document.getElementById('checksOverlayCanvas');
            const verifyFaceBtn = document.getElementById('verifyFaceBtn');
            const faceAttemptDisplay = document.getElementById('faceAttemptDisplay');
            const verifyArea = document.getElementById('verifyArea');
            const verifyStatus = document.getElementById('verifyStatus');

            // ----- State -----
            let currentUser = null;
            let stats = null;
            let allEvents = [];
            let sessionEvents = [];
            let examRunning = false;
            let examPaused = false;
            let cameraStream = null;
            let wizardStream = null;
            let checksStream = null;
            let timerInterval = null;
            let faceDetectionInterval = null;
            let sessionStartTime = null;
            let totalPausedDuration = 0;
            let elapsedSeconds = 0;
            let faceNotDetectedLogged = false;
            let faceNotDetectedStart = null;
            let faceAbsenceTriggered = false;
            const DETECTION_INTERVAL = 2000;
            let referenceExists = false;
            let capturedImageData = null;
            let captureAttempts = 0;
            const MAX_ATTEMPTS = 3;
            let currentStep = 1;
            let faceMatchAttempts = 0;
            let faceVerified = false;
            let checksPassed = false;
            let autoChecksDone = false;

            // ----- Helper functions (same) -----
            function apiFetch(url, options = {}) {
                return fetch(url, {
                    ...options,
                    credentials: 'include',
                    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) }
                });
            }

            function showToast(msg, type = 'success') {
                toast.className = 'toast ' + type;
                toastMsg.textContent = msg;
                const icon = toast.querySelector('i');
                icon.className = type === 'success' ? 'fas fa-check-circle' : 'fas fa-exclamation-circle';
                toast.classList.add('show');
                clearTimeout(toast._timer);
                toast._timer = setTimeout(() => toast.classList.remove('show'), 3500);
            }

            function formatTime(sec) {
                const m = Math.floor(sec / 60);
                const s = Math.floor(sec % 60);
                return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
            }

            // ----- Filter events -----
            function filterSessionEvents(events, startedAt, endedAt) {
                if (!startedAt) return [];
                const start = new Date(startedAt).getTime();
                const end = endedAt ? new Date(endedAt).getTime() : Date.now();
                return events.filter(ev => {
                    const ts = new Date(ev.timestamp).getTime();
                    return ts >= start && ts <= end;
                });
            }

            // ----- Render timeline (horizontal) -----
            function renderTimeline(eventsArray) {
    const timeline = document.getElementById('timeline');
    if (!eventsArray || eventsArray.length === 0) {
        timeline.innerHTML = '<p style="color:rgba(255,255,255,0.3);padding:20px;width:100%;text-align:center;">No events to display</p>';
        return;
    }

    // We need session start and end timestamps from stats
    const startedAt = stats ? stats.started_at : null;
    const endedAt = stats ? stats.ended_at : null;
    let startTime = startedAt ? new Date(startedAt).getTime() : null;
    let endTime = endedAt ? new Date(endedAt).getTime() : null;
    if (!startTime && eventsArray.length > 0) {
        // fallback: use first event timestamp as start
        startTime = new Date(eventsArray[0].timestamp).getTime();
    }
    if (!endTime && eventsArray.length > 0) {
        endTime = new Date(eventsArray[eventsArray.length-1].timestamp).getTime();
    }
    if (!startTime || !endTime) {
        timeline.innerHTML = '<p style="color:rgba(255,255,255,0.3);padding:20px;width:100%;text-align:center;">Insufficient data for timeline</p>';
        return;
    }

    const duration = endTime - startTime;
    if (duration <= 0) {
        timeline.innerHTML = '<p style="color:rgba(255,255,255,0.3);padding:20px;width:100%;text-align:center;">No valid time range</p>';
        return;
    }

    // Sort events by timestamp ascending
    const sorted = [...eventsArray].sort((a,b) => new Date(a.timestamp) - new Date(b.timestamp));

    let html = '';

    // Helper to format time
    function formatTimeDisplay(ts) {
        const d = new Date(ts);
        return d.toTimeString().slice(0,8); // HH:MM:SS
    }

    // Add Start marker (if we have started_at)
    if (startedAt) {
        const startTs = new Date(startedAt).getTime();
        html += `
            <div class="timeline-item start">
                <div class="event-time time-start">${formatTimeDisplay(startTs)}</div>
                <div class="timeline-dot"></div>
                <div class="event-type type-start">Start</div>
                <div class="event-deduction" style="color: rgba(255,255,255,0.4);">Session started</div>
            </div>
        `;
    }

    // Add event dots
    sorted.forEach((ev) => {
        const evTs = new Date(ev.timestamp).getTime();
        const isSuspicious = ev.deducted > 0;
        const cls = isSuspicious ? 'timeline-item suspicious' : 'timeline-item';
        // map event type to short label
        let label = ev.type;
        if (label === 'Face Absence') label = 'Face Absence';
        else if (label === 'Multiple Faces') label = 'Multiple Face';
        else if (label === 'Browser Focus Loss') label = 'Browser Focus Loss';
        else if (label === 'Tab Switching') label = 'Tab Switching';
        else if (label === 'Face Not Detected') label = 'Face Not Detected';
        else label = ev.type;

        html += `
            <div class="${cls}">
                <div class="event-time">${formatTimeDisplay(evTs)}</div>
                <div class="timeline-dot"></div>
                <div class="event-type">${label}</div>
                ${ev.deducted ? `<div class="event-deduction">-${ev.deducted} points</div>` : ''}
            </div>
        `;
    });

    // Add End marker
    if (endedAt) {
        const endTs = new Date(endedAt).getTime();
        html += `
            <div class="timeline-item end">
                <div class="event-time time-end">${formatTimeDisplay(endTs)}</div>
                <div class="timeline-dot"></div>
                <div class="event-type type-end">End</div>
                <div class="event-deduction" style="color: rgba(255,255,255,0.4);">Session ended</div>
            </div>
        `;
    }

    timeline.innerHTML = html;
}

                        // ----- Candidate profile popup -----
            function getShortDisplayName(name) {
                const normalized = String(name || '').trim();
                if (!normalized) return 'User';
                const firstName = normalized.split(/\s+/)[0];
                return firstName.length > 16 ? firstName.slice(0, 16) + '…' : firstName;
            }

            function calculateAge(dateOfBirth) {
                if (!dateOfBirth) return null;
                const birthDate = new Date(dateOfBirth);
                if (Number.isNaN(birthDate.getTime())) return null;
                const today = new Date();
                let age = today.getFullYear() - birthDate.getFullYear();
                const beforeBirthday = today.getMonth() < birthDate.getMonth() || (today.getMonth() === birthDate.getMonth() && today.getDate() < birthDate.getDate());
                if (beforeBirthday) age -= 1;
                return age >= 0 ? age : null;
            }

            function formatProfileDate(value) {
                if (!value) return 'Not provided';
                const date = new Date(value);
                return Number.isNaN(date.getTime()) ? String(value) : date.toLocaleDateString([], { year: 'numeric', month: 'short', day: 'numeric' });
            }

            function renderProfile(user, dashboardData) {
                if (!user) return;
                const age = user.age ?? calculateAge(user.date_of_birth || user.birth_date);
                const avatarUrl = user.profile_image ? '/api/profile/avatar/' + encodeURIComponent(user.id) + '?v=' + Date.now() : DEFAULT_PROFILE_IMAGE;
                if (profileAvatarImage) profileAvatarImage.src = avatarUrl;
                if (profileTriggerAvatar) profileTriggerAvatar.src = avatarUrl;
                if (settingsAvatarPreview) settingsAvatarPreview.src = avatarUrl;

                const safeSetText = (id, text) => {
                    const el = document.getElementById(id);
                    if (el) el.textContent = text;
                };

                safeSetText('profileName', user.name || 'Candidate');
                safeSetText('profileRoleLabel', user.role === 'admin' ? 'Administrator account' : 'Candidate account');
                safeSetText('profileRole', user.role ? user.role.charAt(0).toUpperCase() + user.role.slice(1) : 'Candidate');
                safeSetText('profileStudentId', user.student_id || 'Not provided');
                safeSetText('profileAge', age !== null && age !== undefined ? `${age} years` : 'Not provided');
                safeSetText('profileEmail', user.email || 'Not provided');
                safeSetText('profileSessionId', user.session_id || 'Not provided');
                safeSetText('profileAccountId', user.id ?? 'Not provided');
                safeSetText('profileCreatedAt', formatProfileDate(user.created_at));
                
                const score = dashboardData && dashboardData.integrity_score !== undefined ? dashboardData.integrity_score : 100;
                safeSetText('profileIntegrityScore', `${score} / 100`);
                safeSetText('profileStatus', 'Account active');
                safeSetText('profileNoteText', age !== null && age !== undefined ? 'Profile information is loaded from your authenticated account and current examination session.' : 'Age is not stored for this account. Other available account and examination details are shown above.');

                // Fallback for new redesign classes if needed
                document.querySelectorAll('.profileNameDisplay').forEach(el => el.textContent = user.name || 'Candidate');
                safeSetText('profileIntegrityScoreNum', score);
                const fillEl = document.getElementById('profileIntegrityFill');
                if (fillEl) fillEl.style.width = score + '%';
            }

            function closeProfileModal() {
                profileModal.classList.remove('is-open');
            }

            function openSettingsModal() {
                if (!currentUser) return;
                settingsName.value = currentUser.name || '';
                settingsEmail.value = currentUser.email || '';
                settingsStudentId.value = currentUser.student_id || '';
                settingsFormMessage.textContent = '';
                settingsFormMessage.classList.remove('success');
                settingsAvatarInput.value = '';
                settingsAvatarPreview.src = profileAvatarImage.src;
                closeProfileModal();
                settingsModal.classList.add('is-open');
            }

            function closeSettingsModal() {
                settingsModal.classList.remove('is-open');
            }

            function showSettingsMessage(message, success = false) {
                settingsFormMessage.textContent = message;
                settingsFormMessage.classList.toggle('success', success);
            }

            function setupProfileModal() {
                profileButton.addEventListener('click', () => profileModal.classList.add('is-open'));
                profileCloseButton.addEventListener('click', closeProfileModal);
                profileDoneButton.addEventListener('click', closeProfileModal);
                openSettingsButton.addEventListener('click', openSettingsModal);
                settingsCloseButton.addEventListener('click', closeSettingsModal);
                settingsCancelButton.addEventListener('click', closeSettingsModal);
                profileModal.addEventListener('click', event => { if (event.target === profileModal) closeProfileModal(); });
                settingsModal.addEventListener('click', event => { if (event.target === settingsModal) closeSettingsModal(); });
                settingsAvatarInput.addEventListener('change', () => {
                    const file = settingsAvatarInput.files && settingsAvatarInput.files[0];
                    if (file) settingsAvatarPreview.src = URL.createObjectURL(file);
                });
                settingsForm.addEventListener('submit', saveProfileSettings);
                document.addEventListener('keydown', event => {
                    if (event.key === 'Escape') { closeProfileModal(); closeSettingsModal(); }
                });
            }

            async function saveProfileSettings(event) {
                event.preventDefault();
                if (!currentUser) return;
                const name = settingsName.value.trim();
                const email = settingsEmail.value.trim().toLowerCase();
                const studentId = settingsStudentId.value.trim();
                if (!name || !email) {
                    showSettingsMessage('Name and email are required.');
                    return;
                }
                settingsSaveButton.disabled = true;
                settingsSaveButton.textContent = 'Saving...';
                showSettingsMessage('');
                try {
                    const profileResponse = await apiFetch('/api/profile', {
                        method: 'PUT',
                        body: JSON.stringify({ name, email, student_id: studentId })
                    });
                    const profileData = await profileResponse.json();
                    if (!profileResponse.ok) throw new Error(profileData.error || 'Unable to update profile');
                    currentUser = profileData.user;

                    const imageFile = settingsAvatarInput.files && settingsAvatarInput.files[0];
                    if (imageFile) {
                        const formData = new FormData();
                        formData.append('avatar', imageFile);
                        const avatarResponse = await fetch('/api/profile/avatar', { method: 'POST', credentials: 'include', body: formData });
                        const avatarData = await avatarResponse.json();
                        if (!avatarResponse.ok) throw new Error(avatarData.error || 'Unable to upload profile image');
                        currentUser = avatarData.user;
                    }

                    renderProfile(currentUser, { integrity_score: stats ? stats.integrity_score : 100 });
                    const shortName = getShortDisplayName(currentUser.name);
                    userNameDisplay.textContent = shortName;
                    const workspaceUserName = document.getElementById('workspaceUserName');
                    if (workspaceUserName) workspaceUserName.textContent = shortName;
                    const workspaceInitial = document.getElementById('workspaceInitial');
                    if (workspaceInitial) workspaceInitial.textContent = shortName.charAt(0).toUpperCase() || 'S';
                    candName.textContent = currentUser.name || 'N/A';
                    candId.textContent = currentUser.student_id || 'N/A';
                    candSession.textContent = currentUser.session_id || 'N/A';
                    showSettingsMessage('Profile updated successfully.', true);
                    await new Promise(resolve => setTimeout(resolve, 500));
                    closeSettingsModal();
                    profileModal.classList.add('is-open');
                } catch (error) {
                    showSettingsMessage(error.message || 'Unable to save changes.');
                } finally {
                    settingsSaveButton.disabled = false;
                    settingsSaveButton.textContent = 'Save changes';
                }
            }

            // ----- Live network diagnostics -----
            let networkSpeedSamples = [];

            function drawNetworkSpeedGraph(samples = networkSpeedSamples) {
                if (!networkSpeedCanvas) return;
                const width = Math.max(networkSpeedCanvas.clientWidth || 560, 260);
                const height = 58;
                const dpr = window.devicePixelRatio || 1;
                if (networkSpeedCanvas.width !== width * dpr || networkSpeedCanvas.height !== height * dpr) {
                    networkSpeedCanvas.width = width * dpr;
                    networkSpeedCanvas.height = height * dpr;
                    networkSpeedCanvas.style.width = width + 'px';
                    networkSpeedCanvas.style.height = height + 'px';
                }
                const ctx = networkSpeedCanvas.getContext('2d');
                ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
                ctx.clearRect(0, 0, width, height);
                ctx.strokeStyle = 'rgba(165,122,255,.14)';
                ctx.lineWidth = 1;
                for (let row = 1; row <= 3; row++) {
                    const y = (height * row) / 4;
                    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(width, y); ctx.stroke();
                }
                if (!samples.length) {
                    ctx.setLineDash([4, 4]); ctx.strokeStyle = 'rgba(255,255,255,.22)';
                    ctx.beginPath(); ctx.moveTo(0, height / 2); ctx.lineTo(width, height / 2); ctx.stroke(); ctx.setLineDash([]);
                    return;
                }
                const maxSpeed = Math.max(1, ...samples.map(sample => sample.speed)) * 1.18;
                const pointFor = sample => ({ x: Math.min(width, Math.max(0, (sample.elapsed / 5) * width)), y: height - 7 - ((sample.speed / maxSpeed) * (height - 14)) });
                const points = samples.map(pointFor);
                const gradient = ctx.createLinearGradient(0, 0, 0, height);
                gradient.addColorStop(0, 'rgba(105,219,124,.34)'); gradient.addColorStop(1, 'rgba(105,219,124,0)');
                ctx.beginPath(); ctx.moveTo(points[0].x, height); points.forEach(point => ctx.lineTo(point.x, point.y)); ctx.lineTo(points[points.length - 1].x, height); ctx.closePath(); ctx.fillStyle = gradient; ctx.fill();
                ctx.beginPath(); points.forEach((point, index) => index ? ctx.lineTo(point.x, point.y) : ctx.moveTo(point.x, point.y)); ctx.strokeStyle = '#69db7c'; ctx.lineWidth = 2; ctx.shadowColor = 'rgba(105,219,124,.5)'; ctx.shadowBlur = 7; ctx.stroke(); ctx.shadowBlur = 0;
                const last = points[points.length - 1]; ctx.beginPath(); ctx.arc(last.x, last.y, 3, 0, Math.PI * 2); ctx.fillStyle = '#b7ffc4'; ctx.fill();
            }

            function resetNetworkSpeedGraph() {
                networkSpeedSamples = [];
                if (networkSpeedValue) networkSpeedValue.textContent = 'Measuring...';
                drawNetworkSpeedGraph();
            }

            async function sampleNetworkSpeed(startedAt) {
                while (performance.now() - startedAt < 5000) {
                    const sampleStartedAt = performance.now();
                    let speed = 0;
                    if (navigator.onLine) {
                        try {
                            const controller = new AbortController();
                            const requestTimeout = window.setTimeout(() => controller.abort(), 700);
                            const response = await fetch('/api/network/speed-test?ts=' + Date.now(), { credentials: 'include', cache: 'no-store', signal: controller.signal, headers: { 'Accept': 'application/octet-stream' } });
                            window.clearTimeout(requestTimeout);
                            if (!response.ok) throw new Error('Speed test HTTP ' + response.status);
                            const payload = await response.arrayBuffer();
                            const elapsedMs = Math.max(1, performance.now() - sampleStartedAt);
                            speed = (payload.byteLength * 8) / (elapsedMs / 1000) / 1000000;
                        } catch (error) {
                            speed = 0;
                        }
                    }
                    networkSpeedSamples.push({ elapsed: Math.min(5, (performance.now() - startedAt) / 1000), speed });
                    if (networkSpeedSamples.length > 10) networkSpeedSamples.shift();
                    drawNetworkSpeedGraph();
                    const latestSpeed = networkSpeedSamples[networkSpeedSamples.length - 1].speed;
                    if (networkSpeedValue) networkSpeedValue.textContent = latestSpeed > 0 ? `${latestSpeed.toFixed(2)} Mbps` : 'No response';
                    const remainingMs = 5000 - (performance.now() - startedAt);
                    if (remainingMs <= 0) break;
                    await new Promise(resolve => setTimeout(resolve, Math.min(650, remainingMs)));
                }
            }

            async function setupOfflineCache() {
                if (!offlineCacheState || !offlineCacheDetail) return;
                const setCacheState = (state, detail, cardClass, iconClass) => {
                    offlineCacheState.textContent = state;
                    offlineCacheDetail.textContent = detail;
                    if (offlineCacheCard) offlineCacheCard.classList.remove('is-cached', 'is-offline-cache');
                    if (offlineCacheCard && cardClass) offlineCacheCard.classList.add(cardClass);
                    if (offlineCacheBadge) offlineCacheBadge.innerHTML = `<i class="fas ${iconClass}"></i>`;
                };
                if (!('serviceWorker' in navigator) || !('caches' in window)) {
                    setCacheState('Unavailable', 'Browser cache not supported', 'is-offline-cache', 'fa-exclamation');
                    return;
                }
                try {
                    const registration = await navigator.serviceWorker.register("{{ url_for('static', filename='sw.js') }}");
                    await navigator.serviceWorker.ready;
                    const cache = await caches.open('exam-monitor-shell-v1');
                    const cachedRequests = await cache.keys();
                    const isOffline = !navigator.onLine;
                    setCacheState(isOffline ? 'Offline ready' : 'Cached', cachedRequests.length ? (isOffline ? 'Using local fallback' : 'Offline fallback available') : 'Preparing local fallback', isOffline ? 'is-offline-cache' : 'is-cached', isOffline ? 'fa-cloud-download-alt' : 'fa-check');
                    window.addEventListener('online', () => setCacheState('Cached', 'Offline fallback available', 'is-cached', 'fa-check'));
                    window.addEventListener('offline', () => setCacheState('Offline ready', 'Using local fallback', 'is-offline-cache', 'fa-cloud-download-alt'));
                    registration.update();
                } catch (error) {
                    setCacheState('Unavailable', 'Offline fallback not ready', 'is-offline-cache', 'fa-exclamation');
                }
            }

            function setNetworkStep(id, status, value, iconClass) {
                const row = document.getElementById('network-step-' + id);
                if (!row) return;
                row.className = 'network-check-row ' + status;
                const icon = row.querySelector('.network-check-icon i');
                const statusElement = row.querySelector('.network-check-status');
                if (icon) icon.className = 'fas ' + (iconClass || (status === 'pending' ? 'fa-spinner' : status === 'pass' ? 'fa-check' : status === 'fail' ? 'fa-times' : 'fa-minus'));
                if (statusElement) statusElement.textContent = value;
            }

            function resetNetworkSteps() {
                ['dns', 'vpn', 'wifi', 'quality', 'ip'].forEach(id => setNetworkStep(id, 'pending', 'Checking...'));
            }

            function getConnectionType() {
                const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
                if (!navigator.onLine) return 'Offline';
                if (!connection) return 'Online';
                const type = connection.effectiveType ? connection.effectiveType.toUpperCase() : 'Online';
                const downlink = Number(connection.downlink);
                return downlink > 0 ? `${type} · ${downlink} Mbps` : type;
            }

            function updateNetworkButtonState(state, label) {
                networkStatusButtons.forEach(button => {
                    button.classList.remove('is-checking', 'is-online', 'is-degraded', 'is-offline');
                    button.classList.add('is-' + state);
                    const text = button.querySelector('.network-copy strong, .reference-status-copy strong');
                    if (text) text.textContent = label;
                    const icon = button.querySelector('.network-icon i, .reference-status-icon i');
                    if (icon) icon.className = state === 'offline' ? 'fas fa-wifi-slash' : (state === 'checking' ? 'fas fa-wifi' : 'fas fa-wifi');
                });
                const connectionDetail = document.getElementById('connectionDetail');
                const connectionCheckBadge = document.getElementById('connectionCheckBadge');
                if (connectionDetail) connectionDetail.textContent = state === 'checking' ? 'Checking examination server...' : state === 'online' ? 'Server connected' : state === 'offline' ? 'No network route' : 'Server connection issue';
                if (connectionCheckBadge) connectionCheckBadge.innerHTML = `<i class="fas ${state === 'checking' ? 'fa-spinner fa-spin' : state === 'online' ? 'fa-check' : 'fa-exclamation'}"></i>`;
                if (networkHeaderState) networkHeaderState.textContent = label;
                if (networkState) networkState.textContent = label;
            }

            function updateNetworkModal(state, title, description) {
                networkModalTitle.textContent = title;
                networkModalDescription.textContent = description;
                networkModalIcon.className = state === 'offline' ? 'fas fa-wifi-slash' : (state === 'checking' ? 'fas fa-spinner fa-spin' : 'fas fa-wifi');
            }

            function closeNetworkModal() {
                networkModal.classList.remove('is-open');
            }

            function setNetworkCompletionState(completed) {
                networkCheckComplete = completed;
                if (networkCloseButtonSecondary) {
                    networkCloseButtonSecondary.textContent = completed ? 'Done' : 'Cancel';
                    networkCloseButtonSecondary.classList.toggle('is-complete', completed);
                }
            }

            async function runNetworkDiagnosis() {
                if (networkCheckInFlight) return;
                networkCheckInFlight = true;
                const diagnosisStartedAt = performance.now();
                let completionState = null;
                resetNetworkSpeedGraph();
                const speedSamplerPromise = sampleNetworkSpeed(diagnosisStartedAt);
                setNetworkCompletionState(false);
                updateNetworkButtonState('checking', 'Checking...');
                updateNetworkModal('checking', 'Diagnosing...', 'Current: Checking network');
                resetNetworkSteps();
                if (networkRefreshButton) networkRefreshButton.disabled = true;

                const startedAt = performance.now();
                let latency = null;
                try {
                    setNetworkStep('dns', 'pending', 'Resolving...');
                    await new Promise(resolve => setTimeout(resolve, 180));
                    if (!navigator.onLine) {
                        setNetworkStep('dns', 'fail', 'No route');
                        setNetworkStep('vpn', 'warn', 'Not exposed', 'fa-shield-alt');
                        setNetworkStep('wifi', 'fail', 'Offline');
                        setNetworkStep('quality', 'fail', 'No signal');
                        setNetworkStep('ip', 'fail', 'Unavailable');
                        completionState = { state: 'offline', label: 'Offline', title: 'Diagnosis complete', description: 'Current: No network connection' };
                        return;
                    }

                    const response = await fetch('/api/network/health?ts=' + Date.now(), {
                        method: 'GET', credentials: 'include', cache: 'no-store',
                        headers: { 'Accept': 'application/json' }
                    });
                    latency = Math.round(performance.now() - startedAt);
                    if (!response.ok) throw new Error('Server returned HTTP ' + response.status);
                    const result = await response.json();
                    if (!result.ok) throw new Error('Server health check failed');

                    setNetworkStep('dns', 'pass', 'Resolved');
                    await new Promise(resolve => setTimeout(resolve, 120));
                    // Browsers intentionally do not expose VPN state or local IP addresses.
                    setNetworkStep('vpn', 'warn', 'Not exposed', 'fa-shield-alt');
                    setNetworkStep('wifi', 'pass', 'Connected');
                    setNetworkStep('quality', latency < 250 ? 'pass' : 'warn', `${latency} ms · ${getConnectionType()}`);
                    setNetworkStep('ip', 'pass', 'Server route OK');
                    const state = latency < 250 ? 'online' : 'degraded';
                    const label = state === 'online' ? 'Stable' : 'Slow';
                    completionState = { state, label, title: 'Connection stable', description: `Current: ${getConnectionType()} · ${latency} ms to examination server` };
                } catch (error) {
                    latency = latency || Math.round(performance.now() - startedAt);
                    setNetworkStep('dns', 'fail', 'Unresolved');
                    setNetworkStep('vpn', 'warn', 'Not exposed', 'fa-shield-alt');
                    setNetworkStep('wifi', 'pass', 'Online');
                    setNetworkStep('quality', 'fail', 'No response');
                    setNetworkStep('ip', 'fail', 'Unreachable');
                    completionState = { state: 'degraded', label: 'Server issue', title: 'Diagnosis complete', description: 'Current: Browser online · examination server unreachable' };
                    console.warn('Network diagnosis failed:', error);
                } finally {
                    await speedSamplerPromise;
                    const remainingMs = Math.max(0, 5000 - (performance.now() - diagnosisStartedAt));
                    if (remainingMs > 0) await new Promise(resolve => setTimeout(resolve, remainingMs));
                    if (networkSpeedSamples.length && networkSpeedValue) {
                        const successfulSamples = networkSpeedSamples.filter(sample => sample.speed > 0);
                        const averageSpeed = successfulSamples.length ? successfulSamples.reduce((sum, sample) => sum + sample.speed, 0) / successfulSamples.length : 0;
                        networkSpeedValue.textContent = averageSpeed > 0 ? `${averageSpeed.toFixed(2)} Mbps average` : 'No response';
                    }
                    if (completionState) {
                        updateNetworkButtonState(completionState.state, completionState.label);
                        updateNetworkModal(completionState.state, completionState.title, completionState.description);
                    }
                    if (networkLastChecked) networkLastChecked.textContent = 'Last checked: ' + new Date().toLocaleTimeString();
                    if (networkRefreshButton) networkRefreshButton.disabled = false;
                    networkCheckInFlight = false;
                    setNetworkCompletionState(true);
                }
            }

            function setupNetworkStatus() {
                networkStatusButtons.forEach(button => button.addEventListener('click', () => {
                    if (networkModal) networkModal.classList.add('is-open');
                    runNetworkDiagnosis();
                }));
                if (networkRefreshButton) networkRefreshButton.addEventListener('click', runNetworkDiagnosis);
                if (networkCloseButton) networkCloseButton.addEventListener('click', closeNetworkModal);
                if (networkCloseButtonSecondary) networkCloseButtonSecondary.addEventListener('click', closeNetworkModal);
                if (networkModal) {
                    networkModal.addEventListener('click', event => {
                        if (event.target === networkModal) closeNetworkModal();
                    });
                }
                if (networkHeaderClock) {
                    const updateClock = () => { networkHeaderClock.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }); };
                    updateClock();
                    window.setInterval(updateClock, 1000);
                }
                document.addEventListener('keydown', event => {
                    if (event.key === 'Escape') closeNetworkModal();
                });
                // The diagnostic runs only from an explicit workspace-button click.
            }

            // ----- Load dashboard data -----
            function loadDashboard() {

                apiFetch('/api/check_verification')
                    .then(res => res.json())
                    .then(data => {
                        referenceExists = data.exists;
                        return apiFetch('/api/dashboard/student');
                    })
                    .then(res => {
                        if (!res.ok) {
                            if (res.status === 401) window.location.href = '/login';
                            throw new Error('Failed to load dashboard');
                        }
                        return res.json();
                    })
                    .then(data => {
                                                currentUser = data.user;
                        renderProfile(currentUser, data);
                        stats = data.stats || {};

                        allEvents = data.events || [];
                        examRunning = data.exam_running || false;
                        const integrityScore = data.integrity_score !== undefined ? data.integrity_score : 100;

                        const startedAt = stats.started_at;
                        const endedAt = stats.ended_at;
                        sessionEvents = filterSessionEvents(allEvents, startedAt, endedAt);

                        let sessionDurationSec = 0;
                        if (startedAt) {
                            const start = new Date(startedAt).getTime();
                            const end = endedAt ? new Date(endedAt).getTime() : Date.now();
                            sessionDurationSec = Math.floor((end - start) / 1000);
                        }

                        // Compute total deducted points for this session
                        let totalDeducted = 0;
                        sessionEvents.forEach(ev => {
                            if (ev.deducted) totalDeducted += ev.deducted;
                        });

                                                const renderBadge = (score) => {
                            const baseStyle = "display:inline-flex; align-items:center; gap:5px; padding:2px 8px; border-radius:12px; font-size:10px; font-weight:700; vertical-align:middle; margin-left:10px; letter-spacing:0.5px; text-transform:uppercase;";
                            if (score >= 90) return ` <span style="${baseStyle} background:rgba(46, 204, 113, 0.15); border:1px solid rgba(46, 204, 113, 0.3); color:#2ecc71; box-shadow:0 0 8px rgba(46, 204, 113, 0.2);"><i class="fas fa-shield-check"></i> High Trust</span>`;
                            if (score >= 70) return ` <span style="${baseStyle} background:rgba(241, 196, 15, 0.15); border:1px solid rgba(241, 196, 15, 0.3); color:#f1c40f; box-shadow:0 0 8px rgba(241, 196, 15, 0.2);"><i class="fas fa-shield-alt"></i> Verified</span>`;
                            return ` <span style="${baseStyle} background:rgba(231, 76, 60, 0.15); border:1px solid rgba(231, 76, 60, 0.3); color:#e74c3c; box-shadow:0 0 8px rgba(231, 76, 60, 0.2);"><i class="fas fa-shield-virus"></i> Unverified</span>`;
                        };

                        const badgeHtml = renderBadge(integrityScore);
                        const shortDisplayName = getShortDisplayName(currentUser ? currentUser.name : 'User');
                        if (userNameDisplay) userNameDisplay.innerHTML = shortDisplayName + badgeHtml;
                        const workspaceUserName = document.getElementById('workspaceUserName');
                        if (workspaceUserName) workspaceUserName.innerHTML = shortDisplayName + badgeHtml;
                        const workspaceInitial = document.getElementById('workspaceInitial');
                        if (workspaceInitial) workspaceInitial.textContent = shortDisplayName.charAt(0).toUpperCase() || 'S';

                        if (candId) candId.textContent = currentUser ? (currentUser.student_id || 'N/A') : 'N/A';

                        if (candName) candName.innerHTML = (currentUser ? currentUser.name : 'N/A') + badgeHtml;
                        if (candSession) candSession.textContent = currentUser ? (currentUser.session_id || 'N/A') : 'N/A';
                        if (faceRatioEl) faceRatioEl.textContent = data.face_ratio !== undefined ? data.face_ratio : 'N/A';

                        const finalScore = data.final_score;
                        if (examRunning) {
                            if (candScore) candScore.textContent = 'In Progress';
                            if (candRemark) candRemark.textContent = 'Exam ongoing';
                        } else if (sessionEvents.length === 0 && !startedAt) {
                            if (candScore) candScore.textContent = '0';
                            if (candRemark) candRemark.textContent = 'Not yet started';
                        } else if (finalScore !== null && finalScore !== undefined && !examRunning) {
                            if (candScore) candScore.textContent = finalScore;
                            let remark = '';
                            if (finalScore >= 90) remark = 'Excellent';
                            else if (finalScore >= 70) remark = 'Good';
                            else if (finalScore >= 50) remark = 'Fair';
                            else remark = 'Needs Improvement';
                            if (candRemark) candRemark.textContent = remark;
                        } else {
                            if (candScore) candScore.textContent = '0';
                            if (candRemark) candRemark.textContent = 'No session';
                        }
                        if (riskLabel) riskLabel.textContent = data.risk_label || 'N/A';

                        let faceAbsenceCount = 0, multipleFacesCount = 0, totalSuspicious = 0;
                        sessionEvents.forEach(ev => {
                            if (ev.type === 'Face Absence') faceAbsenceCount++;
                            else if (ev.type === 'Multiple Faces') multipleFacesCount++;
                            if (ev.deducted > 0) totalSuspicious++;
                        });
                        if (faceAbsenceCountEl) faceAbsenceCountEl.textContent = faceAbsenceCount;
                        if (multipleFacesCountEl) multipleFacesCountEl.textContent = multipleFacesCount;
                        if (totalSuspiciousEl) totalSuspiciousEl.textContent = totalSuspicious;

                        const readinessStateEl = document.getElementById('readinessState');
                        const readinessDetailEl = document.getElementById('readinessDetail');
                        const notificationStateEl = document.getElementById('notificationState');
                        const notificationDetailEl = document.getElementById('notificationDetail');
                        if (readinessStateEl) readinessStateEl.textContent = examRunning ? 'In progress' : 'Diagnose system';
                        if (readinessDetailEl) readinessDetailEl.textContent = examRunning ? 'Monitoring active' : 'Run system check';
                        if (notificationStateEl) notificationStateEl.textContent = totalSuspicious ? `${totalSuspicious} flagged` : '0 new';
                        if (notificationDetailEl) notificationDetailEl.textContent = totalSuspicious ? 'Review integrity events' : 'You\'re all caught up!';

                        if (scoreValue) scoreValue.textContent = integrityScore;

                        if (scoreBar) {
                            scoreBar.style.width = integrityScore + '%';
                            if (integrityScore >= 70) {
                                scoreBar.style.background = 'linear-gradient(90deg, #51cf66, #69db7c)';
                            } else if (integrityScore >= 40) {
                                scoreBar.style.background = 'linear-gradient(90deg, #fcc419, #ffd43b)';
                            } else {
                                scoreBar.style.background = 'linear-gradient(90deg, #ff6b6b, #ff8787)';
                            }
                        }

                        const durationFormatted = formatTime(sessionDurationSec);
                        if (sessionDurationEl) sessionDurationEl.textContent = durationFormatted;
                        if (statsDurationEl) statsDurationEl.textContent = durationFormatted;
                        if (totalDeductedEl) totalDeductedEl.textContent = totalDeducted;
                        elapsedSeconds = sessionDurationSec;

                        renderEventLog(sessionEvents);
                        renderTimeline(sessionEvents);
                        drawPieChart(sessionEvents);

                        // Exam state
                        if (examRunning) {
                            startBtn.disabled = true;
                            togglePauseBtn.disabled = false;
                            togglePauseBtn.textContent = 'Pause';
                            togglePauseBtn.classList.remove('resume');
                            togglePauseBtn.innerHTML = '<i class="fas fa-pause"></i> Pause';
                            endBtn.disabled = false;
                            if (!cameraStream) startCamera();
                            if (!timerInterval) {
                                sessionStartTime = Date.now() - totalPausedDuration;
                                startTimer();
                            }
                        } else {
                            startBtn.disabled = false;
                            togglePauseBtn.disabled = true;
                            togglePauseBtn.textContent = 'Pause';
                            togglePauseBtn.classList.remove('resume');
                            togglePauseBtn.innerHTML = '<i class="fas fa-pause"></i> Pause';
                            endBtn.disabled = true;
                            if (cameraStream) stopCamera();
                            if (timerInterval) {
                                clearInterval(timerInterval);
                                timerInterval = null;
                            }
                        }
                    })
                    .catch(err => {
                        console.error(err);
                        showToast('Error loading dashboard', 'error');
                    });
            }

            function renderEventLog(eventsArray) {
                if (!eventsArray || eventsArray.length === 0) {
                    eventLogBody.innerHTML = `<tr><td colspan="3" style="text-align:center;color:rgba(255,255,255,0.3);">No events in this session</td></tr>`;
                    return;
                }
                let html = '';
                eventsArray.slice().reverse().forEach(ev => {
                    let iconHtml = '<div class="event-icon" style="background: rgba(255,255,255,0.1); color: #fff;"><i class="fas fa-info-circle"></i></div>';
                    let evType = (ev.type || '').toLowerCase();
                    if (evType.includes('browser') || evType.includes('focus')) {
                        iconHtml = '<div class="event-icon" style="background: rgba(255,107,107,0.1); color: #ff6b6b;"><i class="fas fa-desktop"></i></div>';
                    } else if (evType.includes('multiple') || evType.includes('face')) {
                        iconHtml = '<div class="event-icon" style="background: rgba(124,77,255,0.1); color: #b8aaff;"><i class="fas fa-users"></i></div>';
                    }
                    let deductedHtml = ev.deducted ? `<span style="color: #ff6b6b;">${ev.deducted}</span>` : '0';
                    html += `<tr>
                        <td><div class="event-type-cell">${iconHtml}<span>${ev.type}</span></div></td>
                        <td>${ev.timestamp}</td>
                        <td>${deductedHtml}</td>
                    </tr>`;
                });
                eventLogBody.innerHTML = html;
            }

            let pieAnimReq;
            function drawPieChart(eventsArray) {
                if (pieAnimReq) cancelAnimationFrame(pieAnimReq);
                
                // 1. Create or get the legend container (HTML based)
                let lgDiv = document.getElementById('pieLegend');
                if (!lgDiv) {
                    const container = pieCanvas.parentElement;
                    lgDiv = document.createElement('div');
                    lgDiv.id = 'pieLegend';
                    lgDiv.style.display = 'flex';
                    lgDiv.style.flexWrap = 'wrap';
                    lgDiv.style.gap = '12px';
                    lgDiv.style.justifyContent = 'center';
                    lgDiv.style.marginTop = '15px';
                    lgDiv.style.fontSize = '12px';
                    container.appendChild(lgDiv);
                }
                
                const ctx = pieCanvas.getContext('2d');
                const w = pieCanvas.width;
                const h = pieCanvas.height;
                const radius = Math.min(w, h) / 2 - 10;
                const cx = w / 2;
                const cy = h / 2;
                
                const counts = {
                    'Face Absence': 0,
                    'Multiple Faces': 0,
                    'Browser Focus Loss': 0,
                    'Tab Switching': 0,
                    'Face Not Detected': 0,
                };
                (eventsArray || []).forEach(ev => {
                    if (counts[ev.type] !== undefined) counts[ev.type]++;
                });

                const activeLabels = [];
                const activeValues = [];
                Object.keys(counts).forEach(k => {
                    if (counts[k] > 0) {
                        activeLabels.push(k);
                        activeValues.push(counts[k]);
                    }
                });

                const total = activeValues.reduce((a, b) => a + b, 0);
                
                // Clear old legend
                lgDiv.innerHTML = '';
                
                if (total === 0) {
                    ctx.clearRect(0, 0, w, h);
                    ctx.fillStyle = 'rgba(255,255,255,0.1)';
                    ctx.font = '16px Inter';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText('No data', cx, cy);
                    return;
                }

                const colors = ['#ff6b6b', '#fcc419', '#4dabf7', '#ff922b', '#845ef7'];
                
                // Populate legend HTML
                activeLabels.forEach((label, i) => {
                    lgDiv.innerHTML += `<div style="display:flex; align-items:center; gap:6px; color:rgba(255,255,255,0.8);"><div style="width:12px;height:12px;background:${colors[i % colors.length]};border-radius:3px;"></div>${label} (${activeValues[i]})</div>`;
                });

                // 2. Animate pie chart
                const duration = 1200; // 1.2s
                const startTime = performance.now();

                function animatePie(time) {
                    let progress = (time - startTime) / duration;
                    if (progress > 1) progress = 1;
                    
                    // Ease out cubic
                    const ease = 1 - Math.pow(1 - progress, 3);
                    
                    ctx.clearRect(0, 0, w, h);
                    let startAngle = -Math.PI / 2;
                    
                    activeValues.forEach((val, i) => {
                        const sliceAngle = (val / total) * 2 * Math.PI * ease;
                        if (sliceAngle <= 0) return;
                        
                        ctx.beginPath();
                        ctx.moveTo(cx, cy);
                        ctx.arc(cx, cy, radius, startAngle, startAngle + sliceAngle);
                        ctx.closePath();
                        ctx.fillStyle = colors[i % colors.length];
                        ctx.fill();
                        
                        // Draw numbers if animation is almost done
                        if (progress > 0.8) {
                            const midAngle = startAngle + sliceAngle / 2;
                            const labelRadius = radius * 0.65;
                            const x = cx + Math.cos(midAngle) * labelRadius;
                            const y = cy + Math.sin(midAngle) * labelRadius;
                            ctx.fillStyle = '#fff';
                            ctx.font = 'bold 16px Inter';
                            ctx.textAlign = 'center';
                            ctx.textBaseline = 'middle';
                            ctx.fillText(val, x, y);
                        }
                        
                        startAngle += sliceAngle;
                    });
                    
                    if (progress < 1) {
                        pieAnimReq = requestAnimationFrame(animatePie);
                    }
                }
                
                pieAnimReq = requestAnimationFrame(animatePie);
            }

            // ----- Log event (server) -----
            function logEventToServer(type, deducted, screenshotBase64 = null) {
                const payload = { type, deducted };
                if (screenshotBase64) payload.screenshot = screenshotBase64;
                return apiFetch('/api/events', {
                    method: 'POST',
                    body: JSON.stringify(payload)
                })
                .then(res => res.json())
                .then(data => {
                    loadDashboard();
                    return data;
                });
            }

            function captureScreenshot() {
                if (!cameraStream) return null;
                const canvas = document.createElement('canvas');
                canvas.width = video.videoWidth || 640;
                canvas.height = video.videoHeight || 480;
                const c = canvas.getContext('2d');
                c.drawImage(video, 0, 0, canvas.width, canvas.height);
                return canvas.toDataURL('image/png');
            }

            // ----- Face detection (server) for main exam -----
            function detectFacesOnServer() {
                if (!examRunning || examPaused || !cameraStream) return;
                const canvas = document.createElement('canvas');
                canvas.width = video.videoWidth || 640;
                canvas.height = video.videoHeight || 480;
                const c = canvas.getContext('2d');
                c.drawImage(video, 0, 0, canvas.width, canvas.height);
                const imageData = canvas.toDataURL('image/jpeg', 0.8);

                apiFetch('/api/detect_faces', {
                    method: 'POST',
                    body: JSON.stringify({ image: imageData })
                })
                .then(res => res.json())
                .then(data => {
                    if (data.error) {
                        console.warn('Detection error:', data.error);
                        return;
                    }
                    const faceCount = data.face_count || 0;
                    // Draw boxes on overlay (if needed)
                    const overlay = document.getElementById('overlayCanvas');
                    if (overlay) {
                        const ctx = overlay.getContext('2d');
                        ctx.clearRect(0, 0, overlay.width, overlay.height);
                        const scaleX = overlay.width / video.videoWidth;
                        const scaleY = overlay.height / video.videoHeight;
                        // optional drawing...
                    }
                    if (faceCount === 0) {
                        if (!faceNotDetectedLogged) {
                            faceNotDetectedLogged = true;
                            const screenshot = captureScreenshot();
                            logEventToServer('Face Not Detected', 2, screenshot);
                        }
                        if (faceNotDetectedStart === null) {
                            faceNotDetectedStart = Date.now();
                        } else {
                            const elapsed = (Date.now() - faceNotDetectedStart) / 1000;
                            if (elapsed > 5 && !faceAbsenceTriggered) {
                                faceAbsenceTriggered = true;
                                const screenshot = captureScreenshot();
                                logEventToServer('Face Absence', 5, screenshot);
                            }
                        }
                    } else if (faceCount > 1) {
                        const screenshot = captureScreenshot();
                        logEventToServer('Multiple Faces', 7, screenshot);
                        faceNotDetectedLogged = false;
                        faceNotDetectedStart = null;
                        faceAbsenceTriggered = false;
                    } else {
                        faceNotDetectedLogged = false;
                        faceNotDetectedStart = null;
                        faceAbsenceTriggered = false;
                    }
                })
                .catch(err => console.warn('Detection request failed:', err));
            }

            // ----- Timer -----
            function startTimer() {
                if (timerInterval) clearInterval(timerInterval);
                if (!sessionStartTime) {
                    sessionStartTime = Date.now() - totalPausedDuration;
                }
                timerInterval = setInterval(() => {
                    if (examRunning && !examPaused) {
                        const now = Date.now();
                        elapsedSeconds = (now - sessionStartTime - totalPausedDuration) / 1000;
                        updateDurationDisplay();
                    }
                }, 1000);
            }

            function updateDurationDisplay() {
                const sec = Math.floor(elapsedSeconds);
                const formatted = formatTime(sec);
                sessionDurationEl.textContent = formatted;
                statsDurationEl.textContent = formatted;
            }

            // ----- Camera (main) -----
            function startCamera() {
                return navigator.mediaDevices.getUserMedia({ video: true })
                    .then(stream => {
                        cameraStream = stream;
                        const video = document.getElementById('video');
                        video.srcObject = stream;
                        video.play();
                        video.onloadedmetadata = () => {
                            const overlay = document.getElementById('overlayCanvas');
                            overlay.width = video.videoWidth;
                            overlay.height = video.videoHeight;
                        };
                        document.getElementById('cameraSection').classList.add('active');
                        if (faceDetectionInterval) clearInterval(faceDetectionInterval);
                        faceDetectionInterval = setInterval(detectFacesOnServer, DETECTION_INTERVAL);
                        return stream;
                    });
            }

            function stopCamera() {
                if (cameraStream) {
                    cameraStream.getTracks().forEach(t => t.stop());
                    cameraStream = null;
                    const video = document.getElementById('video');
                    video.srcObject = null;
                    document.getElementById('cameraSection').classList.remove('active');
                }
                if (faceDetectionInterval) {
                    clearInterval(faceDetectionInterval);
                    faceDetectionInterval = null;
                }
                const overlay = document.getElementById('overlayCanvas');
                if (overlay) {
                    const ctx = overlay.getContext('2d');
                    ctx.clearRect(0, 0, overlay.width, overlay.height);
                }
            }

            // ----- Wizard cameras -----
            function startWizardCamera() {
                return navigator.mediaDevices.getUserMedia({ video: true })
                    .then(stream => {
                        wizardStream = stream;
                        wizardVideo.srcObject = stream;
                        wizardVideo.play();
                        wizardVideo.onloadedmetadata = () => {
                            wizardCanvas.width = wizardVideo.videoWidth;
                            wizardCanvas.height = wizardVideo.videoHeight;
                        };
                        return stream;
                    });
            }

            function stopWizardCamera() {
                if (wizardStream) {
                    wizardStream.getTracks().forEach(t => t.stop());
                    wizardStream = null;
                    wizardVideo.srcObject = null;
                }
            }

            function startChecksCamera() {
                return navigator.mediaDevices.getUserMedia({ video: true })
                    .then(stream => {
                        checksStream = stream;
                        checksVideo.srcObject = stream;
                        checksVideo.play();
                        checksVideo.onloadedmetadata = () => {
                            checksOverlayCanvas.width = checksVideo.videoWidth;
                            checksOverlayCanvas.height = checksVideo.videoHeight;
                        };
                        return stream;
                    });
            }

            function stopChecksCamera() {
                if (checksStream) {
                    checksStream.getTracks().forEach(t => t.stop());
                    checksStream = null;
                    checksVideo.srcObject = null;
                }
            }

            // ========== WIZARD LOGIC ==========

            function openWizard() {
                wizardOverlay.classList.add('active');

                // Reset state
                captureAttempts = 0;
                capturedImageData = null;
                capturedPreview.style.display = 'none';
                submitPhotoBtn.disabled = true;
                nextStep1Btn.disabled = true;
                attemptDisplay.textContent = 'Attempts: 0 / ' + MAX_ATTEMPTS;
                faceMatchAttempts = 0;
                faceVerified = false;
                checksPassed = false;
                nextStep2Btn.disabled = true;
                verifyFaceBtn.disabled = false;
                verifyFaceBtn.textContent = 'Verify Face';
                faceAttemptDisplay.textContent = 'Attempts: 0 / 3';
                verifyArea.style.display = 'none';
                verifyStatus.textContent = '';
                autoChecksDone = false;

                if (referenceExists) {
                    // Skip capture step
                    step1Label.textContent = 'Skipped';
                    dot1.classList.add('done');
                    goToStep(2);
                    startChecksCamera().catch(err => {
                        showToast('Camera access denied: ' + err.message, 'error');
                    });
                    verifyArea.style.display = 'block';
                } else {
                    step1Label.textContent = 'Capture';
                    dot1.classList.remove('done');
                    goToStep(1);
                    startWizardCamera().catch(err => {
                        showToast('Camera access denied: ' + err.message, 'error');
                    });
                }
            }

            function closeWizard() {
                wizardOverlay.classList.remove('active');
                stopWizardCamera();
                stopChecksCamera();
            }

            function goToStep(step) {
                currentStep = step;
                document.querySelectorAll('.wizard-step').forEach(el => el.classList.remove('active'));
                document.querySelectorAll('.step-dot').forEach(el => el.classList.remove('active', 'done'));
                if (step === 1) {
                    step1.classList.add('active');
                    dot1.classList.add('active');
                } else if (step === 2) {
                    step2.classList.add('active');
                    dot1.classList.add('done');
                    dot2.classList.add('active');
                    runSystemChecks();
                } else if (step === 3) {
                    step3.classList.add('active');
                    dot1.classList.add('done');
                    dot2.classList.add('done');
                    dot3.classList.add('active');
                }
            }

            // ----- Step 1: Capture Photo (only when no reference) -----
            captureBtn.addEventListener('click', function() {
                if (captureAttempts >= MAX_ATTEMPTS) {
                    showToast('Maximum attempts reached. Please submit.', 'error');
                    return;
                }
                const canvas = document.createElement('canvas');
                canvas.width = wizardVideo.videoWidth || 640;
                canvas.height = wizardVideo.videoHeight || 480;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(wizardVideo, 0, 0, canvas.width, canvas.height);
                capturedImageData = canvas.toDataURL('image/png');
                capturedImg.src = capturedImageData;
                capturedPreview.style.display = 'block';
                captureAttempts++;
                attemptDisplay.textContent = 'Attempts: ' + captureAttempts + ' / ' + MAX_ATTEMPTS;
                submitPhotoBtn.disabled = false;
                if (captureAttempts >= MAX_ATTEMPTS) {
                    captureBtn.disabled = true;
                }
            });

            submitPhotoBtn.addEventListener('click', function() {
                if (!capturedImageData) {
                    showToast('Please capture a photo first.', 'error');
                    return;
                }
                submitPhotoBtn.disabled = true;
                submitPhotoBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Submitting...';
                apiFetch('/api/detect_faces', {
                    method: 'POST',
                    body: JSON.stringify({ image: capturedImageData })
                })
                .then(res => res.json())
                .then(data => {
                    if (data.face_count === 0) {
                        throw new Error('No face detected. Please retry.');
                    } else if (data.face_count > 1) {
                        throw new Error('Multiple faces detected. Capture only your face.');
                    }
                    return apiFetch('/api/verify_photo', {
                        method: 'POST',
                        body: JSON.stringify({ image: capturedImageData })
                    });
                })
                .then(() => {
                    submitPhotoBtn.innerHTML = '<i class="fas fa-check"></i> Submitted';
                    showToast('Photo saved successfully!', 'success');
                    referenceExists = true;
                    nextStep1Btn.disabled = false;
                })
                .catch(err => {
                    submitPhotoBtn.disabled = false;
                    submitPhotoBtn.innerHTML = '<i class="fas fa-check"></i> Submit';
                    showToast('Error: ' + err.message, 'error');
                });
            });

            nextStep1Btn.addEventListener('click', function() {
                stopWizardCamera();
                goToStep(2);
                startChecksCamera().catch(err => {
                    showToast('Camera access denied: ' + err.message, 'error');
                });
                verifyArea.style.display = 'block';
            });

            // ----- Step 2: System Checks -----

            function runSystemChecks() {
                const checks = [
                    { id: 'camera', label: 'Camera access' },
                    { id: 'microphone', label: 'Microphone access' },
                    { id: 'browser', label: 'Browser compatibility' },
                    { id: 'internet', label: 'Internet connection' },
                ];
                if (referenceExists) {
                    checks.push({ id: 'face_match', label: 'Face verification (live vs reference)' });
                }
                checkList.innerHTML = '';
                checks.forEach((chk) => {
                    const div = document.createElement('div');
                    div.className = 'check-item pending';
                    div.id = `check-${chk.id}`;
                    div.innerHTML = `
                        <span class="status-icon"><i class="fas fa-spinner"></i></span>
                        <span class="check-label">${chk.label}</span>
                        <span class="check-status">Checking...</span>
                    `;
                    checkList.appendChild(div);
                });

                // Run auto checks
                Promise.all([
                    performCheckCamera(),
                    performCheckMicrophone(),
                    performCheckBrowser(),
                    performCheckInternet()
                ])
                .then(() => {
                    autoChecksDone = true;
                    if (referenceExists) {
                        // Face verification remains pending; user must click "Verify Face"
                        updateCheckStatus('face_match', 'pending', 'Click "Verify Face"');
                        verifyFaceBtn.disabled = false;
                        // Next remains disabled until face is verified
                    } else {
                        // No reference needed – all checks pass
                        checksPassed = true;
                        nextStep2Btn.disabled = false;
                        showToast('All system checks passed!', 'success');
                    }
                })
                .catch(err => {
                    showToast('System check failed: ' + err.message, 'error');
                    nextStep2Btn.disabled = true;
                });
            }

            function updateCheckStatus(itemId, status, text) {
                const item = document.getElementById('check-' + itemId);
                if (!item) return;
                item.className = `check-item ${status}`;
                const icon = item.querySelector('.status-icon i');
                const statusSpan = item.querySelector('.check-status');
                if (status === 'pending') icon.className = 'fas fa-spinner';
                else if (status === 'pass') icon.className = 'fas fa-check-circle';
                else if (status === 'fail') icon.className = 'fas fa-times-circle';
                statusSpan.textContent = text;
            }

            function performCheckCamera() {
                return new Promise((resolve, reject) => {
                    updateCheckStatus('camera', 'pending', 'Requesting...');
                    navigator.mediaDevices.getUserMedia({ video: true })
                        .then(stream => {
                            stream.getTracks().forEach(t => t.stop());
                            updateCheckStatus('camera', 'pass', '✅ Available');
                            resolve();
                        })
                        .catch(err => {
                            updateCheckStatus('camera', 'fail', '❌ Denied');
                            reject(new Error('Camera access required'));
                        });
                });
            }

            function performCheckMicrophone() {
                return new Promise((resolve) => {
                    updateCheckStatus('microphone', 'pending', 'Requesting...');
                    navigator.mediaDevices.getUserMedia({ audio: true })
                        .then(stream => {
                            stream.getTracks().forEach(t => t.stop());
                            updateCheckStatus('microphone', 'pass', '✅ Available');
                            resolve();
                        })
                        .catch(() => {
                            updateCheckStatus('microphone', 'pass', '⚠️ Not required');
                            resolve();
                        });
                });
            }

            function performCheckBrowser() {
                return new Promise((resolve) => {
                    const compatible = 'MediaRecorder' in window && 'fetch' in window && 'Promise' in window;
                    if (compatible) {
                        updateCheckStatus('browser', 'pass', '✅ Compatible');
                    } else {
                        updateCheckStatus('browser', 'fail', '❌ Outdated');
                    }
                    resolve();
                });
            }

            function performCheckInternet() {
                return new Promise((resolve, reject) => {
                    updateCheckStatus('internet', 'pending', 'Checking...');
                    if (!navigator.onLine) {
                        updateCheckStatus('internet', 'fail', '❌ Offline');
                        reject(new Error('No internet connection'));
                    } else {
                        fetch('/api/dashboard/student', { method: 'HEAD', credentials: 'include' })
                            .then(() => {
                                updateCheckStatus('internet', 'pass', '✅ Connected');
                                resolve();
                            })
                            .catch(() => {
                                updateCheckStatus('internet', 'fail', '❌ Server unreachable');
                                reject(new Error('Connectivity issue'));
                            });
                    }
                });
            }

            // ----- Verify Face button -----
            verifyFaceBtn.addEventListener('click', function() {
                if (faceMatchAttempts >= MAX_ATTEMPTS) {
                    showToast('Maximum attempts reached. Redirecting to dashboard.', 'error');
                    closeWizard();
                    return;
                }
                if (!checksStream) {
                    showToast('Camera not ready.', 'error');
                    return;
                }
                // Capture frame from checks video
                const canvas = document.createElement('canvas');
                canvas.width = checksVideo.videoWidth || 640;
                canvas.height = checksVideo.videoHeight || 480;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(checksVideo, 0, 0, canvas.width, canvas.height);
                const imageData = canvas.toDataURL('image/png');
                faceMatchAttempts++;
                faceAttemptDisplay.textContent = 'Attempts: ' + faceMatchAttempts + ' / 3';
                verifyFaceBtn.disabled = true;
                verifyFaceBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Verifying...';
                verifyStatus.textContent = '';

                apiFetch('/api/verify_face', {
                    method: 'POST',
                    body: JSON.stringify({ image: imageData })
                })
                .then(res => res.json())
                .then(data => {
                    if (data.match) {
                        faceVerified = true;
                        updateCheckStatus('face_match', 'pass', '✅ Match');
                        showToast('Face verification successful!', 'success');
                        checksPassed = true;
                        nextStep2Btn.disabled = false;
                        verifyFaceBtn.innerHTML = '<i class="fas fa-check"></i> Verified';
                        verifyFaceBtn.disabled = true;
                        verifyStatus.textContent = '✅ Face matched!';
                        verifyStatus.style.color = '#51cf66';
                    } else {
                        updateCheckStatus('face_match', 'fail', '❌ Does not match reference');
                        if (faceMatchAttempts >= MAX_ATTEMPTS) {
                            verifyStatus.textContent = '❌ You have attempted 3 times and failed.';
                            verifyStatus.style.color = '#ff6b6b';
                            showToast('Face verification failed after 3 attempts. Redirecting to dashboard.', 'error');
                            setTimeout(() => {
                                closeWizard();
                            }, 2000);
                        } else {
                            verifyStatus.textContent = '❌ Face does not match. Please try again.';
                            verifyStatus.style.color = '#ff6b6b';
                            showToast('Face did not match. Please try again.', 'error');
                            verifyFaceBtn.disabled = false;
                            verifyFaceBtn.innerHTML = 'Verify Face';
                            // keep check as fail but allow retry
                        }
                    }
                })
                .catch(err => {
                    showToast('Error: ' + err.message, 'error');
                    verifyFaceBtn.disabled = false;
                    verifyFaceBtn.innerHTML = 'Verify Face';
                });
            });

            nextStep2Btn.addEventListener('click', function() {
                stopChecksCamera();
                goToStep(3);
            });

            // ----- Step 3: Instructions & Consent -----
            consentCheck.addEventListener('change', function() {
                startExamFinalBtn.disabled = !this.checked;
            });

            startExamFinalBtn.addEventListener('click', function() {
                closeWizard();
                startExam();
            });

            // ========== EXAM ACTIONS ==========

            function startExam() {
                if (examRunning) return;
                apiFetch('/api/exam/start', { method: 'POST' })
                    .then(res => {
                        if (!res.ok) throw new Error('Failed to start exam');
                        return res.json();
                    })
                    .then(() => {
                        startCamera().then(() => {
                            examRunning = true;
                            examPaused = false;
                            startBtn.disabled = true;
                            togglePauseBtn.disabled = false;
                            togglePauseBtn.textContent = 'Pause';
                            togglePauseBtn.classList.remove('resume');
                            togglePauseBtn.innerHTML = '<i class="fas fa-pause"></i> Pause';
                            endBtn.disabled = false;
                            totalPausedDuration = 0;
                            sessionStartTime = Date.now();
                            startTimer();
                            showToast('Exam started!', 'success');
                            loadDashboard();
                        }).catch(err => {
                            showToast('Camera access denied: ' + err.message, 'error');
                        });
                    })
                    .catch(err => showToast(err.message, 'error'));
            }

            function togglePause() {
                if (!examRunning) return;
                if (examPaused) {
                    startCamera().then(() => {
                        examPaused = false;
                        togglePauseBtn.textContent = 'Pause';
                        togglePauseBtn.classList.remove('resume');
                        togglePauseBtn.innerHTML = '<i class="fas fa-pause"></i> Pause';
                        showToast('Exam resumed', 'success');
                    }).catch(err => {
                        showToast('Failed to resume camera: ' + err.message, 'error');
                    });
                } else {
                    stopCamera();
                    examPaused = true;
                    togglePauseBtn.textContent = 'Resume';
                    togglePauseBtn.classList.add('resume');
                    togglePauseBtn.innerHTML = '<i class="fas fa-play"></i> Resume';
                    totalPausedDuration += (Date.now() - sessionStartTime - totalPausedDuration) - elapsedSeconds * 1000;
                    showToast('Exam paused', 'success');
                }
            }

            function endExam() {
                if (!examRunning) return;
                apiFetch('/api/exam/end', { method: 'POST' })
                    .then(res => {
                        if (!res.ok) throw new Error('Failed to end exam');
                        return res.json();
                    })
                    .then(() => {
                        examRunning = false;
                        examPaused = false;
                        stopCamera();
                        if (timerInterval) {
                            clearInterval(timerInterval);
                            timerInterval = null;
                        }
                        startBtn.disabled = false;
                        togglePauseBtn.disabled = true;
                        togglePauseBtn.textContent = 'Pause';
                        togglePauseBtn.classList.remove('resume');
                        togglePauseBtn.innerHTML = '<i class="fas fa-pause"></i> Pause';
                        endBtn.disabled = true;
                        loadDashboard();
                        showToast('Exam ended.', 'success');
                    })
                    .catch(err => showToast(err.message, 'error'));
            }

            // ----- Focus handlers (tab switch, focus loss) -----
            function setupFocusHandlers() {
                window.addEventListener('blur', () => {
                    if (!examRunning || examPaused) return;
                    logEventToServer('Browser Focus Loss', 3, null);
                });
                document.addEventListener('visibilitychange', () => {
                    if (document.hidden && examRunning && !examPaused) {
                        logEventToServer('Tab Switching', 5, null);
                    }
                });
            }

            // ----- Logout and report -----
            function logout() {
                if (examRunning) {
                    if (!confirm('Exam is running. Logout will lose progress. Continue?')) return;
                }
                apiFetch('/api/logout', { method: 'POST' })
                    .then(() => window.location.href = '/login')
                    .catch(() => window.location.href = '/login');
            }

            function escapeReportHtml(value) {
                return String(value ?? '').replace(/[&<>\"']/g, character => ({
                    '&': '&amp;', '<': '&lt;', '>': '&gt;', '\"': '&quot;', "'": '&#039;'
                }[character]));
            }

            function filterReportEvents(events, startedAt, endedAt) {
                if (!startedAt) return events || [];
                const start = new Date(startedAt).getTime();
                const end = endedAt ? new Date(endedAt).getTime() : Date.now();
                return (events || []).filter(event => {
                    const timestamp = new Date(event.timestamp).getTime();
                    return timestamp >= start && timestamp <= end;
                });
            }

            function formatReportDuration(startedAt, endedAt) {
                if (!startedAt) return 'N/A';
                const start = new Date(startedAt);
                const end = endedAt ? new Date(endedAt) : new Date();
                const seconds = Math.max(0, Math.floor((end - start) / 1000));
                const hours = Math.floor(seconds / 3600);
                const minutes = Math.floor((seconds % 3600) / 60);
                const remainingSeconds = seconds % 60;
                return `${hours}h ${minutes}m ${remainingSeconds}s${endedAt ? '' : ' (ongoing)'}`;
            }

            async function loadInlineReport() {
                const reportBody = document.getElementById('reportEventBody');
                const refreshButton = document.getElementById('reportRefreshBtn');
                if (!reportBody) return;
                if (refreshButton) {
                    refreshButton.disabled = true;
                    refreshButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading report';
                }
                reportBody.innerHTML = '<tr><td colspan="4" class="report-empty">Loading report...</td></tr>';
                try {
                    const response = await apiFetch('/api/integrity_report');
                    const payload = await response.json();
                    if (!response.ok) throw new Error(payload.error || `Report request failed (HTTP ${response.status})`);

                    const user = payload.user || {};
                    const stats = payload.stats || {};
                    const events = filterReportEvents(payload.events, stats.started_at, stats.ended_at);
                    const score = payload.score ?? payload.final_score ?? payload.integrity_score ?? 'N/A';
                    const remark = score >= 90 ? 'Excellent' : score >= 70 ? 'Good' : score >= 50 ? 'Fair' : 'Needs Improvement';
                    const reviews = payload.reviews || [];
                    const setReportText = (id, value) => {
                        const element = document.getElementById(id);
                        if (element) element.textContent = value ?? 'N/A';
                    };

                    setReportText('reportName', user.name || 'N/A');
                    setReportText('reportStudentId', user.student_id || 'N/A');
                    setReportText('reportSessionId', user.session_id || 'N/A');
                    setReportText('reportScore', score);
                    setReportText('reportRemark', remark);
                    setReportText('reportReviewState', reviews.length ? reviews[0].decision : (stats.review_state || 'Not Reviewed'));
                    setReportText('reportStart', stats.started_at || (events[0] && events[0].timestamp) || 'N/A');
                    setReportText('reportEnd', stats.ended_at || (events.length && events[events.length - 1].timestamp) || 'N/A');
                    setReportText('reportDuration', formatReportDuration(stats.started_at, stats.ended_at));
                    setReportText('reportStatus', stats.exam_running ? 'In Progress' : (stats.started_at ? 'Completed' : 'Not Started'));
                    setReportText('reportRisk', payload.risk_label || 'N/A');
                    setReportText('reportFaceRatio', payload.face_ratio !== undefined ? `${payload.face_ratio}%` : 'N/A');
                    setReportText('reportFaceAbsence', events.filter(event => event.type === 'Face Absence').length);
                    setReportText('reportFocusLoss', events.filter(event => event.type === 'Browser Focus Loss').length);
                    setReportText('reportSuspicious', events.filter(event => Number(event.deducted) > 0).length);

                    if (!events.length) {
                        reportBody.innerHTML = '<tr><td colspan="4" class="report-empty">No events recorded in this session.</td></tr>';
                    } else {
                        reportBody.innerHTML = events.map(event => {
                            const screenshot = event.screenshot_path
                                ? `<span class="report-screenshot" style="color: #4dabf7; cursor: pointer; text-decoration: underline;" data-screenshot="${escapeReportHtml(event.screenshot_path)}">View</span>`
                                : '<span style="color:rgba(255,255,255,0.25);">No</span>';
                            const deductedHtml = event.deducted > 0 ? `<span style="color: #ff6b6b;">${escapeReportHtml(event.deducted)}</span>` : '0';
                            return `<tr><td>${escapeReportHtml(event.type || 'Event')}</td><td>${escapeReportHtml(event.timestamp || 'N/A')}</td><td>${deductedHtml}</td><td>${screenshot}</td></tr>`;
                        }).join('');
                        reportBody.querySelectorAll('[data-screenshot]').forEach(link => {
                            link.addEventListener('click', () => {
                                const url = `/evidence/${encodeURIComponent(link.dataset.screenshot)}`;
                                if (document.getElementById('screenshotModalImg') && document.getElementById('screenshotModal')) {
                                    document.getElementById('screenshotModalImg').src = url;
                                    document.getElementById('screenshotModal').classList.add('is-open');
                                } else {
                                    window.open(url, '_blank', 'noopener');
                                }
                            });
                        });
                    }
                } catch (error) {
                    reportBody.innerHTML = `<tr><td colspan="4" class="report-empty">Unable to load report: ${escapeReportHtml(error.message)}</td></tr>`;
                } finally {
                    if (refreshButton) {
                        refreshButton.disabled = false;
                        refreshButton.innerHTML = '<i class="fas fa-sync-alt"></i> Refresh report';
                    }
                }
            }

            function generateReport() {
                switchDashboardTab('report');
            }

            // ----- Start Exam button on dashboard (opens wizard) -----
            startBtn.addEventListener('click', function() {
                if (examRunning) return;
                openWizard();
            });

            // Dropdown listeners removed because UI changed
            window.switchDashboardTab = function(panelName) {
                document.querySelectorAll('.tab').forEach(btn => btn.classList.remove('active'));
                const activeBtn = Array.from(document.querySelectorAll('.tab')).find(btn => btn.getAttribute('onclick') && btn.getAttribute('onclick').includes(panelName));
                if (activeBtn) activeBtn.classList.add('active');
                document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
                const targetPanel = document.getElementById('panel' + panelName.charAt(0).toUpperCase() + panelName.slice(1));
                if (targetPanel) targetPanel.classList.add('active');

                const examControls = document.querySelector('.exam-controls');
                const integrityScore = document.querySelector('.integrity-score');
                if (examControls) {
                    examControls.style.display = (panelName === 'candidate') ? 'flex' : 'none';
                }
                if (integrityScore) {
                    integrityScore.style.display = (panelName === 'candidate') ? 'flex' : 'none';
                }

                if (panelName === 'session') { renderEventLog(sessionEvents); renderTimeline(sessionEvents); }
                else if (panelName === 'stats') { drawPieChart(sessionEvents); }
                                else if (panelName === 'report') { loadInlineReport(); }

            };

                        document.getElementById('reportRefreshBtn')?.addEventListener('click', loadInlineReport);
            // ----- Event listeners for exam controls -----
            togglePauseBtn.addEventListener('click', togglePause);

            endBtn.addEventListener('click', endExam);
            logoutBtn.addEventListener('click', logout);

            // ----- Init -----
            setupProfileModal();
            setupOfflineCache();
            loadDashboard();
            setupFocusHandlers();
            setupNetworkStatus();

            // Add camera section container (hidden initially) for main exam
            const cameraSection = document.createElement('div');
            cameraSection.id = 'cameraSection';
            cameraSection.className = 'camera-section';
            cameraSection.innerHTML = `
                <div class="camera-container">
                    <video id="video" autoplay playsinline></video>
                    <canvas id="overlayCanvas"></canvas>
                </div>
            `;
            document.body.appendChild(cameraSection);

                // ====== SYSTEM DIAGNOSTICS LOGIC ======
        const sysDiagBtn = document.getElementById('sysDiagBtn');
        const runSysDiagBtn = document.getElementById('runSysDiagBtn');

        if (sysDiagBtn) {
            sysDiagBtn.addEventListener('click', () => {
                const systemDiagModal = document.getElementById('systemDiagModal');
                if (systemDiagModal) systemDiagModal.classList.add('is-open');
            });
        }
        document.body.addEventListener('click', (e) => {
            const systemDiagModal = document.getElementById('systemDiagModal');
            if (!systemDiagModal) return;
            if (e.target.closest('#sysDiagCloseBtn') || e.target === systemDiagModal) {
                systemDiagModal.classList.remove('is-open');
            }
        });

        const setDiagItemState = (id, state, message) => {
            const li = document.getElementById(id);
            if (!li) return;
            const icon = li.querySelector('i');
            const span = li.querySelector('span');
            if (state === 'loading') {
                icon.className = 'fas fa-spinner fa-spin';
                icon.style.color = '#fff';
            } else if (state === 'success') {
                icon.className = 'fas fa-check-circle';
                icon.style.color = '#51cf66';
            } else if (state === 'error') {
                icon.className = 'fas fa-times-circle';
                icon.style.color = '#ff6b6b';
            }
            if (message) span.textContent = message;
        };

        if (runSysDiagBtn) {
            runSysDiagBtn.addEventListener('click', async () => {
                runSysDiagBtn.disabled = true;
                runSysDiagBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Running...';
                
                const ids = ['chkBrowser', 'chkCamera', 'chkMic', 'chkNetwork'];
                ids.forEach(id => setDiagItemState(id, 'loading', 'Checking...'));

                // 1. Browser
                await new Promise(r => setTimeout(r, 600));
                const isSupported = !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
                setDiagItemState('chkBrowser', isSupported ? 'success' : 'error', isSupported ? 'Browser is compatible' : 'Incompatible browser');

                // 2. Camera
                if (isSupported) {
                    try {
                        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                        stream.getTracks().forEach(t => t.stop());
                        setDiagItemState('chkCamera', 'success', 'Camera access granted');
                    } catch (err) {
                        setDiagItemState('chkCamera', 'error', 'Camera access denied or unavailable');
                    }
                } else {
                    setDiagItemState('chkCamera', 'error', 'Cannot test camera');
                }

                // 3. Mic
                if (isSupported) {
                    try {
                        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                        stream.getTracks().forEach(t => t.stop());
                        setDiagItemState('chkMic', 'success', 'Microphone access granted');
                    } catch (err) {
                        setDiagItemState('chkMic', 'error', 'Microphone access denied or unavailable');
                    }
                } else {
                    setDiagItemState('chkMic', 'error', 'Cannot test microphone');
                }

                // 4. Network
                await new Promise(r => setTimeout(r, 500));
                if (navigator.onLine) {
                    try {
                        const start = performance.now();
                        await fetch('/api/network/health?ts=' + Date.now());
                        const ping = Math.round(performance.now() - start);
                        setDiagItemState('chkNetwork', 'success', 'Connected (' + ping + 'ms latency)');
                    } catch (err) {
                        setDiagItemState('chkNetwork', 'error', 'Network unstable');
                    }
                } else {
                    setDiagItemState('chkNetwork', 'error', 'Offline');
                }

                runSysDiagBtn.disabled = false;
                runSysDiagBtn.innerHTML = '<i class="fas fa-sync-alt"></i> Run Diagnostics Again';
            });
        }

})();
    