#!/usr/bin/env bash

JQ=${JQ:-"jq -C"}

function hit() {
    echo $1:
    curl -s $1 | ${JQ}
    echo
}

echo "== IDP METADATA =="
hit http://localhost/idp/realms/pid-issuer-realm/.well-known/openid-configuration

echo "== GET ACCESS TOKEN FROM IDP =="
TMP=$(mktemp)
curl -k -s -XPOST https://localhost/idp/realms/pid-issuer-realm/protocol/openid-connect/token \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "grant_type=password" \
     -d "username=tneal" \
     -d "password=password" \
     -d "scope=openid eu.europa.ec.eudiw.pid_mso_mdoc eu.europa.ec.eudiw.pid_vc_sd_jwt org.iso.18013.5.1.mDL" \
     -d "client_id=wallet-dev" --output ${TMP}
ACCESS_TOKEN=$(cat ${TMP} | jq -r .access_token)
echo ACCESS_TOKEN: ${ACCESS_TOKEN}
echo DECODED:
echo ${ACCESS_TOKEN} | cut -d '.' -f 2 | base64 --decode | jq 
echo

echo "== GET USERINFO (IDP) =="
curl -k -s https://localhost/idp/realms/pid-issuer-realm/protocol/openid-connect/userinfo \
     -H "Content-type: application/json" -H "Accept: application/json" -H "Authorization: Bearer ${ACCESS_TOKEN}" | ${JQ}
echo

echo "== INTROSPECT TOKEN (IDP) =="
curl -k -s -XPOST https://localhost/idp/realms/pid-issuer-realm/protocol/openid-connect/token/introspect -d "token=${ACCESS_TOKEN}" \
     -H "Content-Type: application/x-www-form-urlencoded" -u "pid-issuer-srv:zIKAV9DIIIaJCzHCVBPlySgU8KgY68U2" | ${JQ}
echo

ISSUER="http://localhost:8080"
# ISSUER="http://localhost/pid-issuer"

echo "== CREDENTIAL ISSUER METADATA =="
hit ${ISSUER}/.well-known/openid-credential-issuer
echo

echo "== GET USERINFO FROM ISSUER =="
curl -s ${ISSUER}/wallet/credentialEndpoint \
     -H "Content-type: application/json" -H "Accept: application/json" -H "Authorization: Bearer ${ACCESS_TOKEN}" | ${JQ}
echo

echo "== PID REQUEST (SD-JWT-VC) [test invocation, for c_nonce] =="
PID_SD_JWT_VC=$(mktemp)
curl -s -XPOST ${ISSUER}/wallet/credentialEndpoint \
    -H "Content-type: application/json" -H "Accept: application/json" -H "Authorization: Bearer ${ACCESS_TOKEN}" \
    --data '{
  "format": "vc+sd-jwt",
  "vct": "eu.europa.ec.eudiw.pid.1",
  "proof": {
    "proof_type": "jwt",
    "jwt": ""
  }
}' --output ${PID_SD_JWT_VC}
cat ${PID_SD_JWT_VC} | ${JQ}
C_NONCE=$(cat ${PID_SD_JWT_VC} | jq -r .c_nonce)
echo "C_NONCE=${C_NONCE}"
echo

echo "== PID REQUEST (SD-JWT-VC) [proper invocation] =="
PROOF_JWT=$(./create_proof_jwt.py ${C_NONCE})
PID_SD_JWT_VC=$(mktemp)
curl -s -XPOST ${ISSUER}/wallet/credentialEndpoint \
    -H "Content-type: application/json" -H "Accept: application/json" -H "Authorization: Bearer ${ACCESS_TOKEN}" \
    --data '{
  "format": "vc+sd-jwt",
  "vct": "eu.europa.ec.eudiw.pid.1",
  "proof": {
    "proof_type": "jwt",
    "jwt": "'${PROOF_JWT}'"
  }
}' --output ${PID_SD_JWT_VC}
cat ${PID_SD_JWT_VC} | ${JQ}
C_NONCE=$(cat ${PID_SD_JWT_VC} | jq -r .c_nonce)
echo "C_NONCE=${C_NONCE}"

if [ "${ISSUER_PID_SD_JWT_VC_DEFERRED}" == "true" ]; then
  TRANSACTION_ID=$(cat ${PID_SD_JWT_VC} | jq -r .transaction_id)
  echo "Deferred, TRANSACTION_ID=${TRANSACTION_ID}"
else
  CREDENTIAL=$(cat ${PID_SD_JWT_VC} | jq -r .credential)
  echo Decoded credential:
  echo ${CREDENTIAL} | cut -d '.' -f 2 | base64 --decode | ${JQ}
fi
echo

if [ "${ISSUER_PID_SD_JWT_VC_DEFERRED}" == "true" ]; then
  echo "== DEFERRED REQUEST =="
  curl -s -XPOST ${ISSUER}/wallet/deferredEndpoint \
      -H "Content-type: application/json" -H "Accept: application/json" -H "Authorization: Bearer ${ACCESS_TOKEN}" \
      --data '{"transaction_id" : "'${TRANSACTION_ID}'"}' --output ${PID_SD_JWT_VC}
  cat ${PID_SD_JWT_VC} | ${JQ}
  CREDENTIAL=$(cat ${PID_SD_JWT_VC} | jq -r .credential)
  echo Decoded credential:
  echo ${CREDENTIAL} | cut -d '.' -f 2 | base64 --decode | ${JQ}
fi
echo

echo "== PID REQUEST (mso-mdoc) =="
PROOF_JWT=$(./create_proof_jwt.py ${C_NONCE})
MSD_MDOC_OUT=$(mktemp)
curl -s -XPOST ${ISSUER}/wallet/credentialEndpoint \
    -H "Content-type: application/json" -H "Accept: application/json" -H "Authorization: Bearer ${ACCESS_TOKEN}" \
    --data '{
  "format": "mso_mdoc",
  "doctype": "eu.europa.ec.eudiw.pid.1",
  "proof": {
    "proof_type": "jwt",
    "jwt": "'${PROOF_JWT}'"
  }
}' --output ${MSD_MDOC_OUT}
cat ${MSD_MDOC_OUT} | ${JQ}
C_NONCE=$(cat ${MSD_MDOC_OUT} | jq -r .c_nonce)
echo "C_NONCE=${C_NONCE}"
echo

echo "== mDL REQUEST (mso_mdoc/mdl) =="
PROOF_JWT=$(./create_proof_jwt.py ${C_NONCE})
curl -s -XPOST ${ISSUER}/wallet/credentialEndpoint \
    -H "Content-type: application/json" -H "Accept: application/json" -H "Authorization: Bearer ${ACCESS_TOKEN}" \
    --data '{
  "format": "mso_mdoc",
  "doctype": "org.iso.18013.5.1.mDL",
  "claims": {
      "org.iso.18013.5.1": {
          "given_name": {},
          "family_name": {},
          "birth_date": {}
      }
  },
  "proof": {
    "proof_type": "jwt",
    "jwt": "'${PROOF_JWT}'"
  }
}' | ${JQ}
echo
