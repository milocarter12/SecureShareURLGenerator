// Initialize DashboardApp namespace
window.DashboardApp = (function() {
    // Private variables
    let timeChart = null;
    let currentViewType = 'weekly';
    let currentDate = new Date();
    const hourlyRate = 4;
    const paidHours = 4;

    // Private utility functions
    function parseDate(dateStr) {
        if (!dateStr) return null;
        const [month, day] = dateStr.split('/');
        const year = new Date().getFullYear();
        return new Date(year, parseInt(month) - 1, parseInt(day));
    }

    function formatDate(date) {
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const day = date.getDate().toString().padStart(2, '0');
        return `${month}/${day}`;
    }

    function getDayName(date) {
        return date.toLocaleDateString('en-US', { weekday: 'short' });
    }

    function getWeekDates(date) {
        const week = [];
        const start = new Date(date);
        start.setDate(date.getDate() - date.getDay());

        for (let i = 0; i < 7; i++) {
            const currentDate = new Date(start);
            currentDate.setDate(start.getDate() + i);
            week.push({
                date: formatDate(currentDate),
                day: getDayName(currentDate)
            });
        }
        return week;
    }

    function getMonthDates(date) {
        const month = [];
        const start = new Date(date.getFullYear(), date.getMonth(), 1);
        const end = new Date(date.getFullYear(), date.getMonth() + 1, 0);

        for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
            month.push({
                date: formatDate(new Date(d)),
                day: getDayName(new Date(d))
            });
        }
        return month;
    }

    function getYearMonths(date) {
        const months = [];
        const year = date.getFullYear();
        
        for (let month = 0; month < 12; month++) {
            const currentDate = new Date(year, month, 1);
            months.push({
                date: formatDate(currentDate),
                month: currentDate.toLocaleString('default', { month: 'short' })
            });
        }
        return months;
    }

    function findDataForDate(date) {
        return window.timeData.find(entry => entry.date === date) || { hours: 0 };
    }

    function getChartData() {
        let dateEntries;
        let labels;

        switch(currentViewType) {
            case 'weekly':
                dateEntries = getWeekDates(currentDate);
                labels = dateEntries.map(d => `${d.date}\n${d.day}`);
                break;
            case 'monthly':
                dateEntries = getMonthDates(currentDate);
                labels = dateEntries.map(d => d.date);
                break;
            case 'yearly':
                dateEntries = getYearMonths(currentDate);
                labels = dateEntries.map(d => d.month);
                break;
            default:
                dateEntries = getWeekDates(currentDate);
                labels = dateEntries.map(d => `${d.date}\n${d.day}`);
        }

        const mappedData = dateEntries.map(entry => {
            const existingData = findDataForDate(entry.date);
            return {
                date: entry.date,
                hours: existingData.hours
            };
        });

        return {
            labels,
            hours: mappedData.map(d => d.hours || null)
        };
    }

    const DashboardManager = {
        init: function() {
            // Calculate remaining hours and amount owed
            const remainingHourlyHours = window.timeData
                .reduce((sum, day) => sum + day.hours, 0) - paidHours;
            
            const remainingOwed = remainingHourlyHours * hourlyRate;

            // Handle view type changes
            const viewTypeSelect = document.getElementById('viewType');
            if (viewTypeSelect) {
                viewTypeSelect.addEventListener('change', function(e) {
                    currentViewType = e.target.value;
                    DashboardManager.updateChart();
                    DashboardManager.updatePeriodLabel();
                });
            }

            // Handle period navigation
            const prevPeriodBtn = document.getElementById('prevPeriod');
            if (prevPeriodBtn) {
                prevPeriodBtn.addEventListener('click', function() {
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
                    DashboardManager.updateChart();
                    DashboardManager.updatePeriodLabel();
                });
            }

            const nextPeriodBtn = document.getElementById('nextPeriod');
            if (nextPeriodBtn) {
                nextPeriodBtn.addEventListener('click', function() {
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
                    DashboardManager.updateChart();
                    DashboardManager.updatePeriodLabel();
                });
            }

            // Render Payment Summary
            const paymentSummary = document.getElementById('paymentSummary');
            if (paymentSummary) {
                paymentSummary.innerHTML = `
                    <div class="d-flex justify-content-between mt-2">
                        <span>Total Hours Worked:</span>
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
            }

            // Render Time Breakdown
            const timeBreakdown = document.getElementById('timeBreakdown');
            if (timeBreakdown) {
                timeBreakdown.innerHTML = window.timeData.map(day => `
                    <div class="time-entry ${day.hourlyPay ? 'hourly' : 'performance'}">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <div class="fw-bold">${day.day} ${day.date}</div>
                                <div class="text-muted small">${day.formattedTime}</div>
                            </div>
                            <div class="text-end">
                                ${day.hourlyPay ? `<div class="fw-bold">$${(day.hours * hourlyRate).toFixed(2)}</div>` : ''}
                            </div>
                        </div>
                    </div>
                `).join('');
            }

            // Initialize components
            this.updatePeriodLabel();
            this.updateChart();
        },

        updateChart: function() {
            const chartData = getChartData();
            const ctx = document.getElementById('timeChart');
            
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
                        backgroundColor: '#9333ea',
                        borderWidth: 0
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
                                    return `${context.formattedValue || '0'} hours`;
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
                        }
                    }
                }
            });
        },

        updatePeriodLabel: function() {
            const label = document.getElementById('periodLabel');
            if (!label) return;
            
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
    };

    return DashboardManager;
})();
