const renderChart = (data, labels) => {
  const ctx = document.getElementById("myChart").getContext("2d");

  new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Last 6 months expenses",
          data: data,
          borderWidth: 1,
          borderColor: 'rgba(54, 162, 235, 0.7)',
          backgroundColor: 'rgb(255, 99, 132)',
        },
      ],
    },
    options: {
      plugins: {
        legend: {
          position: "bottom",
          color: "#000000",
          labels: {
            usePointStyle: true,
          },
        },
        title: {
          display: true,
          text: "Expenses per category",
          fontColor: "rgb(44,62,80)",
          padding: 8,
          font: {
            size: "15",
          },
        },
      },
      animation: {
        duration: 1000,
        easing: "linear",
      },
    },
  });
};

const getChartData = () => {
  console.log("fetching");
  fetch("/expense/expense_category_summary")
    .then((res) => res.json())
    .then((results) => {
      console.log("results", results);
      const category_data = results.expense_category_data;
      const [labels, data] = [
        Object.keys(category_data),
        Object.values(category_data),
      ];

      renderChart(data, labels);
    });
};
document.onload = getChartData();

//second
const renderChart_line = (data, labels) => {
  const ctx = document.getElementById("myChart_line").getContext("2d");

  new Chart(ctx, {
    data: {
      labels: labels,
      datasets: [
        {
          type: "bar",
          label: "Last 6 months expenses (Bar Dataset)",
          data: data,
          borderWidth: 1,
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          borderColor: 'rgb(75, 192, 192)',
        },
        {
          type: "line",
          label: "Last 6 months expenses(Line Dataset)",
          data: data,
          borderWidth: 1,
          borderColor: "rgb(54, 162, 235)",
        },
      ],
    },
    options: {
      plugins: {
        legend: {
          position: "bottom",
          color: "#000000",
          labels: {
            usePointStyle: true,
          },
        },
        title: {
          display: true,
          text: "Expenses per category",
          fontColor: "rgb(44,62,80)",
          padding: 8,
          font: {
            size: "15",
          },
        },
      },
      animation: {
        duration: 1000,
        easing: "linear",
      },
    },
  });
};

const getChartData_line = () => {
  console.log("fetching");
  fetch("/expense/expense_category_summary")
    .then((res) => res.json())
    .then((results) => {
      console.log("results", results);
      const category_data = results.expense_category_data;
      const [labels, data] = [
        Object.keys(category_data),
        Object.values(category_data),
      ];

      renderChart_line(data, labels);
    });
};

document.onload = getChartData_line();



const renderChart_polar = (data, labels) => {
  const ctx = document.getElementById("myChart_polar").getContext("2d");

  new Chart(ctx, {
    data: {
      labels: labels,
      datasets: [
        {
          type: "radar",
          label: "Last 6 months expenses",
          data: data,
          borderWidth: 1,
        },
       
      ],
    },
    options: {
      plugins: {
        legend: {
          position: "bottom",
          color: "#000000",
          labels: {
            usePointStyle: true,
          },
        },
        title: {
          display: true,
          text: "Expenses per category",
          fontColor: "rgb(44,62,80)",
          padding: 8,
          font: {
            size: "15",
          },
        },
      },
      animation: {
        duration: 1000,
        easing: "linear",
      },
    },
  });
};

const getChartData_polar = () => {
  console.log("fetching");
  fetch("/expense/expense_category_summary")
    .then((res) => res.json())
    .then((results) => {
      console.log("results", results);
      const category_data = results.expense_category_data;
      const [labels, data] = [
        Object.keys(category_data),
        Object.values(category_data),
      ];

      renderChart_polar(data, labels);
    });
};

document.onload = getChartData_polar();
