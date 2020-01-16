import json
from flask import Response


def json_response(data, status=200, headers={}):
    serialized = json.dumps(data, indent=2, default=str)
    headers["Content-Type"] = "application/json"

    for key in headers.keys():
        value = headers.pop(key)
        headers[str(key)] = str(value)

    return Response(serialized, status=status, headers=headers)
