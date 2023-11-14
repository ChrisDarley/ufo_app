
# testing the requests and seeing what is broken down in my code
import pandas as pd
import aiohttp
import backoff
import asyncio
import time
import numpy as np
import json

def make_requests():
    
    df = pd.read_csv("tweaked_map_data.csv",
        index_col='datetime',
        parse_dates=True)

    us_data = (df
    # select rows where country is 'us' and lat and lon are not null
    .loc[lambda df_: 
        (df_["country"]=='us')&
        (~df_["latitude"].isna())&
        (~df_["longitude"].isna())    
        ]
    .assign(
        # make a query string for every row based on latitude and
        # longitude and add it to a column
        query_string=lambda df_: df_.apply(lambda row:
            f"https://geo.fcc.gov/api/census/block/find?latitude="
            f"{row['latitude']}%09&longitude={row['longitude']}&c"
            f"ensusYear=2020&showall=false&format=json", axis=1)
            )
    )

    print('Query strings generated. Making requests now.')
    urls = us_data["query_string"]

    responses = []

    # def fatal_code(e):
    #     return 400 <= e.response.status_code < 500

    @backoff.on_exception(
        backoff.constant,
        aiohttp.ClientError,
        raise_on_giveup=False,
        max_time=500,
        interval=0.01,
    )
    async def get_url(session, url):
        async with session.get(url) as response:
            if response.status == 200:
                responses.append(json.dumps(await response.json()))
            else:
                responses.append('additional_query_needed')
            # await responses.append(response.status_code())
            
    async def main():
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            counter = 0
            current = time.time()
            start = time.time()
            for url in urls:
                counter +=1
                await get_url(session, url)
                if counter%1000==0:
                    print('\n Request Count: ', counter, '\n\n',
                        'Total time: ',
                        f'{np.floor((time.time()-start)/3600)} hours, '
                        f'{np.floor(((time.time()-start)%3600)/60)} minutes, '
                        f'{np.floor((time.time()-start)%60)} seconds',
                        '\n\n', 'Time for last 1000: ',
                        f'{np.floor((time.time()-current)/3600)} hours, '
                        f'{np.floor(((time.time()-current)%3600)/60)} minutes, '
                        f'{np.floor((time.time()-current)%60)} seconds', '\n\n'
                        )
                    current=time.time()
                    

    asyncio.run(main())

    if len(responses)==len(us_data):
        us_data = us_data.assign(json=responses)
        us_data.to_csv('map_data_raw.csv')
        print('map_data_raw.csv created')
    else:
        print('failed to create map_data_raw.csv')





