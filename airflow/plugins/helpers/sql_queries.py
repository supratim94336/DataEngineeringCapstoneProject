class SqlQueries:
    """
    all create queries
    """

    immigration = """
        CREATE TABLE IF NOT EXISTS public.immigration (
        cicid numeric(18,0),
        i94yr numeric(18,0),
        i94mon numeric(18,0),
        i94cit numeric(18,0),
        i94res numeric(18,0),
        i94port varchar(256),
        arrdate numeric(18,0),
        i94mode numeric(18,0),
        i94addr varchar,
        depdate numeric(18,0),
        i94bir numeric(18,0),
        i94visa numeric(18,0),
        count numeric(18,0),
        dtadfile varchar(256),
        visapost varchar(256),
        occup varchar(256),
        entdepa varchar(256),
        entdepd varchar(256),
        entdepu varchar(256),
        matflag varchar(256),
        biryear numeric(18,0),
        dtaddto varchar(256),
        gender varchar(256),
        insnum varchar(256),
        airline varchar(256),
        admnum numeric(18,0),
        fltno varchar(256),
        visatype varchar(256)
        );
    """

    airports = """
    CREATE TABLE IF NOT EXISTS public.airport_codes (
    ident varchar(256),
    type varchar(256),
    name varchar(256),
    elevation_ft numeric(18,0),
    continent varchar(256),
    iso_country varchar(256),
    iso_region varchar(256),
    municipality varchar(256),
    gps_code varchar(256),
    iata_code varchar(256),
    local_code varchar(256),
    coordinates varchar(256),
    lat numeric(18,0),
    long numeric(18,0)
    );
    """

    i94ports = """
    CREATE TABLE IF NOT EXISTS public.i94ports (
    port_code varchar(256),
    port_of_entry varchar(256),
    port_city varchar(256),
    port_state_or_country varchar(256)
    );
    """

    i94visa = """
    CREATE TABLE IF NOT EXISTS public.i94visa (
    visa_code int4,
    visa_reason varchar(256)
    );
    """

    i94mode = """
    CREATE TABLE IF NOT EXISTS public.i94mode (
    trans_code int4,
    trans_name varchar(256)
    );
    """

    i94addr = """
    CREATE TABLE IF NOT EXISTS public.i94addr (
    state_code varchar(256),
    state_name varchar(256)
    );
    """

    i94res = """
    CREATE TABLE IF NOT EXISTS public.i94res (
    country_code int4,
    country_name varchar(256)
    );
    """

    us_cities_demographics = """
    CREATE TABLE IF NOT EXISTS public.us_cities_demographics (
    city varchar(256),
    state varchar(256),
    median_age numeric(18,0),
    male_population numeric(18,0),
    female_population numeric(18,0),
    total_population numeric(18,0),
    number_of_veterans numeric(18,0),
    foreign_born numeric(18,0),
    average_household_size numeric(18,0),
    state_code varchar(256),
    race varchar(256),
    count int4
    );
    """

    drop_table = """
    DROP TABLE IF EXISTS public.{};
    """

    create_tables = immigration + airports + i94ports + i94visa + i94mode + i94addr + i94res + us_cities_demographics
    tables = ["immigration", "airport_codes", "i94port", "i94visa",
              "i94mode", "i94addr", "i94res", "us-cities-demographics"]
    drop_all = []
    for table in tables:
        drop_all.append(drop_table.format(table))
    drop_tables = drop_all

    copy_csv_cmd = """
                        COPY {}.{} FROM '{}'
                        CREDENTIALS 'aws_access_key_id={};aws_secret_access_key={}'
                        IGNOREHEADER 1
                        COMPUPDATE OFF
                        TRUNCATECOLUMNS
                        CSV;
                        """

    copy_parquet_cmd = """
                        COPY {}.{} FROM '{}'
                        CREDENTIALS 'aws_access_key_id={};aws_secret_access_key={}'
                        FORMAT AS PARQUET;
                       """