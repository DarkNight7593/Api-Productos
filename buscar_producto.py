import boto3
import json

def lambda_handler(event, context):
    print(event)

    # Obtener datos del body
    body = event['body']
    tenant_id = body['tenant_id']
    producto_id = body['producto_id']

    # Inicio - Proteger el Lambda
    token = event['headers']['Authorization']
    lambda_client = boto3.client('lambda')
    payload_string = json.dumps({ "token": token })

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

    # Consultar producto por tenant_id y producto_id
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('t_productos')

    try:
        db_response = table.get_item(
            Key={
                'tenant_id': tenant_id,
                'producto_id': producto_id
            }
        )
        item = db_response.get('Item')
        if item:
            return {
                'statusCode': 200,
                'producto': item
            }
        else:
            return {
                'statusCode': 404,
                'message': 'Producto no encontrado'
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'error': str(e)
        }
