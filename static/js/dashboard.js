/**
 * SENTINEL X — Threat Analysis Dashboard Controller (Phase 4)
 * Student PRN: 202401110046
 */

document.addEventListener('DOMContentLoaded', () => {
    const emptyStateCard = document.getElementById('empty-state-card');
    const dashboardContent = document.getElementById('dashboard-content');
    
    const statTotal = document.getElementById('stat-total-scans');
    const statSuspicious = document.getElementById('stat-suspicious-count');
    const statClean = document.getElementById('stat-clean-count');
    const statRate = document.getElementById('stat-detection-rate');
    
    const latestBadge = document.getElementById('latest-scan-status-badge');
    const latestDetails = document.getElementById('latest-scan-details');
    const historyBody = document.getElementById('history-table-body');
    const historyCountBadge = document.getElementById('history-count-badge');
    
    const btnExportJson = document.getElementById('btn-export-json');
    const btnExportCsv = document.getElementById('btn-export-csv');
    const btnClearHistory = document.getElementById('btn-clear-history');

    let verdictChartInstance = null;
    let categoryChartInstance = null;
    let timelineChartInstance = null;

    function loadDashboard() {
        const history = getScanHistory();

        if (!history || history.length === 0) {
            if (emptyStateCard) emptyStateCard.style.display = 'block';
            if (dashboardContent) dashboardContent.style.display = 'none';
            return;
        }

        if (emptyStateCard) emptyStateCard.style.display = 'none';
        if (dashboardContent) dashboardContent.style.display = 'block';

        // 1. Calculate Summary Stats
        const total = history.length;
        const suspiciousCount = history.filter(s => s.is_suspicious).length;
        const cleanCount = total - suspiciousCount;
        const detectionRate = total > 0 ? Math.round((suspiciousCount / total) * 100) : 0;

        if (statTotal) statTotal.textContent = total;
        if (statSuspicious) statSuspicious.textContent = suspiciousCount;
        if (statClean) statClean.textContent = cleanCount;
        if (statRate) statRate.textContent = `${detectionRate}%`;
        if (historyCountBadge) historyCountBadge.textContent = `${total} Record${total === 1 ? '' : 's'}`;

        // 2. Render Latest Scan Breakdown
        // Prioritize session latest if present, otherwise first history entry
        let latestScan = null;
        try {
            const rawSession = sessionStorage.getItem('sentinel_latest_scan');
            if (rawSession) latestScan = JSON.parse(rawSession);
        } catch (e) {}

        if (!latestScan && history.length > 0) {
            latestScan = history[0];
        }

        renderLatestScan(latestScan);

        // 3. Render Charts
        renderCharts(history, suspiciousCount, cleanCount);

        // 4. Render History Table
        renderHistoryTable(history);
    }

    function renderLatestScan(scan) {
        if (!scan || !latestDetails) return;

        const isSuspicious = scan.is_suspicious;

        if (latestBadge) {
            latestBadge.innerHTML = isSuspicious 
                ? `<span class="badge badge-danger">${escapeHtml(scan.status || 'SUSPICIOUS INDICATOR DETECTED')}</span>`
                : `<span class="badge badge-clean">${escapeHtml(scan.status || 'NO CONFIGURED INDICATOR MATCHED')}</span>`;
        }

        const matchedRules = scan.matched_rules || [];
        const rulesListHtml = matchedRules.length > 0
            ? matchedRules.map(r => `
                <div style="background: var(--bg-secondary); border: 1px solid var(--bg-card-border); border-radius: var(--radius-md); padding: 1rem; margin-top: 0.75rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <strong style="color: var(--text-primary); font-size: 1rem;">${escapeHtml(r.name)}</strong>
                            <span class="badge badge-purple">${escapeHtml(r.category)}</span>
                            <span class="badge badge-danger">${escapeHtml(r.severity || 'HIGH')}</span>
                        </div>
                        <span class="font-mono" style="font-size: 0.8rem; color: var(--accent-cyan);">${r.match_count} match${r.match_count > 1 ? 'es' : ''}</span>
                    </div>

                    <div style="margin-bottom: 0.5rem;">
                        <span style="font-size: 0.8rem; color: var(--text-muted);">Regex Pattern:</span>
                        <code style="display: block; background: #08172b; padding: 0.4rem 0.6rem; border-radius: 4px; font-size: 0.85rem; color: var(--accent-cyan); margin-top: 0.2rem;">${escapeHtml(r.pattern)}</code>
                    </div>

                    <div style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.5;">
                        <strong style="color: var(--text-muted);">Explanation:</strong> ${escapeHtml(r.explanation || r.purpose)}
                    </div>
                </div>
            `).join('')
            : `<div style="padding: 1rem; background: var(--bg-secondary); border-radius: var(--radius-md); font-size: 0.9rem; color: var(--color-success); border-left: 3px solid var(--color-success); margin-top: 0.75rem;">
                No suspicious regular expression signatures were triggered by this input. All pattern rules evaluated clean.
               </div>`;

        latestDetails.innerHTML = `
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 1rem; font-family: var(--font-mono); font-size: 0.85rem;">
                <div style="background: var(--bg-secondary); padding: 0.65rem 0.85rem; border-radius: 6px;">
                    <span style="color: var(--text-muted);">Timestamp:</span>
                    <div style="color: var(--text-primary); font-weight: 600;">${escapeHtml(scan.timestamp || 'N/A')}</div>
                </div>
                <div style="background: var(--bg-secondary); padding: 0.65rem 0.85rem; border-radius: 6px;">
                    <span style="color: var(--text-muted);">Execution Latency:</span>
                    <div style="color: var(--accent-cyan); font-weight: 600;">${scan.scan_duration_ms || 0} ms</div>
                </div>
                <div style="background: var(--bg-secondary); padding: 0.65rem 0.85rem; border-radius: 6px;">
                    <span style="color: var(--text-muted);">Rules Triggered:</span>
                    <div style="color: ${isSuspicious ? 'var(--color-danger)' : 'var(--color-success)'}; font-weight: 600;">
                        ${matchedRules.length} / 5 Rules
                    </div>
                </div>
            </div>

            <div>
                <div style="font-weight: 600; font-size: 0.9rem; margin-bottom: 0.4rem;">
                    Input Payload &amp; Match Highlighting:
                </div>
                <div style="background: #08172b; padding: 1rem; border-radius: var(--radius-md); font-family: var(--font-mono); font-size: 0.88rem; word-break: break-all; border: 1px solid var(--bg-card-border); max-height: 200px; overflow-y: auto;">
                    ${scan.highlighted_html || escapeHtml(scan.full_input || scan.input_snippet || '')}
                </div>
            </div>

            <div style="margin-top: 1rem;">
                <div style="font-weight: 600; font-size: 0.9rem; margin-bottom: 0.4rem;">
                    Detection Rule Details:
                </div>
                ${rulesListHtml}
            </div>
        `;
    }

    function renderCharts(history, suspiciousCount, cleanCount) {
        // Chart 1: Verdict Doughnut
        const ctxVerdicts = document.getElementById('chart-verdicts');
        if (ctxVerdicts) {
            if (verdictChartInstance) verdictChartInstance.destroy();
            verdictChartInstance = new Chart(ctxVerdicts, {
                type: 'doughnut',
                data: {
                    labels: ['Suspicious Findings', 'No-Match / Clean'],
                    datasets: [{
                        data: [suspiciousCount, cleanCount],
                        backgroundColor: ['#FF5263', '#20C997'],
                        borderColor: '#102640',
                        borderWidth: 3,
                        hoverOffset: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: { color: '#A8B8CC', font: { family: 'Inter', size: 12 } }
                        }
                    },
                    cutout: '70%'
                }
            });
        }

        // Chart 2: Category Distribution Bar
        const categoryCounts = {
            'SQL Injection': 0,
            'Script Injection': 0,
            'Directory Traversal': 0,
            'Command Injection': 0,
            'Phishing / Malicious URL': 0
        };

        history.forEach(scan => {
            if (scan.matched_rules) {
                scan.matched_rules.forEach(r => {
                    const cat = r.category || 'Other';
                    if (categoryCounts[cat] !== undefined) {
                        categoryCounts[cat] += r.match_count || 1;
                    }
                });
            }
        });

        const ctxCategories = document.getElementById('chart-categories');
        if (ctxCategories) {
            if (categoryChartInstance) categoryChartInstance.destroy();
            categoryChartInstance = new Chart(ctxCategories, {
                type: 'bar',
                data: {
                    labels: Object.keys(categoryCounts),
                    datasets: [{
                        label: 'Matches',
                        data: Object.values(categoryCounts),
                        backgroundColor: [
                            'rgba(37, 137, 255, 0.75)',
                            'rgba(53, 213, 255, 0.75)',
                            'rgba(128, 103, 255, 0.75)',
                            'rgba(255, 82, 99, 0.75)',
                            'rgba(255, 171, 0, 0.75)'
                        ],
                        borderColor: [
                            '#2589FF', '#35D5FF', '#8067FF', '#FF5263', '#FFAB00'
                        ],
                        borderWidth: 1,
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        x: {
                            ticks: { color: '#A8B8CC', font: { size: 10 } },
                            grid: { display: false }
                        },
                        y: {
                            beginAtZero: true,
                            ticks: { color: '#A8B8CC', stepSize: 1 },
                            grid: { color: 'rgba(30, 61, 102, 0.4)' }
                        }
                    }
                }
            });
        }

        // Chart 3: Latency Line
        const recentSubset = history.slice(0, 10).reverse();
        const ctxTimeline = document.getElementById('chart-timeline');
        if (ctxTimeline) {
            if (timelineChartInstance) timelineChartInstance.destroy();
            timelineChartInstance = new Chart(ctxTimeline, {
                type: 'line',
                data: {
                    labels: recentSubset.map((s, idx) => `Scan #${idx + 1}`),
                    datasets: [{
                        label: 'Execution Latency (ms)',
                        data: recentSubset.map(s => s.scan_duration_ms || 0.1),
                        borderColor: '#35D5FF',
                        backgroundColor: 'rgba(53, 213, 255, 0.15)',
                        borderWidth: 2,
                        tension: 0.35,
                        fill: true,
                        pointBackgroundColor: '#35D5FF',
                        pointRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        x: {
                            ticks: { color: '#A8B8CC', font: { size: 10 } },
                            grid: { display: false }
                        },
                        y: {
                            beginAtZero: true,
                            ticks: { color: '#A8B8CC' },
                            grid: { color: 'rgba(30, 61, 102, 0.4)' }
                        }
                    }
                }
            });
        }
    }

    function renderHistoryTable(history) {
        if (!historyBody) return;
        historyBody.innerHTML = '';

        history.forEach((scan, index) => {
            const tr = document.createElement('tr');
            const isSuspicious = scan.is_suspicious;
            const badgeClass = isSuspicious ? 'badge-danger' : 'badge-clean';
            const badgeText = isSuspicious ? 'SUSPICIOUS' : 'NO-MATCH';

            tr.innerHTML = `
                <td class="font-mono" style="font-size: 0.8rem; color: var(--accent-cyan);">${escapeHtml(scan.id || `SCAN-${index + 1}`)}</td>
                <td class="font-mono" style="font-size: 0.8rem; color: var(--text-muted);">${escapeHtml(scan.timestamp || '')}</td>
                <td class="font-mono" style="font-size: 0.85rem; max-width: 260px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                    ${escapeHtml(scan.input_snippet || scan.full_input || '')}
                </td>
                <td><span class="badge ${badgeClass}">${badgeText}</span></td>
                <td class="font-mono" style="font-size: 0.85rem;">${scan.matched_rules_count || 0} Rule(s)</td>
                <td class="font-mono" style="font-size: 0.85rem; color: var(--text-secondary);">${scan.scan_duration_ms || 0} ms</td>
                <td>
                    <button class="btn btn-secondary btn-sm btn-inspect" data-index="${index}">
                        Inspect
                    </button>
                </td>
            `;

            historyBody.appendChild(tr);
        });

        // Add Inspect event listeners
        document.querySelectorAll('.btn-inspect').forEach(btn => {
            btn.addEventListener('click', () => {
                const idx = parseInt(btn.getAttribute('data-index'), 10);
                const scan = history[idx];
                inspectScanModal(scan);
            });
        });
    }

    function inspectScanModal(scan) {
        if (!scan) return;

        let rulesHtml = '';
        if (scan.matched_rules && scan.matched_rules.length > 0) {
            rulesHtml = `
                <div style="margin-top: 1rem;">
                    <h4 style="margin-bottom: 0.5rem; color: var(--accent-cyan);">Matched Rules:</h4>
                    ${scan.matched_rules.map(r => `
                        <div style="background: var(--bg-secondary); border: 1px solid var(--bg-card-border); padding: 0.75rem; border-radius: 6px; margin-bottom: 0.5rem;">
                            <div style="display: flex; justify-content: space-between;">
                                <strong>${escapeHtml(r.name)}</strong>
                                <span class="badge badge-danger">${r.match_count} match(es)</span>
                            </div>
                            <code style="display:block; margin: 0.3rem 0; font-size: 0.8rem; color: var(--accent-cyan);">${escapeHtml(r.pattern)}</code>
                            <p style="font-size: 0.8rem; margin: 0;">${escapeHtml(r.explanation || r.purpose)}</p>
                        </div>
                    `).join('')}
                </div>
            `;
        }

        const content = `
            <div style="display: flex; justify-content: space-between; margin-bottom: 1rem;">
                <span class="badge ${scan.is_suspicious ? 'badge-danger' : 'badge-clean'}">${escapeHtml(scan.status || '')}</span>
                <span class="font-mono" style="font-size: 0.8rem; color: var(--text-muted);">${escapeHtml(scan.timestamp || '')}</span>
            </div>
            <div>
                <strong>Payload Content:</strong>
                <pre style="background: #08172b; padding: 0.85rem; border-radius: 6px; font-size: 0.85rem; margin-top: 0.4rem; white-space: pre-wrap; word-break: break-all; border: 1px solid var(--bg-card-border);">${escapeHtml(scan.full_input || scan.input_snippet || '')}</pre>
            </div>
            ${rulesHtml}
            <div style="margin-top: 1.25rem; display: flex; justify-content: flex-end;">
                <button class="btn btn-secondary btn-sm" onclick="closeModal()">Close</button>
            </div>
        `;

        openModal(`Scan Inspection: ${scan.id || 'Details'}`, content);
    }

    // Export JSON
    if (btnExportJson) {
        btnExportJson.addEventListener('click', () => {
            const history = getScanHistory();
            if (!history || history.length === 0) {
                showToast('No scan telemetry available to export.', 'danger');
                return;
            }
            exportToJson(history, 'sentinel-x-threat-scans.json');
        });
    }

    // Export CSV
    if (btnExportCsv) {
        btnExportCsv.addEventListener('click', () => {
            const history = getScanHistory();
            if (!history || history.length === 0) {
                showToast('No scan telemetry available to export.', 'danger');
                return;
            }
            const headers = ['Scan ID', 'Timestamp', 'Verdict', 'Suspicious', 'Rules Triggered', 'Duration (ms)', 'Input Payload'];
            const rows = history.map(s => [
                s.id || '',
                s.timestamp || '',
                s.status || '',
                s.is_suspicious ? 'YES' : 'NO',
                s.matched_rules_count || 0,
                s.scan_duration_ms || 0,
                s.full_input || s.input_snippet || ''
            ]);
            exportToCsv(headers, rows, 'sentinel-x-threat-scans.csv');
        });
    }

    // Clear History
    if (btnClearHistory) {
        btnClearHistory.addEventListener('click', () => {
            if (confirm('Are you sure you want to clear all scan telemetry history?')) {
                clearScanHistory();
                sessionStorage.removeItem('sentinel_latest_scan');
                loadDashboard();
            }
        });
    }

    // Initialize Dashboard
    loadDashboard();
});

