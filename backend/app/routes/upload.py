from fastapi import APIRouter, UploadFile, File
import os
import shutil

from app.services.pdf_service import extract_text_from_pdf
from app.services.ai_service import detect_changes, analyze_impact, generate_actions, detect_compliance_gaps

from app.rag.pipeline import process_document
from app.rag.retriever import retrieve_with_metadata

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload-documents")
async def upload_documents(
    old_file: UploadFile = File(...),
    new_file: UploadFile = File(...),
    policy_file: UploadFile = File(...)
):
    try:
        # =========================
        # 1. SAVE FILES
        # =========================
        old_path = os.path.join(UPLOAD_DIR, old_file.filename)
        new_path = os.path.join(UPLOAD_DIR, new_file.filename)
        policy_path = os.path.join(UPLOAD_DIR, policy_file.filename)

        with open(old_path, "wb") as buffer:
            shutil.copyfileobj(old_file.file, buffer)

        with open(new_path, "wb") as buffer:
            shutil.copyfileobj(new_file.file, buffer)

        with open(policy_path, "wb") as buffer:
            shutil.copyfileobj(policy_file.file, buffer)

        # =========================
        # 2. EXTRACT TEXT
        # =========================
        old_text = extract_text_from_pdf(old_path)
        new_text = extract_text_from_pdf(new_path)
        policy_text = extract_text_from_pdf(policy_path)

        # =========================
        # 3. STORE IN VECTOR DB (RAG)
        # =========================
        process_document(old_text, "old_regulation")
        process_document(new_text, "new_regulation")
        process_document(policy_text, "internal_policy")

        # =========================
        # 4. RETRIEVE CONTEXT (RAG)
        # =========================
        old_context = "\n\n".join(
            retrieve_with_metadata("key regulatory clauses", "old_regulation")
        )

        new_context = "\n\n".join(
            retrieve_with_metadata("latest regulatory changes", "new_regulation")
        )

        policy_context = "\n\n".join(
            retrieve_with_metadata("internal compliance rules", "internal_policy")
        )

        # =========================
        # 5. AI INTELLIGENCE
        # =========================

        # 🔥 Detect changes (Old vs New)
        changes = detect_changes(old_context, new_context)

        # 🔥 Detect compliance gaps (New vs Policy)
        compliance_gaps = detect_compliance_gaps(new_context, policy_context)

        # 🔥 Impact analysis
        impact = analyze_impact(
            str(changes) + "\n" + str(compliance_gaps)
        )

        # 🔥 Action generation
        actions = generate_actions(
            str(changes),
            str(impact) + "\n" + str(compliance_gaps)
        )

        # =========================
        # 6. RESPONSE
        # =========================
        return {
            "changes": changes,
            "compliance_gaps": compliance_gaps,
            "impact": impact,
            "actions": actions
        }

    except Exception as e:
        return {"error": str(e)}