// Ambient HUD Animations
document.addEventListener("DOMContentLoaded", () => {
    const crosshair = document.querySelector('.crosshair');
    if (crosshair) {
        setInterval(() => {
            // Pulse effect
            crosshair.style.opacity = (Math.random() * 0.5 + 0.5).toFixed(2);
        }, 1000);
    }

    const labels = document.querySelectorAll('.metric-label');
    labels.forEach(label => {
        label.addEventListener('mouseover', () => {
            label.style.color = 'var(--neon-green)';
            label.style.textShadow = '0 0 10px var(--neon-green)';
        });
        label.addEventListener('mouseout', () => {
            label.style.color = 'var(--text-muted)';
            label.style.textShadow = 'none';
        });
    });

    const terminalLogs = document.querySelectorAll('.term-body');
    terminalLogs.forEach(term => {
        // Occasional pseudo-glitch on idle logs
        setInterval(() => {
            if (Math.random() > 0.9) {
                term.style.transform = `translate(${Math.random() * 2 - 1}px, 0)`;
                term.style.opacity = 0.8;
                setTimeout(() => {
                    term.style.transform = 'none';
                    term.style.opacity = 1;
                }, 50);
            }
        }, 2000);
    });
});
