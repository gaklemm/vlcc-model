import pandas as pd
from compute import compute_distance, compute_speed, estimate_fuel_consumption


class DataHandler(object):
    """
    Basic data management class.
    """

    def __init__(self, file):
        """
        :param file: input spreadsheet
        """
        self.file = file
        self.df = None

    def load(self):
        """
        :return: dataframe of input data
        """
        print('Loading spreadsheet: {name}'.format(name=str(self.file)))
        # load spreadsheet into pandas dataframe
        self.df = pd.read_excel(io=self.file)
        # force datetime format
        if 'AIS Date Time' in self.df.columns:
            self.df['AIS Date Time'] = pd.to_datetime(self.df['AIS Date Time'])
        return self.df

    def get_vessel_ids(self):
        """
        :return: list of vessel IMO numbers
        """
        return list(self.df['IMO'].unique())


class Vessel(object):
    """
    Class containing vessel information
    """

    def __init__(self, vessel_id, df):
        """
        :param vessel_id: list of vessel IMO numbers
        :param df: dataframe of input data
        """
        self.vessel_id = vessel_id
        print('Building table for vessel {vessel_id}...'.format(vessel_id=self.vessel_id))
        self.data = df[df['IMO'] == self.vessel_id].copy()
        self.journey_start = None
        self.journey_end = None
        self.total_journey_time = None
        self.total_distance = None
        self.average_speed = None
        self.total_fuel_consumption_daily = None
        self.total_fuel_consumption = None

    def get_position(self):
        # add column for current position
        self.data['current_position'] = list(zip(self.data['Latitude'], self.data['Longitude']))
        # add column for previous position
        self.data['previous_position'] = self.data['current_position'].shift(1)
        # replace NaN in first column with next value
        self.data['previous_position'].iat[0] = self.data['current_position'].iat[0]

    def get_time(self):
        # add time differences
        self.data['time_difference'] = self.data['AIS Date Time'].diff()
        # set time difference in first column to zero
        self.data['time_difference'].fillna(pd.Timedelta(seconds=0), inplace=True)
        # convert time difference to hours
        self.data['time_difference_hours'] = self.data['time_difference'].dt.total_seconds() / 3600
        # compute journey time
        self.journey_start = self.data['AIS Date Time'].iat[0]
        self.journey_end = self.data['AIS Date Time'].iat[-1]
        self.total_journey_time = self.journey_end - self.journey_start

    def get_distance(self):
        # compute distances for journey segments
        self.data['distance'] = compute_distance(self.data[['previous_position', 'current_position']])
        # compute total distance
        self.total_distance = sum(self.data['distance'])

    def get_speed(self):
        # compute speeds (in knots) for journey segments
        self.data['speed'] = self.data['distance'] / self.data['time_difference_hours']
        self.data['speed'].fillna(0, inplace=True)
        self.average_speed = compute_speed(self.data['distance'], self.total_journey_time)

    def get_fuel_consumption(self, curve):
        # estimate daily fuel consumption for journey segments
        self.data['fuel_consumption_daily'] = self.data['speed'].map(
            lambda x: estimate_fuel_consumption(x, curve=curve))
        # convert daily fuel consumption estimate to actual travel time
        self.data['fuel_consumption'] = self.data['fuel_consumption_daily'] * self.data['time_difference_hours'] / 24
        # compute total daily and adjusted fuel consumption
        self.total_fuel_consumption_daily = sum(self.data['fuel_consumption_daily'])
        self.total_fuel_consumption = sum(self.data['fuel_consumption'])
