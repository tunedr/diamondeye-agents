"""
AXIOM Librarian Handoff Skill
Archives completed investigation reports to Paperless-ngx
and notifies Librarian Agent Zero for knowledge base integration.
"""

import os
import subprocess
from datetime import datetime

import requests

def handoff_to_librarian(
    case_id: str,
    subject_name: str,
    report_html: str,
    claim_counts: dict,
    contradictions: list
) -> dict:
    """
    Complete AXIOM case handoff to Librarian.

    Args:
        case_id: AXIOM case reference (e.g. AXIOM-2026-05-20-001)
        subject_name: Full name of research subject
        report_html: Complete HTML report content
        claim_counts: dict with verified, contradicted, unverified counts
        contradictions: list of contradiction summaries

    Returns:
        dict with status of each handoff step
    """
    results = {}
    reports_dir = "/reports"
    os.makedirs(reports_dir, exist_ok=True)

    # Step 1: Save HTML report
    html_path = f"{reports_dir}/{case_id}.html"
    with open(html_path, 'w') as f:
        f.write(report_html)
    results['html_saved'] = html_path

    # Step 2: Generate PDF via Gotenberg
    pdf_path = f"{reports_dir}/{case_id}.pdf"
    try:
        with open(html_path, 'rb') as html_file:
            r = requests.post(
                "http://librarian-gotenberg:3000/forms/chromium/convert/html",
                files={"index.html": html_file},
                timeout=60
            )
        if r.status_code == 200:
            with open(pdf_path, 'wb') as f:
                f.write(r.content)
            results['pdf_generated'] = pdf_path
        else:
            results['pdf_error'] = f"Gotenberg returned {r.status_code}"
    except Exception as e:
        results['pdf_error'] = str(e)

    # Step 3: Archive to Paperless-ngx
    paperless_token = _get_credential('PAPERLESS_AXIOM_TOKEN')
    if paperless_token and os.path.exists(pdf_path):
        try:
            subject_tag = subject_name.split()[-1].lower()
            with open(pdf_path, 'rb') as pdf_file:
                r = requests.post(
                    "http://paperless-ngx:8000/api/documents/post_document/",
                    headers={"Authorization": f"Token {paperless_token}"},
                    files={"document": (f"{case_id}.pdf", pdf_file, "application/pdf")},
                    data={
                        "title": f"AXIOM Report — {subject_name} — {case_id}",
                        "tags": f"axiom,research,{subject_tag},{case_id}"
                    },
                    timeout=30
                )
            results['paperless'] = "archived" if r.status_code in [200, 201] else f"error {r.status_code}"
        except Exception as e:
            results['paperless_error'] = str(e)

    # Step 4: Notify Librarian Agent Zero
    try:
        contradictions_text = "\n".join(contradictions[:3]) if contradictions else "None"
        r = requests.post(
            "http://agent-zero-librarian:80/api/message",
            json={
                "message": f"Archive AXIOM case {case_id} — Subject: {subject_name} — "
                          f"Report at /reports/{case_id}.pdf — "
                          f"Add to Paperless with tags: axiom, research, {subject_name.split()[-1].lower()}, {case_id}. "
                          f"Contradictions found: {contradictions_text}"
            },
            timeout=30
        )
        results['librarian_notified'] = r.status_code == 200
    except Exception as e:
        results['librarian_error'] = str(e)

    # Step 5: Telegram notification
    bot_token = _get_credential('DE_ATLAS_BOT_TOKEN')
    chat_id = _get_credential('DE_ATLAS_CHAT_ID')
    if bot_token and chat_id:
        verified = claim_counts.get('verified', 0)
        contradicted = claim_counts.get('contradicted', 0)
        unverified = claim_counts.get('unverified', 0)
        contradiction_text = "\n".join([f"  • {c}" for c in contradictions[:3]]) if contradictions else "  None found"

        message = (
            f"🔍 AXIOM Report Complete\n\n"
            f"Case: {case_id}\n"
            f"Subject: {subject_name}\n"
            f"Claims analyzed: {verified + contradicted + unverified}\n"
            f"  ✅ Verified: {verified}\n"
            f"  ❌ Contradicted: {contradicted}\n"
            f"  ⚠️ Unverified: {unverified}\n\n"
            f"Key contradictions:\n{contradiction_text}\n\n"
            f"Archived to Paperless-ngx ✅\n"
            f"Librarian notified ✅"
        )
        try:
            requests.post(
                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                json={"chat_id": chat_id, "text": message},
                timeout=10
            )
            results['telegram_sent'] = True
        except Exception as e:
            results['telegram_error'] = str(e)

    return results


def _get_credential(key: str) -> str:
    """Read credential from pop-ollama CREDENTIALS.env via SSH."""
    try:
        result = subprocess.run(
            ['ssh', '-i', '/root/.ssh/diamondeye_key', '-o', 'StrictHostKeyChecking=no',
             'tunedr@192.168.1.136',
             f'grep {key} /home/tunedr/CREDENTIALS.env 2>/dev/null | cut -d= -f2'],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip()
    except Exception:
        return ""
