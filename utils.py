import numpy as np
import pandas as pd


def group_table(table, groupby_col, agg_col, agg_type='sum', freq='W'):
    """
    :param table: dataframe with enriched fleet data
    :param groupby_col: dataframe column used for data grouping
    :param agg_col: dataframe column on which to aggregate the data
    :param agg_type: method of aggregation
    :param freq: interval frequency for grouping on date columns
    :return: 2-column dataframe
    """

    group = table.groupby(pd.Grouper(key=groupby_col, freq=freq))
    if agg_type == 'sum':
        return group[agg_col].sum()
    elif agg_type == 'avg':
        return group[agg_col].mean()
    else:
        print("Method of aggregation <{agg_type}> not recognized (currently supported: 'sum' or 'avg').".format(
            agg_type=agg_type)
        )
