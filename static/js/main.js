/**
 * SENTINEL X — Main UI & Utilities
 * Student PRN: 202401110046
 */

// ================= AMBIENT CYBER CANVAS =================
(function initCyberCanvas() {
    const canvas = document.getElementById('cyber-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    let width, height;
    let particles = [];
    const particleCount = 45;
    const maxDistance = 140;

    function resize() {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    }

    function createParticles() {
        particles = [];
        for (let i = 0; i < particleCount; i++) {
            particles.push({
                x: Math.random() * width,
                y: Math.random() * height,
                vx: (Math.random() - 0.5) * 0.6,
                vy: (Math.random() - 0.5) * 0.6,
                radius: Math.random() * 2 + 1,
                color: Math.random() > 0.4 ? 'rgba(53, 213, 255, ' : 'rgba(37, 137, 255, '
            });
        }
    }

    function animate() {
        ctx.clearRect(0, 0, width, height);

        for (let i = 0; i < particles.length; i++) {
            const p = particles[i];
            p.x += p.vx;
            p.y += p.vy;

            if (p.x < 0 || p.x > width) p.vx *= -1;
            if (p.y < 0 || p.y > height) p.vy *= -1;

            ctx.beginPath();
            ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            ctx.fillStyle = p.color + '0.6)';
            ctx.fill();

            // Connect nearby particles
            for (let j = i + 1; j < particles.length; j++) {
                const p2 = particles[j];
                const dx = p.x - p2.x;
                const dy = p.y - p2.y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < maxDistance) {
                    const alpha = (1 - dist / maxDistance) * 0.25;
                    ctx.beginPath();
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.strokeStyle = `rgba(37, 137, 255, ${alpha})`;
                    ctx.lineWidth = 0.8;
                    ctx.stroke();
                }
            }
        }
        requestAnimationFrame(animate);
    }

    window.addEventListener('resize', () => {
        resize();
        createParticles();
    });

    resize();
    createParticles();
    animate();
})();

// ================= TOAST SYSTEM =================
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    let icon = 'ℹ️';
    if (type === 'success') icon = '✓';
    if (type === 'danger') icon = '⚠️';

    toast.innerHTML = `
        <span style="font-weight:bold; font-size:1.1rem;">${icon}</span>
        <span style="flex:1;">${escapeHtml(message)}</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(50px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ================= MODAL SYSTEM =================
function openModal(title, htmlContent) {
    const modal = document.getElementById('global-modal');
    const titleEl = document.getElementById('modal-title');
    const bodyEl = document.getElementById('modal-body');
    if (!modal || !titleEl || !bodyEl) return;

    titleEl.textContent = title;
    bodyEl.innerHTML = htmlContent;
    modal.classList.add('active');
}

function closeModal() {
    const modal = document.getElementById('global-modal');
    if (modal) modal.classList.remove('active');
}

// Close modal when clicking outside
window.addEventListener('click', (e) => {
    const modal = document.getElementById('global-modal');
    if (modal && e.target === modal) {
        closeModal();
    }
});

// ================= LOCAL STORAGE HISTORY =================
const STORAGE_KEY = 'sentinel_x_scan_history';

function getScanHistory() {
    try {
        const raw = localStorage.getItem(STORAGE_KEY);
        return raw ? JSON.parse(raw) : [];
    } catch (e) {
        console.error('Failed to read scan history:', e);
        return [];
    }
}

function saveScanResult(scanData) {
    try {
        const history = getScanHistory();
        // Prepend latest scan
        history.unshift({
            id: 'SCAN-' + Date.now().toString(36).toUpperCase(),
            timestamp: scanData.timestamp || new Date().toLocaleString(),
            input_snippet: (scanData.original_input || '').substring(0, 100),
            full_input: scanData.original_input || '',
            is_suspicious: scanData.is_suspicious,
            status: scanData.status,
            matched_rules_count: scanData.matched_rules_count || 0,
            matched_rules: scanData.matched_rules || [],
            scan_duration_ms: scanData.scan_duration_ms || 0
        });

        // Retain max 50 recent scans
        if (history.length > 50) history.pop();
        localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
    } catch (e) {
        console.error('Failed to save scan result:', e);
    }
}

function clearScanHistory() {
    try {
        localStorage.removeItem(STORAGE_KEY);
        showToast('Scan history cleared successfully.', 'info');
    } catch (e) {
        console.error('Failed to clear history:', e);
    }
}

// ================= UTILITIES =================
function escapeHtml(str) {
    if (!str) return '';
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showToast('Copied to clipboard!', 'success');
        }).catch(() => {
            showToast('Failed to copy', 'danger');
        });
    } else {
        const ta = document.createElement('textarea');
        ta.value = text;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        showToast('Copied to clipboard!', 'success');
    }
}

function exportToJson(data, filename = 'sentinel-x-export.json') {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
    showToast(`Exported ${filename}`, 'success');
}

function exportToCsv(headers, rows, filename = 'sentinel-x-scans.csv') {
    const escapeCsv = (val) => {
        if (val === null || val === undefined) return '""';
        const str = String(val).replace(/"/g, '""');
        return `"${str}"`;
    };

    const lines = [headers.map(escapeCsv).join(',')];
    rows.forEach(row => {
        lines.push(row.map(escapeCsv).join(','));
    });

    const csvContent = lines.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
    showToast(`Exported ${filename}`, 'success');
}

