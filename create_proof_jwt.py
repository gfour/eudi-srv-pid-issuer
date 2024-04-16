#!/usr/bin/env python
import json
import jwt
import sys
import time
from jwt.algorithms import get_default_algorithms

# private_jwk = {
#     "p": "6HOsP9RfFhLd0jJhfsprTeae7dAnZtqQDlb75c6Gfc0h8EktnUzP7frX1v-_wIV13968ogKhMbeBph_C1ey6_Yyab6o-tXiKsFCKebe23K9HnzWnMCwMIvL9vbzWa3YhE_f9QH0UxQuMByh151KRB7YhA4UG_J2TmQ6SpJkWoN8",
#     "kty": "RSA",
#     "q": "yRK4qdF65vJnut_oXw5HLYIENotWy8V2jpCsjFu0RYu4FoqaRJ4HL2tGkAxZD1Gz5Rp-TWtGKMzWgJPTtwqaMwqku8OVDd9lERGqPMBy3dAU9cXKCmEscbtYEQeTpUUKydkbjLDKB09YrFhIcHXmZOc7mc7Z9AEmG-d3VMgGWzs",
#     "d": "Fd_oDtAAp09P6Ong0U2D40ASAXIlven9mER5uhsp4tLYLV1mu7FsD5hNvCHhsbFVVjV7jLVo7ZFT03H-xHqKvfwLr0vlZ-zJLWHSBHpERZt1UcsQfeYaFpiVLKkKe2d6mRxsRAMd5xoOR-21mWL_2FdQgAf_4pbiV5uGKoEedBXc9F5WzEUSvisT9EZsyBedhlCKjGlkc2XnmpFOoYp2gAeYADH5y0Eo-sm8vIRoc1kwwPSpP8VwiDbFa_VZZQRjjIn2sdyik0bRuENX8DyYWZ872b0MvxwjHsW7L6GCpslHG4oBOIyG9YTD2qbfvJZ4u1jGQmdXgodC4u0IZgHrEQ",
#     "e": "AQAB",
#     "use": "sig",
#     "kid": "p2Nn-dW_bmgM0TGLxjCD9La_1nof8KiFBN8s4T5A-1A",
#     "qi": "KMBUWTGBc594cDIB5L3C3zJi-MvY8pXphNhq0WxScl8F6Pc1gO7FggSMhjcUFuY0pHZNx1DJwpNkdY23c-Y1U_51aIe1F-jLeFoLuAC6NGV4s7rLc-0mwiGQsuqEZGV2TU2Kpx2_153ljgk4uJ4MoEyfx4ILtkL-SY2PH7raTLM",
#     "dp": "SFXGok5KEKpqUMDQyg3femxrxIFj4YPeFDhJRugPvhIZn5aGFU8T3XCTvhnz58sgNTww4xGCa-A4_iMgFEYIomIgpOMLhJkwP1Gw5dOfmekJlqexkTIDzNRk1ahv6Rznijk_m9PQpMjFGG0k04lEDGxGtbutwuqeRaDdTU8-VW0",
#     "alg": "RS256",
#     "dq": "g3bjF9znr1H0MkGtK2Epdn6YhJUL1cUwY7wBpO9caVAVt189x_lOl1lbVFlObW6s4PE2fSXTRF_RK1X7yaR79z1RQZZ5wQ07hjJ3jKsDLzWaTqrYE3s_VMj5poC-rwL6L8jsc0svfCILxvsdubHMRlLNLB4LcLbDlOD8q4jwZvs",
#     "n": "tpPSDZCcNkAjOAFcTjF3F3kQWdv6yRZqOsDQnS0fXSNwjYyWiCfl81yi5kvUTEJ6kqz8B1WaotQYrFWfceSWg2qZ_vFqq_SPQ4Vkfh5HuQv2hUtSlSVtkcIL6Hew2qKwmRKQQCST9dOTCiv_ta8vMBhIv7kNhFQlgnk2DpU5KPdsvWfBLLGonm97kza6-ltJ6jRRxaWcSPyrRAUT-C_PS7-NzCagfYU5LNNmVpmPigMrraMTkVVNI2zPSJwSdJZIv1UvNI3gSs9yEBSjSPiVAs3UANGN4_lnQwiJbqAhbwIQ1bKVL1yhYrWJXFEijqKiRgjPxUJrqPzqXwS8UKBYZQ"
# }
# public_jwk = {
#     "kty": "RSA",
#     "e": "AQAB",
#     "use": "sig",
#     "kid": "p2Nn-dW_bmgM0TGLxjCD9La_1nof8KiFBN8s4T5A-1A",
#     "alg": "RS256",
#     "n": "tpPSDZCcNkAjOAFcTjF3F3kQWdv6yRZqOsDQnS0fXSNwjYyWiCfl81yi5kvUTEJ6kqz8B1WaotQYrFWfceSWg2qZ_vFqq_SPQ4Vkfh5HuQv2hUtSlSVtkcIL6Hew2qKwmRKQQCST9dOTCiv_ta8vMBhIv7kNhFQlgnk2DpU5KPdsvWfBLLGonm97kza6-ltJ6jRRxaWcSPyrRAUT-C_PS7-NzCagfYU5LNNmVpmPigMrraMTkVVNI2zPSJwSdJZIv1UvNI3gSs9yEBSjSPiVAs3UANGN4_lnQwiJbqAhbwIQ1bKVL1yhYrWJXFEijqKiRgjPxUJrqPzqXwS8UKBYZQ"
# }

