import pandas as pd
import json
import urllib.request
import math
import datetime as dt


class CovidData:
    def __init__(self):
        self.total_individuals_tested = 0
        self.total_confirmed = 0
        self.total_recovered = 0
        self.total_deceased = 0
        self.total_active = 0
        self.latest_top_5_date = None

        self.data_json_raw = 0
        self.df_data_tested = pd.DataFrame()
        self.df_cts = pd.DataFrame()
        self.df_sts_conf = pd.DataFrame()
        self.df_sts_recov = pd.DataFrame()
        self.df_sts_dec = pd.DataFrame()
        self.df_districts = pd.DataFrame()
        self.df_sts_test = pd.DataFrame()
        self.df_recovery = pd.DataFrame()
        self.df_deceased = pd.DataFrame()
        self.df_states = None
        self.df_zones = None
        self.df_conf_top5 = None
        self.df_conf_dt = None
        self.zone_categories = []
        self.zone_count = []
        self.last_updated_time = None

        self.update_data()

    def get_data_json(self):
        response = urllib.request.urlopen('https://api.covid19india.org/data.json')
        self.data_json_raw = json.loads(response.read())

        self.df_data_tested = pd.DataFrame(self.data_json_raw['tested'])
        self.total_individuals_tested = self.df_data_tested.iloc[-1]['totalsamplestested']

        self.df_cts = pd.DataFrame(self.data_json_raw['cases_time_series'])
        self.total_confirmed = self.df_cts.iloc[-1]['totalconfirmed']
        self.total_recovered = self.df_cts.iloc[-1]['totalrecovered']
        self.total_deceased = self.df_cts.iloc[-1]['totaldeceased']
        self.total_active = int(self.total_confirmed) - int(self.total_recovered) - int(self.total_deceased)

        self.df_cts = self.df_cts.astype({'totalconfirmed': 'int32', 'totalrecovered': 'int32',
                                          'totaldeceased': 'int32', 'dailyconfirmed': 'int32',
                                          'dailyrecovered': 'int32', 'dailydeceased': 'int32'})

        self.df_cts['totalactive'] = self.df_cts['totalconfirmed'] - self.df_cts['totalrecovered'] - \
            self.df_cts['totaldeceased']
        self.df_cts['dailyactive'] = self.df_cts['dailyconfirmed'] - self.df_cts['dailyrecovered'] - \
            self.df_cts['dailydeceased']

        self.df_cts['date'] = self.df_cts.apply(lambda row: str(row['date']) + '2020', axis=1)
        self.df_cts['date'] = pd.to_datetime(self.df_cts['date'], errors='ignore', format='%d %B %Y')

        # compute exponential moving average
        # self.df_cts['ema'] = self.df_cts.dailyconfirmed.ewm(span=5, adjust=False).mean()

    def compute_states_cumulative(self):
        df = self.df_sts_conf.iloc[:, 2:-1]
        df_conf = df.sum(axis=0, skipna=True).astype('int32')

        df = self.df_sts_recov.iloc[:, 2:-1]
        df_recov = df.sum(axis=0, skipna=True).astype('int32')

        df = self.df_sts_dec.iloc[:, 2:-1]
        df_dec = df.sum(axis=0, skipna=True).astype('int32')

        df_act = df_conf.subtract(df_recov)
        df_act = df_act.subtract(df_dec)

        return df_conf, df_recov, df_dec, df_act

    def get_states_data(self):
        self.df_sts_conf = pd.read_csv('http://api.covid19india.org/states_daily_csv/confirmed.csv')
        self.df_sts_recov = pd.read_csv('https://api.covid19india.org/states_daily_csv/recovered.csv')
        self.df_sts_dec = pd.read_csv('https://api.covid19india.org/states_daily_csv/deceased.csv')

        df_conf, df_recov, df_dec, df_act = self.compute_states_cumulative()
        # df = self.df_sts_conf.iloc[:, 2:-1]
        # df_conf = df.sum(axis=0, skipna=True).astype('int32')
        df_conf.drop(['LA', 'UN'], inplace=True)

        # df = self.df_sts_recov.iloc[:, 2:-1]
        # df_recov = df.sum(axis=0, skipna=True).astype('int32')
        df_recov.drop(['LA', 'UN'], inplace=True)

        # df = self.df_sts_dec.iloc[:, 2:-1]
        # df_dec = df.sum(axis=0, skipna=True).astype('int32')
        df_dec.drop(['LA', 'UN'], inplace=True)

        # TODO: add the Ladakh active cases to J&K before deleting the Ladakh row

        # df_act = df_conf.subtract(df_recov)
        # df_act = df_act.subtract(df_dec)
        df_act.drop(['LA', 'UN'], inplace=True)

        self.df_states = pd.DataFrame(
            {
                'state_code': df_act.index.values.tolist(),
                'state_names': ['Andaman & Nicobar Island', 'Andhra Pradesh', 'Arunanchal Pradesh', 'Assam', 'Bihar',
                                'Chandigarh', 'Chhattisgarh', 'Daman & Diu', 'NCT of Delhi', 'Dadara & Nagar Havelli',
                                'Goa', 'Gujarat', 'Himachal Pradesh', 'Haryana', 'Jharkhand', 'Jammu & Kashmir',
                                'Karnataka', 'Kerala', 'Lakshadweep', 'Maharashtra', 'Meghalaya', 'Manipur',
                                'Madhya Pradesh', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 'Puducherry', 'Rajasthan',
                                'Sikkim', 'Telangana', 'Tamil Nadu', 'Tripura', 'Uttar Pradesh', 'Uttarakhand',
                                'West Bengal'],
                'Confirmed': df_conf.tolist(),
                'Recovered': df_recov.tolist(),
                'Deceased': df_dec.tolist(),
                'Active': df_act.tolist()
            }
        )

    def get_zone_data(self):
        response = urllib.request.urlopen('https://api.covid19india.org/zones.json')

        json_data = json.loads(response.read())
        self.df_zones = pd.DataFrame(json_data['zones'])

        self.zone_categories = self.df_zones['zone'].value_counts().index.values
        self.zone_categories[-1] = 'Unknown'
        self.zone_count = self.df_zones['zone'].value_counts().tolist()

    def compute_latest_daily_top_5_states(self):
        df = self.df_sts_conf.copy()
        df = df.iloc[-1, :]
        self.latest_top_5_date = df['date']
        df = df.drop(['date', 'TT', 'Unnamed: 40'])
        df = df.astype('int32')
        self.df_conf_top5 = df.nlargest(5)

    def compute_doubling_time(self):
        df = self.df_sts_conf.copy()
        df = df.loc[:, ['date', 'TT']]
        initial_val = df.iloc[0, 1]
        # df['rsum'] = df['TT'].expanding().sum()
        df['ln1'] = df['TT'].apply(lambda x: math.log(x / initial_val))
        # df['ln1'] = df['rsum'].apply(lambda x: math.log(x / initial_val))
        df['days'] = df.index.values
        df['k'] = df['ln1'].div(df['days'])
        df = df.iloc[1:, :]
        df['DT'] = df['k'].apply(lambda x: math.log(2) / x)
        df = df.loc[df['DT'] >= 0]
        self.df_conf_dt = df.iloc[5:, :]  # Remove initial rows as outliers

    def get_district_data(self):
        self.df_districts = pd.read_csv('https://api.covid19india.org/csv/latest/district_wise.csv')

    def get_states_test_data(self):
        self.df_sts_test = pd.read_csv('https://api.covid19india.org/csv/latest/statewise_tested_numbers_data.csv')

        self.df_sts_test = self.df_sts_test.loc[:, ['Updated On', 'State', 'Total Tested', 'Positive', 'Negative',
                                                    'Test positivity rate', 'Tests per thousand', 'Tests per million',
                                                    'Tests per positive case', 'Population NCP 2019 Projection']]

    def get_raw_data(self):
        raw_data_src = ['https://api.covid19india.org/csv/latest/raw_data1.csv',
                        'https://api.covid19india.org/csv/latest/raw_data2.csv',
                        'https://api.covid19india.org/csv/latest/raw_data3.csv',
                        'https://api.covid19india.org/csv/latest/raw_data4.csv',
                        'https://api.covid19india.org/csv/latest/raw_data5.csv',
                        'https://api.covid19india.org/csv/latest/raw_data6.csv']

        def process_recov_dec(df):
            df['Date Announced'] = pd.to_datetime(df['Date Announced'], format='%d/%m/%Y')
            df['Status Change Date'] = pd.to_datetime(df['Status Change Date'], format='%d/%m/%Y')
            df['Duration'] = df['Status Change Date'] - df['Date Announced']
            df['Duration'] = df['Duration'].dt.days

        for src in raw_data_src:
            df_raw = pd.read_csv(src)
            df_raw = df_raw.loc[:,
                                ['Date Announced', 'Detected State', 'State code', 'Current Status',
                                 'Status Change Date']]
            df_raw_recov = df_raw.loc[df_raw['Current Status'] == 'Recovered'].copy()
