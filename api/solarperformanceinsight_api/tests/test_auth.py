from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
import pytest


from solarperformanceinsight_api import auth, settings


pytestmark = pytest.mark.asyncio


async def test_get_auth_key(mocker):
    settings.auth_key = None
    client = mocker.spy(auth.httpx.AsyncClient, "get")
    key0 = await auth.get_auth_key()
    key1 = await auth.get_auth_key()
    assert key0 == key1
    assert client.call_count == 1


@pytest.mark.parametrize(
    "token",
    [
        "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ikd3LWZTdDZ0MVBidHo4V2FjSFJZZiJ9.eyJpc3MiOiJodHRwczovL3NvbGFycGVyZm9ybWFuY2VpbnNpZ2h0LnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1ZmE5NTk2Y2NmNjRmOTAwNmU4NDFhM2EiLCJhdWQiOiJodHRwczovL2FwcC5zb2xhcnBlcmZvcm1hbmNlaW5zaWdodC5vcmcvYXBpIiwiaWF0IjoxNjA2MjU4MjE4LCJleHAiOjE2MDYyNjkwMTgsImF6cCI6IkcxWXlmTGRzZVluMTBSUW8xMUxxZWUyVGhYajVsNWZoIiwiZ3R5IjoicGFzc3dvcmQifQ.Qj24kazTfx09QsXocTbqobpDMR7ulGABJ2861L2SBkSs7EZVsjWLaF1WVeeSg0w_bbADPMgEISBqVHfu3XMk9f6VITNuvUMVv8uiQL_17jK1MGoQ8B0qpWoIXXGqqszGEuXwbvdt0chsA59PPrSurUZ7Xu1Pm7-1MTywi1_9X3SiYZ48rrpOXxfzI067OQzfhrI5ltNh-pKUjkiee8toQ5ST6yaECHfpQFXXPpgkvWSq84vTTp8d6nH5kFw-Uup-3sBHCg3xkZ5F2cY2lnOImSTGl0SPEo5_RuBZhnmeAMwzAejRPXqSrh-qmweSWoFNTMFIky21fAzOGPcKkVmYog",  # NOQA
        "hXtD_wm0fVP0A2I_zX352YSP7seqd_l-",
        "Totally not a token",
    ],
)
async def test_get_user_id_invalid(token):
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    with pytest.raises(HTTPException) as err:
        await auth.get_user_id(creds)
    assert err.value.status_code == 401


async def test_get_user_id(valid_token):
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=valid_token)
    user_id = await auth.get_user_id(creds)
    assert user_id.startswith("auth0")