private_jwk = {
    "kty": "EC",
    "d": "BMtpLFf4dxoPeJSg917huMaIs9rgHlU4EmIymbKIOZo",
    "use": "sig",
    "crv": "P-256",
    "x": "lPytfPjf1XOfcsF-8ceI5MXxLd4HDGrdlTwcO8VS3go",
    "y": "m6OUQbcruidyrOEQKLWuALlWaB5Z8_Zqwy-LOmYMFuA",
    "alg": "ES256"
}
public_jwk = {
    "kty": "EC",
    "use": "sig",
    "crv": "P-256",
    "x": "lPytfPjf1XOfcsF-8ceI5MXxLd4HDGrdlTwcO8VS3go",
    "y": "m6OUQbcruidyrOEQKLWuALlWaB5Z8_Zqwy-LOmYMFuA",
    "alg": "ES256"
}


def encode_jwt(payload, jwk, header, algorithm):
    key = get_default_algorithms()[algorithm].from_jwk(json.dumps(jwk))
    return jwt.encode(
        payload, key, algorithm=algorithm, headers=header,
    )


now = int(time.time())

payload = {
  "exp": now + 100000,
  "iat": now,
  "jti": "ac66b86e-1ca4-4229-9622-360fcf17d2ea",
  "iss": "https://localhost/idp/realms/pid-issuer-realm",
  "sub": "60b8ba5f-c73f-4976-b0da-48d0e53335de",
  "typ": "Bearer",
  "azp": "wallet-dev",
  "session_state": "6085dc68-467a-4819-983d-e30c3e273133",
  "allowed-origins": [
    "/*"
  ],
  "scope": "openid eu.europa.ec.eudiw.pid_vc_sd_jwt eu.europa.ec.eudiw.pid_mso_mdoc",
  "sid": "6085dc68-467a-4819-983d-e30c3e273133",
  "aud": [
      # "wallet-dev",
      "http://localhost",
  ],
  "nonce": sys.argv[1],
}

jwt_token = encode_jwt(
    payload=payload,
    jwk=private_jwk,
    # algorithm="RS256",
    algorithm="ES256",
    header={
        "typ": "openid4vci-proof+jwt",
        "jwk": public_jwk,
    },
)
print(jwt_token)
