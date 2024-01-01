from flask import request
from azure_ai_search.query_helper import prepare_body_headers_with_data
from logger.log_main import get_logger
import azure_ai_search.settings as settings

def azure_search():
    logger = get_logger()
    try:
        if settings.AZURE_SEARCH_SERVICE and settings.AZURE_SEARCH_INDEX and settings.AZURE_SEARCH_KEY:
            logger.debug("Using Azure AI Search")
        else:
            logger.info("Azure search settings are not defined")
            return

        return prepare_body_headers_with_data(request)
        
    except Exception as e:
        logger.exception("Exception in conversation_azure_search")