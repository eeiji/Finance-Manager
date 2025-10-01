const charts = {};
const monthNames = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"];

/**
 * Cria ou substitui um gráfico no canvas especificado
 * @param {string} canvasId - ID do canvas HTML
 * @param {string} type - Tipo do gráfico (bar, pie, line, etc.)
 * @param {object} data - Dados do gráfico (labels, datasets)
 * @param {object} options - Configurações do gráfico
 */

function renderChart(canvasId, type, data, options = {}) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  // Se já existir gráfico nesse canvas, destruir antes
  if (charts[canvasId]) {
    charts[canvasId].destroy();
  }

  charts[canvasId] = new Chart(ctx.getContext("2d"), {
    type,
    data,
    options: Object.assign(
      {
        responsive: true,
        maintainAspectRatio: false
      },
      options
    )
  });
}

/**
 * Renderiza os relatórios (gráficos de receitas/despesas e categorias)
 * @param {Array} monthlyData - [{month, type, total}, ...]
 * @param {Array} categoriesData - [{category, type, total}, ...]
 */
function renderReports(monthlyData, categoriesData) {
    const hasMonthly = Array.isArray(monthlyData) && monthlyData.length > 0;
    const hasCategories = Array.isArray(categoriesData) && categoriesData.length > 0;

    const monthlyContainer = document.getElementById("monthlyChartContainer");
    const categoryContainer = document.getElementById("categoryChartContainer");

  // --- Gráfico de Receitas vs Despesas (Mensal) ---
    if (hasMonthly) {
      const months = [...new Set(monthlyData.map(m => monthNames[parseInt(m.month) - 1]))].sort();

      const incomes = months.map(m => {
        const row = monthlyData.find(r => monthNames[parseInt(r.month) - 1] === m && r.type === "income");
        return row ? Number(row.total) : 0;
      });

      const expenses = months.map(m => {
        const row = monthlyData.find(r => monthNames[parseInt(r.month) - 1] === m && r.type === "expense");
        return row ? Number(row.total) : 0;
      });

      const saldo = months.map((m, i) => incomes[i] - expenses[i] + (i > 0 ? saldo[i-1] : 0));

      renderChart("monthlyChart", "bar", {
        labels: months,
        datasets: [
          { label: "Incomes", data: incomes, backgroundColor: "rgba(40,167,69,0.8)" },
          { label: "Expenses", data: expenses, backgroundColor: "rgba(220,53,69,0.8)" },
          { label: "Accumulated balance", type: "line", data: saldo, borderColor: "blue", fill: false }
        ]
      });
    }

  // --- Category Chart (only expenses) ---
  if (hasCategories) {
    const expenseCats = categoriesData.filter(c => c.type === "expense");
    const catLabels = expenseCats.map(c => c.category);
    const catValues = expenseCats.map(c => Number(c.total));

    if (catLabels.length > 0) {
      renderChart("categoryChart", "pie", {
        labels: catLabels,
        datasets: [{
          data: catValues,
          backgroundColor: [
            "#FF6384","#36A2EB","#FFCE56","#4BC0C0","#9966FF","#FF9F40",
            "#8A8A8A","#6FAF98","#C77DFF"
          ]
        }]
      });
    }
  } else {
    if (categoryContainer) {
      categoryContainer.innerHTML = "<p>There is no data for expenses by category graph.</p>";
    }
  }
}


