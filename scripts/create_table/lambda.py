import os
import psycopg2
import boto3
import json


# Aurora PostgreSQL接続情報
RDS_HOST = os.environ.get('RDS_HOST')
print(f"debug: RDS_PORT: {os.environ.get('RDS_PORT')}")
RDS_PORT = 5432
RDS_DB = os.environ.get('RDS_DB')
print(f"debug: RDS_DB: {RDS_DB}")
RDS_DB = "mydatabase"
SECRET_ARN = os.environ.get('RDS_SECRET_ARN')  # Secrets ManagerのARN

def get_db_credentials(secret_arn):
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager')
    secret_value = client.get_secret_value(SecretId=secret_arn)
    secret_dict = json.loads(secret_value['SecretString'])
    return secret_dict['username'], secret_dict['password']

CREATE_TABLE_SQL = '''
CREATE TABLE ships (
  ship_ID VARCHAR(255) PRIMARY KEY,
  ship_kind VARCHAR(255),
  ship_quality VARCHAR(255),
  navigation_area VARCHAR(255),
  ship_owner_ID VARCHAR(255),
  purpose VARCHAR(255),
  ship_weight DOUBLE PRECISION,
  capacity_passengers INTEGER,
  capacity_crew INTEGER,
  capacity_other_boarders INTEGER,
  main_engine_type VARCHAR(255),
  Continuous_Maximum_Output VARCHAR(255),
  Maximum_Speed DOUBLE PRECISION,
  Cruising_Speed DOUBLE PRECISION,
  Overall_Length DOUBLE PRECISION,
  Width DOUBLE PRECISION,
  Maximum_Height DOUBLE PRECISION,
  Maximum_Full_Load_Draft DOUBLE PRECISION,
  SHIPYARD_ID VARCHAR(255),
  Radio_Equipment VARCHAR(255),
  Maneuverability_Turning_Radius TEXT,
  Maneuverability_Drift_Distance TEXT,
  Special_Maneuvering_Equipment TEXT,
  Barrier_Free_Support_Status VARCHAR(255)
);
'''


def main():
    user, password = get_db_credentials(SECRET_ARN)
    conn = psycopg2.connect(
        host=RDS_HOST,
        port=RDS_PORT,
        user=user,
        password=password,
        dbname=RDS_DB
    )
    with conn:
        with conn.cursor() as cur:
            cur.execute(CREATE_TABLE_SQL)
            print('CREATE TABLE executed.')
    conn.close()

def lambda_handler(event, context):
    main()
    return {'status': 'success'}
