from __future__ import annotations

from pyspark.sql import SparkSession


def get_spark_session(app_name: str = "hospital-analytics") -> SparkSession:
    """
    Create and return a local Spark session for development.
    """
    spark = (
        SparkSession.builder
        .appName(app_name)
        .master("local[*]")
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )

    return spark

if __name__ == "__main__":
    spark = get_spark_session()
    print("Spark session created successfully.")
    print(f"Spark version: {spark.version}")
    spark.stop()