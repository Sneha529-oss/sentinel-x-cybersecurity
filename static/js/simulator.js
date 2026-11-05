/**
 * SENTINEL X — DFA Simulator Controller (Phase 8)
 * Student PRN: 202401110046
 */

document.addEventListener('DOMContentLoaded', () => {
    const simForm = document.getElementById('simulator-form');
    const simPattern = document.getElementById('sim-pattern');
    const simInputString = document.getElementById('sim-input-string');
    const simType = document.getElementById('sim-automaton-type');
    
    const btnReset = document.getElementById('btn-sim-reset');
    const btnPlay = document.getElementById('btn-sim-play');
    const btnPause = document.getElementById('btn-sim-pause');
    const btnStep = document.getElementById('btn-sim-step');
    const speedSelect = document.getElementById('sim-speed');
    
    const currentStepLabel = document.getElementById('sim-current-step-label');
    const currentStateLabel = document.getElementById('sim-current-state-label');
    const verdictBanner = document.getElementById('sim-verdict-banner');
    const graphStateBadge = document.getElementById('graph-state-badge');
    const timelineStepCount = document.getElementById('timeline-step-count');
    const timelineBody = document.getElementById('sim-timeline-body');
    const btnExportSim = document.getElementById('btn-export-sim-json');

    let simData = null;
    let currentStepIdx = 0;
    let playInterval = null;
    let cySim = null;

    // Presets handler
    document.querySelectorAll('.btn-sim-preset').forEach(btn => {
        btn.addEventListener('click', () => {
            const expr = btn.getAttribute('data-expr');
            const str = btn.getAttribute('data-str');
            if (simPattern) simPattern.value = expr;
            if (simInputString) simInputString.value = str;
            loadSimulation();
        });
    });

    // Check query params
    const params = new URLSearchParams(window.location.search);
    if (params.get('pattern')) simPattern.value = params.get('pattern');
    if (params.get('string')) simInputString.value = params.get('string');
    if (params.get('type')) simType.value = params.get('type');

    if (simForm) {
        simForm.addEventListener('submit', (e) => {
            e.preventDefault();
            loadSimulation();
        });
    }

    async function loadSimulation() {
        pausePlayback();
        const pattern = simPattern.value.trim();
        const inputString = simInputString.value;
        const automatonType = simType.value;

        if (!pattern) {
            showToast('Regular expression pattern is required.', 'danger');
            return;
        }

        try {
            const res = await fetch('/api/automata/simulate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    pattern: pattern,
                    input_string: inputString,
                    automaton_type: automatonType,
                    include_dead_state: true
                })
            });

            const data = await res.json();
            if (!res.ok || !data.success) {
                throw new Error(data.error || 'Simulation setup failed.');
            }

            simData = data;
            initCytoscapeSimulator(data.automaton);
            buildTimeline(data.simulation.steps);
            resetSimulation();

            showToast(`Simulation loaded: ${data.simulation.steps_count - 1} transitions computed.`, 'info');

        } catch (err) {
            console.error(err);
            showToast(err.message, 'danger');
        }
    }

    function initCytoscapeSimulator(automaton) {
        const container = document.getElementById('sim-cy');
        if (!container || !window.cytoscape) return;

        if (cySim) cySim.destroy();

        const elements = automaton.cytoscape_elements || [];

        cySim = cytoscape({
            container: container,
            elements: elements,
            style: [
                {
                    selector: 'node',
                    style: {
                        'background-color': '#102640',
                        'label': 'data(short_label)',
                        'color': '#F1F5FA',
                        'font-family': 'JetBrains Mono, monospace',
                        'font-size': '12px',
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'width': 48,
                        'height': 48,
                        'border-width': 2,
                        'border-color': '#2589FF',
                        'transition-property': 'background-color, border-color, width, height',
                        'transition-duration': '0.2s'
                    }
                },
                {
                    selector: 'node.start-node',
                    style: {
                        'border-color': '#20C997',
                        'border-width': 3,
                        'background-color': '#0B2E28'
                    }
                },
                {
                    selector: 'node.accept-node',
                    style: {
                        'border-color': '#35D5FF',
                        'border-width': 4,
                        'border-style': 'double'
                    }
                },
                {
                    selector: 'node.dead-node',
                    style: {
                        'background-color': '#301319',
                        'border-color': '#FF5263'
                    }
                },
                {
                    selector: 'node.active-sim-node',
                    style: {
                        'background-color': '#FFD166 !important',
                        'color': '#071426 !important',
                        'border-color': '#FFAB00 !important',
                        'border-width': 6,
                        'width': 58,
                        'height': 58,
                        'font-weight': 'bold',
                        'z-index': 99
                    }
                },
                {
                    selector: 'edge',
                    style: {
                        'width': 2,
                        'line-color': '#2589FF',
                        'target-arrow-color': '#2589FF',
                        'target-arrow-shape': 'triangle',
                        'curve-style': 'bezier',
                        'label': 'data(label)',
                        'color': '#A8B8CC',
                        'font-family': 'JetBrains Mono, monospace',
                        'font-size': '11px',
                        'text-background-color': '#071426',
                        'text-background-opacity': 0.85,
                        'text-background-padding': '2px',
                        'text-background-shape': 'roundrectangle'
                    }
                },
                {
                    selector: 'edge.active-sim-edge',
                    style: {
                        'width': 4,
                        'line-color': '#FFD166 !important',
                        'target-arrow-color': '#FFD166 !important',
                        'color': '#FFD166 !important',
                        'z-index': 99
                    }
                }
            ],
            layout: {
                name: 'breadthfirst',
                directed: true,
                padding: 30,
                spacingFactor: 1.25,
                roots: automaton.start_state ? [`${automaton.start_state}`] : undefined
            }
        });
    }

    function buildTimeline(steps) {
        if (!timelineBody) return;
        timelineBody.innerHTML = '';
        if (timelineStepCount) timelineStepCount.textContent = `${steps.length} Step(s)`;

        steps.forEach((st, idx) => {
            const tr = document.createElement('tr');
            tr.id = `step-row-${idx}`;
            tr.style.cursor = 'pointer';

            let typeBadge = '';
            if (st.is_dead) {
                typeBadge = '<span class="badge badge-danger">Dead State</span>';
            } else if (st.is_accepting) {
                typeBadge = '<span class="badge badge-clean">Accepting</span>';
            } else {
                typeBadge = '<span class="badge badge-blue">Normal</span>';
            }

            let transitionText = '';
            if (st.symbol === 'START') {
                transitionText = `Start at <strong>${escapeHtml(st.to_state)}</strong>`;
            } else if (st.to_state) {
                transitionText = `δ(${escapeHtml(st.from_state)}, '${escapeHtml(st.symbol)}') → <strong>${escapeHtml(st.to_state)}</strong>`;
            } else {
                transitionText = `<span style="color:var(--color-danger);">Abort on '${escapeHtml(st.symbol)}'</span>`;
            }

            tr.innerHTML = `
                <td class="font-mono" style="color:var(--accent-cyan); font-weight:600;">#${st.step}</td>
                <td class="font-mono" style="color:#fff; font-weight:600;">${st.symbol === 'START' ? 'λ' : escapeHtml(st.symbol)}</td>
                <td class="font-mono">${transitionText}</td>
                <td>${typeBadge}</td>
            `;

            tr.addEventListener('click', () => {
                pausePlayback();
                goToStep(idx);
            });

            timelineBody.appendChild(tr);
        });
    }

    function goToStep(idx) {
        if (!simData || !simData.simulation || !simData.simulation.steps) return;
        const steps = simData.simulation.steps;
        if (idx < 0 || idx >= steps.length) return;

        currentStepIdx = idx;
        const step = steps[idx];

        // Update Labels
        if (currentStepLabel) currentStepLabel.textContent = `${idx} / ${steps.length - 1}`;
        if (currentStateLabel) currentStateLabel.textContent = step.to_state || '(None)';
        if (graphStateBadge) {
            graphStateBadge.textContent = step.to_state ? `State: ${step.to_state}` : 'Terminated';
            graphStateBadge.className = step.is_dead ? 'badge badge-danger' : (step.is_accepting ? 'badge badge-clean' : 'badge badge-cyan');
        }

        // Highlight Timeline Row
        document.querySelectorAll('#sim-timeline-body tr').forEach(r => {
            r.style.background = '';
        });
        const activeRow = document.getElementById(`step-row-${idx}`);
        if (activeRow) {
            activeRow.style.background = 'rgba(53, 213, 255, 0.15)';
            activeRow.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }

        // Highlight Cytoscape Graph
        if (cySim) {
            cySim.elements().removeClass('active-sim-node active-sim-edge');

            // Highlight destination node
            if (step.to_state) {
                const targetNode = cySim.getElementById(step.to_state);
                if (targetNode) {
                    targetNode.addClass('active-sim-node');
                }
            }

            // Highlight traversed edge
            if (step.from_state && step.to_state && step.symbol) {
                const edges = cySim.edges(`[source = "${step.from_state}"][target = "${step.to_state}"][label = "${step.symbol}"]`);
                if (edges.length > 0) {
                    edges.addClass('active-sim-edge');
                }
            }
        }

        // Check if reached end of simulation
        if (idx === steps.length - 1) {
            pausePlayback();
            showVerdict(simData.simulation);
        } else {
            if (verdictBanner) verdictBanner.style.display = 'none';
        }
    }

    function showVerdict(sim) {
        if (!verdictBanner) return;
        verdictBanner.style.display = 'block';

        if (sim.accepted) {
            verdictBanner.style.background = 'rgba(32, 201, 151, 0.15)';
            verdictBanner.style.borderColor = 'var(--color-success)';
            verdictBanner.style.color = '#fff';
            verdictBanner.innerHTML = `
                <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.25rem;">
                    <strong style="color:var(--color-success); font-size:1.1rem;">✓ STRING ACCEPTED</strong>
                    <span class="badge badge-clean">Final State In F</span>
                </div>
                <div>${escapeHtml(sim.explanation)}</div>
            `;
            showToast('✓ String accepted by automaton!', 'success');
        } else {
            verdictBanner.style.background = 'rgba(255, 82, 99, 0.15)';
            verdictBanner.style.borderColor = 'var(--color-danger)';
            verdictBanner.style.color = '#fff';
            verdictBanner.innerHTML = `
                <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.25rem;">
                    <strong style="color:var(--color-danger); font-size:1.1rem;">✗ STRING REJECTED</strong>
                    <span class="badge badge-danger">Rejection Verdict</span>
                </div>
                <div>${escapeHtml(sim.explanation)}</div>
            `;
            showToast('✗ String rejected by automaton.', 'danger');
        }
    }

    function stepNext() {
        if (!simData || !simData.simulation) return;
        const total = simData.simulation.steps.length;
        if (currentStepIdx + 1 < total) {
            goToStep(currentStepIdx + 1);
        }
    }

    function resetSimulation() {
        pausePlayback();
        goToStep(0);
        if (verdictBanner) verdictBanner.style.display = 'none';
    }

    function startPlayback() {
        if (!simData || !simData.simulation) return;
        const total = simData.simulation.steps.length;
        if (currentStepIdx >= total - 1) {
            goToStep(0);
        }

        btnPlay.style.display = 'none';
        btnPause.style.display = 'inline-flex';

        const speed = parseInt(speedSelect ? speedSelect.value : 750, 10);
        playInterval = setInterval(() => {
            if (currentStepIdx + 1 < total) {
                goToStep(currentStepIdx + 1);
            } else {
                pausePlayback();
            }
        }, speed);
    }

    function pausePlayback() {
        if (playInterval) {
            clearInterval(playInterval);
            playInterval = null;
        }
        if (btnPlay) btnPlay.style.display = 'inline-flex';
        if (btnPause) btnPause.style.display = 'none';
    }

    if (btnStep) btnStep.addEventListener('click', () => {
        pausePlayback();
        stepNext();
    });

    if (btnPlay) btnPlay.addEventListener('click', startPlayback);
    if (btnPause) btnPause.addEventListener('click', pausePlayback);
    if (btnReset) btnReset.addEventListener('click', resetSimulation);

    // Export Trace JSON
    if (btnExportSim) {
        btnExportSim.addEventListener('click', () => {
            if (!simData) {
                showToast('No active simulation trace to export.', 'danger');
                return;
            }
            exportToJson(simData, `sentinel-x-simulation-${Date.now()}.json`);
        });
    }

    // Load initial simulation on page load
    loadSimulation();
});

