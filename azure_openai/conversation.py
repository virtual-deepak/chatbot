from flask import Response, jsonify
import openai
import global_settings
from helper_methods import streaming_helper


def conversation_aoai(request_body) -> (str, str, int):
    openai.api_type = "azure"
    openai.api_base = global_settings.AZURE_OPENAI_ENDPOINT if global_settings.AZURE_OPENAI_ENDPOINT else f"https://{global_settings.AZURE_OPENAI_RESOURCE}.openai.azure.com/"
    openai.api_version = "2023-08-01-preview"
    openai.api_key = global_settings.AZURE_OPENAI_KEY

    request_messages = None
    if request_body:
        request_messages = request_body["messages"]
    messages = [
        {
            "role": "system",
            "content": global_settings.AZURE_OPENAI_SYSTEM_MESSAGE
        }
    ]

    if request_messages:
        for message in request_messages:
            if message:
                messages.append({
                    "role": message["role"] ,
                    "content": message["content"]
                })

    response = openai.ChatCompletion.create(
        engine=global_settings.AZURE_OPENAI_MODEL,
        messages = messages,
        temperature=float(global_settings.AZURE_OPENAI_TEMPERATURE),
        max_tokens=int(global_settings.AZURE_OPENAI_MAX_TOKENS),
        top_p=float(global_settings.AZURE_OPENAI_TOP_P),
        stop=global_settings.AZURE_OPENAI_STOP_SEQUENCE.split("|") if global_settings.AZURE_OPENAI_STOP_SEQUENCE else None,
        stream=global_settings.SHOULD_STREAM
    )

    history_metadata = None
    if request_body:
        history_metadata = request_body.get("history_metadata", {})

    if global_settings.SHOULD_STREAM:
        return Response(streaming_helper.stream_without_data(response, history_metadata), mimetype='text/event-stream', status=200)
    else:
        response_obj = {
            "model": response.model,
            "created": response.created,
            "object": response.object,
            "choices": [{
                "messages": [{
                    "role": "assistant",
                    "content": response.choices[0].message.content
                }]
            }],
            "history_metadata": history_metadata
        }

        return jsonify(response_obj)