GRAPHENE = {
    'SCHEMA': 'reposter.schema.schema',
    'MIDDLEWARE': [
        'graphene_django.debug.DjangoDebugMiddleware',
        'graphql_jwt.middleware.JSONWebTokenMiddleware',
    ],
}
