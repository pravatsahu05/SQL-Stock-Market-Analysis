document.addEventListener('DOMContentLoaded', () => {
    let currentTaskData = null;
    let currentQueryResults = null;

    // Element References
    const navTabs = document.querySelectorAll('.nav-tab');
    const sections = document.querySelectorAll('.dashboard-section');
    const taskListEl = document.getElementById('task-list');
    const queryTitleEl = document.getElementById('query-title');
    const queryDescEl = document.getElementById('query-desc');
    const queryCatEl = document.getElementById('query-cat');
    const sqlTextarea = document.getElementById('sql-editor');
    const runBtn = document.getElementById('btn-run-query');
    const exportBtn = document.getElementById('btn-export-csv');
    const execTimeEl = document.getElementById('exec-time');
    const rowCountEl = document.getElementById('row-count');
    const checkpointEl = document.getElementById('checkpoint-desc');
    const tableHeaderEl = document.getElementById('table-header');
    const tableBodyEl = document.getElementById('table-body');
    const searchInput = document.getElementById('table-search');
    const chartsGridEl = document.getElementById('charts-grid');

    // 1. Navigation Tab Switching
    navTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const target = tab.dataset.target;
            navTabs.forEach(t => t.classList.remove('active'));
            sections.forEach(s => s.classList.remove('active'));
            tab.classList.add('active');
            document.getElementById(target).classList.add('active');

            if (target === 'sec-charts' && chartsGridEl.children.length === 0) {
                loadChartInsights();
            }
        });
    });

    // 2. Fetch and Load Preset Tasks into Sidebar
    async function loadTasks() {
        try {
            const res = await fetch('/api/tasks');
            const tasks = await res.json();

            taskListEl.innerHTML = '';
            tasks.forEach((task, idx) => {
                const item = document.createElement('div');
                item.className = `task-item ${idx === 0 ? 'active' : ''}`;
                item.dataset.taskId = task.id;
                item.innerHTML = `
                    <div class="task-item-title">${task.title}</div>
                    <div class="task-item-cat">${task.category}</div>
                `;
                item.addEventListener('click', () => selectTask(task, item));
                taskListEl.appendChild(item);
            });

            if (tasks.length > 0) {
                selectTask(tasks[0], taskListEl.children[0]);
            }
        } catch (err) {
            console.error('Error loading tasks:', err);
        }
    }

    // 3. Select a Task and Execute
    function selectTask(task, element) {
        document.querySelectorAll('.task-item').forEach(i => i.classList.remove('active'));
        element.classList.add('active');

        currentTaskData = task;
        queryTitleEl.textContent = task.title;
        queryDescEl.textContent = task.description;
        queryCatEl.textContent = task.category;
        sqlTextarea.value = task.sql;
        checkpointEl.textContent = task.checkpoint;

        runQuery(task.id);
    }

    // 4. Execute SQL Query (Preset or Custom)
    async function runQuery(taskId = null) {
        tableHeaderEl.innerHTML = '<tr><th>Loading Query Results...</th></tr>';
        tableBodyEl.innerHTML = '';
        execTimeEl.textContent = 'Executing...';
        rowCountEl.textContent = 'Running...';

        try {
            let res, data;
            if (taskId) {
                res = await fetch(`/api/query/${taskId}`);
                data = await res.json();
            } else {
                // Custom Query Execution
                const customSql = sqlTextarea.value;
                res = await fetch('/api/custom_query', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ sql: customSql })
                });
                data = await res.json();
            }

            if (!data.success) {
                renderError(data.error || 'Failed to execute query');
                return;
            }

            currentQueryResults = data;
            execTimeEl.textContent = `${data.execution_time_ms} ms`;
            rowCountEl.textContent = `${data.count} Rows Returned`;

            renderTable(data.columns, data.rows);
        } catch (err) {
            renderError('Connection error or invalid query response');
            console.error(err);
        }
    }

    // 5. Render Data Table
    function renderTable(columns, rows) {
        if (!columns || columns.length === 0) {
            tableHeaderEl.innerHTML = '<tr><th>Query Executed Successfully</th></tr>';
            tableBodyEl.innerHTML = '<tr><td>No tabular rows returned.</td></tr>';
            return;
        }

        let hdrHtml = '<tr>';
        columns.forEach(col => {
            hdrHtml += `<th>${col}</th>`;
        });
        hdrHtml += '</tr>';
        tableHeaderEl.innerHTML = hdrHtml;

        renderTableBody(rows);
    }

    function renderTableBody(rows) {
        if (!rows || rows.length === 0) {
            tableBodyEl.innerHTML = '<tr><td colspan="100">No matching rows found.</td></tr>';
            return;
        }

        let bodyHtml = '';
        rows.forEach(row => {
            bodyHtml += '<tr>';
            row.forEach(val => {
                let cellContent = val !== null ? val : '<span style="color:#e74c3c;font-weight:bold;">NULL</span>';

                // Format signal pills if column is a signal
                if (cellContent === 'Buy') {
                    cellContent = '<span class="signal-pill signal-buy">▲ BUY</span>';
                } else if (cellContent === 'Sell') {
                    cellContent = '<span class="signal-pill signal-sell">▼ SELL</span>';
                } else if (cellContent === 'Hold') {
                    cellContent = '<span class="signal-pill signal-hold">HOLD</span>';
                }

                bodyHtml += `<td>${cellContent}</td>`;
            });
            bodyHtml += '</tr>';
        });
        tableBodyEl.innerHTML = bodyHtml;
    }

    function renderError(errMsg) {
        execTimeEl.textContent = 'Error';
        rowCountEl.textContent = '0 Rows';
        tableHeaderEl.innerHTML = '<tr><th style="color:#ff1744;">SQL Execution Error</th></tr>';
        tableBodyEl.innerHTML = `<tr><td style="color:#ff5252;font-family:monospace;padding:1.5rem;">${errMsg}</td></tr>`;
    }

    // 6. Search Filter on Table Data
    searchInput.addEventListener('input', (e) => {
        if (!currentQueryResults || !currentQueryResults.rows) return;

        const term = e.target.value.toLowerCase().trim();
        if (!term) {
            renderTableBody(currentQueryResults.rows);
            return;
        }

        const filtered = currentQueryResults.rows.filter(row => {
            return row.some(cell => cell !== null && String(cell).toLowerCase().includes(term));
        });

        renderTableBody(filtered);
    });

    // 7. Run Button Click Listener
    runBtn.addEventListener('click', () => {
        runQuery(null); // Execute custom query in editor
    });

    // 8. Export CSV Functionality
    exportBtn.addEventListener('click', () => {
        if (!currentQueryResults || !currentQueryResults.rows) {
            alert('No query data available to export.');
            return;
        }

        const cols = currentQueryResults.columns;
        const rows = currentQueryResults.rows;

        let csvContent = cols.join(',') + '\n';
        rows.forEach(row => {
            const formattedRow = row.map(val => {
                if (val === null) return 'NULL';
                const str = String(val).replace(/"/g, '""');
                return str.includes(',') ? `"${str}"` : str;
            });
            csvContent += formattedRow.join(',') + '\n';
        });

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.setAttribute('href', url);
        link.setAttribute('download', `SQL_Query_Results_${Date.now()}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    });

    // 9. Fetch and Render Chart Gallery with Business Insights & Recommendations
    async function loadChartInsights() {
        chartsGridEl.innerHTML = '<div style="color:var(--text-muted);padding:2rem;">Loading Chart Studio & Business Insights...</div>';
        try {
            const res = await fetch('/api/chart_insights');
            const chartsData = await res.json();

            chartsGridEl.innerHTML = '';

            Object.values(chartsData).forEach(chart => {
                const card = document.createElement('div');
                card.className = 'chart-card';

                const insightsHtml = chart.insights.map(i => `<li>${i}</li>`).join('');
                const recomHtml = chart.recommendations.map(r => `<li>${r}</li>`).join('');
                const caveatHtml = chart.caveats.map(c => `<li>${c}</li>`).join('');

                card.innerHTML = `
                    <div class="chart-header">
                        <div class="chart-title-group">
                            <span class="chart-category">${chart.category}</span>
                            <h3 class="chart-title">${chart.title}</h3>
                        </div>
                    </div>
                    <div class="chart-image-container">
                        <img src="/static/${chart.filename}" alt="${chart.title}" class="chart-img" />
                    </div>
                    <div class="insights-container">
                        <div class="insight-box">
                            <div class="box-header insight-title">📌 Key Business Insights</div>
                            <ul class="insight-bullet-list">${insightsHtml}</ul>
                        </div>
                        <div class="insight-box">
                            <div class="box-header recom-title">💡 Strategic Recommendations</div>
                            <ul class="insight-bullet-list recom-list">${recomHtml}</ul>
                        </div>
                        <div class="insight-box">
                            <div class="box-header caveat-title">⚠️ Methodological Risk & Caveats</div>
                            <ul class="insight-bullet-list caveat-list">${caveatHtml}</ul>
                        </div>
                    </div>
                `;

                chartsGridEl.appendChild(card);
            });
        } catch (err) {
            chartsGridEl.innerHTML = '<div style="color:var(--accent-red);padding:2rem;">Error loading chart studio. Make sure server is active.</div>';
            console.error(err);
        }
    }

    // Initialize
    loadTasks();
});
