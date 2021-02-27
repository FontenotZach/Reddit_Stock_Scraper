import Chart from 'chart.js';
import ChartDataSource from 'chartjs-plugin-datasource';
import './index.css';
var ReactDOM = require('react-dom');

var chartColors = {
	red: 'rgb(255, 99, 132)',
	blue: 'rgb(54, 162, 235)',
  black: 'rgb(0,0,0)'
};

var color = Chart.helpers.color;
var config_1 = {
  type: 'bar',
	data: {
		datasets: [{
      yAxisID: 'score',
			backgroundColor: color(chartColors.blue).alpha(.2).rgbString(),
			borderColor: color(chartColors.blue).rgbString(),
      borderWidth: 1.5
		}]
	},
	plugins: [ChartDataSource],
	options: {
		title: {
			display: true,
			text: 'R/Investing Top Mentions'
		},
		scales: {
			xAxes: [{
				scaleLabel: {
					display: true,
					labelString: 'Ticker'
				}
			}],
			yAxes: [{
				id: 'score',
				gridLines: {
					drawOnChartArea: false
				},
				scaleLabel: {
					display: true,
					labelString: 'Mention Score'
				}
			}]
		},
		plugins: {
      datasource: {
				type: 'sheet',
				url: 'sample-2-index.xlsx',
				rowMapping: 'datapoint',
				datapointLabels: 'Sheet1!A1:C1',
				datapointLabelMapping: {
					_dataset: 'dataset',
					_index: 'symbol',
					x: 'symbol',
					y: 'score'
				},
				data: 'Sheet1!A2:C20'
			}
		}
	}
};

var config_2 = {
  type: 'bar',
	data: {
		datasets: [{
      yAxisID: 'score',
			backgroundColor: color(chartColors.red).alpha(.2).rgbString(),
			borderColor: color(chartColors.red).rgbString(),
      borderWidth: 1.5
		}]
	},
	plugins: [ChartDataSource],
	options: {
		title: {
			display: true,
			text: 'R/WallStreetBets Top Mentions'
		},
		scales: {
			xAxes: [{
				scaleLabel: {
					display: true,
					labelString: 'Ticker'
				}
			}],
			yAxes: [{
				id: 'score',
				gridLines: {
					drawOnChartArea: false
				},
				scaleLabel: {
					display: true,
					labelString: 'Mention Score'
				}
			}]
		},
		plugins: {
      datasource: {
				type: 'sheet',
				url: 'sample-1-index.xlsx',
				rowMapping: 'datapoint',
				datapointLabels: 'Sheet1!A1:C1',
				datapointLabelMapping: {
					_dataset: 'dataset',
					_index: 'symbol',
					x: 'symbol',
					y: 'score'
				},
				data: 'Sheet1!A2:C20'
			}
		}
	}
};

window.onload = function() {
  var canvas = document.getElementById('InvestingChart')
	var ctx = canvas.getContext('2d');
	window.myChart = new Chart(ctx, config_1);
	

  var canvas = document.getElementById('WSBChart')
	var ctx = canvas.getContext('2d');
	window.myChart = new Chart(ctx, config_2);
};
