document.addEventListener('DOMContentLoaded', function () {
    // Get the data from the server
    fetch('/get_expenses')
        .then(response => response.json())
        .then(data => {
            // Call functions to draw pie chart and bar graph
            drawPieChart(data);
            drawBarGraph(data);
        })
        .catch(error => console.error('Error:', error));
});

function drawPieChart(data) {
    // Filter data for a specific month (you can modify this logic as per your requirement)
    const today = new Date();
    const currentMonth = today.getMonth() + 1; // Months are zero-based
    const currentYear = today.getFullYear();
    const filteredData = data.filter(expense => {
        const expenseDate = new Date(expense.date);
        return expenseDate.getMonth() + 1 === currentMonth && expenseDate.getFullYear() === currentYear;
    });

    // Initialize variables to store total expenses and savings for each category
    let totalFoodExpenses = 0;
    let totalTravelExpenses = 0;
    let totalAccommodationExpenses = 0;
    let totalOtherExpenses = 0;
    let totalSavings = 0;

    // Calculate total expenses and total savings for the current month
    for (const expense of filteredData) {
        totalFoodExpenses += expense.food_expenses;
        totalTravelExpenses += expense.travel_expenses;
        totalAccommodationExpenses += expense.accommodation;
        totalOtherExpenses += expense.other_expenses;
        totalSavings += expense.savings;
    }

    // Draw the pie chart
    const ctx = document.getElementById('expensePieChart').getContext('2d');
    const myPieChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Food Expenses', 'Travel Expenses', 'Accommodation', 'Other Expenses', 'Savings'],
            datasets: [{
                data: [totalFoodExpenses, totalTravelExpenses, totalAccommodationExpenses, totalOtherExpenses, totalSavings],
                backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#FF5733', '#4BC0C0'],
                hoverBackgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#FF5733', '#4BC0C0']
            }]
        }
    });
}

function drawBarGraph(data) {
    // Initialize variables to store data for the past 12 months
    const monthlyData = {};
    const today = new Date();

    // Calculate the date 12 months ago from today
    const twelveMonthsAgo = new Date(today.getFullYear(), today.getMonth() - 11, 1);

    // Extract and process data for the past 12 months
    for (const expense of data) {
        const date = new Date(expense.date);
        // Check if the expense date is within the past 12 months
        if (date >= twelveMonthsAgo && date <= today) {
            const monthYear = `${date.getMonth() + 1}-${date.getFullYear()}`;
            if (!monthlyData[monthYear]) {
                monthlyData[monthYear] = { expenses: 0, savings: 0 };
            }

            const foodExpenses = Number(expense.food_expenses) || 0;
            const travelExpenses = Number(expense.travel_expenses) || 0;
            const accommodation = Number(expense.accommodation) || 0;
            const otherExpenses = Number(expense.other_expenses) || 0;

            monthlyData[monthYear].expenses += (foodExpenses + travelExpenses + accommodation + otherExpenses);
            monthlyData[monthYear].savings += Number(expense.savings);
        }
    }

    // Prepare data for the chart
    const labels = [];
    const expensesData = [];
    const savingsData = [];
    for (const monthYear in monthlyData) {
        labels.push(monthYear);

        // Ensure you populate expensesData and savingsData here
        console.log("Monthly data for", monthYear, ":", monthlyData[monthYear]);
        expensesData.push(monthlyData[monthYear].expenses);
        console.log("Expenses data:", expensesData);
        savingsData.push(monthlyData[monthYear].savings);
        console.log("Savings data:", savingsData);
    }

    // Draw the bar chart
    const ctx = document.getElementById('expenseBarGraph').getContext('2d');
    const myBarChart = new Chart(ctx, {
        type: 'bar', // Change from 'line' to 'bar'
        data: {
            labels: labels,
            datasets: [{
                label: 'Expenses',
                backgroundColor: '#FF6384', // Use backgroundColor for bars
                borderColor: '#FF6384',
                data: expensesData,
                fill: false
            }, {
                label: 'Savings',
                backgroundColor: '#36A2EB', // Use backgroundColor for bars
                borderColor: '#36A2EB',
                data: savingsData,
                fill: false
            }]
        },
        options: {
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: true
                    }
                }],
                xAxes: [{
                    stacked: true // Enable stacking for better comparison
                }]
            }
        }
    });
}
