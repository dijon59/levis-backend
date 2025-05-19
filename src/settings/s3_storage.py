from storages.backends.s3boto3 import S3StaticStorage


class PublicMediaStorage(S3StaticStorage):
    default_acl = 'public-read'
