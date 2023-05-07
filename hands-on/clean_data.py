from pyspark.sql import SparkSession
from pyspark.sql.functions import split, when

spark = SparkSession.builder.appName("SensorStream").getOrCreate()

sensor_df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "url_kafka") \
    .option("subscribe", "singgih-data-raw") \
    .option("startingOffsets", "earliest") \
    .option("kafka.security.protocol","SASL_SSL") \
    .option("kafka.sasl.mechanism", "PLAIN") \
    .option("kafka.sasl.username","username_kafka") \
    .option("kafka.sasl.password", "password_kafka") \
    .option("kafka.sasl.jaas.config", """org.apache.kafka.common.security.plain.PlainLoginModule required username="username_kafka" password="password_kafka";""") \
    .load()

raw_df = sensor_df.selectExpr("SPLIT(CAST(value AS STRING), ',' ) arr")

select_df = raw_df.withColumn("beach_name", raw_df['arr'][0]) \
        .withColumn("measurement_timestamp", raw_df['arr'][1]) \
        .withColumn("water_temperature", raw_df['arr'][2] ) \
        .withColumn("turbidity", raw_df['arr'][3]) \
        .withColumn("transducer_depth", raw_df['arr'][4]) \
        .withColumn("wave_height", raw_df['arr'][5]) \
        .withColumn("wave_period", raw_df['arr'][6]) \
        .withColumn("battery_life", raw_df['arr'][7]) \
        .withColumn("measurement_timestamp_label", raw_df['arr'][8]) \
        .withColumn("measurement_id", raw_df['arr'][9]) \
        .select("beach_name","measurement_timestamp","water_temperature","turbidity","transducer_depth","wave_height","wave_period","battery_life","measurement_timestamp_label","measurement_id")

#set transformation here
clean_df = select_df.withColumn("water_temperature", select_df['water_temperature'] )

query = clean_df.selectExpr("CAST(measurement_id AS STRING) AS key", "to_json(struct(*)) AS value") \
    .writeStream \
    .format("kafka") \
    .outputMode("append") \
    .option("checkpointLocation", "checkpoint") \
    .option("kafka.bootstrap.servers", "url_kafka") \
    .option("topic", "singgih-data-clean") \
    .option("kafka.security.protocol","SASL_SSL") \
    .option("kafka.sasl.mechanism", "PLAIN") \
    .option("kafka.sasl.username","username_kafka") \
    .option("kafka.sasl.password", "password_kafka") \
    .option("kafka.sasl.jaas.config", """org.apache.kafka.common.security.plain.PlainLoginModule required username="username_kafka" password="password_kafka";""") \
    .start()

query.awaitTermination()