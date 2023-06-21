# Databricks notebook source
import pyspark.sql.functions as F

# COMMAND ----------

df = (
  spark.table('dse_products.beacon_v1_api_aggregated')
  .filter(F.col('entity_type') == 'Merchant-Level')
  .filter(F.col('metric_type') == 'level')
  .filter(F.col('period') == 'Calendar_Quarter')
  .filter(F.col('metric_name') == 'DollarIndex')
  .filter(F.col('sector') == 'Consumer Discretionary')

  .withColumn('instruction', F.concat(
    F.lit('What was the dollar index of '),
    F.col('company'),
    F.lit(' for the calendar quarter ending '),
    F.col('end_date'),
    F.lit('?')
  ))
  .withColumn('context', F.concat(
    F.col('company'),
    F.lit(' belongs to the '),
    F.col('sector'),
    F.lit(' sector, the '),
    F.col('industry'),
    F.lit(' industry, and the '),
    F.col('subindustry'),
    F.lit(' subindustry.'),
  ))          
  .withColumn('response', F.concat(
    F.lit('The dollar index of '),
    F.col('company'),
    F.lit(' for the calendar quarter ending '),
    F.col('end_date'),
    F.lit(' is '),
    F.col('metric'),
    F.lit('.'),
  ))
  .withColumn('category', F.lit('information_extraction'))

  .select('instruction', 'context', 'response', 'category')
)

# COMMAND ----------

df.count()

# COMMAND ----------

json_dataset = df.toJSON().collect()

# COMMAND ----------

import json

with open("/dbfs/FileStore/data_for_test/train.json", "w") as f:
  json.dump(json_dataset, f)

