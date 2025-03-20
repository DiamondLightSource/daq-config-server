from fastapi.testclient import TestClient

from daq_config_server.app import app

client = TestClient(app)

GRAPHQL_ENDPOINT = "/graphql"


def graphql_query(query: str, variables: dict | None = None):
    """Helper function to send GraphQL queries."""
    if variables is None:
        variables = {}
    response = client.post(
        GRAPHQL_ENDPOINT, json={"query": query, "variables": variables}
    )
    return response.json()


def test_fetch_single_beamline_parameter():
    query = """
    query ($key: String!) {
        beamlineParameter(key: $key) {
            key
            value
        }
    }
    """
    variables = {"key": "energy"}
    response = graphql_query(query, variables)

    assert "errors" not in response
    assert response["data"]["beamlineParameter"]["key"] == "energy"
    assert response["data"]["beamlineParameter"]["value"] is not None


def test_fetch_all_beamline_parameters():
    query = """
    query {
        allBeamlineParameters {
            key
            value
        }
    }
    """
    response = graphql_query(query)

    assert "errors" not in response
    assert isinstance(response["data"]["allBeamlineParameters"], list)
    assert len(response["data"]["allBeamlineParameters"]) > 0


def test_fetch_feature_flags():
    query = """
    query {
        featureFlags {
            name
        }
    }
    """
    response = graphql_query(query)

    assert "errors" not in response
    assert isinstance(response["data"]["featureFlags"], list)


def test_fetch_feature_flags_with_values():
    query = """
    query {
        featureFlags(getValues: true) {
            name
            value
        }
    }
    """
    response = graphql_query(query)

    assert "errors" not in response
    assert isinstance(response["data"]["featureFlags"], list)
    for flag in response["data"]["featureFlags"]:
        assert isinstance(flag["name"], str)
        assert isinstance(flag["value"], bool)


def test_create_feature_flag():
    mutation = """
    mutation ($name: String!, $value: Boolean!) {
        createFeatureFlag(name: $name, value: $value) {
            name
            value
        }
    }
    """
    variables = {"name": "dark_mode", "value": True}
    response = graphql_query(mutation, variables)

    assert "errors" not in response
    assert response["data"]["createFeatureFlag"]["name"] == "dark_mode"
    assert response["data"]["createFeatureFlag"]["value"] is True


def test_update_feature_flag():
    mutation = """
    mutation ($name: String!, $value: Boolean!) {
        updateFeatureFlag(name: $name, value: $value) {
            name
            value
        }
    }
    """
    variables = {"name": "dark_mode", "value": False}
    response = graphql_query(mutation, variables)

    assert "errors" not in response
    assert response["data"]["updateFeatureFlag"]["name"] == "dark_mode"
    assert response["data"]["updateFeatureFlag"]["value"] is False


def test_delete_feature_flag():
    mutation = """
    mutation ($name: String!) {
        deleteFeatureFlag(name: $name)
    }
    """
    variables = {"name": "dark_mode"}
    response = graphql_query(mutation, variables)

    assert "errors" not in response
    assert response["data"]["deleteFeatureFlag"] is True
