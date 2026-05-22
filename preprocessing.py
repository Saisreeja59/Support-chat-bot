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
