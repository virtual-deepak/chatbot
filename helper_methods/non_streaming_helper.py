import requests
import global_settings
from helper_methods import format_helper

def get_result(endpoint: str, headers: dict, body: dict, history_metadata: any) -> (str, str):
    response = requests.post(endpoint, headers=headers, json=body)
    status_code = response.status_code
    response = response.json()
    if global_settings.AZURE_OPENAI_PREVIEW_API_VERSION == "2023-06-01-preview":
        response['history_metadata'] = history_metadata
        return format_helper.format_as_ndjson(response), status_code
    else:
        result = format_helper.formatApiResponseNoStreaming(response)
        result['history_metadata'] = history_metadata
        return format_helper.format_as_ndjson(result), status_code
