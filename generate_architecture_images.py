"""
Generate architecture diagram images for GeoSupply Copilot.
Produces two PNG files in the project root:
  - architecture_system.png   (system architecture overview)
  - architecture_dataflow.png (data-flow diagram for Q&A)
"""

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ── Colour palette ──────────────────────────────────────────────────
C_BG        = "#F8FAFC"
C_USER      = "#DBEAFE"
C_USER_BD   = "#3B82F6"
C_SERVER    = "#FEF3C7"
C_SERVER_BD = "#F59E0B"
C_DATA      = "#D1FAE5"
C_DATA_BD   = "#10B981"
C_AI        = "#EDE9FE"
C_AI_BD     = "#8B5CF6"
C_VALID     = "#FFE4E6"
C_VALID_BD  = "#F43F5E"
C_WHITE     = "#FFFFFF"
C_TEXT      = "#1E293B"
C_GRAY      = "#64748B"
C_ARROW     = "#475569"


def _box(ax, x, y, w, h, label, sublabel=None, fc=C_WHITE, ec="#CBD5E1", lw=1.5, fs=10, sub_fs=8):
    """Draw a rounded box with a bold title and optional subtitle."""
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.02",
        facecolor=fc, edgecolor=ec, linewidth=lw,
        transform=ax.transData, zorder=2,
    )
    ax.add_patch(box)
    if sublabel:
        ax.text(x + w / 2, y + h / 2 + 0.018, label,
                ha="center", va="center", fontsize=fs, fontweight="bold", color=C_TEXT, zorder=3)
        ax.text(x + w / 2, y + h / 2 - 0.022, sublabel,
                ha="center", va="center", fontsize=sub_fs, color=C_GRAY, zorder=3, style="italic")
    else:
        ax.text(x + w / 2, y + h / 2, label,
                ha="center", va="center", fontsize=fs, fontweight="bold", color=C_TEXT, zorder=3)
    return box


def _section(ax, x, y, w, h, title, fc, ec, lw=2, fs=11):
    """Draw a coloured section rectangle with a title at the top-left."""
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.01",
        facecolor=fc, edgecolor=ec, linewidth=lw,
        transform=ax.transData, zorder=1,
    )
    ax.add_patch(box)
    ax.text(x + 0.015, y + h - 0.025, title,
            ha="left", va="top", fontsize=fs, fontweight="bold", color=ec, zorder=3)


def _arrow(ax, x1, y1, x2, y2, label=None, color=C_ARROW):
    """Draw a straight arrow between two points with optional label."""
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle="-|>", color=color, lw=2),
        zorder=4,
    )
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mx + 0.01, my, label, fontsize=8, color=C_GRAY, va="center", zorder=5)


def _bullet_box(ax, x, y, w, h, title, bullets, fc=C_WHITE, ec="#CBD5E1"):
    """Draw a box with a title and bullet-point list."""
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.015",
        facecolor=fc, edgecolor=ec, linewidth=1.5,
        transform=ax.transData, zorder=2,
    )
    ax.add_patch(box)
    ax.text(x + w / 2, y + h - 0.022, title,
            ha="center", va="top", fontsize=9.5, fontweight="bold", color=C_TEXT, zorder=3)
    for i, bullet in enumerate(bullets):
        ax.text(x + 0.015, y + h - 0.050 - i * 0.028, f"• {bullet}",
                ha="left", va="top", fontsize=7.5, color=C_GRAY, zorder=3)


# ════════════════════════════════════════════════════════════════════
# DIAGRAM 1: System Architecture
# ════════════════════════════════════════════════════════════════════