#            df_raw_recov['Date Announced'] = pd.to_datetime(df_raw_recov['Date Announced'], format='%d/%m/%Y')
#            df_raw_recov['Status Change Date'] = pd.to_datetime(df_raw_recov['Status Change Date'], format='%d/%m/%Y')
#            df_raw_recov['Duration'] = df_raw_recov['Status Change Date'] - df_raw_recov['Date Announced']
#            df_raw_recov['Duration'] = df_raw_recov['Duration'].dt.days
            process_recov_dec(df_raw_recov)

            self.df_recovery = self.df_recovery.append(df_raw_recov, ignore_index=True)

            df_raw_dec = df_raw.loc[df_raw['Current Status'] == 'Deceased'].copy()
#            df_raw_dec['Date Announced'] = pd.to_datetime(df_raw_dec['Date Announced'], format='%d/%m/%Y')
#            df_raw_dec['Status Change Date'] = pd.to_datetime(df_raw_dec['Status Change Date'], format='%d/%m/%Y')
#            df_raw_dec['Duration'] = df_raw_dec['Status Change Date'] - df_raw_dec['Date Announced']
#            df_raw_dec['Duration'] = df_raw_dec['Duration'].dt.days
            process_recov_dec(df_raw_dec)

            self.df_deceased = self.df_deceased.append(df_raw_dec, ignore_index=True)

    def update_data(self):
        self.get_data_json()
        self.get_states_data()
        self.get_zone_data()
        self.compute_latest_daily_top_5_states()
        self.compute_doubling_time()
        self.get_district_data()
        self.get_states_test_data()
        self.get_raw_data()

        self.last_updated_time = dt.datetime.now()

    def refresh_data(self):
        cur_time = dt.datetime.now()
        if (cur_time - self.last_updated_time).seconds > 14400:
            print(f'Current Time: {cur_time}, Last Update Time: {self.last_updated_time}. Forcing update')
            self.update_data()


data = CovidData()
