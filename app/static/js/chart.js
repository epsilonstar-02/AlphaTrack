// Chart configuration
const chartConfig = {
    responsive: true,
    displayModeBar: true,
    modeBarButtonsToRemove: ['lasso2d', 'select2d', 'autoScale2d'],
    displaylogo: false,
    toImageButtonOptions: {
        format: 'png',
        filename: 'stock_chart',
        height: 500,
        width: 800,
        scale: 1
    }
};

// Update chart with stock data
function updateChart(stockData) {
    const chartDiv = document.getElementById('stockChart');
    
    if (!chartDiv) {
        console.error('Chart container not found');
        return;
    }
    
    if (!stockData || !stockData.data || !Array.isArray(stockData.data) || stockData.data.length === 0) {
        showChartError('No data available for chart');
        return;
    }
    
    try {
        const dates = stockData.data.map(item => item.date);
        const closePrices = stockData.data.map(item => item.close);
    const highPrices = stockData.data.map(item => item.high);
    const lowPrices = stockData.data.map(item => item.low);
    const openPrices = stockData.data.map(item => item.open);
    const volumes = stockData.data.map(item => item.volume);
        
        // Create traces
        const traces = [
            {
                x: dates,
                y: closePrices,
                type: 'scatter',
                mode: 'lines',
                name: 'Close Price',
                line: {
                    color: '#007bff',
                    width: 2
                },
                hovertemplate: 
                    '<b>Date:</b> %{x}<br>' +
                    '<b>Close:</b> $%{y:.2f}<br>' +
                    '<extra></extra>'
            }
        ];
        
        const layout = {
            title: {
                text: `${stockData.symbol} Stock Price Trend`,
                font: { size: 16, color: '#333' },
                x: 0.02
            },
            xaxis: {
                title: 'Date',
                type: 'date',
                showgrid: true,
                gridcolor: '#f0f0f0',
                showline: true,
                linecolor: '#d0d0d0'
            },
            yaxis: {
                title: 'Price ($)',
                showgrid: true,
                gridcolor: '#f0f0f0',
                showline: true,
                linecolor: '#d0d0d0',
                tickformat: '$.2f'
            },
            plot_bgcolor: 'white',
            paper_bgcolor: 'white',
            font: {
                family: 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif',
                size: 12,
                color: '#333'
            },
            margin: {
                l: 60,
                r: 30,
                t: 60,
                b: 40
            },
            showlegend: false,
            hovermode: 'x unified'
        };
        
        hideElement(document.getElementById('chartPlaceholder'));
        hideElement(document.getElementById('chartError'));
        showElement(chartDiv);
        
        Plotly.newPlot(chartDiv, traces, layout, chartConfig);
        
        chartDiv.on('plotly_click', function(data) {
            if (data.points && data.points.length > 0) {
                const point = data.points[0];
                const date = point.x;
                const price = point.y;
                showDataPointInfo(date, price, stockData);
            }
        });
        
    } catch (error) {
        console.error('Error rendering chart:', error);
        showChartError('Failed to render chart. Please try again.');
    }
}

function updateCandlestickChart(stockData) {
    const chartDiv = document.getElementById('stockChart');
    
    if (!chartDiv || !stockData.data || stockData.data.length === 0) {
        showChartError('No data available for chart');
        return;
    }
    
    try {
        const dates = stockData.data.map(item => item.date);
        const openPrices = stockData.data.map(item => item.open);
        const highPrices = stockData.data.map(item => item.high);
        const lowPrices = stockData.data.map(item => item.low);
        const closePrices = stockData.data.map(item => item.close);
        
        const trace = {
            x: dates,
            close: closePrices,
            high: highPrices,
            low: lowPrices,
            open: openPrices,
            type: 'candlestick',
            name: stockData.symbol,
            increasing: { line: { color: '#28a745' } },
            decreasing: { line: { color: '#dc3545' } }
        };
        
        const layout = {
            title: `${stockData.symbol} Candlestick Chart`,
            xaxis: {
                title: 'Date',
                type: 'date',
                showgrid: true,
                gridcolor: '#f0f0f0'
            },
            yaxis: {
                title: 'Price ($)',
                showgrid: true,
                gridcolor: '#f0f0f0'
            },
            plot_bgcolor: 'white',
            paper_bgcolor: 'white',
            margin: { l: 60, r: 30, t: 60, b: 40 },
            showlegend: false
        };
        
        hideElement(document.getElementById('chartPlaceholder'));
        hideElement(document.getElementById('chartError'));
        showElement(chartDiv);
        
        Plotly.newPlot(chartDiv, [trace], layout, chartConfig);
        
    } catch (error) {
        console.error('Error rendering candlestick chart:', error);
        showChartError('Failed to render chart. Please try again.');
    }
}

// Create volume chart
function updateVolumeChart(stockData) {
    const chartDiv = document.getElementById('stockChart');
    
    if (!chartDiv || !stockData.data || stockData.data.length === 0) {
        showChartError('No data available for chart');
        return;
    }
    
    try {
        const dates = stockData.data.map(item => item.date);
        const volumes = stockData.data.map(item => item.volume);
        
        const trace = {
            x: dates,
            y: volumes,
            type: 'bar',
            name: 'Volume',
            marker: {
                color: '#17a2b8',
                opacity: 0.7
            },
            hovertemplate: 
                '<b>Date:</b> %{x}<br>' +
                '<b>Volume:</b> %{y:,.0f}<br>' +
                '<extra></extra>'
        };
        
        const layout = {
            title: `${stockData.symbol} Trading Volume`,
            xaxis: {
                title: 'Date',
                type: 'date',
                showgrid: true,
                gridcolor: '#f0f0f0'
            },
            yaxis: {
                title: 'Volume',
                showgrid: true,
                gridcolor: '#f0f0f0'
            },
            plot_bgcolor: 'white',
            paper_bgcolor: 'white',
            margin: { l: 60, r: 30, t: 60, b: 40 },
            showlegend: false
        };
        
        hideElement(document.getElementById('chartPlaceholder'));
        hideElement(document.getElementById('chartError'));
        showElement(chartDiv);
        
        Plotly.newPlot(chartDiv, [trace], layout, chartConfig);
        
    } catch (error) {
        console.error('Error rendering volume chart:', error);
        showChartError('Failed to render chart. Please try again.');
    }
}

// Show data point information
function showDataPointInfo(date, price, stockData) {
    const formattedDate = new Date(date).toLocaleDateString();
    const message = `Date: ${formattedDate}\nPrice: $${price.toFixed(2)}`;
    
    console.log('Data point clicked:', message);
}

// Resize chart when window resizes
window.addEventListener('resize', function() {
    const chartDiv = document.getElementById('stockChart');
    if (chartDiv && chartDiv.data) {
        Plotly.Plots.resize(chartDiv);
    }
});

function clearChart() {
    const chartDiv = document.getElementById('stockChart');
    if (chartDiv) {
        Plotly.purge(chartDiv);
        hideElement(chartDiv);
        showElement(document.getElementById('chartPlaceholder'));
    }
}

function switchChartType(type, stockData) {
    if (!stockData) return;
    
    switch (type) {
        case 'line':
            updateChart(stockData);
            break;
        case 'candlestick':
            updateCandlestickChart(stockData);
            break;
        case 'volume':
            updateVolumeChart(stockData);
            break;
        default:
            updateChart(stockData);
    }
}
