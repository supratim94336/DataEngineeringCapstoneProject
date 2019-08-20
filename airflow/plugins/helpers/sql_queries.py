class SqlQueries:
    """
    all create queries
    """

    immigration = """
                    CREATE TABLE IF NOT EXISTS public.immigration (
                    cicid FLOAT,
                    i94yr FLOAT,
                    i94mon FLOAT,
                    i94cit FLOAT,
                    i94res FLOAT,
                    i94port VARCHAR,
                    arrdate FLOAT,
                    i94mode FLOAT,
                    i94addr varchar,
                    depdate FLOAT,
                    i94bir FLOAT,
                    i94visa FLOAT,
                    count FLOAT,
                    dtadfile VARCHAR,
                    visapost VARCHAR,
                    occup VARCHAR,
                    entdepa VARCHAR,
                    entdepd VARCHAR,
                    entdepu VARCHAR,
                    matflag VARCHAR,
                    biryear FLOAT,
                    dtaddto VARCHAR,
                    gender VARCHAR,
                    insnum VARCHAR,
                    airline VARCHAR,
                    admnum FLOAT,
                    fltno VARCHAR,
                    visatype VARCHAR
                    );
                """

    airports = """
                CREATE TABLE IF NOT EXISTS public.airport_codes (
                ident VARCHAR,
                type VARCHAR,
                name VARCHAR,
                elevation_ft VARCHAR,
                continent VARCHAR,
                iso_country VARCHAR,
                iso_region VARCHAR,
                municipality VARCHAR,
                gps_code VARCHAR,
                iata_code VARCHAR,
                local_code VARCHAR,
                latitude VARCHAR,
                longitude VARCHAR
                );
               """

    i94ports = """
                CREATE TABLE IF NOT EXISTS public.i94ports (
                port_code VARCHAR,
                port_of_entry VARCHAR,
                port_city VARCHAR,
                port_state_or_country VARCHAR
                );
               """

    i94visa = """
                CREATE TABLE IF NOT EXISTS public.i94visa (
                visa_code INT,
                visa_reason VARCHAR
                );
               """

    i94mode = """
                CREATE TABLE IF NOT EXISTS public.i94mode (
                trans_code INT,
                trans_name VARCHAR
                );
              """

    i94addr = """
                CREATE TABLE IF NOT EXISTS public.i94addr (
                state_code VARCHAR,
                state_name VARCHAR
                );
               """

    i94res = """
            CREATE TABLE IF NOT EXISTS public.i94res (
            country_code INT,
            country_name VARCHAR
            );
            """

    us_cities_demographics = """
            CREATE TABLE IF NOT EXISTS public.us_cities_demographics (
                            city VARCHAR,
                            state VARCHAR,
                            median_age FLOAT,
                            male_population FLOAT,
                            female_population FLOAT,
                            total_population FLOAT,
                            number_of_veterans FLOAT,
                            foreign_born FLOAT,
                            average_household_size FLOAT,
                            state_code VARCHAR,
                            race VARCHAR,
                            count INT
                            );
                             """

    drop_tables = """
                    DROP TABLE IF EXISTS public.immigration;
                    DROP TABLE IF EXISTS public.airport_codes;
                    DROP TABLE IF EXISTS public.i94port;
                    DROP TABLE IF EXISTS public.i94visa;
                    DROP TABLE IF EXISTS public.i94mode;
                    DROP TABLE IF EXISTS public.i94addr;
                    DROP TABLE IF EXISTS public.i94res;
                    DROP TABLE IF EXISTS public.us_cities_demographics;
                  """

    create_tables = immigration + airports + i94ports + i94visa + \
                    i94mode + i94addr + i94res + us_cities_demographics
    tables = ["immigration", "airport_codes", "i94ports", "i94visa",
              "i94mode", "i94addr", "i94res", "us_cities_demographics"]

    copy_csv_cmd = """
                    COPY public.{} FROM '{}'
                    CREDENTIALS 'aws_access_key_id={};aws_secret_access_key={}'
                    IGNOREHEADER 1
                    DELIMITER '{}'
                    COMPUPDATE OFF
                    TRUNCATECOLUMNS
                    CSV;
                    """
    count_check = """
                   SELECT CASE WHEN COUNT(*) > 1 THEN 1 ELSE 0 END AS 
                   non_empty FROM {}
                  """

    copy_parquet_cmd = """
                        COPY public.{} FROM '{}'
                        IAM_ROLE '{}'
                        FORMAT AS PARQUET;
                       """