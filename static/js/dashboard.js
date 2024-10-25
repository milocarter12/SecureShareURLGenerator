document.addEventListener('DOMContentLoaded', function() {
    const hourlyRate = 4;
    const paidHours = 4;
    let currentViewType = 'weekly';
    let currentDate = new Date();
    let wordCountData = [];

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
                    label: 'Hours',
                    data: chartData.hours,
                    backgroundColor: chartData.colors,
                    borderWidth: 0
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
                        display: true
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                if (context.dataset.label === 'Hours') {
                                    const day = timeData[context.dataIndex];
                                    return `${day.formattedTime}${!day.hourlyPay ? ' (Performance Based)' : ''}`;
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
        // This is a simplified version - you would need to implement proper date filtering
        return {
            labels: timeData.map(d => `${d.date}\n${d.day}`),
            hours: timeData.map(d => d.hours),
            colors: timeData.map(d => 
                ['10/24', '10/25'].includes(d.date) ? '#94a3b8' : '#9333ea'
            ),
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

    // Handle word count form submission
    document.getElementById('wordCountForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const date = document.getElementById('wordCountDate').value;
        const totalWords = parseInt(document.getElementById('totalWords').value);
        const pricePerWord = parseFloat(document.getElementById('pricePerWord').value);

        const entry = {
            date: formatDate(new Date(date)),
            totalWords: totalWords,
            pricePerWord: pricePerWord,
            totalAmount: totalWords * pricePerWord
        };

        // Remove any existing entry for the same date
        wordCountData = wordCountData.filter(item => item.date !== entry.date);
        wordCountData.push(entry);

        updateChart();
        updateWordCountSummary();
        this.reset();
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

    // Initialize components
    updatePeriodLabel();
    updateChart();
    updateWordCountSummary();

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
