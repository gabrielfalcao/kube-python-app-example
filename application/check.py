import os
import requests

host = str(os.getenv("FLASK_HOST", "0.0.0.0"))
port = int(os.getenv("FLASK_PORT", 5000))
base_url = f"http://{host}:{port}"


def main():
    response = requests.get("{base_url}/api/example")
    if response.status_code != 200:
        print(response.headers)
        print(response.status_code)
        print(response.data)
        raise SystemExit(1)

    print(response.json())


if __name__ == "__main__":
    main()
