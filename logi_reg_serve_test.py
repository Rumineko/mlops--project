import requests
import json

# The data you want to make predictions on
data = {
    "inputs": [
        [
            45,
            1,
            3,
            2,
            3,
            0,
            39,
            5,
            1,
            3,
            12691.0,
            777,
            11914.0,
            1.335,
            1144,
            42,
            1.625,
            0.061,
            1,
            0,
            0,
        ]
    ]
}

response = requests.post(
    "http://localhost:1234/invocations",
    data=json.dumps(data),
    headers={"Content-Type": "application/json"},
)

print(response.json())
