import copy
import json
from azure_ai_search import settings
from azure_ai_search.user_groups import fetchUserGroups
import global_settings
from logger.log_main import get_logger


def prepare_body_headers_with_data(request):
    logger = get_logger()
    request_messages = request.json["messages"]
    body = {
        "messages": request_messages,
        "temperature": float(global_settings.AZURE_OPENAI_TEMPERATURE),
        "max_tokens": int(global_settings.AZURE_OPENAI_MAX_TOKENS),
        "top_p": float(global_settings.AZURE_OPENAI_TOP_P),
        "stop": global_settings.AZURE_OPENAI_STOP_SEQUENCE.split("|") if global_settings.AZURE_OPENAI_STOP_SEQUENCE else None,
        "stream": global_settings.SHOULD_STREAM,
        "dataSources": []
    }

    query_type = "simple"
    if settings.AZURE_SEARCH_QUERY_TYPE:
        query_type = settings.AZURE_SEARCH_QUERY_TYPE
    elif settings.AZURE_SEARCH_USE_SEMANTIC_SEARCH.lower() == "true" and settings.AZURE_SEARCH_SEMANTIC_SEARCH_CONFIG:
        query_type = "semantic"

    # Set filter
    filter = None
    userToken = None
    if settings.AZURE_SEARCH_PERMITTED_GROUPS_COLUMN:
        userToken = request.headers.get('X-MS-TOKEN-AAD-ACCESS-TOKEN', "")
        logger.debug(f"USER TOKEN is {'present' if userToken else 'not present'}")

        filter = generateFilterString(userToken)
        logger.debug(f"FILTER: {filter}")

    body["dataSources"].append(
    {
        "type": "AzureCognitiveSearch",
        "parameters": {
            "endpoint": f"https://{settings.AZURE_SEARCH_SERVICE}.search.windows.net",
            "key": settings.AZURE_SEARCH_KEY,
            "indexName": settings.AZURE_SEARCH_INDEX,
            "fieldsMapping": {
                "contentFields": settings.AZURE_SEARCH_CONTENT_COLUMNS.split("|") if settings.AZURE_SEARCH_CONTENT_COLUMNS else [],
                "titleField": settings.AZURE_SEARCH_TITLE_COLUMN if settings.AZURE_SEARCH_TITLE_COLUMN else None,
                "urlField": settings.AZURE_SEARCH_URL_COLUMN if settings.AZURE_SEARCH_URL_COLUMN else None,
                "filepathField": settings.AZURE_SEARCH_FILENAME_COLUMN if settings.AZURE_SEARCH_FILENAME_COLUMN else None,
                "vectorFields": settings.AZURE_SEARCH_VECTOR_COLUMNS.split("|") if settings.AZURE_SEARCH_VECTOR_COLUMNS else []
            },
            "inScope": True if settings.AZURE_SEARCH_ENABLE_IN_DOMAIN.lower() == "true" else False,
            "topNDocuments": settings.AZURE_SEARCH_TOP_K,
            "queryType": query_type,
            "semanticConfiguration": settings.AZURE_SEARCH_SEMANTIC_SEARCH_CONFIG if settings.AZURE_SEARCH_SEMANTIC_SEARCH_CONFIG else "",
            "roleInformation": global_settings.AZURE_OPENAI_SYSTEM_MESSAGE,
            "filter": filter,
            "strictness": int(settings.AZURE_SEARCH_STRICTNESS)
        }
    })

    if "vector" in query_type.lower():
        if global_settings.AZURE_OPENAI_EMBEDDING_NAME:
            body["dataSources"][0]["parameters"]["embeddingDeploymentName"] = global_settings.AZURE_OPENAI_EMBEDDING_NAME
        else:
            body["dataSources"][0]["parameters"]["embeddingEndpoint"] = global_settings.AZURE_OPENAI_EMBEDDING_ENDPOINT
            body["dataSources"][0]["parameters"]["embeddingKey"] = global_settings.AZURE_OPENAI_EMBEDDING_KEY

    body_clean_for_logging = copy.deepcopy(body)
    if body_clean_for_logging["dataSources"][0]["parameters"].get("key"):
        body_clean_for_logging["dataSources"][0]["parameters"]["key"] = "*****"
    if body_clean_for_logging["dataSources"][0]["parameters"].get("connectionString"):
        body_clean_for_logging["dataSources"][0]["parameters"]["connectionString"] = "*****"
    if body_clean_for_logging["dataSources"][0]["parameters"].get("embeddingKey"):
        body_clean_for_logging["dataSources"][0]["parameters"]["embeddingKey"] = "*****"
    
    logger.debug(f"REQUEST BODY: {json.dumps(body_clean_for_logging, indent=4)}")
    headers = {
        'Content-Type': 'application/json',
        'api-key': global_settings.AZURE_OPENAI_KEY,
        "x-ms-useragent": "GitHubSampleWebApp/PublicAPI/3.0.0"
    }

    return body, headers

def generateFilterString(userToken):
    logger = get_logger()
    
    # Get list of groups user is a member of
    userGroups = fetchUserGroups(userToken)

    # Construct filter string
    logger.debug("No user groups found")

    group_ids = ", ".join([obj['id'] for obj in userGroups])
    return f"{settings.AZURE_SEARCH_PERMITTED_GROUPS_COLUMN}/any(g:search.in(g, '{group_ids}'))"