# spark_data_lake


***Credits***
Udacity Data Engineer Nanodegree Program

This python script allows extracting data, transforming it and loading it. The result can be seen in this image:

![S3_output](https://github.com/ablazleon/spark_data_lake/blob/master/S3_output.png)


## Rubric
## 1. Discuss the purpose of this database in the context of the startup, Sparkify, and their analytical goals.
## 2. State and justify your database schema design and ETL pipeline.

-----------


## Rubric

ETL

- [x] ***The etl.py script runs without errors***: The script, etl.py, runs in the terminal without errors. The script reads song_data and load_data from S3, transforms them to create five different tables, and writes them to partitioned parquet files in table directories on S3.

- [x] ***Analytics tables are correctly organized on S3***: Each of the five tables are written to parquet files in a separate analytics directory on S3. Each table has its own folder within the directory. Songs table files are partitioned by year and then artist. Time table files are partitioned by year and month. Songplays table files are partitioned by year and month.

- [x] ***The correct data is included in all tables***: Each table includes the right columns and data types. Duplicates are addressed where appropriate.

Code Quality

- [x] ***The project shows proper use of documentation***: The README file includes a summary of the project, how to run the Python scripts, and an explanation of the files in the repository. Comments are used effectively and each function has a docstring.

- [x] ***The project code is clean and modular***: Scripts have an intuitive, easy-to-follow structure with code separated into logical functions. Naming for variables and functions follows the PEP8 style guidelines.

## 1. Discuss the purpose of this database in the context of the startup, Sparkify, and their analytical goals.

Service logs are proposed to be stored in a db, so to access them easily: it is propose to store them in a an unstructured way (what is called a data lake)

 To do so:
 
 0. It is created an spark cluster on EMR, and from it run the etl.py. This file do this:
 1. First the songs and log data are extracted
 2. Then, it is used spark to transform the data in an schema 
 3. After that, the files are stored in parket files.
 
 After ssh to the cluster is done the following command:
 
 ```
 spark submit etl.py --master yarn
 ```

## 2. State and justify your database schema design and ETL pipeline.

In this uml class diagram it is approached the start schema proposed.

<img src="http://yuml.me/diagram/plain/class/[songplays|songplay_id;start_time;user_id;level;song_id;artist_id;session_id;location;user_agent]-[Users {bg:orange}| user_id; first_name;last_name;gender;level], [songplays]-[songs {bg:orange}|song_id;title;artist_id;year;duration] , [songplays]-[artists {bg:orange}|artist_id;name;location;latitude;longitude], [songplays]-[time {bg:orange}|start_time;hour;day;week;month;year;weekday]">
