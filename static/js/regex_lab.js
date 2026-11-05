/**
 * SENTINEL X — Regex Laboratory Controller (Phase 5)
 * Student PRN: 202401110046
 */

document.addEventListener('DOMContentLoaded', () => {
    const customForm = document.getElementById('custom-regex-form');
    const customPatternInput = document.getElementById('custom-pattern');
    const customTextInput = document.getElementById('custom-test-text');
    const customCaseCheck = document.getElementById('custom-case-sensitive');
    const customErrorBox = document.getElementById('custom-error-box');
    
    const resultsPanel = document.getElementById('custom-results-panel');
    const matchCountBadge = document.getElementById('custom-match-count-badge');
    const durationBadge = document.getElementById('custom-duration-badge');
    const highlightedView = document.getElementById('custom-highlighted-view');
    const matchesCoords = document.getElementById('custom-matches-coords');

    // Quick load buttons
    document.querySelectorAll('.btn-quick-load, .btn-load-to-tester').forEach(btn => {
        btn.addEventListener('click', () => {
            const pattern = btn.getAttribute('data-pattern');
            const sample = btn.getAttribute('data-sample') || '';

            if (customPatternInput) customPatternInput.value = pattern;
            if (customTextInput && sample) customTextInput.value = sample;

            window.scrollTo({ top: 0, behavior: 'smooth' });
            runCustomTest();
        });
    });

    // Form submission
    if (customForm) {
        customForm.addEventListener('submit', (e) => {
            e.preventDefault();
            runCustomTest();
        });
    }

    async function runCustomTest() {
        const pattern = customPatternInput.value.trim();
        const text = customTextInput.value;
        const caseSensitive = customCaseCheck.checked;

        if (!pattern) {
            showToast('Pattern cannot be empty.', 'danger');
            return;
        }

        if (customErrorBox) customErrorBox.style.display = 'none';

        try {
            const res = await fetch('/api/regex/test', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    pattern: pattern,
                    text: text,
                    case_sensitive: caseSensitive
                })
            });

            const data = await res.json();

            if (!res.ok || !data.valid) {
                if (customErrorBox) {
                    customErrorBox.textContent = data.error || 'Regex syntax or evaluation error.';
                    customErrorBox.style.display = 'block';
                }
                showToast(data.error || 'Evaluation failed.', 'danger');
                return;
            }

            renderCustomResults(data);
            showToast(`Regex executed: ${data.match_count} match${data.match_count === 1 ? '' : 'es'} found.`, 'info');

        } catch (err) {
            console.error(err);
            if (customErrorBox) {
                customErrorBox.textContent = err.message;
                customErrorBox.style.display = 'block';
            }
            showToast(err.message, 'danger');
        }
    }

    function renderCustomResults(data) {
        if (!resultsPanel) return;

        resultsPanel.style.display = 'block';

        const count = data.match_count || 0;
        if (count > 0) {
            matchCountBadge.className = 'badge badge-danger';
            matchCountBadge.textContent = `${count} Match${count > 1 ? 'es' : ''} Found`;
        } else {
            matchCountBadge.className = 'badge badge-clean';
            matchCountBadge.textContent = 'No Match Found';
        }

        durationBadge.textContent = `${data.duration_ms} ms`;
        highlightedView.innerHTML = data.highlighted_html || '(empty input)';

        // Render coordinate chips
        if (matchesCoords) {
            if (count === 0) {
                matchesCoords.innerHTML = `<span style="font-size: 0.8rem; color: var(--text-muted); font-family: var(--font-mono);">No matched intervals to display.</span>`;
            } else {
                matchesCoords.innerHTML = data.matches.map((m, idx) => `
                    <div style="background: rgba(37, 137, 255, 0.1); border: 1px solid var(--accent-blue); padding: 0.35rem 0.65rem; border-radius: 4px; font-family: var(--font-mono); font-size: 0.78rem;">
                        <span style="color: var(--accent-cyan); font-weight: 600;">#${idx + 1}</span>
                        <span style="color: var(--text-muted);"> [${m.start}:${m.end}] </span>
                        <span style="color: #fff; font-weight: 600;">"${escapeHtml(m.matched_text)}"</span>
                    </div>
                `).join('');
            }
        }
    }

    // Run custom test on page load once
    if (customPatternInput && customPatternInput.value) {
        runCustomTest();
    }

    // Benchmark Suite Runner for built-in rules
    document.querySelectorAll('.btn-run-rule-suite').forEach(btn => {
        btn.addEventListener('click', async () => {
            const ruleId = btn.getAttribute('data-rule-id');
            const ruleCard = document.getElementById(`card-${ruleId}`);
            if (!ruleCard) return;

            btn.disabled = true;
            btn.textContent = 'Evaluating Suite...';

            const matchingRows = ruleCard.querySelectorAll('.matching-list .test-case-row');
            const nonMatchingRows = ruleCard.querySelectorAll('.non-matching-list .test-case-row');

            // Find rule pattern from card
            const codeEl = ruleCard.querySelector('code');
            let pattern = codeEl ? codeEl.textContent.trim() : '';
            // Strip outer math markers if present
            if (pattern.startsWith('$') && pattern.endsWith('$')) {
                pattern = pattern.substring(1, pattern.length - 1);
            }

            let passedTests = 0;
            const totalTests = matchingRows.length + nonMatchingRows.length;

            // Evaluate expected matching
            for (const row of matchingRows) {
                const str = row.getAttribute('data-string');
                const badge = row.querySelector('.tc-result-badge');

                try {
                    const res = await fetch('/api/regex/test', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ pattern: pattern, text: str, case_sensitive: true })
                    });
                    const d = await res.json();
                    if (d.valid && d.match_count > 0) {
                        badge.className = 'tc-result-badge badge badge-clean';
                        badge.textContent = `✓ MATCH (${d.match_count})`;
                        passedTests++;
                    } else {
                        badge.className = 'tc-result-badge badge badge-danger';
                        badge.textContent = `✗ NO MATCH`;
                    }
                } catch (e) {
                    badge.className = 'tc-result-badge badge badge-danger';
                    badge.textContent = 'ERROR';
                }
            }

            // Evaluate expected non-matching
            for (const row of nonMatchingRows) {
                const str = row.getAttribute('data-string');
                const badge = row.querySelector('.tc-result-badge');

                try {
                    const res = await fetch('/api/regex/test', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ pattern: pattern, text: str, case_sensitive: true })
                    });
                    const d = await res.json();
                    if (d.valid && d.match_count === 0) {
                        badge.className = 'tc-result-badge badge badge-clean';
                        badge.textContent = `✓ NO MATCH`;
                        passedTests++;
                    } else {
                        badge.className = 'tc-result-badge badge badge-danger';
                        badge.textContent = `✗ UNEXPECTED MATCH (${d.match_count})`;
                    }
                } catch (e) {
                    badge.className = 'tc-result-badge badge badge-danger';
                    badge.textContent = 'ERROR';
                }
            }

            btn.disabled = false;
            btn.textContent = `▶ Suite Passed: ${passedTests}/${totalTests}`;
            showToast(`${ruleId} benchmark suite passed: ${passedTests}/${totalTests} tests verified!`, 'success');
        });
    });
});

