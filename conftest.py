"""conftest
"""

def pytest_addoption(parser):
    """pytest_addoption

    Args:
        parser ([type]): [description]
    """
    parser.addoption("--user_name", action="store", default="your_user_name")
    parser.addoption("--user_password", action="store", default="your_password")


def pytest_generate_tests(metafunc):
    """pytest_generate_tests

    Args:
        metafunc ([type]): [description]
    """
    # This is called for every test. Only get/set command line arguments
    # if the argument is specified in the list of test "fixturenames".
    option_value = metafunc.config.option.user_name
    if 'user_name' in metafunc.fixturenames and option_value is not None:
        metafunc.parametrize("user_name", [option_value])

    option_value = metafunc.config.option.user_password
    if 'user_password' in metafunc.fixturenames and option_value is not None:
        metafunc.parametrize("user_password", [option_value])
