from __future__ import annotations

import json
from html import escape
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


TEAL = colors.HexColor("#0F766E")
INK = colors.HexColor("#111827")
SLATE = colors.HexColor("#475569")
BORDER = colors.HexColor("#D9E0E4")
SURFACE = colors.HexColor("#F8FAFC")
AMBER = colors.HexColor("#A16207")
RED = colors.HexColor("#B91C1C")


def _text(value: object) -> str:
    return escape(str(value if value not in (None, "") else "Not recorded"))


def _json_block(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, default=str)


def render_evidence_markdown(pack: dict) -> str:
    risk = pack.get("risk") or {}
    policy = pack.get("policy") or {}
    lines = [
        "# AI Decision Audit Evidence Pack",
        "",
        f"- Evidence ID: `{pack['evidence_pack_id']}`",
        f"- Run ID: `{pack['run_id']}`",
        f"- Generated at: `{pack['generated_at']}`",
        f"- User: `{pack.get('user_id') or 'Not recorded'}`",
        f"- Policy version: `{pack.get('policy_version') or 'Not recorded'}`",
        f"- Policy decision: `{policy.get('decision') or 'Not recorded'}`",
        f"- Risk: `{risk.get('score', 0)}/100 ({risk.get('level', 'unknown')})`",
        "",
        "## Question",
        "",
        pack.get("question") or "Not recorded",
        "",
        "## Final Answer",
        "",
        pack.get("final_answer") or "Not recorded",
        "",
        "## Risk Factors",
        "",
    ]
    factors = risk.get("factors", [])
    lines.extend([f"- `{item['code']}` (+{item['weight']}): {item['label']}" for item in factors] or ["- No elevated factors recorded."])
    lines.extend(["", "## Retrieved Citations", ""])
    for citation in pack.get("citations", []):
        lines.extend(
            [
                f"### {citation.get('title', 'Untitled source')}",
                "",
                f"Document `{citation.get('document_id')}`, chunk `{citation.get('chunk_id')}`, score `{citation.get('score')}`",
                "",
                citation.get("content") or "No content recorded.",
                "",
            ]
        )
    if not pack.get("citations"):
        lines.extend(["No citations were recorded.", ""])
    for title, key in (
        ("Tool Calls", "tool_calls"),
        ("Approvals", "approvals"),
        ("Approval Decisions", "approval_decisions"),
        ("Audit Timeline", "audit"),
    ):
        lines.extend([f"## {title}", "", "```json", _json_block(pack.get(key, [])), "```", ""])
    lines.extend(
        [
            "## Integrity and Redaction",
            "",
            f"- Schema: `{pack.get('schema_version')}`",
            f"- PII redaction: `{pack.get('redaction', {}).get('status', 'unknown')}`",
            f"- Started at: `{pack.get('timestamps', {}).get('started_at')}`",
            f"- Completed at: `{pack.get('timestamps', {}).get('completed_at')}`",
            "",
        ]
    )
    return "\n".join(lines)


