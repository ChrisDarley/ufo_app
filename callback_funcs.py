import pandas as pd
import numpy as np

def get_n_shapes_ranked(df_, n):
    """This function populates data for the bump chart which displays yearly rank
    of shapes, with n shapes to be displayed"""
    def map_fn(row):
        d = dict(zip(np.arange(1.0,row.rank_size+1.0),np.arange(row.rank_size,0.0,-1.0)))
        row['shape_rank'] = d[row.reversed_rank]
        return row
    return (df_
    .sort_values(by=['year', 'temp_rank'], ascending=[True, False])
    .groupby('year')
    .nth(slice(n))
    .assign(reversed_rank=lambda df_: df_
        .groupby('year')
        .temp_rank
        .transform('rank', method='first'))
    .dropna(subset='reversed_rank')
    .assign(rank_size=lambda df_: df_
        .groupby('year')
        .reversed_rank
        .transform('max'))
    .assign(shape_rank=np.nan)
    .apply(map_fn, axis=1)
    .sort_index()
    )

def get_country_shape_counts_chained(tweaked_, country: str='all'):
    """This function populates yearly count and cumulative count
    data for each shape, for use by the double bar chart"""
    if country!='all':
        country_df = tweaked_.loc[lambda df_: df_['country']==country]
    else:
        country_df = tweaked_
    return (country_df
     .groupby([country_df.index.year, 'shape'])
     .shape.count()
     .unstack()
     .fillna(value=0)
     .stack()
     .reset_index(name='year_count')
     .assign(
        cumsum=lambda df_: df_.groupby('shape')
        .year_count
        .transform('cumsum'),
        year_count_log=lambda df_: df_["year_count"].add(1),
        cumsum_log=lambda df_: df_["cumsum"].add(1))
     )