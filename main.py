from compute import compute_fleet_data
from data import DataHandler, Vessel
from model import Curve
import pandas as pd
from utils import group_table
from plot import Graph

# assign input files
vlcc_long_lat = 'data/vlcc_long_lat.xlsx'
vlcc_consumption_curve = 'data/VLCC_consumption_curve.xlsx'

# initialize data handler
vessel_positions = DataHandler(file=vlcc_long_lat)
fuel_consumption = DataHandler(file=vlcc_consumption_curve)

# load main table, vessel IDs, and fuel consumption curve
position_data = vessel_positions.load()
vessel_ids = vessel_positions.get_vessel_ids()
fuel_consumption_curve = fuel_consumption.load()

# instantiate Curve class
curve = Curve(feature=fuel_consumption_curve['Speed (knots)'],
              target=fuel_consumption_curve['VLCC Fuel Oil Consumption in tonnes per day']
              )

# generate dictionary of classes containing individual vessel tables
vessels = {}
for vessel_id in vessel_ids:
    vessel = Vessel(df=position_data, vessel_id=vessel_id)
    if vessel.data.shape[0] > 1:
        # enrich vessel tables
        vessel.get_position()
        vessel.get_time()
        vessel.get_distance()
        vessel.get_speed()
        vessel.get_fuel_consumption(curve=curve)
    vessels[vessel_id] = vessel

# get aggregate data
fleet_dist, fleet_avg_speed, fleet_fc_daily, fleet_fc = compute_fleet_data(vessel_data=vessels)

# print key metrics to console
print('Distance travelled by fleet: {dist_nm:,} nautical miles ({dist_km:,} kilometres)'.format(
    dist_nm=int(fleet_dist),
    dist_km=int(1.852*fleet_dist)),
    '\nAverage speed: {speed:.2f} knots'.format(speed=round(fleet_avg_speed, 2)),
    '\nEstimated fuel consumption: {fuel_consumption:,} tonnes'.format(fuel_consumption=int(fleet_fc)),
)

# build aggregate table from enriched vessel tables
agg_table = pd.concat([v.data for v in vessels.values()], sort=True)

# add date column for easier grouping
agg_table['date'] = pd.to_datetime(agg_table['AIS Date Time'].dt.date)

# make grouped tables for plotting
date_distance = group_table(table=agg_table, groupby_col='date', agg_col='distance', agg_type='sum')
date_speed = group_table(table=agg_table, groupby_col='date', agg_col='speed', agg_type='avg')
date_fuel_consumption = group_table(table=agg_table, groupby_col='date', agg_col='fuel_consumption', agg_type='sum')
date_fuel_consumption_daily = group_table(table=agg_table, groupby_col='date', agg_col='fuel_consumption_daily',
                                          agg_type='sum')
date_draught = group_table(table=agg_table, groupby_col='date', agg_col='fuel_consumption', agg_type='avg')

# instantiate graphs
date_distance_graph = Graph(data=date_distance, name='distance_over_time', value='Distance (nm)')
date_speed_graph = Graph(data=date_speed, name='avg_speed_over_time', value='Average speed (knots)')
date_fuel_consumption_graph = Graph(data=date_fuel_consumption, name='est_fuel_consumption_over_time',
                                    value='Estimated fuel consumption (tonnes)')
date_fuel_consumption_daily_graph = Graph(data=date_fuel_consumption_daily,
                                          name='est_daily_fuel_consumption_over_time',
                                          value='Estimated fuel consumption (tonnes per day)')
date_draught_graph = Graph(data=date_draught, name='draught_pct_over_time', value='Draught Percentage')


# generate plots
graphs = [date_distance_graph, date_speed_graph, date_fuel_consumption_graph, date_fuel_consumption_daily_graph,
          date_draught_graph]
for graph in graphs:
    graph.plot()
    graph.save()