def render_evidence_pdf(pack: dict) -> bytes:
    buffer = BytesIO()
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="EvidenceTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=20, leading=24, textColor=INK, spaceAfter=4))
    styles.add(ParagraphStyle(name="EvidenceSubtitle", parent=styles["Normal"], fontSize=9, leading=13, textColor=SLATE))
    styles.add(ParagraphStyle(name="Section", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=INK, spaceBefore=11, spaceAfter=6))
    styles.add(ParagraphStyle(name="BodySmall", parent=styles["BodyText"], fontSize=8.5, leading=12, textColor=SLATE))
    styles.add(ParagraphStyle(name="Cell", parent=styles["BodyText"], fontSize=7.5, leading=10, textColor=INK))
    styles.add(ParagraphStyle(name="CellMuted", parent=styles["BodyText"], fontSize=7, leading=9, textColor=SLATE))
    styles.add(ParagraphStyle(name="Footer", parent=styles["Normal"], fontSize=7, textColor=SLATE, alignment=TA_RIGHT))

    def footer(canvas, document):
        canvas.saveState()
        canvas.setStrokeColor(BORDER)
        canvas.line(18 * mm, 13 * mm, A4[0] - 18 * mm, 13 * mm)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(SLATE)
        canvas.drawString(18 * mm, 8 * mm, f"Evidence pack {pack['evidence_pack_id']}")
        canvas.drawRightString(A4[0] - 18 * mm, 8 * mm, f"Page {document.page}")
        canvas.restoreState()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=f"Audit Evidence Pack - {pack['run_id']}",
        author="Regulated AI Agent Platform",
    )
    story = []
    story.append(Paragraph("AI Decision Audit Evidence Pack", styles["EvidenceTitle"]))
    story.append(Paragraph(f"Regulated AI Agent Platform / {_text(pack['run_id'])}", styles["EvidenceSubtitle"]))
    story.append(Spacer(1, 8))

    risk = pack.get("risk") or {}
    policy = pack.get("policy") or {}
    summary = Table(
        [
            ["POLICY DECISION", "RISK", "POLICY VERSION", "USER"],
            [
                Paragraph(_text(policy.get("decision")), styles["Cell"]),
                Paragraph(f"{risk.get('score', 0)}/100 - {_text(risk.get('level'))}", styles["Cell"]),
                Paragraph(_text(pack.get("policy_version")), styles["Cell"]),
                Paragraph(_text(pack.get("user_id")), styles["Cell"]),
            ],
        ],
        colWidths=[42 * mm, 35 * mm, 53 * mm, 43 * mm],
    )
    summary.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), SURFACE),
                ("TEXTCOLOR", (0, 0), (-1, 0), SLATE),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 6.5),
                ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
                ("BOX", (0, 0), (-1, -1), 0.8, TEAL),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    story.append(summary)

    def section(title: str, body: object):
        story.append(Paragraph(title, styles["Section"]))
        story.append(Paragraph(_text(body), styles["BodySmall"]))

    section("Question", pack.get("question"))
    section("Final Answer", pack.get("final_answer"))

    factors = risk.get("factors", [])
    story.append(Paragraph("Risk Assessment", styles["Section"]))
    risk_rows = [["Factor", "Weight", "Rationale"]]
    for item in factors:
        risk_rows.append(
            [
                Paragraph(_text(item.get("code")), styles["Cell"]),
                Paragraph(f"+{item.get('weight', 0)}", styles["Cell"]),
                Paragraph(_text(item.get("label")), styles["CellMuted"]),
            ]
        )
    if not factors:
        risk_rows.append([Paragraph("none", styles["Cell"]), Paragraph("+0", styles["Cell"]), Paragraph("No elevated factors recorded.", styles["CellMuted"])])
    risk_table = Table(risk_rows, colWidths=[44 * mm, 22 * mm, 107 * mm], repeatRows=1)
    risk_table.setStyle(_table_style())
    story.append(risk_table)

    story.append(Paragraph("Retrieved Evidence", styles["Section"]))
    citations = pack.get("citations", [])
    if citations:
        for citation in citations:
            story.append(
                KeepTogether(
                    [
                        Paragraph(_text(citation.get("title", "Untitled source")), styles["Cell"]),
                        Paragraph(
                            f"Document {_text(citation.get('document_id'))} / chunk {_text(citation.get('chunk_id'))} / score {_text(citation.get('score'))}",
                            styles["CellMuted"],
                        ),
                        Spacer(1, 3),
                        Paragraph(_text(citation.get("content")), styles["BodySmall"]),
                        Spacer(1, 8),
                    ]
                )
            )
    else:
        story.append(Paragraph("No citations were recorded for this run.", styles["BodySmall"]))

    story.append(Paragraph("Tool Calls", styles["Section"]))
    tool_calls = pack.get("tool_calls", [])
    if tool_calls:
        tool_rows = [["Decision", "Summary", "Scope and Payload"]]
        for entry in tool_calls:
            metadata = entry.get("metadata", {})
            tool_rows.append(
                [
                    Paragraph(_text(entry.get("decision")), styles["Cell"]),
                    Paragraph(_text(entry.get("summary")), styles["CellMuted"]),
                    Paragraph(
                        f"Scope: {_text(metadata.get('scope'))}<br/>Payload: {_text(_json_block(metadata.get('payload', {})))}",
                        styles["CellMuted"],
                    ),
                ]
            )
        tool_table = Table(tool_rows, colWidths=[31 * mm, 61 * mm, 81 * mm], repeatRows=1)
        tool_table.setStyle(_table_style())
        story.append(tool_table)
    else:
        story.append(Paragraph("No tool calls were recorded.", styles["BodySmall"]))

    story.append(Paragraph("Approvals and Decisions", styles["Section"]))
    approval_decisions = pack.get("approval_decisions", [])
    if approval_decisions:
        approval_rows = [["Operator", "Decision", "Comment", "Timestamp"]]
        for entry in approval_decisions:
            approval_rows.append(
                [
                    Paragraph(_text(entry.get("user_id")), styles["Cell"]),
                    Paragraph(_text(entry.get("decision")), styles["Cell"]),
                    Paragraph(_text(entry.get("metadata", {}).get("comment")), styles["CellMuted"]),
                    Paragraph(_text(entry.get("created_at")), styles["CellMuted"]),
                ]
            )
        approval_table = Table(approval_rows, colWidths=[40 * mm, 29 * mm, 62 * mm, 42 * mm], repeatRows=1)
        approval_table.setStyle(_table_style())
        story.append(approval_table)
    else:
        story.append(Paragraph("No approvals and decisions were recorded.", styles["BodySmall"]))

    story.append(PageBreak())
    story.append(Paragraph("Audit Timeline", styles["Section"]))
    audit_rows = [["Timestamp", "Event", "Decision", "Summary"]]
    for event in pack.get("audit", []):
        audit_rows.append(
            [
                Paragraph(_text(event.get("created_at")), styles["CellMuted"]),
                Paragraph(_text(event.get("event_type")), styles["Cell"]),
                Paragraph(_text(event.get("decision")), styles["Cell"]),
                Paragraph(_text(event.get("summary")), styles["CellMuted"]),
            ]
        )
    audit_table = Table(audit_rows, colWidths=[35 * mm, 34 * mm, 28 * mm, 76 * mm], repeatRows=1)
    audit_table.setStyle(_table_style())
    story.append(audit_table)
    story.append(Spacer(1, 10))
    story.append(Paragraph("Integrity and Redaction", styles["Section"]))
    story.append(
        Paragraph(
            f"Schema {_text(pack.get('schema_version'))}. PII redaction status: {_text(pack.get('redaction', {}).get('status'))}. "
            f"Run window: {_text(pack.get('timestamps', {}).get('started_at'))} to {_text(pack.get('timestamps', {}).get('completed_at'))}. "
            f"Generated at {_text(pack.get('generated_at'))}.",
            styles["BodySmall"],
        )
    )

    document.build(story, onFirstPage=footer, onLaterPages=footer)
    return buffer.getvalue()


def _table_style() -> TableStyle:
    return TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), SURFACE),
            ("TEXTCOLOR", (0, 0), (-1, 0), SLATE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 6.5),
            ("GRID", (0, 0), (-1, -1), 0.45, BORDER),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]
    )
