from abc import ABCMeta, abstractmethod
from openpyxl.chart import LineChart, Reference
import pandas as pd


# todo: format date axis (add spacing, rotation & shorten)
# todo: adjust the scaling of the y-axis

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

    def _plot_line_chart_against_date_in_excel(self, writer, y_axis_min=0.98, y_axis_max=1.009,
                                               sheet="backtest_results", y_series_col=9,
                                               chart_title="Equity Curve", cell_ref="M12"):
        # Add a line chart
        # Point to the sheet 'backtest_results', where the chart will be added
        wb = writer.book
        ws = wb[sheet]

        # Grab the maximum row number in the sheet
        max_row = ws.max_row

        # Refer to the data of equity_curve by the range of rows and cols on the sheet
        values_equity_curve = Reference(ws, min_col=y_series_col, min_row=1, max_col=y_series_col, max_row=max_row)

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

        chart.y_axis.scaling.max = y_axis_max
        chart.y_axis.scaling.min = y_axis_min

        # Add title to the chart
        chart.title = chart_title

        # Add the chart to the cell of M12 on the sheet ws
        ws.add_chart(chart, cell_ref)

    def generate_report(self, report_title='test_report', y_axis_min=0.98, y_axis_max=1.009):

        # Set up an ExcelWriter
        with pd.ExcelWriter(f'reports/{report_title}.xlsx', engine='openpyxl') as writer:

            # Export data
            self.backtest_results_df.to_excel(writer, sheet_name="backtest_results")

            # add line chart for the equity curve
            self._plot_line_chart_against_date_in_excel(writer=writer, y_axis_min=y_axis_min, y_axis_max=y_axis_max)

            # add line chart for the returns curve
            self._plot_line_chart_against_date_in_excel(writer=writer, y_axis_min=y_axis_min, y_axis_max=y_axis_max,
                                                        sheet="backtest_results", y_series_col=8,
                                                        chart_title="Returns Plot", cell_ref="M40"
                                                        )

            # add line chart for liquidity index curve

            # add line chart for the fixed rate curve

            # add line chart for cumulative apy curve

            # place the backtest summary stats into the report


