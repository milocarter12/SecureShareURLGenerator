document.addEventListener('DOMContentLoaded', function() {
    const socket = io();
    const hourlyRate = 4;
    const paidHours = 4;
    let currentViewType = 'weekly';
    let currentDate = new Date();

    // Calculate remaining hours and amount owed
    const remainingHourlyHours = timeData
        .filter(day => day.hourlyPay && !['10/24', '10/25'].includes(day.date))
        .reduce((sum, day) => sum + day.hours, 0) - paidHours;
    
    const remainingOwed = remainingHourlyHours * hourlyRate;

    // Initialize Chart
    const ctx = document.getElementById('timeChart').getContext('2d');
    let timeChart;

    function updateChart() {
        const chartData = getChartData();
        
        if (timeChart) {
            timeChart.destroy();
        }

        timeChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: 'Hourly Pay',
                    data: chartData.hourlyHours,
                    backgroundColor: '#9333ea',
                    borderWidth: 0,
                    yAxisID: 'y'
                }, {
                    label: 'Performance Based',
                    data: chartData.performanceHours,
                    backgroundColor: '#94a3b8',
                    borderWidth: 0,
                    yAxisID: 'y'
                }, {
                    label: 'Word Count',
                    data: chartData.wordCounts,
                    backgroundColor: '#3b82f6',
                    borderWidth: 0,
                    yAxisID: 'wordCount'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            pointStyle: 'rect'
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                if (context.dataset.label !== 'Word Count') {
                                    const day = timeData[context.dataIndex];
                                    return day ? `${day.formattedTime}` : '';
                                }
                                return `${context.formattedValue} words`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Hours'
                        }
                    },
                    wordCount: {
                        position: 'right',
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Word Count'
                        }
                    }
                }
            }
        });
    }

    function getChartData() {
        return {
            labels: timeData.map(d => `${d.date}\n${d.day}`),
            hourlyHours: timeData.map(d => d.hourlyPay ? d.hours : null),
            performanceHours: timeData.map(d => !d.hourlyPay ? d.hours : null),
            wordCounts: timeData.map(d => {
                const wordCount = wordCountData.find(w => w.date === d.date);
                return wordCount ? wordCount.totalWords : 0;
            })
        };
    }

    // Handle view type changes
    document.getElementById('viewType').addEventListener('change', function(e) {
        currentViewType = e.target.value;
        updateChart();
        updatePeriodLabel();
    });

    // Handle period navigation
    document.getElementById('prevPeriod').addEventListener('click', function() {
        switch(currentViewType) {
            case 'weekly':
                currentDate.setDate(currentDate.getDate() - 7);
                break;
            case 'monthly':
                currentDate.setMonth(currentDate.getMonth() - 1);
                break;
            case 'yearly':
                currentDate.setFullYear(currentDate.getFullYear() - 1);
                break;
        }
        updateChart();
        updatePeriodLabel();
    });

    document.getElementById('nextPeriod').addEventListener('click', function() {
        switch(currentViewType) {
            case 'weekly':
                currentDate.setDate(currentDate.getDate() + 7);
                break;
            case 'monthly':
                currentDate.setMonth(currentDate.getMonth() + 1);
                break;
            case 'yearly':
                currentDate.setFullYear(currentDate.getFullYear() + 1);
                break;
        }
        updateChart();
        updatePeriodLabel();
    });

    function updatePeriodLabel() {
        const label = document.getElementById('periodLabel');
        const options = { year: 'numeric', month: 'short' };
        
        switch(currentViewType) {
            case 'weekly':
                const weekStart = new Date(currentDate);
                weekStart.setDate(currentDate.getDate() - currentDate.getDay());
                const weekEnd = new Date(weekStart);
                weekEnd.setDate(weekStart.getDate() + 6);
                label.textContent = `${weekStart.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - ${weekEnd.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`;
                break;
            case 'monthly':
                label.textContent = currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
                break;
            case 'yearly':
                label.textContent = currentDate.toLocaleDateString('en-US', { year: 'numeric' });
                break;
        }
    }

    // Handle word count form submission with WebSocket
    document.getElementById('wordCountForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const date = document.getElementById('wordCountDate').value;
        const totalWords = parseInt(document.getElementById('totalWords').value);
        const pricePerWord = parseFloat(document.getElementById('pricePerWord').value);

        const entry = {
            date: formatDate(new Date(date)),
            totalWords: totalWords,
            pricePerWord: pricePerWord
        };

        // Emit the entry to the server
        socket.emit('word_count_entry', entry);
        this.reset();
    });

    // Handle WebSocket updates
    socket.on('word_count_update', function(data) {
        wordCountData = data.wordCountData;
        wordCountLogs = data.logs;
        updateChart();
        updateWordCountSummary();
        updateWordCountLogs();
    });

    function formatDate(date) {
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const day = date.getDate().toString().padStart(2, '0');
        return `${month}/${day}`;
    }

    function updateWordCountSummary() {
        const summary = document.getElementById('wordCountSummary');
        const today = formatDate(new Date());
        const todayEntry = wordCountData.find(item => item.date === today);

        if (todayEntry) {
            summary.innerHTML = `
                <div class="d-flex justify-content-between">
                    <span>Total Words:</span>
                    <span class="fw-bold">${todayEntry.totalWords}</span>
                </div>
                <div class="d-flex justify-content-between">
                    <span>Price per Word:</span>
                    <span class="fw-bold">$${todayEntry.pricePerWord.toFixed(3)}</span>
                </div>
                <div class="d-flex justify-content-between mt-2 pt-2 border-top">
                    <span>Total Amount:</span>
                    <span class="fw-bold">$${todayEntry.totalAmount.toFixed(2)}</span>
                </div>
            `;
        } else {
            summary.innerHTML = '<p class="text-muted mb-0">No word count data for today</p>';
        }
    }

    function updateWordCountLogs() {
        const logsContainer = document.getElementById('wordCountLogs');
        logsContainer.innerHTML = wordCountLogs.map(log => `
            <div class="activity-log-entry border-bottom pb-2 mb-2">
                <div class="d-flex justify-content-between">
                    <small class="text-muted">${log.timestamp}</small>
                    <small class="text-muted">${log.ip_address}</small>
                </div>
                <div class="mt-1">
                    <strong>${log.totalWords}</strong> words added for ${log.date}
                    <div class="text-success">$${log.totalAmount.toFixed(2)}</div>
                </div>
            </div>
        `).join('');
    }

    // Initialize components
    updatePeriodLabel();
    updateChart();
    updateWordCountSummary();
    updateWordCountLogs();

    // Render Payment Summary
    const paymentSummary = document.getElementById('paymentSummary');
    paymentSummary.innerHTML = `
        <div class="d-flex justify-content-between mt-2">
            <span>Total Hours Worked (Hourly):</span>
            <span class="fw-bold">${(remainingHourlyHours + paidHours).toFixed(2)} hours</span>
        </div>
        <div class="d-flex justify-content-between mt-2">
            <span>Hours Already Paid:</span>
            <span class="text-success fw-bold">${paidHours} hours ($${(paidHours * hourlyRate).toFixed(2)})</span>
        </div>
        <div class="d-flex justify-content-between mt-2">
            <span>Remaining Hours to Pay:</span>
            <span class="text-primary fw-bold">${remainingHourlyHours.toFixed(2)} hours</span>
        </div>
        <div class="d-flex justify-content-between mt-3 pt-2 border-top">
            <span class="fw-bold">Amount Still Owed:</span>
            <span class="fw-bold">$${remainingOwed.toFixed(2)}</span>
        </div>
    `;

    // Render Time Breakdown
    const timeBreakdown = document.getElementById('timeBreakdown');
    timeBreakdown.innerHTML = timeData.map(day => `
        <div class="time-entry ${day.hourlyPay ? 'hourly' : 'performance'}">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <div class="fw-bold">${day.day} ${day.date}</div>
                    <div class="text-muted small">
                        ${day.formattedTime}
                        ${!day.hourlyPay ? " (Performance Based)" : ""}
                    </div>
                </div>
                <div class="text-end">
                    ${day.hourlyPay ? `
                        <div class="fw-bold">$${(day.hours * hourlyRate).toFixed(2)}</div>
                    ` : ''}
                </div>
            </div>
        </div>
    `).join('');
});
