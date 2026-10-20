from __future__ import annotations

import json
import logging
import os
from typing import Literal
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, ValidationError

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PromptVersion = Literal["A", "B", "C"]
DEFAULT_MODEL = "openai/gpt-oss-120b"

# Prompt A: sederhana; Prompt B: Role + Task + Context;
# Prompt C: Role + Task + Context + Constraint + Output Format.
PROMPTS: dict[str, str] = {
    "A": (
        "Ringkas materi berikut dalam Bahasa Indonesia. "
        "Ambil ide-ide utamanya dan buat hasil yang mudah dipahami."
    ),
    "B": (
        "Peran: Kamu adalah asisten belajar untuk mahasiswa. "
        "Task: Ringkas materi dan identifikasi konsep serta istilah penting. "
        "Context: Materi yang diberikan adalah teks pembelajaran atau catatan kuliah. "
        "Gunakan Bahasa Indonesia yang jelas dan mudah dipahami."
    ),
    "C": (
        "Peran: Kamu adalah asisten belajar akademik yang teliti dan tidak mengarang. "
        "Task: Analisis materi belajar dan ubah menjadi ringkasan, konsep utama, "
        "daftar istilah, dan pertanyaan latihan beserta jawabannya. "
        "Context: Input dapat berupa catatan kuliah, artikel, atau penjelasan konsep. "
        "Gunakan hanya informasi yang didukung oleh teks yang diberikan. "
        "Constraint: Jawab dalam Bahasa Indonesia. Buat ringkasan 2–4 kalimat. "
        "Pilih 3–6 konsep utama jika materi memang cukup informatif. "
        "Definisi istilah dan jawaban kuis harus didukung oleh teks. "
        "Jangan menebak atau menambahkan fakta eksternal seolah-olah berasal dari materi. "
        "Jika teks berisi kata acak, tidak jelas, atau terlalu sedikit informasi, "
        "jelaskan keterbatasannya pada summary dan kosongkan key_concepts, key_terms, "
        "serta quiz_questions. "
        "Output Format: Kembalikan JSON yang sesuai dengan schema API: title, summary, "
        "key_concepts, key_terms, quiz_questions, difficulty_level. "
        "Jangan gunakan Markdown atau code fence."
    ),
}

# Groq Structured Outputs (strict mode) memakai schema ini untuk menjaga bentuk JSON.
OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "description": "Judul singkat materi dalam Bahasa Indonesia.",
        },
        "summary": {
            "type": "string",
            "description": "Ringkasan materi dalam Bahasa Indonesia.",
        },
        "key_concepts": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Konsep-konsep utama yang didukung oleh teks.",
        },
        "key_terms": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "term": {"type": "string"},
                    "definition": {"type": "string"},
                },
                "required": ["term", "definition"],
                "additionalProperties": False,
            },
        },
        "quiz_questions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                    "answer": {"type": "string"},
                },
                "required": ["question", "answer"],
                "additionalProperties": False,
            },
        },
        "difficulty_level": {
            "type": "string",
            "enum": ["pemula", "menengah", "lanjut"],
        },
    },
    "required": [
        "title",
        "summary",
        "key_concepts",
        "key_terms",
        "quiz_questions",
        "difficulty_level",
    ],
    "additionalProperties": False,
}


class AnalyzeRequest(BaseModel):
    """Request untuk satu kali analisis materi."""

    text: str = Field(
        ...,
        min_length=30,
        max_length=12000,
        description="Teks materi belajar, minimal 30 dan maksimal 12.000 karakter.",
    )
    prompt_version: PromptVersion = Field(
        default="C",
        description="Versi prompt yang digunakan: A, B, atau C.",
    )


class ExperimentRequest(BaseModel):
    """Request untuk menjalankan Prompt A, B, dan C dengan input yang sama."""

    text: str = Field(
        ...,
        min_length=30,
        max_length=12000,
        description="Teks materi yang sama untuk ketiga eksperimen.",
    )


class KeyTerm(BaseModel):
    term: str
    definition: str


class QuizQuestion(BaseModel):
    question: str
    answer: str


class StudyAnalysis(BaseModel):
    title: str
    summary: str
    key_concepts: list[str]
    key_terms: list[KeyTerm]
    quiz_questions: list[QuizQuestion]
    difficulty_level: Literal["pemula", "menengah", "lanjut"]


