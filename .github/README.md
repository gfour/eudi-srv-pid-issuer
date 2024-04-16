This is a testing fork of the eudi-srv-pid-issuer, to demonstrate issuance formats.

## Setup

1. Install Docker (+ Docker Compose), OpenJDK, and jq:
```
sudo apt install docker-ce docker-compose-plugin openjdk-17-jdk jq
```
2. Set up Python for the test JWT proof generator:
```
python3 -m venv .venv
source .venv/bin/activate
pip install pyjwt==2.0.1 cryptography==3.4.8
```

## Run script

Open 3 terminals:

* Terminal 1: run the Docker containers that will start the Keycloak authentication server:
```
cd docker-compose
docker compose up
```

* Terminal 2: run the development server:
```
source shell.env
./gradlew bootRun
```

* Terminal 3: when the servers above have started up, run the test script:
```
source .venv/bin/activate
./test.sh
```
