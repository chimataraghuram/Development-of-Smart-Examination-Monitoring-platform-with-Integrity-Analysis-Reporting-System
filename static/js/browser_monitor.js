let focusLossCount = 0;

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

window.addEventListener("blur", function () {
    let statusEl = document.getElementById("browser-status");
    if (statusEl) statusEl.innerHTML = "Inactive";

    focusLossCount++;
    let countEl = document.getElementById("focus-count");
    if (countEl) countEl.innerHTML = focusLossCount;

    let currentTime = new Date().toLocaleTimeString();
    let lastEl = document.getElementById("last-focus");
    if (lastEl) lastEl.innerHTML = currentTime;

    console.log("Browser Lost Focus");
    sendBrowserEvent("lost");
});

window.addEventListener("focus", function () {
    let statusEl = document.getElementById("browser-status");
    if (statusEl) statusEl.innerHTML = "Active";

    console.log("Browser Active");
    sendBrowserEvent("regained");
});
