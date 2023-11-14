## python file with all of the sql queries
import pandas as pd
from sqlalchemy import create_engine
# from sqlalchemy.engine.url import URL
from sqlalchemy_utils import database_exists, create_database
import psycopg2
# import json
import configparser

def set_config():
    # parsing the config file for sqlalchemy and psycopg2
    config = configparser.ConfigParser()
    config.read('ufo_viz.ini')
    return config

def format_map_data():
    """creates a database with map data, extracts relevant columns
    from json column, and saves the table to a csv""" 

    config = set_config()

    # sqlalchemy con string
    sqlalchemy_con_string = (
        f"postgresql+psycopg2://{config['sqlalchemy']['username']}:"
        f"{config['sqlalchemy']['password']}@"
        f"{config['sqlalchemy']['host']}:"
        f"{config['sqlalchemy']['port']}/"
        f"{config['sqlalchemy']['database']}"
        )

    # Creating database using sqlalchemy
    engine = create_engine(sqlalchemy_con_string)
    if database_exists(engine.url):
        raise RuntimeError("""
            Database already exists.
            Drop database "ufo_viz_db" to re-run this file.""")
    if not database_exists(engine.url):
        create_database(engine.url)

    # connecting to database using psycopg2
    conn = psycopg2.connect(**config['psycopg2'])

        # exporting map_data_raw to the postgres database
    map_data_raw = pd.read_csv("map_data_raw.csv",
        index_col='datetime', parse_dates=True)
    map_data_raw.to_sql(name="map_data", con=sqlalchemy_con_string,
        if_exists='replace')

    # changing json column to jsonb data type
    map_data_change_type_sql = """
    ALTER TABLE map_data
    ALTER COLUMN json TYPE JSONB using json::JSONB;
    """

    # adding columns to the dataframe 
    map_data_add_columns_sql = """
    ALTER TABLE map_data
    ADD COLUMN fips TEXT,   
    ADD COLUMN state_name TEXT,
    ADD COLUMN county_name TEXT"""

    # extracting data from json column to fill out the added columns
    map_data_update_columns_sql = """
    UPDATE map_data SET
    fips = json#>>'{County,FIPS}',
    state_name = json#>>'{State,name}',
    county_name = json#>>'{County,name}'
    """

    # executing the sql
    with conn:
        with conn.cursor() as curs:
            curs.execute(map_data_change_type_sql)
            curs.execute(map_data_add_columns_sql)
            curs.execute(map_data_update_columns_sql)

    # closing connection
    conn.close()

    # reading table from sql and saving as a csv

    # reading from sql  
    map_data_formatted = pd.read_sql_table('map_data', 
        sqlalchemy_con_string, index_col='datetime',
        parse_dates=True)
    
    
    map_data_formatted = (map_data_formatted
        #dropping 'county' from after each county name
        .assign(county_name=lambda df_: df_["county_name"].apply(
            lambda row: row.rsplit(' ', 1)[0]))
        # renaming city column to match with county_name and state_name
        .rename(columns={'city':'city_name'})
        # sorting the index chronologically
        .sort_index()
    )

    # saving select columns to a csv file
    map_data_formatted.to_csv('map_data_formatted.csv', columns=[
        'city_name', 'county_name', 'state_name', 'shape',
        'comments', 'latitude', 'longitude', 'comment_length',
        'duration_formatted', 'duration_seconds', 'minutes',
        'seconds', 'fips'])

















# Creating and populating requests_data table

# # loading location from csv
# location = pd.read_csv(
#     'location_raw.csv', index_col='datetime',
#     parse_dates=True)

# # exporting df to dataframe
# location['json'].to_sql(name="requests_data", con=sqlalchemy_con_string,
#     if_exists='replace')

# requests_data_add_columns_sql = """
# ALTER TABLE requests_data
# ADD COLUMN state_fips TEXT,
# ADD COLUMN state_code TEXT,
# ADD COLUMN state_name TEXT,
# ADD COLUMN county_fips TEXT,
# ADD COLUMN county_name TEXT;
# """

# requests_data_change_type_sql = """
# ALTER TABLE requests_data
# ALTER COLUMN json TYPE JSONB using json::JSONB;
# """

# requests_data_update_columns_sql = """
# UPDATE requests_data SET
# state_fips = json#>>'{State,FIPS}',
# state_code = json#>>'{State,code}',
# state_name = json#>>'{State,name}',
# county_fips = json#>>'{County,FIPS}',
# county_name = json#>>'{County,name}';
# """

# # Adding column definitions to requests_data and populating added columns
# with conn:
#     with conn.cursor() as curs:
#         curs.execute(requests_data_add_columns_sql)
#         curs.execute(requests_data_change_type_sql)
#         curs.execute(requests_data_update_columns_sql)




# # Creating and populating the counties table

# # Creating table to store counties.json and extracted columns
# with open("counties.json") as f:
#     counties = json.load(f)

# counties_creation_sql = """
# CREATE TABLE counties (
#     id SERIAL,
#     json JSONB
# );
# """

# counties_insertion_sql = """
# INSERT INTO counties (json)
# VALUES (%s);
# """

# counties_add_columns_sql = """
# ALTER TABLE counties
# ADD COLUMN fips TEXT,
# ADD COLUMN state_fips TEXT,
# ADD COLUMN county_fips TEXT,
# ADD COLUMN county_name TEXT,
# ADD COLUMN census_area TEXT;
# """

# counties_update_sql = """
# UPDATE counties SET
# fips = concat(
#     json->'properties'->>'STATE',
#     json->'properties'->>'COUNTY'),
# state_fips = json->'properties'->>'STATE',
# county_fips = json->'properties'->>'COUNTY',
# county_name = json->'properties'->>'NAME',
# census_area = json->'properties'->>'CENSUSAREA';
# """

# # create and populate counties table
# with conn:
#     with conn.cursor() as curs:
#         curs.execute(counties_creation_sql)
#         for county in counties["features"]:
#             curs.execute(counties_insertion_sql, (json.dumps(county),))
#         curs.execute(counties_add_columns_sql)
#         curs.execute(counties_update_sql)




# # joing the counties table and requests_data table to 
# # combine the import columns into one table and leave out 
# # the raw json

# join_sql = """
# CREATE TABLE joined AS
# SELECT 
#     datetime, state_name, counties.county_name, fips, census_area
# FROM requests_data
# LEFT JOIN counties
# ON requests_data.county_fips = counties.fips
# ORDER BY datetime;"""

# # join the two dataframe on their combined state + county level
# # fips codes
# with conn:
#     with conn.cursor() as curs:
#         curs.execute(join_sql)



#### creating the table for the map and expanding the json
####  to multiple columns

# map_data_update_sql = """
# ALTER TABLE map_data
# ADD COLUMN """



## still needed:
# develop operations to join the other two dataframes

# I need to add a fips column to the test dataframe for the join
# Or i could join based on two columns state and county