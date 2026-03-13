let currentMode = 'webcam';
let telemetryInterval = null;

function setMode(mode) {
    currentMode = mode;
    
    // Update active button
    document.querySelectorAll('.mode-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById(`btn-${mode}`).classList.add('active');
    
    const uploadControls = document.getElementById('upload-controls');
    const mainDisplay = document.getElementById('main-display');
    
    if (mode === 'webcam') {
        uploadControls.classList.add('hidden');
        mainDisplay.src = '/video_feed?mode=webcam';
        logMessage("Webcam stream initialized. Re-calibrating optics...");
        startTelemetryPolling();
    } else {
        uploadControls.classList.remove('hidden');
        mainDisplay.src = ''; // Clear image
        logMessage(`Awaiting ${mode} source package...`);
        stopTelemetryPolling();
    }
}

async function processUpload() {
    const fileInput = document.getElementById('file-upload');
    const file = fileInput.files[0];
    if (!file) {
        logMessage("ERROR: No target file verified.", "red");
        return;
    }
    
    logMessage(`Ingesting source block: ${file.name}...`);
    document.getElementById('upload-status').classList.remove('hidden');
    
    const formData = new FormData();
    formData.append("file", file);
    
    const endpoint = currentMode === 'video' ? '/detect-video' : '/detect-image';
    
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        
        if (data.status === "success") {
            logMessage(`Pipeline processing complete.`);
            const mainDisplay = document.getElementById('main-display');
            
            if (currentMode === 'video') {
                mainDisplay.src = `/video_feed?mode=video&filepath=${encodeURIComponent(data.filepath)}`;
                startTelemetryPolling();
            } else {
                // Add timestamp to prevent caching
                mainDisplay.src = `/${data.filepath}?t=${new Date().getTime()}`;
                updateTelemetryUI(data.stats);
            }
        } else {
            logMessage(`CRITICAL ERROR: ${data.message}`, "red");
        }
    } catch (err) {
        logMessage(`CRITICAL ERROR: ${err.message}`, "red");
    } finally {
        document.getElementById('upload-status').classList.add('hidden');
    }
}

function startTelemetryPolling() {
    if (telemetryInterval) clearInterval(telemetryInterval);
    telemetryInterval = setInterval(async () => {
        try {
            const res = await fetch('/telemetry');
            const data = await res.json();
            updateTelemetryUI(data);
        } catch (e) {
            console.error("Telemetry socket timeout.");
        }
    }, 1000);
}

function stopTelemetryPolling() {
    if (telemetryInterval) {
        clearInterval(telemetryInterval);
        telemetryInterval = null;
    }
}

function updateTelemetryUI(stats) {
    if(!stats) return;
    document.getElementById('t-fps').innerText = stats.fps;
    document.getElementById('t-total').innerText = stats.total_count;
    document.getElementById('t-active').innerText = stats.active_count;
    
    // Update FPS bar pseudo-visual (assuming target FPS ~30 for green bar)
    let percent = Math.min((stats.fps / 30) * 100, 100);
    document.getElementById('bar-fps').style.width = `${percent}%`;
}

function logMessage(msg, color="#0f0") {
    const logContainer = document.getElementById('sys-log');
    const p = document.createElement('p');
    p.innerText = `> ${msg}`;
    p.style.color = color;
    logContainer.appendChild(p);
    logContainer.scrollTop = logContainer.scrollHeight;
}

// Initialize boot seq
window.onload = () => {
    logMessage("Booting AutoTrack Engine...");
    setTimeout(() => {
        setMode('webcam');
        logMessage("Neural Link Established.");
    }, 500);
};
