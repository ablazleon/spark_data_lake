import configparser
from datetime import datetime
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.functions import year, month, dayofmonth, hour, weekofyear, date_format


config = configparser.ConfigParser()
config.read('dl.cfg')
print(config)

os.environ['AWS_ACCESS_KEY_ID']=config['AWS']['AWS_ACCESS_KEY_ID']
os.environ['AWS_SECRET_ACCESS_KEY']=config['AWS']['AWS_SECRET_ACCESS_KEY']


def create_spark_session():
    """
    Create a spark session
    """
    spark = SparkSession \
        .builder \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:2.7.0") \
        .getOrCreate()
    return spark


def process_song_data(spark, input_data, output_data):
    """
    Songs logs are loaded and write in parquet form
    
    PARAMETERS
        spark: session
        input_data: location of the data
        output_data: location of the results
    
    """
    # get filepath to song data file
    song_data = input_data + 'song_data/*/*/*/*.json'
    
    # read song data file
    df = spark.read.json(song_data)

    # extract columns to create songs table
    songs_t = df.select("song_id","title","artist_id","year","duration").drop_duplicates()
    
    # write songs table to parquet files partitioned by year and artist
    songs_t.write.mode('overwrite').partitionBy("year", "artist_id").parquet(output_data+'songs_t/')
        
    # extract columns to create artists table
    artists_t = df.select("artist_id","artist_name","artist_location","artist_latitude","artist_longitude").drop_duplicates()

    # write artists table to parquet files
    artists_t.write.mode('overwrite').parquet(output_data+'artists_t/')


def process_log_data(spark, input_data, output_data):
    """
    Read log data and store it
    
    PARAMETERS:
        spark: session
        input_data: location of the data
        output_data: location of the results
    """
    # get filepath to log data file
    log_data = os.path.join(input_data, "log-data/")

    # read log data file
    df = spark.read.json(log_data, mode='PERMISSIVE', columnNameOfCorruptRecord='corrupt_record').drop_duplicates()
    
    # filter by actions for song plays
    df = df.filter(df.page == "NextSong")

    # extract columns for users table    
    users_t = df.select("userId","firstName","lastName","gender","level").drop_duplicates()
    
    # write users table to parquet files
    users_t.write.parquet(os.path.join(output_data, "users/") , mode="overwrite")

    # create timestamp column from original timestamp column
    get_ts = udf(lambda x : datetime.utcfromtimestamp(int(x)/1000), TimestampType())
    df = df.withColumn("start_time", get_ts("ts"))
    
    # extract columns to create time table
    time_t = df.withColumn("hour",hour("start_time"))\
                    .withColumn("day",dayofmonth("start_time"))\
                    .withColumn("week",weekofyear("start_time"))\
                    .withColumn("month",month("start_time"))\
                    .withColumn("year",year("start_time"))\
                    .withColumn("weekday",dayofweek("start_time"))\
                    .select("ts","start_time","hour", "day", "week", "month", "year", "weekday").drop_duplicates()
    
    # write time table to parquet files partitioned by year and month
    time_t.write.parquet(os.path.join(output_data, "time_t/"), mode='overwrite', partitionBy=["year","month"])

    # read in song data to use for songplays table
    song_df = spark.read\
                .format("parquet")\
                .option("basePath", os.path.join(output_data, "songs/"))\
                .load(os.path.join(output_data, "songs/*/*/"))

    # extract columns from joined song and log datasets to create songplays table 
    songplays_t = df.join(song_df, df.song == song_df.title, how='inner').select(monotonically_increasing_id().alias("songplay_id"),col("start_time"),col("userId").alias("user_id"),"level","song_id","artist_id", col("sessionId").alias("session_id"), "location", col("userAgent").alias("user_agent"))

    songplays_t = songplays_t.join(time_t, songplays_t.start_time == time_t.start_time, how="inner").select("songplay_id", songplays_t.start_time, "user_id", "level", "song_id", "artist_id", "session_id", "location", "user_agent", "year", "month")
    
    # write songplays table to parquet files partitioned by year and month
    songplays_t.drop_duplicates().write.parquet(os.path.join(output_data, "songplays/"), mode="overwrite", partitionBy=["year","month"])


def main():
    spark = create_spark_session()
    input_data = "s3://udacity-dend/"
    output_data = "s3a://udacity-dend/dloutput/"
    
    process_song_data(spark, input_data, output_data)    
    process_log_data(spark, input_data, output_data)

if __name__ == "__main__":
    main()