def draw_system_architecture(outpath: str):
    fig, ax = plt.subplots(figsize=(16, 11))
    fig.patch.set_facecolor(C_BG)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_aspect("equal")

    # Title
    ax.text(0.50, 0.97, "GeoSupply Copilot — System Architecture",
            ha="center", va="top", fontsize=18, fontweight="bold", color=C_TEXT)
    ax.text(0.50, 0.945, "High-level overview for non-technical audiences",
            ha="center", va="top", fontsize=10, color=C_GRAY, style="italic")

    # ── USER LAYER ──────────────────────────────────────────────────
    _section(ax, 0.04, 0.74, 0.92, 0.18, "USER LAYER  —  Web Browser", C_USER, C_USER_BD)
    dashboard_items = [
        ("Trade-Block\nScenario", 0.07),
        ("Shipment\nHealth", 0.23),
        ("Risk\nAlerts", 0.39),
        ("Alternate\nSourcing", 0.55),
        ("Q&A\nChat", 0.71),
        ("Drill-Down\nDetails", 0.87),
    ]
    for label, bx in dashboard_items:
        _box(ax, bx, 0.775, 0.12, 0.09, label, fc=C_WHITE, ec=C_USER_BD, fs=8.5)

    # Arrow down
    _arrow(ax, 0.50, 0.74, 0.50, 0.69, "User opens page / asks a question")

    # ── APPLICATION SERVER ──────────────────────────────────────────
    _section(ax, 0.04, 0.30, 0.92, 0.38, "APPLICATION SERVER  —  Python (Flask)", C_SERVER, C_SERVER_BD)

    _bullet_box(ax, 0.07, 0.48, 0.20, 0.16, "Risk Detection",
                ["Scans news for trade-", "block events", "Flags at-risk shipments", "Assigns severity"],
                fc=C_WHITE, ec=C_SERVER_BD)

    _bullet_box(ax, 0.30, 0.48, 0.20, 0.16, "Alternative Sourcing",
                ["Finds safe suppliers", "outside blocked countries", "Ranks by performance"],
                fc=C_WHITE, ec=C_SERVER_BD)

    _bullet_box(ax, 0.53, 0.48, 0.20, 0.16, "RAG Pipeline",
                ["Turns data into search-", "able documents", "Finds relevant snippets", "Feeds context to AI"],
                fc=C_WHITE, ec=C_SERVER_BD)

    _bullet_box(ax, 0.76, 0.48, 0.17, 0.16, "Smart Q&A",
                ["Primary: AI answers", "grounded in data", "Fallback: built-in", "rule engine"],
                fc=C_WHITE, ec=C_SERVER_BD)

    # Validation bar
    _box(ax, 0.07, 0.34, 0.86, 0.10,
         "Safety & Validation Layer",
         sublabel="Checks AI answers against real data  •  Verifies IDs  •  Falls back if needed",
         fc=C_VALID, ec=C_VALID_BD, fs=10)

    # Arrows down
    _arrow(ax, 0.30, 0.30, 0.30, 0.24, "reads")
    _arrow(ax, 0.70, 0.30, 0.70, 0.24, "calls")

    # ── DATA LAYER ──────────────────────────────────────────────────
    _section(ax, 0.04, 0.04, 0.44, 0.19, "DATA LAYER  —  JSON Files", C_DATA, C_DATA_BD)
    data_items = [("News", 0.065), ("Suppliers", 0.19), ("Shipments", 0.315), ("Performance", 0.44)]
    for label, bx in data_items:
        _box(ax, bx - 0.01, 0.06, 0.115, 0.07, label, fc=C_WHITE, ec=C_DATA_BD, fs=8)

    # ── AI LAYER ────────────────────────────────────────────────────
    _section(ax, 0.52, 0.04, 0.44, 0.19, "AI LAYER  —  Optional", C_AI, C_AI_BD)
    _box(ax, 0.55, 0.06, 0.38, 0.12,
         "Any OpenAI-Compatible LLM",
         sublabel="Ollama  •  LM Studio  •  Cloud endpoint  •  Swap via env vars",
         fc=C_WHITE, ec=C_AI_BD, fs=9.5)

    fig.savefig(outpath, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)
    print(f"✅ Saved {outpath}")


# ════════════════════════════════════════════════════════════════════
# DIAGRAM 2: Data Flow (Q&A)
# ════════════════════════════════════════════════════════════════════

