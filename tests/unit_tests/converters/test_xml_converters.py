import json

import xmltodict
from tests.constants import TestDataPaths


def test_xml_to_dict_gives_expected_result_and_can_be_jsonified():
    with open(TestDataPaths.TEST_GOOD_XML_PATH) as f:
        contents = f.read()
    expected = {
        "JCameraManSettings": {
            "levels": {
                "zoomLevel": [
                    {
                        "level": "1.0",
                        "micronsPerXPixel": "2.432",
                        "micronsPerYPixel": "2.432",
                        "position": "0",
                    },
                    {
                        "level": "1.5",
                        "micronsPerXPixel": "1.888",
                        "micronsPerYPixel": "1.888",
                        "position": "16.3",
                    },
                ],
            },
            "tolerance": "1.0",
        },
    }
    result = xmltodict.parse(contents)
    assert result == expected
    json.dumps(result)
