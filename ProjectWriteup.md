## Scoping the Project
---
The purpose is to produce interesting stats from the US immigration 
data, airports around the world, and different dimensions such as visa 
type, transport mode, nationality etc.

### Steps Taken:
The steps taken are in the following order:
    - Gather the data:
        This took a while as different kinds of formats were chosen, I
        needed to fix my mindset on which data I will actually use in 
        future for my analysis and queries. I fixated on .sas7bdat 
        formatted immigration data which fulfills the minimum number of 
        rows requirements, the cleaned airport data for dimensions and
        SAS descriptor file for fulfilling the different kind of formats
        to be chosen for the project
    - Study the data:
        This took a while as I needed to understand what kind of 
        pre-processing I would use to clean the individual datasets 
        mentioned above. Dropping rows on a condition, filtering rows 
        according to other dimensions and facts etc.
    - Choice of infrastructure:
        After studying the data I decided upon certain tools and 
        technologies, to the point where I am comfortable; I made use of
        maximum number of skills that I think I learnt through out the 
        process.
    - Implementation and Testing: 
        Once my pipeline started running, I did all kinds of quality 
        checks to ensure that data is processed correctly and provided a
        Jupyter notebook to test the project.
       
### Purpose of Final Data Model:
Gather interesting insights like demographic population based on certain
 dimensions based upon some filter conditions.
 e.g.   
 - Compare immigration of different nationalities
 - Compare immigration based on visa type
 - Different kinds of airport statistics
 - Aggregate flow of immigrants through different ports

So I am using the airport codes, US immigration data of '94 and 
dimensions such as visa type, mode of transport, nationality codes, US 
state code information


## Addressing other scenarios
---

### Data Increased by 100%:
 - I am using columnar format of redshift so querying will not be slower
 - Incremental update is provided so that every time full amount is not 
 inserted
 - Spark is used where heavy data is read and parsed, so distributed 
 processing is also involved
 - Spark memory and configuration is editable to handle more pressure
 - S3 storage is used which is scalable and easily accessible with other
 AWS infrastructure
 

### The pipelines would be run on a daily basis by 7 am every day:
- The pipeline is scheduled as per requirements

### The database needed to be accessed by 100+ people:
- People are granted usage on schema, so not everyone but people who 
have access to the data can use it as necessary. Best way is to use 
groups. Below we use the 'webDevuser2pass' to manage 100 different users

Follow the code:-
```bash
create schema webapp;
create group webdevusers;
grant all on schema webapp to group webdevusers;
create group webappusers;
create user webdevuser1 password 'webDevuser2pass' in group webappusers;
grant usage on schema webapp to group webappusers;
```


## Defending Decisions
---

### The choice of tools, technologies:
- Airflow to view, monitor and log flow of information
- S3 Storage to store data on a large scale 
- Redshift to make advantage of columnar format and faster querying 
strategies
- Spark for distributed processing of heavy data
- Pandas for cleaning data frames


