import base64
import io
from typing import Any, Dict, Optional

# Attempt to import ReportLab for PDF generation. If unavailable, provide a graceful fallback.
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
except Exception:  # pragma: no cover
    # Minimal stubs when ReportLab is not installed.
    A4 = (595.27, 841.89)  # Approximate A4 size in points.
    class _DummyCanvas:
        def __init__(self, buffer, pagesize=None):
            self.buffer = buffer
        def setFont(self, *args, **kwargs):
            pass
        def drawString(self, *args, **kwargs):
            pass
        def showPage(self):
            pass
        def save(self):
            # Ensure the buffer is empty.
            self.buffer.seek(0)
            self.buffer.truncate()
    def canvas(buffer, pagesize=None):  # type: ignore
        return _DummyCanvas(buffer, pagesize=pagesize)

def generate_checklist_pdf(
    checklist_info: Dict[str, Any],
    farmer_name: str = "Farmer",
) -> str:
    """Generate a printable checklist PDF and return it as a base64 string.

    If the ReportLab library is unavailable, an empty base64 string is returned.
    """
    buffer = io.BytesIO()
    pdf = canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 55

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(45, y, str(checklist_info.get("title", "Scheme Checklist"))[:85])
    y -= 28

    pdf.setFont("Helvetica", 10)
    pdf.drawString(45, y, f"Farmer: {farmer_name}"[:100])
    y -= 22

    for label, key in [
        ("Scheme", "scheme_name"),
        ("Official Portal", "portal"),
        ("Helpline", "official_helpline"),
    ]:
        value = str(checklist_info.get(key, "N/A"))
        pdf.drawString(45, y, f"{label}: {value}"[:110])
        y -= 18

    y -= 10
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(45, y, "Required Documents")
    y -= 22
    pdf.setFont("Helvetica", 10)

    for item in checklist_info.get("required_documents", []):
        name = str(item.get("name", "Document"))
        mandatory = "Mandatory" if item.get("mandatory", True) else "Optional"
        for line in [f"- {name} ({mandatory})", str(item.get("description", ""))]:
            if y < 65:
                pdf.showPage()
                y = height - 55
                pdf.setFont("Helvetica", 10)
            pdf.drawString(50, y, line[:110])
            y -= 15
        y -= 5

    y -= 8
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(45, y, "Submission Steps")
    y -= 22
    pdf.setFont("Helvetica", 10)

    for step in checklist_info.get("submission_steps", []):
        if y < 65:
            pdf.showPage()
            y = height - 55
            pdf.setFont("Helvetica", 10)
        pdf.drawString(50, y, f"- {str(step)}"[:110])
        y -= 17

    pdf.save()
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    buffer.close()
    return encoded
