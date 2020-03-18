import boto3
import os
import uuid


# ExtraArgs={'ACL':'public-read'}
# ACL
def upload_file(file):
    filePath = file['filePath']
    try:
        file_name = file['fileName']
    except (KeyError, AttributeError):
        file_name = os.path.basename(filePath)
    try:
        sendAs = file['sendAs']
    except (KeyError, AttributeError):
        sendAs = 'attachment'
    try:
        access_control = file['access_control']
    except (KeyError, AttributeError):
        access_control = 'public-read'
    try:
        bucket = file['bucket']
    except (KeyError, AttributeError):
        bucket = 'message-hub'

    object_key = str(uuid.uuid4())[:12] + '--' + file_name

    session = boto3.session.Session()
    client = session.client('s3',
                            region_name='sgp1',
                            endpoint_url='https://sgp1.digitaloceanspaces.com'
                            )

    if sendAs == 'url':
        if access_control not in ['public-read', 'public-read-write']:
            access_control2 = 'public-read'
        else:
            access_control2 = access_control
    else:
        access_control2 = access_control

    client.upload_file(filePath, bucket, object_key, ExtraArgs={
        'ACL': access_control2
    })

    print('--upload_file--object_key--\n', object_key)

    return {'fileName': file_name, 'key': object_key, 'sendAs': sendAs, 'filePath': filePath,
            'url': f'https://sgp1.digitaloceanspaces.com/message-hub/{object_key}'}
