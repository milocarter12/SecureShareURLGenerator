document.addEventListener('DOMContentLoaded', function() {
    const hourlyRate = 4;
    const paidHours = 4;

    // Calculate remaining hours and amount owed
    const remainingHourlyHours = timeData
        .filter(day => day.hourlyPay && !['10/24', '10/25'].includes(day.date))
        .reduce((sum, day) => sum + day.hours, 0) - paidHours;
    
    const remainingOwed = remainingHourlyHours * hourlyRate;

    // Initialize Chart
    const ctx = document.getElementById('timeChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: timeData.map(d => `${d.date}\n${d.day}`),
            datasets: [{
                data: timeData.map(d => d.hours),
                backgroundColor: timeData.map(d => 
                    ['10/24', '10/25'].includes(d.date) ? '#94a3b8' : '#9333ea'
                ),
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const day = timeData[context.dataIndex];
                            return `${day.formattedTime}${!day.hourlyPay ? ' (Performance Based)' : ''}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

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
