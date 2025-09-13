import os
import io
import json
import requests
import pandas as pd
import psycopg2
import boto3
from sqlalchemy import create_engine

# RDS接続情報（Secrets Managerから取得）
RDS_HOST = os.environ.get('RDS_HOST')
RDS_PORT = int(os.environ.get('RDS_PORT', 5432))
RDS_DB = os.environ.get('RDS_DB')
RDS_TABLE = os.environ.get('RDS_TABLE')
SECRET_ARN = os.environ.get('RDS_SECRET_ARN')

def get_db_credentials(secret_arn):
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager')
    secret_value = client.get_secret_value(SecretId=secret_arn)
    secret_dict = json.loads(secret_value['SecretString'])
    return secret_dict['username'], secret_dict['password']

def main():
    user, password = get_db_credentials(SECRET_ARN)

    url = "https://www.geospatial.jp/ckan/dataset/9f9f90bb-c3be-4cd5-93ea-c8df94abc1cc/resource/bf008fa9-9bb1-4471-bbf4-1b2050b7346d/download/01_ippanryokyakuteikikourojigyoukyokashinseisyo.csv"
    response = requests.get(url)
    df = pd.read_csv(io.BytesIO(response.content))

    df.dropna(subset=['ship_kind'], inplace=True)

    float_columns = [
        'Maximum_Speed',
        'Cruising_Speed',
        'Overall_Length',
        'Width',
        'Maximum_Height',
        'Maximum_(Full_Load)_Draft',
        'ship_weight',
    ]

    integer_columns = [
        'capacity_passengers',
        'capacity_crew',
        'capacity_other_boarders'
    ]

    all_numeric_columns = float_columns + integer_columns
    for col in all_numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    for col in integer_columns:
        df[col] = df[col].astype('Int64')

    df['SHIPYARD_ID'] = df['SHIPYARD_ID'].astype(str)

    df = df.rename(columns={
        'Maximum_(Full_Load)_Draft': 'Maximum_Full_Load_Draft',
        'Maneuverability_(Turning_Radius)': 'Maneuverability_Turning_Radius',
        'Maneuverability_(Drift_Distance)': 'Maneuverability_Drift_Distance',
        'Barrier-Free_Support_Status': 'Barrier_Free_Support_Status',
    })

    schema_columns = [
        'ship_ID',
        'ship_kind',
        'ship_quality',
        'navigation_area',
        'ship_owner_ID',
        'purpose',
        'ship_weight',
        'capacity_passengers',
        'capacity_crew',
        'capacity_other_boarders',
        'main_engine_type',
        'Continuous_Maximum_Output',
        'Maximum_Speed',
        'Cruising_Speed',
        'Overall_Length',
        'Width',
        'Maximum_Height',
        'Maximum_Full_Load_Draft',
        'SHIPYARD_ID',
        'Radio_Equipment',
        'Maneuverability_Turning_Radius',
        'Maneuverability_Drift_Distance',
        'Special_Maneuvering_Equipment',
        'Barrier_Free_Support_Status'
    ]

    df_final = df[schema_columns].copy()
    engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{RDS_HOST}:{RDS_PORT}/{RDS_DB}")
    df_final.to_sql(RDS_TABLE, con=engine, if_exists='append', index=False)

def lambda_handler(event, context):
  main()
  return {'status': 'success'}
