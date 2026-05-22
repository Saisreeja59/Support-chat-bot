# import os
# import ssl
# import certifi
# import logging
# from azure.core.credentials import AzureKeyCredential
# from azure.ai.translation.text import TextTranslationClient
# from dotenv import load_dotenv

# load_dotenv()

# # 🔑 Fix SSL verification issue
# def _patched_ssl_context(*args, **kwargs):
#     return ssl.create_default_context(cafile=certifi.where())

# ssl._create_default_https_context = _patched_ssl_context

# # Setup logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# TRANSLATOR_ENDPOINT = os.getenv("AZURE_TRANSLATOR_ENDPOINT")
# TRANSLATOR_KEY = os.getenv("AZURE_TRANSLATOR_KEY")

# client = TextTranslationClient(
#     endpoint=TRANSLATOR_ENDPOINT,
#     credential=AzureKeyCredential(TRANSLATOR_KEY)
# )

# def detect_and_translate(text: str, to_lang: str = "en") -> str:
#     """
#     Translate input text to `to_lang`.
#     Falls back to original text if translation fails.
#     """
#     if not text.strip():
#         return text

#     try:
#         response = client.translate(
#             content=[text],
#             to=[to_lang]
#         )
#         translations = response[0].translations
#         if translations:
#             return translations[0].text
#     except Exception as e:
#         # 🚀 User gets clean text, backend logs the error
#         logger.warning(f"Translation failed (fallback to original). Error: {e}")
#         return text

#     return text
























# import os
# import logging
# import google.generativeai as genai
# from dotenv import load_dotenv

# load_dotenv()

# # Setup logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# genai.configure(api_key=GEMINI_API_KEY)
# _translation_model = genai.GenerativeModel(GEMINI_MODEL)

# # ISO 639-1 code → language name mapping for natural prompting
# _LANG_NAMES = {
#     "en": "English", "hi": "Hindi", "te": "Telugu", "ta": "Tamil",
#     "kn": "Kannada", "ml": "Malayalam", "mr": "Marathi", "bn": "Bengali",
#     "gu": "Gujarati", "pa": "Punjabi", "ur": "Urdu", "fr": "French",
#     "de": "German", "es": "Spanish", "pt": "Portuguese", "it": "Italian",
#     "nl": "Dutch", "ru": "Russian", "ja": "Japanese", "ko": "Korean",
#     "zh": "Chinese", "ar": "Arabic", "tr": "Turkish", "pl": "Polish",
# }

# def _lang_name(code: str) -> str:
#     return _LANG_NAMES.get(code.lower().split("-")[0], code)


# def detect_and_translate(text: str, to_lang: str = "en") -> str:
#     """
#     Translate input text to `to_lang` using Gemini.
#     Falls back to original text if translation fails.
#     """
#     if not text.strip():
#         return text

#     target_language = _lang_name(to_lang)

#     prompt = (
#         f"Translate the following text to {target_language}. "
#         "Return ONLY the translated text with no explanation, preamble, or quotation marks.\n\n"
#         f"{text}"
#     )

#     try:
#         response = _translation_model.generate_content(prompt)
#         translated = response.text.strip()
#         if translated:
#             return translated
#     except Exception as e:
#         logger.warning(f"Translation failed (fallback to original). Error: {e}")

#     return text






import os
import logging

# Fix corporate SSL certificate issue
os.environ.pop("REQUESTS_CA_BUNDLE", None)
os.environ.pop("SSL_CERT_FILE", None)

from deep_translator import GoogleTranslator

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def detect_and_translate(text: str, to_lang: str = "en") -> str:
    """
    Translate text to target language using GoogleTranslator.

    Examples:
        Tamil  -> English
        Hindi  -> English
        English -> Telugu
        English -> Hindi
    """

    if not text or not text.strip():
        return text

    try:
        translated = GoogleTranslator(
            source="auto",
            target=to_lang
        ).translate(text)

        return translated

    except Exception as e:

        logger.warning(
            f"Translation failed (fallback to original). Error: {e}"
        )

        return text