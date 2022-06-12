from abc import ABCMeta, abstractmethod
from openpyxl.chart import LineChart, Reference
import pandas as pd


class Reporter(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def generate_report(self):
        """
        Generates a report based on the results of the backtest
        """

        raise NotImplementedError("Should implement generate_report()")


class SimpleBacktestReporter(Reporter):


    def __init__(self, backtest_results_df, summary_stats):

        self.backtest_results_df = backtest_results_df
        self.summary_stats = summary_stats

    def generate_report(self, report_title='test_report'):

        # Set up an ExcelWriter
        with pd.ExcelWriter(f'reports/{report_title}.xlsx', engine='openpyxl') as writer:

            # Export data
            self.backtest_results_df.to_excel(writer, sheet_name="backtest_results")

            # Add a line chart
            # Point to the sheet 'backtest_results', where the chart will be added
            wb = writer.book
            ws = wb['backtest_results']

            # Grab the maximum row number in the sheet
            max_row = ws.max_row

            # Refer to the data of equity_curve by the range of rows and cols on the sheet
            values_equity_curve = Reference(ws, min_col=5, min_row=1, max_col=5, max_row=max_row)

            # Refer to the date
            dates = Reference(ws, min_col=1, min_row=2, max_col=1, max_row=max_row)

            # Create a LineChart
            chart = LineChart()

            # Add data of equity_curve to the chart
            chart.add_data(values_equity_curve, titles_from_data=True)

            # Set the dates as the x axis and format it
            chart.set_categories(dates)
            chart.x_axis.number_format = 'mmm-yy'
            chart.x_axis.majorTimeUnit = 'days'
            chart.x_axis.title = 'Date'

            # Add title to the chart
            chart.title = 'Backtest Equity Curve'

            # Refer to equity_curve data, which is with index 1 within the chart, and style it
            s1 = chart.series[1]
            s1.graphicalProperties.line.dashStyle = 'sysDot'
            # Add the chart to the cell of G12 on the sheet ws
            ws.add_chart(chart, 'G12')