class PromptExperimentResult(BaseModel):
    prompt_version: PromptVersion
    result: StudyAnalysis


class ExperimentsResponse(BaseModel):
    input_length: int
    experiments: list[PromptExperimentResult]


app = FastAPI(
    title="StudyMate AI",
    version="1.0.0",
    description=(
        "Learning Material Analyzer: mengubah materi belajar menjadi ringkasan, "
        "konsep utama, istilah, dan pertanyaan latihan dalam JSON terstruktur."
    ),
)



# Frontend StudyMate AI: buka melalui http://127.0.0.1:8000/app
APP_DIR = Path(__file__).resolve().parent


@app.get("/app", include_in_schema=False)
def study_app() -> FileResponse:
    """Menampilkan antarmuka web StudyMate AI."""
    return FileResponse(APP_DIR / "static" / "index.html")


@app.get("/")
def home() -> dict[str, str]:
    """Endpoint untuk memastikan API berjalan."""
    return {"message": "StudyMate AI is running", "docs": "/docs"}


@app.get("/health")
def health() -> dict[str, str | bool]:
    """Pemeriksaan sederhana tanpa mengungkap API key."""
    return {
        "status": "ok",
        "provider": "groq",
        "model": os.getenv("GROQ_MODEL", DEFAULT_MODEL),
        "api_key_configured": bool(os.getenv("GROQ_API_KEY")),
    }


async def generate_analysis(text: str, prompt_version: PromptVersion) -> StudyAnalysis:
    """Kirim teks ke Groq, lalu validasi hasilnya dengan Pydantic."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail=(
                "GROQ_API_KEY belum diatur. Salin .env.example menjadi .env, "
                "lalu isi API key Groq milikmu."
            ),
        )

    model_name = os.getenv("GROQ_MODEL", DEFAULT_MODEL)

    try:
        # Import SDK only when an actual LLM request is made. This keeps local
        # API validation tests runnable before provider dependencies are installed.
        from groq import AsyncGroq

        async with AsyncGroq(
            api_key=api_key,
            timeout=60.0,
            max_retries=1,
        ) as client:
            response = await client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": PROMPTS[prompt_version]},
                    {
                        "role": "user",
                        "content": f"Teks materi:\n{text}",
                    },
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "study_material_analysis",
                        "strict": True,
                        "schema": OUTPUT_SCHEMA,
                    },
                },
                temperature=0.2,
                max_completion_tokens=1600,
            )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Permintaan ke Groq gagal: %s", type(exc).__name__)
        raise HTTPException(
            status_code=502,
            detail=(
                "Permintaan ke layanan LLM gagal. Periksa koneksi internet, "
                "API key, kuota akun, dan nama model di file .env."
            ),
        ) from exc

    content = response.choices[0].message.content
    if not content:
        raise HTTPException(
            status_code=502,
            detail="Layanan LLM mengembalikan respons kosong. Silakan coba lagi.",
        )

    try:
        parsed = json.loads(content)
        return StudyAnalysis.model_validate(parsed)
    except (json.JSONDecodeError, ValidationError) as exc:
        logger.exception("Output LLM tidak sesuai schema.")
        raise HTTPException(
            status_code=502,
            detail=(
                "Output LLM tidak sesuai struktur yang diharapkan. "
                "Coba ulangi permintaan atau perbaiki prompt."
            ),
        ) from exc


@app.post("/analyze", response_model=StudyAnalysis)
async def analyze(request: AnalyzeRequest) -> StudyAnalysis:
    """Analisis materi dengan satu versi prompt."""
    return await generate_analysis(request.text, request.prompt_version)


@app.post("/experiments", response_model=ExperimentsResponse)
async def run_prompt_experiments(request: ExperimentRequest) -> ExperimentsResponse:
    """Jalankan Prompt A, B, dan C dengan teks yang sama."""
    results: list[PromptExperimentResult] = []
    for version in ("A", "B", "C"):
        result = await generate_analysis(request.text, version)  # type: ignore[arg-type]
        results.append(PromptExperimentResult(prompt_version=version, result=result))

    return ExperimentsResponse(
        input_length=len(request.text),
        experiments=results,
    )
