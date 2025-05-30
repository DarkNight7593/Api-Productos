import boto3
import json

def lambda_handler(event, context):
    print(event)

    # Obtener datos del body
    body = json.loads(event['body'])
    tenant_id = body['tenant_id']
    producto_id = body['producto_id']
    nuevo_nombre = body['nombre']  # Campo a modificar

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

    # Actualizar producto en DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('t_productos')

    try:
        update_response = table.update_item(
            Key={
                'tenant_id': tenant_id,
                'producto_id': producto_id
            },
            UpdateExpression="set nombre = :n",
            ExpressionAttributeValues={
                ':n': nuevo_nombre
            },
            ReturnValues="UPDATED_NEW"
        )

        return {
            'statusCode': 200,
            'message': 'Producto actualizado correctamente',
            'nuevos_valores': update_response.get('Attributes', {})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'error': str(e)
        }
