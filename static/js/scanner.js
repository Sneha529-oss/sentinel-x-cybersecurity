/**
 * SENTINEL X — Threat Scanner Controller (Phase 2 & Phase 3 integration)
 * Student PRN: 202401110046
 */

document.addEventListener('DOMContentLoaded', () => {
    const threatInput = document.getElementById('threat-input');
    const charCounter = document.getElementById('char-counter');
    const btnClear = document.getElementById('btn-clear-input');
    const scannerForm = document.getElementById('scanner-form');
    const categorySelect = document.getElementById('threat-category');
    const btnAnalyze = document.getElementById('btn-analyze');
    const btnText = document.getElementById('btn-text');
    const btnSpinner = document.getElementById('btn-spinner');
    
    const quickResultCard = document.getElementById('quick-result-card');
    const quickVerdictBadge = document.getElementById('quick-verdict-badge');
    const quickResultDetails = document.getElementById('quick-result-details');
    const sampleButtons = document.querySelectorAll('.sample-btn');

    // Update character counter
    function updateCharCount() {
        if (!threatInput || !charCounter) return;
        const count = threatInput.value.length;
        charCounter.textContent = `${count} char${count === 1 ? '' : 's'}`;
    }

    if (threatInput) {
        threatInput.addEventListener('input', updateCharCount);
    }

    // Clear input
    if (btnClear) {
        btnClear.addEventListener('click', () => {
            threatInput.value = '';
            updateCharCount();
            if (quickResultCard) quickResultCard.style.display = 'none';
            threatInput.focus();
        });
    }

    // Sample buttons loader
    sampleButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const sampleText = btn.getAttribute('data-sample');
            const category = btn.getAttribute('data-cat') || 'all';

            threatInput.value = sampleText;
            categorySelect.value = category;
            updateCharCount();

            // Flash animation on textarea
            threatInput.style.borderColor = 'var(--accent-cyan)';
            threatInput.style.boxShadow = '0 0 20px var(--accent-cyan-glow)';
            setTimeout(() => {
                threatInput.style.borderColor = '';
                threatInput.style.boxShadow = '';
            }, 500);

            showToast('Loaded benchmark sample payload.', 'info');
        });
    });

    // Form submission
    if (scannerForm) {
        scannerForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const text = threatInput.value.trim();
            const category = categorySelect.value;

            if (!text) {
                showToast('Please enter an input payload to analyze.', 'danger');
                threatInput.focus();
                return;
            }

            // Set loading state
            btnAnalyze.disabled = true;
            btnText.style.display = 'none';
            btnSpinner.style.display = 'flex';

            try {
                const response = await fetch('/api/scan', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text, category })
                });

                const data = await response.json();

                if (!response.ok || !data.success) {
                    throw new Error(data.error || 'Failed to scan payload.');
                }

                // Persist scan result to localStorage history & sessionStorage for dashboard view
                saveScanResult(data);
                sessionStorage.setItem('sentinel_latest_scan', JSON.stringify(data));

                // Display quick preview
                renderQuickResult(data);

                if (data.is_suspicious) {
                    showToast(`⚠️ ${data.status} (${data.matched_rules_count} rule${data.matched_rules_count > 1 ? 's' : ''}) in ${data.scan_duration_ms}ms`, 'danger');
                } else {
                    showToast(`✓ ${data.status} in ${data.scan_duration_ms}ms`, 'success');
                }

            } catch (err) {
                console.error(err);
                showToast(err.message, 'danger');
            } finally {
                btnAnalyze.disabled = false;
                btnText.style.display = 'flex';
                btnSpinner.style.display = 'none';
            }
        });
    }

    function renderQuickResult(scan) {
        if (!quickResultCard) return;

        quickResultCard.style.display = 'block';

        if (scan.is_suspicious) {
            quickVerdictBadge.className = 'badge badge-danger';
            quickVerdictBadge.textContent = scan.status;
        } else {
            quickVerdictBadge.className = 'badge badge-clean';
            quickVerdictBadge.textContent = scan.status;
        }

        let rulesHtml = '';
        if (scan.matched_rules && scan.matched_rules.length > 0) {
            rulesHtml = `
                <div style="margin-top: 0.75rem;">
                    <div style="font-weight: 600; margin-bottom: 0.4rem; color: var(--accent-cyan);">Matched Detection Rules:</div>
                    <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                        ${scan.matched_rules.map(r => `
                            <div style="background: rgba(7, 20, 38, 0.7); border: 1px solid var(--bg-card-border); padding: 0.65rem 0.85rem; border-radius: 6px; display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <span style="font-weight: 600; color: #fff;">${escapeHtml(r.name)}</span>
                                    <span class="badge badge-purple" style="margin-left: 0.5rem;">${escapeHtml(r.category)}</span>
                                </div>
                                <span class="badge badge-danger">${r.match_count} match${r.match_count > 1 ? 'es' : ''}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        quickResultDetails.innerHTML = `
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem; font-size: 0.82rem; color: var(--text-muted); font-family: var(--font-mono);">
                <span>Execution Time: <strong style="color:var(--text-primary);">${scan.scan_duration_ms} ms</strong></span>
                <span>Rules Evaluated: <strong style="color:var(--text-primary);">${scan.rules_checked}</strong></span>
                <span>Total Matches: <strong style="color:var(--text-primary);">${scan.total_matches}</strong></span>
            </div>

            <div style="margin-top: 0.6rem;">
                <div style="font-weight: 600; margin-bottom: 0.3rem;">Highlighted Input:</div>
                <div style="background: #08172b; padding: 0.75rem; border-radius: 6px; font-family: var(--font-mono); font-size: 0.85rem; word-break: break-all; border: 1px solid var(--bg-card-border);">
                    ${scan.highlighted_html}
                </div>
            </div>

            ${rulesHtml}
        `;
    }
});

