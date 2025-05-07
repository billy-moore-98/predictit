-- create database and schema for predictit data
USE ROLE SYSADMIN;

CREATE DATABASE IF NOT EXISTS predictit;

USE DATABASE predictit;

CREATE SCHEMA IF NOT EXISTS markets;

-- setup storage integration to s3 bucket
USE ROLE ACCOUNTADMIN;

CREATE STORAGE INTEGRATION predictit_s3
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = 'S3'
  ENABLED = TRUE
  STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::<UID>:role/snowflake_access_role'
  STORAGE_ALLOWED_LOCATIONS = ('s3://<bucket>/<folder>/', 's3://<bucket>/<folder>/');

GRANT USAGE ON INTEGRATION predictit_s3 TO ROLE SYSADMIN;

-- create external stage using the storage integration and a json file format
USE ROLE SYSADMIN;

USE SCHEMA predictit.markets;

CREATE OR REPLACE FILE FORMAT predictit_json
    TYPE = 'JSON'
    COMPRESSION = NONE;

CREATE OR REPLACE STAGE predictit_s3_stage
    STORAGE_INTEGRATION = predictit_s3
    URL = 's3://<bucket>/<folder>/'
    FILE_FORMAT = predictit_json;
