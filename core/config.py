from google.generativeai.types import HarmCategory, HarmBlockThreshold

TEXT_SIZE_LIMIT_MB = 5

generation_config_={
            "max_output_tokens": 800,
            "top_p": 0.9,
            "temperature": 0.6
        }

request_options_ = {
    "timeout": 60,
}

safety_settings_={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            }

prompt_= (f"You are a bot that can comprehend the entire text given and produce the most appropriate answer to "
          f"the question asked by the user, and the user wants to get the answer to the following question related "
          f"to the text: ")