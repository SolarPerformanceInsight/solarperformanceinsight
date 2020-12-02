import datetime as dt


import httpx
import pytest


from solarperformanceinsight_api import settings, models, storage


@pytest.fixture(scope="session")
def auth_token():
    token_req = httpx.post(
        settings.auth_token_url,
        headers={"content-type": "application/json"},
        data=(
            '{"grant_type": "password", '
            '"username": "testing@solarperformanceinsight.org",'
            '"password": "Thepassword123!", '
            f'"audience": "{settings.auth_audience}", '
            f'"client_id": "{settings.auth_client_id}"'
            "}"
        ),
    )
    if token_req.status_code != 200:  # pragma: no cover
        pytest.skip("Cannot retrieve valid Auth0 token")
    else:
        token = token_req.json()["access_token"]
        return token


@pytest.fixture(scope="module")
def add_example_db_data():
    conn = storage._make_sql_connection_partial(user="root", password="testpassword")()
    curs = conn.cursor()
    curs.callproc("add_example_data")
    conn.commit()
    yield curs
    curs.callproc("remove_example_data")
    conn.commit()
    conn.close()


@pytest.fixture(scope="module")
def auth0_id():
    return "auth0|5fa9596ccf64f9006e841a3a"


@pytest.fixture(scope="module")
def user_id():
    return "17fbf1c6-34bd-11eb-af43-f4939feddd82"


@pytest.fixture(scope="module")
def system_id():
    return "6b61d9ac-2e89-11eb-be2a-4dc7a6bcd0d9"


@pytest.fixture(scope="module")
def other_system_id():
    return "6513485a-34cd-11eb-8f13-f4939feddd82"


@pytest.fixture()
def system_def():
    return models.PVSystem(
        name="Test PV System",
        latitude=33.98,
        longitude=-115.323,
        elevation=2300,
        albedo=0.2,
        inverters=[
            models.Inverter(
                name="Inverter 1",
                make_model="ABB__MICRO_0_25_I_OUTD_US_208__208V_",
                inverter_parameters=models.SandiaInverterParameters(
                    Pso=2.08961,
                    Paco=250,
                    Pdco=259.589,
                    Vdco=40,
                    C0=-4.1e-05,
                    C1=-9.1e-05,
                    C2=0.000494,
                    C3=-0.013171,
                    Pnt=0.075,
                ),
                losses={},
                arrays=[
                    models.PVArray(
                        name="Array 1",
                        make_model="Canadian_Solar_Inc__CS5P_220M",
                        modules_per_string=7,
                        strings=5,
                        tracking=models.FixedTracking(
                            tilt=20.0,
                            azimuth=180.0,
                        ),
                        temperature_model_parameters=models.PVsystTemperatureParameters(
                            u_c=29.0, u_v=0.0, eta_m=0.1, alpha_absorption=0.9
                        ),
                        module_parameters=models.PVsystModuleParameters(
                            alpha_sc=0.004539,
                            gamma_ref=1.2,
                            mu_gamma=-0.003,
                            I_L_ref=5.11426,
                            I_o_ref=8.10251e-10,
                            R_sh_ref=381.254,
                            R_s=1.06602,
                            R_sh_0=400.0,
                            cells_in_series=96,
                        ),
                    )
                ],
            ),
        ],
    )


@pytest.fixture()
def stored_system(system_def, system_id):
    extime = dt.datetime(2020, 12, 1, 1, 23, tzinfo=dt.timezone.utc)
    return models.StoredPVSystem(
        system_id=system_id,
        created_at=extime,
        modified_at=extime,
        definition=system_def,
    )
