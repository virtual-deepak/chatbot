from dotenv import load_dotenv
load_dotenv()

from http import HTTPStatus
from flask import Flask, Response, jsonify, request

import azure_ai_search.conversation as azure_ai_search_conversation
import azure_openai.conversation as azure_openai_conversation
from helper_methods import streaming_helper
import helper_methods.non_streaming_helper as non_streaming_helper
from logger.log_main import get_logger
import global_settings


app = Flask(__name__)

@app.route("/conversation/azure/aisearch", methods=["GET", "POST"])
def conversation_azure_aisearch():
    logger = get_logger()
    try:
        body, headers = azure_ai_search_conversation.azure_search()
        if body is None or headers is None:
            return Response("Refer log for more details.", status=HTTPStatus.OK)
        return get_conversation_response(request.json, body, headers)
    except Exception as e:
        logger.exception("Exception in conversation_azure_aisearch")
        return jsonify({"error": str(e)}), 500

@app.route("/conversation/azure/simple", methods=["GET", "POST"])
def conversation_azure_simple():
    logger = get_logger()
    try:
        response = azure_openai_conversation.conversation_aoai(request.json if request.content_length else None)
        if response is None:
            return Response("Refer log for more details.", status=HTTPStatus.OK)
        return response
    except Exception as e:
        logger.exception("Exception in conversation_azure_aisearch")
        return jsonify({"error": str(e)}), 500


def get_conversation_response(request_body: str, body: dict, headers: dict):
    base_url = global_settings.AZURE_OPENAI_ENDPOINT if global_settings.AZURE_OPENAI_ENDPOINT else f"https://{global_settings.AZURE_OPENAI_RESOURCE}.openai.azure.com/"
    endpoint = f"{base_url}openai/deployments/{global_settings.AZURE_OPENAI_MODEL}/extensions/chat/completions?api-version={global_settings.AZURE_OPENAI_PREVIEW_API_VERSION}"
    history_metadata = request_body.get("history_metadata", {})
    if global_settings.SHOULD_STREAM:
        return Response(streaming_helper.stream_with_data(body, headers, endpoint, history_metadata), mimetype='text/event-stream')
    else:
        result, status_code = non_streaming_helper.get_result()
        return Response(result, status=status_code)

if __name__ == "__main__":
    app.run()