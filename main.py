# import os
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from agent import run_swarm_conversation
# from preprocessing import detect_and_translate  # Azure Translator integration

# app = FastAPI(title="AutoRouteAI Swarm Backend")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# class ChatRequest(BaseModel):
#     query: str
#     lang: str = "en"

# @app.post("/chat")
# def chat(req: ChatRequest):
#     try:
#         # Translate user query to English for the AI
#         translated_query = detect_and_translate(req.query, to_lang="en")

#         # Run the Swarm Master agent
#         reply = run_swarm_conversation(translated_query)

#         # Translate back to original language if needed
#         if req.lang != "en":
#             reply = detect_and_translate(reply, to_lang=req.lang)

#         return {"response": reply}
#     except Exception as e:
#         return {"error": f"Agent error: {e}"}













import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent import run_swarm_conversation
from preprocessing import detect_and_translate

app = FastAPI(title="AutoRouteAI Swarm Backend")

# ──────────────────────────────────────────────
# CORS
# ──────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────
# REQUEST MODELS
# ──────────────────────────────────────────────
class ChatRequest(BaseModel):
    query: str
    lang: str = "en"


class TranslateRequest(BaseModel):
    text: str
    to_lang: str


# ──────────────────────────────────────────────
# CHAT ENDPOINT
# ──────────────────────────────────────────────
@app.post("/chat")
def chat(req: ChatRequest):

    try:
        print("\n" + "=" * 60)
        print("NEW REQUEST")
        print("=" * 60)

        print("Original Query :", req.query)
        print("User Language  :", req.lang)

        # Translate user query to English
        translated_query = detect_and_translate(
            req.query,
            to_lang="en"
        )

        print("Translated Query:", translated_query)

        # Run Swarm Agent
        reply = run_swarm_conversation(
            translated_query
        )

        print("Agent Reply:", reply)

        # Translate response back to user's language
        if req.lang != "en":

            translated_reply = detect_and_translate(
                reply,
                to_lang=req.lang
            )

            print("Translated Reply:", translated_reply)

            reply = translated_reply

        return {
            "response": reply
        }

    except Exception as e:

        print("\nERROR IN /chat")
        print(type(e).__name__)
        print(str(e))

        # Don't expose Gemini internals to users
        return {
            "response":
            "Sorry, the service is temporarily unavailable. Please try again in a few moments."
        }


# ──────────────────────────────────────────────
# TRANSLATION ENDPOINT
# ──────────────────────────────────────────────
@app.post("/translate")
def translate(req: TranslateRequest):

    try:

        translated = detect_and_translate(
            req.text,
            to_lang=req.to_lang
        )

        return {
            "translated": translated
        }

    except Exception as e:

        print("\nERROR IN /translate")
        print(type(e).__name__)
        print(str(e))

        return {
            "translated": req.text
        }


# ──────────────────────────────────────────────
# HEALTH CHECK
# ──────────────────────────────────────────────
@app.get("/")
def health_check():

    return {
        "status": "running",
        "service": "AutoRouteAI Swarm Backend"
    }