import logging
import pytest
import collections

logger = logging.getLogger(__name__)


HW_IDS: list[str] = [
    "FIRST",
    "SECOND",
]

SECOND_HW_PARAM: list[str] = ["!ZZZ!", "!XXX!"]


OTHER_PARAMETERS: list[str] = ["p_1_1", "p_1_2"]
OTHER_PARAMETERS_2: list[str] = ["p_2_1", "p_2_2"]


calls_cache = collections.Counter()


@pytest.fixture(scope="session")
def heavy_fixture(request: pytest.FixtureRequest) -> str:
    param1, param2 = request.param
    calls_cache[(param1, param2)] += 1
    logger.info(f" ************ {param1} {param2} - {calls_cache[(param1, param2)]}")
    return f"{param1}/{param2}"

    
@pytest.fixture(scope="function", autouse=True)
def print_current_test_name(request: pytest.FixtureRequest):
    yield
    logger.info(f"-> {request.node.name}")

    
@pytest.fixture(scope="session", autouse=True)
def print_calls_cache():
    yield
    logger.info(" Fixture calls cache:")
    for (param1, param2), calls in calls_cache.items():
        logger.info(f" - {param1} {param2} -> {calls}")
    logger.info(f" Total times fixtures called: {sum(calls_cache.values())}")
    logger.info(f" Total heavy fixtures: {len(calls_cache)}")


@pytest.fixture(scope="module")
def fixture_1() -> str:
    return "fixture_1"


@pytest.fixture(scope="module")
def fixture_param_1(request: pytest.FixtureRequest) -> str:
    return request.param


@pytest.mark.parametrize(
    "heavy_fixture",
    [(m, b) for m in HW_IDS for b in SECOND_HW_PARAM],
    ids=lambda p: f"{p[0]}/{p[1]}",
    indirect=["heavy_fixture"],
)
def test_one_fxt(heavy_fixture: str, fixture_1):
    pass


@pytest.mark.parametrize("config", OTHER_PARAMETERS)
@pytest.mark.parametrize(
    "heavy_fixture",
    [(HW_IDS[0], SECOND_HW_PARAM[0])],
    ids=lambda p: f"{p[0]}/{p[1]}",
    indirect=["heavy_fixture"],
)
def test_with_params_one(heavy_fixture: str, config: str):    
    pass


@pytest.mark.parametrize("config", OTHER_PARAMETERS)
@pytest.mark.parametrize("config_2", OTHER_PARAMETERS_2)
@pytest.mark.parametrize(
    "heavy_fixture",
    [(HW_IDS[0], SECOND_HW_PARAM[1])],
    ids=lambda p: f"{p[0]}/{p[1]}",
    indirect=["heavy_fixture"],
)
def test_with_params_one_second_param(heavy_fixture: str, config: str, config_2: str):    
    pass


@pytest.mark.parametrize("config", OTHER_PARAMETERS)
@pytest.mark.parametrize(
    "heavy_fixture",
    [(HW_IDS[0], b) for b in SECOND_HW_PARAM],
    ids=lambda p: f"{p[0]}/{p[1]}",
    indirect=["heavy_fixture"],
)
def test_with_params_all_models(heavy_fixture: str, config: str):    
    pass


ITEMS_DATA = [
    ((hw, b), "fp_1") for hw in HW_IDS for b in SECOND_HW_PARAM
]


ITEMS_DATA_2 = [
    ((hw, b), "fp_2") for hw in HW_IDS for b in SECOND_HW_PARAM
]


def multiple_fixture_parametrize(
    items: tuple[tuple[str, str], str]
):
    return pytest.mark.parametrize(
        "heavy_fixture, fixture_param_1",
        items,
        indirect=["heavy_fixture", "fixture_param_1"],
        ids=[f"{item[0][0]}/{item[0][1]}/{item[1]}" for item in items]
    )
    
    

@multiple_fixture_parametrize(ITEMS_DATA)
def test_multiple_fixture_parametrize(heavy_fixture: str, fixture_param_1: str):
    pass

    

@multiple_fixture_parametrize(ITEMS_DATA_2)
def test_multiple_fixture_parametrize_second(heavy_fixture: str, fixture_param_1: str):
    pass
