document.addEventListener('DOMContentLoaded', function() {
    const socket = io();
    const hourlyRate = 4;
    const paidHours = 4;
    let currentViewType = 'weekly';
    let currentDate = new Date();

    // Initialize Chart
    const ctx = document.getElementById('timeChart').getContext('2d');
    let timeChart;

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

    function filterDataForCurrentPeriod(data) {
        return data.filter(entry => {
            const entryDate = parseDate(entry.date);
            if (!entryDate) return false;

            switch(currentViewType) {
                case 'weekly':
                    const weekStart = new Date(currentDate);
                    weekStart.setDate(currentDate.getDate() - currentDate.getDay());
                    const weekEnd = new Date(weekStart);
                    weekEnd.setDate(weekStart.getDate() + 6);
                    return entryDate >= weekStart && entryDate <= weekEnd;
                case 'monthly':
                    return entryDate.getMonth() === currentDate.getMonth() &&
                           entryDate.getFullYear() === currentDate.getFullYear();
                case 'yearly':
                    return entryDate.getFullYear() === currentDate.getFullYear();
                default:
                    return true;
            }
        });
    }

    function updatePaymentSummary() {
        const filteredData = filterDataForCurrentPeriod(timeData);
        const hourlyData = filteredData.filter(day => day.hourlyPay);
        
        const totalHourlyHours = hourlyData.reduce((sum, day) => sum + day.hours, 0);
        const periodPaidHours = Math.min(paidHours, totalHourlyHours);
        const periodRemainingHours = totalHourlyHours - periodPaidHours;
        const periodRemainingOwed = periodRemainingHours * hourlyRate;

        const paymentSummary = document.getElementById('paymentSummary');
        paymentSummary.innerHTML = `
            <div class="d-flex justify-content-between mt-2">
                <span>Total Hours Worked (Hourly):</span>
                <span class="fw-bold">${totalHourlyHours.toFixed(2)} hours</span>
            </div>
            <div class="d-flex justify-content-between mt-2">
                <span>Hours Already Paid:</span>
                <span class="text-success fw-bold">${periodPaidHours.toFixed(2)} hours ($${(periodPaidHours * hourlyRate).toFixed(2)})</span>
            </div>
            <div class="d-flex justify-content-between mt-2">
                <span>Remaining Hours to Pay:</span>
                <span class="text-primary fw-bold">${periodRemainingHours.toFixed(2)} hours</span>
            </div>
            <div class="d-flex justify-content-between mt-3 pt-2 border-top">
                <span class="fw-bold">Amount Still Owed:</span>
                <span class="fw-bold">$${periodRemainingOwed.toFixed(2)}</span>
            </div>
        `;
    }

    function updateTimeBreakdown() {
        const filteredData = filterDataForCurrentPeriod(timeData);
        const timeBreakdown = document.getElementById('timeBreakdown');
        
        timeBreakdown.innerHTML = filteredData.map(day => `
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
        `).join('') || '<p class="text-muted">No time entries for this period</p>';
    }

    function updateAll() {
        updateChart();
        updatePaymentSummary();
        updateTimeBreakdown();
        updatePeriodLabel();
        updateWordCountSummary();
    }

    // [Previous chart-related functions remain the same...]
    // Include all the existing chart functions here

    // Handle view type changes
    document.getElementById('viewType').addEventListener('change', function(e) {
        currentViewType = e.target.value;
        updateAll();
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
        updateAll();
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
        updateAll();
    });

    function updateWordCountLogs() {
        const logsContainer = document.getElementById('wordCountLogs');
        logsContainer.innerHTML = wordCountLogs.map(log => `
            <div class="activity-log-entry border-bottom pb-2 mb-2">
                <div class="d-flex justify-content-between">
                    <small class="text-muted">${log.timestamp}</small>
                    <small class="text-muted">${log.location}</small>
                </div>
                <div class="mt-1">
                    <strong>${log.totalWords}</strong> words added for ${log.date}
                    <div class="text-success">$${log.totalAmount.toFixed(2)}</div>
                </div>
            </div>
        `).join('');
    }

    // Initialize components
    updateAll();
});
