import traceback

from db.database import update_task

# ✅ import your existing functions
from app.services.pdf_service import extract_text_from_pdf
from app.services.ai_service import (
    detect_changes,
    analyze_impact,
    generate_actions,
    detect_compliance_gaps
)
from app.rag.pipeline import process_document
from app.rag.retriever import retrieve_with_metadata


def build_context(chunks, limit=3000):
    text = "\n\n".join(chunks)
    return text[:limit]


def process_task(task_id: str, file_paths: dict):
    try:
        old_path = file_paths["old"]
        new_path = file_paths["new"]
        policy_path = file_paths["policy"]

        # -----------------------------
        # 1. EXTRACT TEXT
        # -----------------------------
        old_text = extract_text_from_pdf(old_path)
        new_text = extract_text_from_pdf(new_path)
        policy_text = extract_text_from_pdf(policy_path)

        # -----------------------------
        # 2. STORE IN RAG
        # -----------------------------
        process_document(old_text, "old_regulation")
        process_document(new_text, "new_regulation")
        process_document(policy_text, "internal_policy")

        # -----------------------------
        # 3. RETRIEVE CONTEXT
        # -----------------------------
        old_context = build_context(
            retrieve_with_metadata("key regulatory clauses", "old_regulation")
        )

        new_context = build_context(
            retrieve_with_metadata("latest regulatory changes", "new_regulation")
        )

        policy_context = build_context(
            retrieve_with_metadata("internal compliance rules", "internal_policy")
        )

        # -----------------------------
        # 4. AI
        # -----------------------------
        changes = detect_changes(old_context, new_context)

        compliance_gaps = detect_compliance_gaps(new_context, policy_context)

        impact = analyze_impact(
            str(changes) + "\n" + str(compliance_gaps)
        )

        actions = generate_actions(
            str(changes),
            str(impact) + "\n" + str(compliance_gaps)
        )

        result = {
            "changes": changes,
            "compliance_gaps": compliance_gaps,
            "impact": impact,
            "actions": actions
        }

        # ✅ SAVE SUCCESS
        update_task(task_id, status="completed", result=result)

    except Exception as e:
        traceback.print_exc()

        update_task(
            task_id,
            status="failed",
            result={"error": str(e)}
        )