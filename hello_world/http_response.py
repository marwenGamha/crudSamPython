import json

class HttpResponse:
    @classmethod
    def _generic_response(cls, message, status):
        return {
            'body': json.dumps(message),
            'statusCode': status,
            'headers': {
                "Content-Type": "application/json",
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Origin': '*'
                }
        }
    @classmethod
    def toJSON(cls, message):
        return json.dumps(message, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

    @classmethod
    def success(cls, message):
        return cls._generic_response(message=message, status=200)

    @classmethod
    def not_found(cls, message):
        return cls._generic_response(message=message, status=404)

    @classmethod
    def bad_request(cls, message):
        return cls._generic_response(message=message, status=400)

    @classmethod
    def unauthorized(cls, message):
        return cls._generic_response(message=message, status=401)

    @classmethod
    def conflict(cls, message):
        return cls._generic_response(message=message, status=409)

    @classmethod
    def internal_error(cls, message):
        return cls._generic_response(message=message, status=500)