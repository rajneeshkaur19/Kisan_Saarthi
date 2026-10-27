import os
import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.schemas import (
    EligibilityRequest, EligibilityData, ReadinessScore, EligibleScheme,
    ChecklistRequest, ChecklistData, DocumentItem
)
from backend.app.db.models import EligibilityAssessment
from backend.app.utils.pdf_generator import generate_checklist_pdf

class EligibilityService:
    def __init__(self):
        self._load_data()

    def _load_data(self):
        schemes_path = os.path.join(settings.DATA_DIR, "schemes.json")
        rules_path = os.path.join(settings.DATA_DIR, "eligibility_rules.json")
        checklists_path = os.path.join(settings.DATA_DIR, "document_checklists.json")

        with open(schemes_path, "r", encoding="utf-8") as f:
            self.schemes = json.load(f)
        with open(rules_path, "r", encoding="utf-8") as f:
            self.rules = json.load(f)
        with open(checklists_path, "r", encoding="utf-8") as f:
            self.checklists = json.load(f)

    def calculate_readiness_score(self, req: EligibilityRequest) -> ReadinessScore:
        # 1. Land Documentation Score (0-25)
        land_score = 0
        if req.land_holding_acres > 0:
            land_score = 20
            if req.land_holding_acres >= 2.0:
                land_score = 25
        else:
            land_score = 5  # Landless / Tenant farmer baseline

        # 2. Banking & DBT (0-25)
        bank_score = 0
        if req.bank_account_status == "aadhaar_linked_dbt":
            bank_score = 25
        elif req.bank_account_status == "bank_account_no_dbt":
            bank_score = 15
        else:
            bank_score = 5

        # 3. Credit Track Record (0-25)
        credit_score = 0
        if req.existing_loan_status == "active_kcc_loan_good_standing":
            credit_score = 25
        elif req.existing_loan_status == "no_active_loan":
            credit_score = 22
        elif req.existing_loan_status == "active_formal_loan":
            credit_score = 18
        else:
            credit_score = 10

        # 4. Income to scale ratio (0-25)
        income_score = 20
        if req.annual_income in ["1 - 3 lakh", "3 - 6 lakh"]:
            income_score = 25
        elif req.annual_income == "> 6 lakh":
            income_score = 22
        else:
            income_score = 18

        total_score = min(100, land_score + bank_score + credit_score + income_score)

        # Classify Tier
        tiers = self.rules.get("readiness_tiers", [])
        chosen_tier = None
        for t in tiers:
            if t["min_score"] <= total_score <= t["max_score"]:
                chosen_tier = t
                break
        if not chosen_tier:
            chosen_tier = tiers[-1]

        summary_lang = chosen_tier["summary"].get(req.language,
                       chosen_tier["summary"].get("en", ""))

        # Actionable tips
        tips = []
        if bank_score < 25:
            if req.language == "hi":
                tips.append("अपने बैंक खाते में आधार लिंक और डीबीटी (DBT) सक्रिय कराएं।")
            elif req.language == "pa":
                tips.append("ਆਪਣੇ ਬੈਂਕ ਖਾਤੇ ਵਿੱਚ ਆਧਾਰ ਕਾਰਡ ਅਤੇ ਡੀਬੀਟੀ ਚਾਲੂ ਕਰਵਾਓ।")
            else:
                tips.append("Link Aadhaar with NPCI mapper at your bank branch to enable instant DBT payments.")

        if req.existing_loan_status == "informal_debt":
            if req.language == "hi":
                tips.append("साहूकारी कर्ज के बजाय 4% ब्याज दर वाले संस्थागत KCC ऋण के लिए आवेदन करें।")
            elif req.language == "pa":
                tips.append("ਸ਼ਾਹੂਕਾਰਾਂ ਦੇ ਕਰਜ਼ੇ ਦੀ ਥਾਂ 4% ਸਸਤੀ ਵਿਆਜ ਵਾਲੇ ਕੇਸੀਸੀ ਕਾਰਡ ਲਈ ਅਪਲਾਈ ਕਰੋ।")
            else:
                tips.append("Refinance informal high-interest borrowing with institutional 4% KCC crop financing.")

        if req.land_holding_acres > 0 and land_score < 25:
            tips.append("Keep digital revenue records (Khasra-Khatauni) certified and up-to-date.")

        if not tips:
            tips.append("All primary documentation criteria are well-aligned for fast-track processing.")

        return ReadinessScore(
            score=total_score,
            label=chosen_tier["label"],
            badge_color=chosen_tier["badge_color"],
            summary=summary_lang,
            breakdown={
                "land_documentation": land_score,
                "banking_dbt": bank_score,
                "credit_track": credit_score,
                "income_stability": income_score
            },
            improvement_tips=tips
        )

    def evaluate_eligibility(
        self,
        req: EligibilityRequest,
        db: Optional[Session] = None
    ) -> EligibilityData:
        readiness = self.calculate_readiness_score(req)
        scheme_rules = self.rules.get("scheme_rules", {})

        recommended = []
        other = []

        for s in self.schemes:
            sid = s["id"]
            rule = scheme_rules.get(sid, {})
            is_eligible = True
            reason = ""

            # Check land requirement
            if rule.get("requires_land_ownership", False) and req.land_holding_acres <= 0:
                is_eligible = False
                reason = "Requires ownership of cultivable land."

            # Check crops if specified
            if is_eligible and "eligible_crops" in rule:
                if req.primary_crop not in rule["eligible_crops"]:
                    is_eligible = False
                    reason = f"Current notification prioritizes crops like {', '.join(rule['eligible_crops'][:4])}."

            # Reason text localized
            if is_eligible:
                match_dict = rule.get("match_reason", {})
                reason = match_dict.get(req.language, match_dict.get("en", "You satisfy official eligibility parameters."))

            # Scheme names localized
            s_names = s.get("names", {})
            localized_name = s_names.get(req.language, s.get("name"))

            scheme_item = EligibleScheme(
                id=s["id"],
                code=s["code"],
                name=localized_name,
                short_name=s.get("short_name", s["name"]),
                category=s.get("category", "Agriculture"),
                financial_benefit=s.get("financial_benefit", ""),
                is_eligible=is_eligible,
                match_reason=reason,
                required_documents=s.get("required_documents", []),
                portal=s.get("official_portal", "")
            )

            if is_eligible:
                recommended.append(scheme_item)
            else:
                other.append(scheme_item)

        # Audit persistence
        if db is not None:
            try:
                audit = EligibilityAssessment(
                    land_acres=req.land_holding_acres,
                    income_bracket=req.annual_income,
                    primary_crop=req.primary_crop,
                    score=readiness.score,
                    readiness_label=readiness.label,
                    language=req.language
                )
                db.add(audit)
                db.commit()
            except Exception as e:
                db.rollback()
                print(f"[EligibilityAudit] Error: {e}")

        disclaimer = (
            "Disclaimer: The readiness score and scheme recommendations represent automated guidance "
            "based on official central and state guidelines. Actual loan sanction and subsidy disbursements "
            "are determined by respective banks and departmental authorities following document scrutiny."
        )

        return EligibilityData(
            readiness_score=readiness,
            recommended_schemes=recommended,
            other_schemes=other,
            official_disclaimer=disclaimer
        )

    def get_document_checklist(self, req: ChecklistRequest) -> ChecklistData:
        cid = req.scheme_id.upper()
        # Fallback to PM-KISAN if not found
        checklist_info = self.checklists.get(cid)
        if not checklist_info:
            cid = "PM-KISAN"
            checklist_info = self.checklists.get(cid, {})

        docs = [
            DocumentItem(
                id=d.get("id", f"doc_{i}"),
                name=d.get("name", ""),
                description=d.get("description", ""),
                mandatory=d.get("mandatory", True)
            )
            for i, d in enumerate(checklist_info.get("required_documents", []))
        ]

        steps = checklist_info.get("submission_steps", [])

        # Printable plain text format
        printable_lines = [
            f"=== {checklist_info.get('title', 'Scheme Checklist')} ===",
            f"Official Portal: {checklist_info.get('portal', 'N/A')}",
            f"Helpline: {checklist_info.get('official_helpline', 'N/A')}",
            "\n--- Required Documents ---"
        ]
        for idx, doc in enumerate(docs, 1):
            m_tag = "[MANDATORY]" if doc.mandatory else "[OPTIONAL]"
            printable_lines.append(f"{idx}. {doc.name} {m_tag}\n   Details: {doc.description}")

        printable_lines.append("\n--- Submission Steps ---")
        for step in steps:
            printable_lines.append(f"{step}")

        printable_lines.append("\nDisclaimer: Guidance only. Verification rests with competent authorities.")
        printable_text = "\n".join(printable_lines)

        pdf_base64 = None
        if req.include_pdf_base64:
            try:
                pdf_base64 = generate_checklist_pdf(checklist_info,
                                                    farmer_name=req.farmer_name or "Farmer")
            except Exception as e:
                print(f"[PDFGenerator] Error generating base64 PDF: {e}")

        return ChecklistData(
            scheme_id=cid,
            scheme_name=checklist_info.get("scheme_name", cid),
            title=checklist_info.get("title", f"{cid} Checklist"),
            portal=checklist_info.get("portal", ""),
            official_helpline=checklist_info.get("official_helpline", ""),
            required_documents=docs,
            submission_steps=steps,
            pdf_base64=pdf_base64,
            printable_text=printable_text
        )

_eligibility_service = None

def get_eligibility_service() -> EligibilityService:
    global _eligibility_service
    if _eligibility_service is None:
        _eligibility_service = EligibilityService()
    return _eligibility_service

def evaluate_eligibility(req, db=None):
    """Compatibility wrapper used by the eligibility API router."""
    return get_eligibility_service().evaluate_eligibility(req, db=db)