def draw_dataflow(outpath: str):
    fig, ax = plt.subplots(figsize=(15, 10))
    fig.patch.set_facecolor(C_BG)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_aspect("equal")

    ax.text(0.50, 0.97, "GeoSupply Copilot — Q&A Data Flow",
            ha="center", va="top", fontsize=18, fontweight="bold", color=C_TEXT)
    ax.text(0.50, 0.945, "What happens when a user asks a question",
            ha="center", va="top", fontsize=10, color=C_GRAY, style="italic")

    # Numbered steps running top-to-bottom (left column) with AI on the right
    step_data = [
        ("① User asks a question", 'e.g. "Which supplier has\nthe most delays?"', 0.84),
        ("② Build knowledge base", "Convert all supply-chain\ndata into searchable text", 0.71),
        ("③ Find relevant snippets", "RAG search identifies the\nmost useful data for this question", 0.58),
        ("④ Send question + context\n     to the AI model", "", 0.45),
        ("⑥ Validate the answer", "Check every ID and fact\nagainst real data", 0.32),
        ("⑦ Return verified answer\n     + data sources to user", "", 0.19),
    ]

    step_x = 0.08
    step_w = 0.38
    step_h = 0.085

    for title, sub, sy in step_data:
        _box(ax, step_x, sy, step_w, step_h, title, sublabel=sub if sub else None,
             fc=C_SERVER, ec=C_SERVER_BD, fs=9, sub_fs=7.5)

    # Arrows between steps
    for i in range(len(step_data) - 1):
        y_from = step_data[i][2]
        y_to = step_data[i + 1][2] + step_h
        ax.annotate("", xy=(step_x + step_w / 2, y_to),
                     xytext=(step_x + step_w / 2, y_from),
                     arrowprops=dict(arrowstyle="-|>", color=C_ARROW, lw=1.8), zorder=4)

    # AI Model box (right side)
    ai_y = 0.40
    ai_x = 0.58
    ai_w = 0.34
    ai_h = 0.20
    _section(ax, ai_x, ai_y, ai_w, ai_h, "AI Model (any LLM)", C_AI, C_AI_BD, fs=10)
    _box(ax, ai_x + 0.03, ai_y + 0.025, ai_w - 0.06, 0.10,
         "⑤ Generate answer",
         sublabel="Uses only the provided context\nto produce a grounded response",
         fc=C_WHITE, ec=C_AI_BD, fs=9, sub_fs=7.5)

    # Arrow from step ④ to AI
    _arrow(ax, step_x + step_w, 0.45 + step_h / 2, ai_x, ai_y + ai_h / 2, "question\n+ context")
    # Arrow from AI back to step ⑥
    _arrow(ax, ai_x, ai_y + 0.02, step_x + step_w, 0.32 + step_h / 2, "AI answer")

    # Fallback box
    fb_x, fb_y, fb_w, fb_h = 0.58, 0.12, 0.34, 0.14
    _section(ax, fb_x, fb_y, fb_w, fb_h, "Fallback Path", C_VALID, C_VALID_BD, fs=10)
    _box(ax, fb_x + 0.03, fb_y + 0.02, fb_w - 0.06, 0.07,
         "Built-in Rule Engine",
         sublabel="Used if AI is unavailable or answer fails validation",
         fc=C_WHITE, ec=C_VALID_BD, fs=9, sub_fs=7.5)

    # Dashed arrow from validate to fallback
    ax.annotate("", xy=(fb_x, fb_y + fb_h / 2),
                xytext=(step_x + step_w, 0.32 + step_h / 2),
                arrowprops=dict(arrowstyle="-|>", color=C_VALID_BD, lw=1.5, linestyle="dashed"), zorder=4)
    ax.text(0.52, 0.34, "if bad\nanswer", fontsize=7, color=C_VALID_BD, ha="center", va="center", style="italic")

    # Data layer at bottom
    _section(ax, 0.08, 0.02, 0.84, 0.08, "Data Layer — JSON Files", C_DATA, C_DATA_BD, fs=9)
    for i, label in enumerate(["News", "Suppliers", "Shipments", "Performance"]):
        _box(ax, 0.11 + i * 0.20, 0.03, 0.16, 0.045, label, fc=C_WHITE, ec=C_DATA_BD, fs=8)

    # Arrow from data to step ②
    ax.annotate("", xy=(step_x + step_w / 2, 0.71),
                xytext=(step_x + step_w / 2, 0.10),
                arrowprops=dict(arrowstyle="-|>", color=C_DATA_BD, lw=1.5, linestyle="dotted"), zorder=0)
    ax.text(0.06, 0.50, "reads\ndata", fontsize=7, color=C_DATA_BD, ha="center", va="center", rotation=90)

    fig.savefig(outpath, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)
    print(f"✅ Saved {outpath}")


if __name__ == "__main__":
    import pathlib
    base = pathlib.Path(__file__).resolve().parent
    draw_system_architecture(str(base / "architecture_system.png"))
    draw_dataflow(str(base / "architecture_dataflow.png"))
    print("\nDone — two images generated.")
