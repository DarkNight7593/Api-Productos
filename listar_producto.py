import boto3
import json


def lambda_handler(event, context):
    print(event)

    # Inicio - Proteger el Lambda
    token = event['headers']['Authorization']
    lambda_client = boto3.client('lambda')
    payload_string = json.dumps({"token": token})

    invoke_response = lambda_client.invoke(
        FunctionName="ValidarTokenAcceso",
        InvocationType='RequestResponse',
        Payload=payload_string
    )

    response = json.loads(invoke_response['Payload'].read())
    print(response)

    if response['statusCode'] == 403:
        return {
            'statusCode': 403,
            'status': 'Forbidden - Acceso No Autorizado'
        }
    # Fin - Proteger el Lambda

    # Listar productos desde DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('t_productos')

    scan_response = table.scan()  # Escanea todos los ítems de la tabla

    productos = scan_response.get('Items', [])

    return {
        'statusCode': 200,
        'productos': productos
    }
