let focusLossCount = 0;
let lostState = false;

function sendBrowserEvent(eventType) {
    fetch("/browser_event", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            event: eventType
        })
    }).catch(function (err) {
        console.error(`Failed to send browser_event ${eventType}:`, err);
    });
}

function updateInactiveState() {
    if (lostState) {
        return;
    }

    lostState = true;
    let statusEl = document.getElementById("browser-status");
    if (statusEl) statusEl.innerHTML = "Inactive";

    focusLossCount++;
    let countEl = document.getElementById("focus-count");
    if (countEl) countEl.innerHTML = focusLossCount;

    let currentTime = new Date().toLocaleTimeString();
    let lastEl = document.getElementById("last-focus");
    if (lastEl) lastEl.innerHTML = currentTime;

    console.log("Browser Lost Focus / Tab changed");
    sendBrowserEvent("lost");
}

function updateActiveState() {
    if (!lostState) {
        return;
    }

    lostState = false;
    let statusEl = document.getElementById("browser-status");
    if (statusEl) statusEl.innerHTML = "Active";

    console.log("Browser Active");
    sendBrowserEvent("regained");
}

if (typeof document.hidden !== "undefined") {
    document.addEventListener("visibilitychange", function () {
        if (document.hidden) {
            updateInactiveState();
        } else {
            updateActiveState();
        }
    });
} else {
    window.addEventListener("blur", updateInactiveState);
    window.addEventListener("focus", updateActiveState);
}
