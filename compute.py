import numpy as np
from geopy.distance import distance


def compute_distance(position_data):
    """
    :param position_data: 2-column dataframe containing coordinate positions
    :return: geodesic distance between two coordinates in nautical miles
    (https://github.com/geopy/geopy/blob/master/geopy/distance.py)
    """
    return position_data.apply(lambda x: distance(*x).nm, axis=1)


def compute_speed(dist, total_journey_time):
    """
    :param dist: list or column of distances
    :param total_journey_time: total journey time
    :return: average speed in knots
    """
    return sum(dist) / (total_journey_time.total_seconds() / 3600)


def estimate_fuel_consumption(speed, curve):
    """
    :param speed: average speed in knots
    :param curve: instance of Curve class
    :return: fuel consumption predicted by curve model
    """
    if 0 <= speed <= 25:
        return curve.interpolate(speed)
    elif speed > 25:
        return curve.quadratic_fit(speed)
    else:
        print("Speed <{speed} knots> is invalid. Applying quadratic fit to prevent program error.".format(speed=speed))
        return curve.quadratic_fit(speed)


def compute_fleet_data(vessel_data):
    """
    :param vessel_data: enriched dataframe for individual vessel
    :return: aggregated fleet metrics: total distance, average speed, total consumption
    """
    fleet_distance = 0
    fuel_consumption_daily = 0
    fuel_consumption = 0
    fleet_speed = 0

    for v in vessel_data.values():
        if v.data.shape[0] > 1:
            # compute fleet-level metrics
            fleet_distance += v.total_distance
            fleet_speed += v.average_speed
            fuel_consumption_daily += v.total_fuel_consumption_daily
            fuel_consumption += v.total_fuel_consumption
        else:
            # skip calculations for empty vessel tables or vessel tables with a single data point
            v.total_distance = np.NaN
            v.total_fuel_consumption_daily = np.NaN
            v.total_fuel_consumption = np.NaN
            v.average_speed = np.NaN

    # calculate simple average speed for fleet
    fleet_average_speed = fleet_speed / len(vessel_data)

    return fleet_distance, fleet_average_speed, fuel_consumption_daily, fuel_consumption
