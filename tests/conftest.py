import pytest
import debugpy


@pytest.fixture(scope="session", autouse=True)
def attach_debugger():
    debugpy.listen(("localhost", 5678))
    print("Waiting for debugger to attach...")
    debugpy.wait_for_client()
    print("Debugger attached.")
