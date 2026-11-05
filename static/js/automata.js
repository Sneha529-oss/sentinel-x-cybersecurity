/**
 * SENTINEL X — Automata Studio Controller (Phases 6 & 7)
 * Student PRN: 202401110046
 */

document.addEventListener('DOMContentLoaded', () => {
    const inputRegex = document.getElementById('automata-regex');
    const checkDeadState = document.getElementById('include-dead-state-check');
    const errorBox = document.getElementById('automata-error-box');
    
    const btnBuildNfa = document.getElementById('btn-build-nfa');
    const btnConvertDfa = document.getElementById('btn-convert-dfa');
    const btnMinimizeDfa = document.getElementById('btn-minimize-dfa');
    
    const tabNfa = document.getElementById('tab-nfa');
    const tabDfa = document.getElementById('tab-dfa');
    const tabMinDfa = document.getElementById('tab-min-dfa');
    const viewTitle = document.getElementById('current-view-title');
    const tableBadge = document.getElementById('table-type-badge');
    
    const comparisonCard = document.getElementById('comparison-card');
    const metricNfaStates = document.getElementById('metric-nfa-states');
    const metricNfaTrans = document.getElementById('metric-nfa-trans');
    const metricDfaStates = document.getElementById('metric-dfa-states');
    const metricDfaTrans = document.getElementById('metric-dfa-trans');
    const metricMinStates = document.getElementById('metric-min-states');
    const metricMinTrans = document.getElementById('metric-min-trans');
    const metricReduced = document.getElementById('metric-states-reduced');
    const metricReducedPct = document.getElementById('metric-reduction-pct');
    const metricDeadState = document.getElementById('metric-dead-state');

    const tableHead = document.getElementById('transition-table-head');
    const tableBody = document.getElementById('transition-table-body');
    const btnSendToSim = document.getElementById('btn-send-to-simulator');

    let cy = null;
    let nfaData = null;
    let dfaData = null;
    let minDfaData = null;
    let currentStage = 'nfa'; // 'nfa', 'dfa', 'min-dfa'

    // Preset expression loaders
    document.querySelectorAll('.btn-preset').forEach(btn => {
        btn.addEventListener('click', () => {
            inputRegex.value = btn.getAttribute('data-expr');
            showToast(`Loaded preset: ${inputRegex.value}`, 'info');
            generateAutomataPipeline();
        });
    });

    // Handle query param if passed from regex lab
    const urlParams = new URLSearchParams(window.location.search);
    const patternParam = urlParams.get('pattern');
    if (patternParam) {
        inputRegex.value = patternParam;
    }

    // Step 1: Build NFA
    if (btnBuildNfa) {
        btnBuildNfa.addEventListener('click', async () => {
            const pattern = inputRegex.value.trim();
            if (!pattern) return;
            hideError();

            try {
                const res = await fetch('/api/automata/nfa', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ pattern })
                });
                const data = await res.json();
                if (!res.ok || !data.success) throw new Error(data.error || 'NFA construction failed.');

                nfaData = data.automaton;
                setStage('nfa');
                showToast(`Thompson NFA generated with ${nfaData.states_count} states.`, 'success');
            } catch (e) {
                showError(e.message);
            }
        });
    }

    // Step 2: Convert to DFA
    if (btnConvertDfa) {
        btnConvertDfa.addEventListener('click', async () => {
            const pattern = inputRegex.value.trim();
            if (!pattern) return;
            hideError();

            try {
                const res = await fetch('/api/automata/dfa', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        pattern,
                        include_dead_state: checkDeadState.checked
                    })
                });
                const data = await res.json();
                if (!res.ok || !data.success) throw new Error(data.error || 'DFA conversion failed.');

                nfaData = data.nfa;
                dfaData = data.dfa;
                updateComparisonMetrics();
                setStage('dfa');
                showToast(`Subset Construction produced DFA with ${dfaData.states_count} states.`, 'success');
            } catch (e) {
                showError(e.message);
            }
        });
    }

    // Step 3: Minimize DFA
    if (btnMinimizeDfa) {
        btnMinimizeDfa.addEventListener('click', async () => {
            const pattern = inputRegex.value.trim();
            if (!pattern) return;
            hideError();

            try {
                const res = await fetch('/api/automata/minimize', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        pattern,
                        include_dead_state: checkDeadState.checked
                    })
                });
                const data = await res.json();
                if (!res.ok || !data.success) throw new Error(data.error || 'DFA minimization failed.');

                nfaData = data.nfa;
                dfaData = data.dfa;
                minDfaData = data.minimized_dfa;
                updateComparisonMetrics();
                setStage('min-dfa');
                showToast(`Minimization reduced ${minDfaData.states_reduced} states (${minDfaData.reduction_percentage}%).`, 'success');
            } catch (e) {
                showError(e.message);
            }
        });
    }

    // Run complete pipeline initially
    async function generateAutomataPipeline() {
        const pattern = inputRegex.value.trim();
        if (!pattern) return;
        hideError();

        try {
            const res = await fetch('/api/automata/minimize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    pattern,
                    include_dead_state: checkDeadState.checked
                })
            });
            const data = await res.json();
            if (!res.ok || !data.success) throw new Error(data.error || 'Automata compilation failed.');

            nfaData = data.nfa;
            dfaData = data.dfa;
            minDfaData = data.minimized_dfa;

            updateComparisonMetrics();
            setStage('nfa'); // start at NFA or min-dfa
        } catch (e) {
            showError(e.message);
        }
    }

    function updateComparisonMetrics() {
        if (!comparisonCard) return;
        comparisonCard.style.display = 'block';

        if (nfaData) {
            metricNfaStates.textContent = nfaData.states_count;
            metricNfaTrans.textContent = `${nfaData.transitions_count} transitions`;
        }
        if (dfaData) {
            metricDfaStates.textContent = dfaData.states_count;
            metricDfaTrans.textContent = `${dfaData.transitions_count} transitions`;
            metricDeadState.textContent = dfaData.dead_state ? dfaData.dead_state : 'None';
        }
        if (minDfaData) {
            metricMinStates.textContent = minDfaData.states_count;
            metricMinTrans.textContent = `${minDfaData.transitions_count} transitions`;
            metricReduced.textContent = minDfaData.states_reduced;
            metricReducedPct.textContent = `${minDfaData.reduction_percentage}% reduction`;
        }
    }

    // Stage Tab Switcher
    if (tabNfa) tabNfa.addEventListener('click', () => setStage('nfa'));
    if (tabDfa) tabDfa.addEventListener('click', () => {
        if (!dfaData) {
            btnConvertDfa.click();
        } else {
            setStage('dfa');
        }
    });
    if (tabMinDfa) tabMinDfa.addEventListener('click', () => {
        if (!minDfaData) {
            btnMinimizeDfa.click();
        } else {
            setStage('min-dfa');
        }
    });

    function setStage(stage) {
        currentStage = stage;

        [tabNfa, tabDfa, tabMinDfa].forEach(t => {
            if (t) {
                t.className = 'btn btn-sm btn-secondary';
            }
        });

        let targetData = null;

        if (stage === 'nfa') {
            if (tabNfa) tabNfa.className = 'btn btn-sm btn-primary';
            viewTitle.textContent = 'NFA (Thompson Construction)';
            tableBadge.textContent = 'NFA Transitions (Includes ε)';
            targetData = nfaData;
        } else if (stage === 'dfa') {
            if (tabDfa) tabDfa.className = 'btn btn-sm btn-primary';
            viewTitle.textContent = 'DFA (Subset Construction)';
            tableBadge.textContent = 'DFA Transitions (Deterministic)';
            targetData = dfaData;
        } else if (stage === 'min-dfa') {
            if (tabMinDfa) tabMinDfa.className = 'btn btn-sm btn-primary';
            viewTitle.textContent = 'MINIMIZED DFA (Partition Refinement)';
            tableBadge.textContent = 'Minimized Transitions (Equivalence Classes)';
            targetData = minDfaData;
        }

        if (targetData) {
            renderCytoscapeGraph(targetData);
            renderTransitionTable(targetData);

            // Update simulator redirect button href
            if (btnSendToSim) {
                const pat = encodeURIComponent(inputRegex.value.trim());
                const type = stage === 'nfa' ? 'dfa' : (stage === 'min-dfa' ? 'minimized' : 'dfa');
                btnSendToSim.href = `/simulator?pattern=${pat}&type=${type}`;
            }
        }
    }

    // Cytoscape Interactive Graph Renderer
    function renderCytoscapeGraph(automaton) {
        const cyContainer = document.getElementById('cy');
        if (!cyContainer || !window.cytoscape) return;

        const elements = automaton.cytoscape_elements || [];

        if (cy) {
            cy.destroy();
        }

        cy = cytoscape({
            container: cyContainer,
            elements: elements,
            style: [
                // Base node
                {
                    selector: 'node',
                    style: {
                        'background-color': '#102640',
                        'label': 'data(label)',
                        'color': '#F1F5FA',
                        'font-family': 'JetBrains Mono, monospace',
                        'font-size': '11px',
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'text-wrap': 'wrap',
                        'width': 50,
                        'height': 50,
                        'border-width': 2,
                        'border-color': '#2589FF',
                        'transition-property': 'background-color, border-color, width, height',
                        'transition-duration': '0.2s'
                    }
                },
                // Start Node
                {
                    selector: 'node.start-node',
                    style: {
                        'border-color': '#20C997',
                        'border-width': 3,
                        'background-color': '#0B2E28'
                    }
                },
                // Accept / Final Node (Double Border effect)
                {
                    selector: 'node.accept-node',
                    style: {
                        'border-color': '#35D5FF',
                        'border-width': 4,
                        'border-style': 'double'
                    }
                },
                // Dead / Trap Node
                {
                    selector: 'node.dead-node',
                    style: {
                        'background-color': '#301319',
                        'border-color': '#FF5263',
                        'border-width': 2
                    }
                },
                // Active Simulator Node
                {
                    selector: 'node.active-sim-node',
                    style: {
                        'background-color': '#FFD166',
                        'color': '#071426',
                        'border-color': '#FFAB00',
                        'border-width': 5,
                        'width': 60,
                        'height': 60,
                        'font-weight': 'bold'
                    }
                },
                // Base Edge
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
                // Epsilon Edge
                {
                    selector: 'edge.epsilon-edge',
                    style: {
                        'line-style': 'dashed',
                        'line-color': '#8067FF',
                        'target-arrow-color': '#8067FF',
                        'color': '#8067FF'
                    }
                },
                // Self Loop Edge
                {
                    selector: 'edge.self-loop-edge',
                    style: {
                        'loop-direction': '-45deg',
                        'loop-sweep': '-90deg'
                    }
                },
                // Dead Edge
                {
                    selector: 'edge.dead-edge',
                    style: {
                        'line-color': 'rgba(255, 82, 99, 0.5)',
                        'target-arrow-color': '#FF5263'
                    }
                },
                // Active Edge during Simulation
                {
                    selector: 'edge.active-sim-edge',
                    style: {
                        'width': 4,
                        'line-color': '#FFD166',
                        'target-arrow-color': '#FFD166',
                        'color': '#FFD166'
                    }
                }
            ],
            layout: {
                name: 'breadthfirst',
                directed: true,
                padding: 40,
                spacingFactor: 1.25,
                roots: automaton.start_state ? [`${automaton.start_state}`] : undefined
            }
        });
    }

    // Transition Table Renderer
    function renderTransitionTable(automaton) {
        if (!tableHead || !tableBody) return;

        const columns = automaton.table_columns || [];
        const rows = automaton.table_rows || [];

        // Build Table Header
        let headHtml = `
            <tr>
                <th style="width: 140px;">State</th>
                ${columns.map(c => `
                    <th style="font-family: var(--font-mono); color: var(--accent-cyan); text-align: center;">
                        ${escapeHtml(c)}
                    </th>
                `).join('')}
            </tr>
        `;
        tableHead.innerHTML = headHtml;

        // Build Table Body
        let bodyHtml = rows.map(r => {
            let statePrefix = '';
            let stateClass = 'state-label';

            if (r.is_start && r.is_accept) {
                statePrefix = '<span style="color:var(--color-success); font-weight:bold;">→</span> <span style="color:var(--accent-cyan); font-weight:bold;">*</span> ';
            } else if (r.is_start) {
                statePrefix = '<span style="color:var(--color-success); font-weight:bold;">→</span> ';
            } else if (r.is_accept) {
                statePrefix = '<span style="color:var(--accent-cyan); font-weight:bold;">*</span> ';
            }

            const stateDisplay = `${statePrefix}<span class="${stateClass}">${escapeHtml(r.state)}</span>`;

            const cellsHtml = columns.map(c => {
                const val = r.transitions[c];
                let cellContent = '-';
                if (Array.isArray(val)) {
                    cellContent = val.length > 0 ? `{${val.join(', ')}}` : '-';
                } else if (val) {
                    cellContent = val;
                }
                const isDead = (cellContent === 'DEAD' || cellContent === 'M_DEAD');
                const cellStyle = isDead ? 'color: var(--color-danger); text-align: center;' : 'text-align: center;';
                return `<td style="${cellStyle}" class="font-mono">${escapeHtml(cellContent)}</td>`;
            }).join('');

            return `
                <tr>
                    <td style="white-space: nowrap;">${stateDisplay}</td>
                    ${cellsHtml}
                </tr>
            `;
        }).join('');

        tableBody.innerHTML = bodyHtml;
    }

    // Graph Toolbar Controls
    const btnFit = document.getElementById('btn-fit-graph');
    const btnReset = document.getElementById('btn-reset-graph');
    const btnPng = document.getElementById('btn-export-graph-png');

    if (btnFit) {
        btnFit.addEventListener('click', () => {
            if (cy) cy.fit(null, 30);
        });
    }

    if (btnReset) {
        btnReset.addEventListener('click', () => {
            if (cy) {
                cy.reset();
                cy.fit(null, 30);
            }
        });
    }

    if (btnPng) {
        btnPng.addEventListener('click', () => {
            if (!cy) return;
            const pngBlob = cy.png({ full: true, scale: 2, output: 'blob' });
            const url = URL.createObjectURL(pngBlob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `sentinel-x-automaton-${currentStage}.png`;
            a.click();
            URL.revokeObjectURL(url);
            showToast('Exported diagram as high-res PNG.', 'success');
        });
    }

    function showError(msg) {
        if (errorBox) {
            errorBox.textContent = `Error: ${msg}`;
            errorBox.style.display = 'block';
        }
        showToast(msg, 'danger');
    }

    function hideError() {
        if (errorBox) errorBox.style.display = 'none';
    }

    // Initial run
    generateAutomataPipeline();
});

