const renderChart_income = (data, labels) => {
    const ctx = document.getElementById("myChartincome").getContext("2d");

    new Chart(ctx, {
        type: "line", 
        data: {
            labels: labels,
            datasets: [{
                label: "Income per source",
                data: data,
                borderColor: 'rgb(75, 192, 192)',
                fill: false,
            }]
        },
        options: {
            plugins: {
                title: {
                    display: true,
                    text: 'Income per source',
                    font: {
                        size: 15
                    }
                },
                legend: {
                    display: false
                }
            }
        }
    });
};


const getChartData_income = () => {
    console.log("fetching");
    fetch("/income/income_source_summary")
        .then((res) => res.json())
        .then((results) => {
            console.log("results", results);
            const source_data = results.income_source_data;
            const [labels, data] = [
                Object.keys(source_data),
                Object.values(source_data),
            ];

            renderChart_income(data, labels);
        });
};

document.onload = getChartData_income();


// second
const renderChart_income_bar = (data, labels) => {
    const ctx = document.getElementById("myChartincomeBar").getContext("2d");

    new Chart(ctx, {
        type: "bar", 
        data: {
            labels: labels,
            datasets: [{
                label: "Income per Source",
                data: data,
                backgroundColor: 'rgba(75, 192, 192, 0.2)', 
                borderColor: 'rgb(75, 192, 192)',
                borderWidth: 1,
            }]
        },
        options: {
            animation: {
                duration: 2000, 
                easing: 'linear', 
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Income per Source',
                    font: {
                        size: 15
                    }
                },
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true 
                }
            }
        }
    });
};

const getChartData_income_bar = () => {
    console.log("fetching");
    fetch("/income/income_source_summary")
        .then((res) => res.json())
        .then((results) => {
            console.log("results", results);
            const source_data = results.income_source_data;
            const [labels, data] = [
                Object.keys(source_data),
                Object.values(source_data),
            ];

            renderChart_income_bar(data, labels);
        });
};

document.onload = getChartData_income_bar();

//third 
const renderChart_income_mixed = (data, labels) => {
    const ctx = document.getElementById("myChartincomeMixed").getContext("2d");

    new Chart(ctx, {
        type: "pie",  
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Income per Source (Bar)",
                    data: data,
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderColor: 'rgb(75, 192, 192)',
                    borderWidth: 1,
                },
                // {
                //     label: "Income per Source (Line)",
                //     data: data,
                //     borderColor: 'rgba(255, 99, 132, 0.7)',
                //     backgroundColor: 'rgba(255, 99, 132, 0.7)',
                //     type: 'line',
                // },
                {
                    label: "Income per Source (Polar)",
                    data: data,
                    borderColor: 'rgba(54, 162, 235, 0.7)',
                    backgroundColor: 'rgba(54, 162, 235, 0.7)',
                    type: 'polarArea',
                }
            ]
        },
        options: {
            animation: {
                duration: 2000,
                easing: 'linear',
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Income per Source (Mixed Chart)',
                    font: {
                        size: 15
                    }
                },
                legend: {
                    display: true
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
};

const getChartData_income_mixed = () => {
    console.log("fetching");
    fetch("/income/income_source_summary")
        .then((res) => res.json())
        .then((results) => {
            console.log("results", results);
            const source_data = results.income_source_data;
            const [labels, data] = [
                Object.keys(source_data),
                Object.values(source_data),
            ];

            renderChart_income_mixed(data, labels);
        });
};

document.onload = getChartData_income_mixed();
