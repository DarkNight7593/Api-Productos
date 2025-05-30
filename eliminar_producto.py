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

    # Eliminar producto en DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('t_productos')

    try:
        delete_response = table.delete_item(
            Key={
                'tenant_id': tenant_id,
                'producto_id': producto_id
            },
            ReturnValues='ALL_OLD'
        )

        if 'Attributes' in delete_response:
            return {
                'statusCode': 200,
                'message': 'Producto eliminado correctamente',
                'producto_eliminado': delete_response['Attributes']
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
