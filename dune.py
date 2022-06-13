from duneanalytics import DuneAnalytics # ref: https://github.com/itzmestar/duneanalytics
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()


class Dune:

    def __init__(self, username, password):

        self.dune = DuneAnalytics(username, password)
        self.dune.login()
        self.dune.fetch_auth_token()

    def query_result(self, query_id):
        # fetch query result id using query id
        # query id for any query can be found from the url of the query:
        # for example:
        # https://duneanalytics.com/queries/4494/8769 => 4494
        # https://duneanalytics.com/queries/3705/7192 => 3705
        # https://duneanalytics.com/queries/3751/7276 => 3751
        result_id = self.dune.query_result_id_v2(query_id=query_id)
        data = self.dune.query_result(result_id)
        return data

    def query_euler_interest_rates(self, coin='usdc'):

        # coin universe for euler: weth, dai, usdc, wbtc, usdt

        raw_data = self.query_result(query_id=695308)['data']['get_result_by_result_id']

        df = pd.DataFrame(columns=['date', 'apy'])

        for i in range(len(raw_data)):

            symbol = raw_data[i]['data']['symbol']

            if symbol == coin.upper():
                date = raw_data[i]['data']['date_trunc']
                apy = raw_data[i]['data'][coin]

                df = df.append({
                    'date': date,
                    'apy': apy,
                }, ignore_index=True)

        return df


    def query_aave_liquidity_index(self, query_id=891837, column_name="liquidityIndexUSDC"):

        # aave usdc query
        # https://dune.com/queries/891837

        # aave dai query
        # https://dune.com/queries/905965

        raw_data = self.query_result(query_id=query_id)['data']['get_result_by_result_id']

        df = pd.DataFrame(columns=['date', 'liquidityIndex'])

        for i in range(len(raw_data)):

            date = raw_data[i]['data']['date']
            liquidityIndex = raw_data[i]['data'][column_name]

            df = df.append({
                'date': date,
                'liquidityIndex': liquidityIndex,
            }, ignore_index=True)

        return df



if __name__ == '__main__':
    # dune = Dune(username=os.environ.get('USERNAME'), password=os.environ.get("PASSWORD"))
    dune = Dune(username=os.environ.get('USERNAME'), password=os.environ.get("PASSWORD"))
    # df = dune.query_euler_interest_rates(coin='usdc')
    aave_liquidity_index_df = dune.query_aave_liquidity_index(query_id=905965, column_name="liquidityIndexDAI")
    aave_liquidity_index_df.to_csv("datasets/aave_dai.csv", index=False)

