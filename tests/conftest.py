import pytest
import debugpy


@pytest.fixture(scope="session", autouse=True)
def attach_debugger():
    debugpy.listen(("localhost", 5678))
    print("Waiting for debugger to attach...")
    debugpy.wait_for_client()
    print("Debugger attached.")


def pytest_collection_modifyitems(config, items):
    # Move the specific test to the beginning of the list
    for i, item in enumerate(items):
        if item.name == "test_run_property_services":
            items.insert(0, items.pop(i))
            break
