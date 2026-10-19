import steadytype_client


def test_package_reports_a_version():
    assert steadytype_client.__version__ == "0.1.0"
