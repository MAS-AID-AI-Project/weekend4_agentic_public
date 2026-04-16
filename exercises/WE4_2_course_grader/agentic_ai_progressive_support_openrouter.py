from __future__ import annotations

import html
import json
import os
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

try:
    from IPython.display import HTML, Markdown, display
except ImportError:  # pragma: no cover
    class HTML(str):
        pass

    class Markdown(str):
        pass

    def display(*objects: Any) -> None:
        for obj in objects:
            print(obj)

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    def load_dotenv(*_args: Any, **_kwargs: Any) -> bool:
        return False


DATA_DIR = Path("data_agentic_course")

TYPE_LABELS = {
    "factual_in_doc": "Factual",
    "cross_doc": "Cross-doc",
    "numeric_requires_tool": "Numeric",
    "unanswerable": "Abstention",
    "overall": "Overall",
}

TYPE_COLORS = {
    "factual_in_doc": "#0f766e",
    "cross_doc": "#2563eb",
    "numeric_requires_tool": "#7c3aed",
    "unanswerable": "#b45309",
    "overall": "#111827",
}

COURSE_WEIGHTS = {
    "homework": 0.40,
    "midterm": 0.20,
    "final_exam": 0.25,
    "project": 0.15,
}

LETTER_THRESHOLDS = [
    ("A", 93.0),
    ("A-", 90.0),
    ("B+", 87.0),
    ("B", 83.0),
    ("B-", 80.0),
]

STOPWORDS = {
    "the", "a", "an", "and", "or", "to", "of", "for", "in", "on", "at", "is", "are",
    "be", "with", "from", "by", "as", "what", "when", "can", "i", "we", "do", "does",
    "if", "how", "many", "may", "my", "it", "this", "that", "within", "after", "all",
    "only", "under", "into", "must", "should", "who", "which", "about", "their",
    "they", "you", "your", "our", "there", "each", "per",
}

SUPPORT_IGNORE_TOKENS = {
    "apply",
    "applying",
    "available",
    "average",
    "averages",
    "counted",
    "counts",
    "course",
    "days",
    "exact",
    "exactly",
    "exam",
    "final",
    "finish",
    "grade",
    "grades",
    "homework",
    "late",
    "midterm",
    "overall",
    "policies",
    "policy",
    "project",
    "reach",
    "score",
    "scores",
    "student",
    "students",
    "submit",
    "submitted",
    "team",
    "teams",
    "use",
    "using",
    "what",
    "which",
}

MISSING_TERM_IGNORE_TOKENS = {
    "condition",
    "conditions",
    "count",
    "counted",
    "counts",
    "exact",
    "exactly",
    "many",
    "maximum",
    "number",
    "normally",
    "private",
    "receive",
    "receives",
    "score",
    "scores",
    "saved",
    "single",
    "submit",
    "submitted",
    "use",
    "using",
    "where",
}

ABSTAIN_TEXT = (
    "I do not have enough support in the provided documents to answer confidently."
)

BASELINE_SYSTEM_PROMPT = """
You are a helpful assistant.

Rules:
- Answer the user question as best you can from your own knowledge.
- Do not mention missing documents, retrieval, or hidden chain-of-thought.
- Be concise and direct.
""".strip()

GROUNDED_SYSTEM_PROMPT = """
You are a course-policy assistant.

Rules:
- Answer using the provided excerpts and tool results when they are available.
- Do not mention hidden chain-of-thought.
- Be concise and precise.
- When evidence is provided, cite document names in square brackets, e.g. [grading.md].
- For calculator-style questions, state the final numeric result explicitly.
""".strip()

TOOL_SELECTION_SYSTEM_PROMPT = """
You are controlling a notebook assistant via function calls.

Choose exactly one allowed function for the current step.
- Call retrieve when you still need course-policy excerpts.
- Call grade_calculator when a numeric course-policy computation is needed.
- Call finish when you can answer the question directly.

Do not output JSON or markdown.
Do not call functions that are not allowed for this step.
When you call finish, provide only the final user-facing answer text.
""".strip()

ABSTAIN_MARKERS = [
    "do not have enough support",
    "cannot determine from the provided documents",
    "cannot provide a confident answer",
    "not enough evidence",
    "not specified in the provided documents",
    "i do not have access to the course policy documents",
    "i do not have access to the provided documents",
    "the provided documents do not say",
    "the provided documents do not specify",
    "the documents do not specify",
    "the documents do not say",
    "i cannot find relevant evidence",
    "i have not found relevant evidence",
    "there is no evidence in the provided documents",
    "there is no information about",
    "do not contain information",
    "does not contain information",
    "do not mention",
    "does not mention",
    "do not address",
    "does not address",
    "cannot answer your question",
    "you would need to check",
    "to get an answer to this question  you would need",
    "to find information  you may want to check",
    "i would need the relevant course policy",
    "i would need the course policy documentation",
]

ABSTAIN_REGEXES = [
    r"cannot determine .* provided documents",
    r"not enough .* (evidence|information|support)",
    r"do not have .* (documents|evidence|information)",
    r"no .* (evidence|information) .* provided documents",
    r"no information about",
    r"do(?:es)? not contain information",
    r"do(?:es)? not (mention|address)",
    r"cannot answer (your question)?",
    r"would need to check",
    r"would need .* (documents|policy|information)",
    r"cannot answer .* provided documents",
    r"documents do not say",
    r"provided text does not mention",
]

UNANSWERABLE_DISQUALIFIERS = [
    "youtube is required",
    "must be uploaded to youtube",
    "uploaded to youtube is required",
    "oral exams are allowed",
    "oral exams are not allowed",
    "the textbook is ",
    "required textbook is",
]

BENCHMARK = [
    {
        "id": 1,
        "type": "factual_in_doc",
        "question": "How many late days does each student receive for the semester?",
        "expected_answer": "Each student receives 3 late days for the semester.",
        "accepted_groups": [["3 late days", "three late days"]],
    },
    {
        "id": 2,
        "type": "factual_in_doc",
        "question": "What is the maximum number of late days allowed on a single homework?",
        "expected_answer": "A maximum of 2 late days may be used on a single homework.",
        "accepted_groups": [[
            "2 late days",
            "two late days",
            "maximum of 2 late days",
            "maximum number of late days allowed on a single homework is 2",
            "maximum is 2",
        ]],
    },
    {
        "id": 3,
        "type": "factual_in_doc",
        "question": "Within how many calendar days must a regrade request be submitted?",
        "expected_answer": "A regrade request must be submitted within 7 calendar days of score release.",
        "accepted_groups": [["7 calendar days", "seven calendar days", "within 7 days"]],
    },
    {
        "id": 4,
        "type": "factual_in_doc",
        "question": "What is the weight of the final project in the course grade?",
        "expected_answer": "The final project is worth 15% of the course grade.",
        "accepted_groups": [["15%", "15 percent"]],
    },
    {
        "id": 5,
        "type": "cross_doc",
        "question": "Can teams of 3 submit the final project, and are late days allowed for that project?",
        "expected_answer": "No. Teams of 3 are not allowed, and late days cannot be used for the final project.",
        "accepted_groups": [
            [
                "teams of 3 are not allowed",
                "teams of 3 not allowed",
                "teams of three are not allowed",
                "teams of 3 cannot submit",
                "teams of 3 are not allowed to submit",
                "teams of three cannot submit",
                "teams of three are not allowed to submit",
                "only teams of 2",
                "at most teams of 2",
            ],
            [
                "late days cannot be used",
                "late days are not allowed",
                "late days are also not allowed",
                "late days are not permitted",
                "no late days",
                "cannot use late days",
            ],
        ],
    },
    {
        "id": 6,
        "type": "factual_in_doc",
        "question": "Where are office hours normally held, and what changes during exam week?",
        "expected_answer": "Office hours are normally held in Room 3.14, and during exam week they move online by video call.",
        "accepted_groups": [["room 3.14"], ["online", "video call"]],
    },
    {
        "id": 7,
        "type": "cross_doc",
        "question": "Is lecture attendance required, and where should private grading issues be sent?",
        "expected_answer": "Lecture attendance is recommended but not required, and private grading issues should be sent by email to the teaching staff.",
        "accepted_groups": [["not required", "recommended but not required"], ["email", "sent by email"]],
    },
    {
        "id": 8,
        "type": "factual_in_doc",
        "question": "Is Julia allowed for the project, and under what condition?",
        "expected_answer": "Yes. Julia is allowed for the final project if the team also submits a short README explaining how to run the code.",
        "accepted_groups": [
            ["julia is permitted", "julia is allowed"],
            [
                "readme",
                "how to run the code",
                "explaining how to run the code",
                "instructions for running the code",
                "instructions explaining how to run the code",
                "short document explaining how to run the code",
            ],
        ],
    },
    {
        "id": 9,
        "type": "numeric_requires_tool",
        "question": (
            "My homework scores are 92.6, 87.1, 78.4, 90.3, and 94.8. "
            "I still have 3 late days left for the semester. "
            "Homework 1 was 2 days late, Homework 3 was 1 day late, and Homework 5 was 4 days late. "
            "If the remaining late days are used optimally under the course policy and the lowest homework is dropped, "
            "what homework average counts?"
        ),
        "tool_payload": {
            "mode": "homework_average_after_policy",
            "homework_scores": [92.6, 87.1, 78.4, 90.3, 94.8],
            "days_late_by_homework": {"1": 2, "3": 1, "5": 4},
            "total_late_days_available": 3,
        },
        "expected_numeric": 87.10,
        "expected_answer": "After allocating the remaining late days optimally and dropping the lowest homework, the counted homework average is 87.10.",
    },
    {
        "id": 10,
        "type": "numeric_requires_tool",
        "question": (
            "My homework scores are 88.7, 91.4, 84.2, 79.9, and 95.1. "
            "I still have 3 late days left for the semester. "
            "Homework 2 was 1 day late, Homework 4 was 3 days late, and Homework 5 was 2 days late. "
            "My midterm is 86.35 and my project is 91.8. "
            "If the remaining late days are used optimally under the course policy, "
            "what exact final exam score do I need for an A- (90 overall)?"
        ),
        "tool_payload": {
            "mode": "needed_final_for_target",
            "homework_scores": [88.7, 91.4, 84.2, 79.9, 95.1],
            "days_late_by_homework": {"2": 1, "4": 3, "5": 2},
            "total_late_days_available": 3,
            "midterm_score": 86.35,
            "project_score": 91.8,
            "target_course_grade": 90.0,
        },
        "expected_numeric": 92.08,
        "expected_answer": "After allocating the remaining late days optimally, you need 92.08 on the final exam to reach 90.00 overall.",
    },
    {
        "id": 11,
        "type": "numeric_requires_tool",
        "question": (
            "My homework scores are 96.2, 82.5, 89.7, 91.8, and 86.4. "
            "I still have 3 late days left for the semester. "
            "Homework 1 was 2 days late, Homework 2 was 2 days late, and Homework 5 was 3 days late. "
            "My midterm is 84.6, my project is 90.3, and my final exam is 87.9. "
            "If the remaining late days are used optimally under the course policy, what overall course grade do I finish with?"
        ),
        "tool_payload": {
            "mode": "overall_course_grade",
            "homework_scores": [96.2, 82.5, 89.7, 91.8, 86.4],
            "days_late_by_homework": {"1": 2, "2": 2, "5": 3},
            "total_late_days_available": 3,
            "midterm_score": 84.6,
            "project_score": 90.3,
            "final_exam_score": 87.9,
        },
        "expected_numeric": 87.46,
        "expected_answer": "After allocating the remaining late days optimally, the final weighted course grade is 87.46.",
    },
    {
        "id": 12,
        "type": "numeric_requires_tool",
        "question": (
            "My homework scores are 74.3, 83.6, 80.1, 77.5, and 92.4. "
            "I still have 3 late days left for the semester. "
            "Homework 1 was 2 days late, Homework 3 was 1 day late, and Homework 5 was 4 days late. "
            "My midterm is 76.5 and my project is 88.2. "
            "If the remaining late days are used optimally under the course policy, "
            "what exact final exam score do I need for a B+ (87 overall), and is that feasible?"
        ),
        "tool_payload": {
            "mode": "needed_final_for_target",
            "homework_scores": [74.3, 83.6, 80.1, 77.5, 92.4],
            "days_late_by_homework": {"1": 2, "3": 1, "5": 4},
            "total_late_days_available": 3,
            "midterm_score": 76.5,
            "project_score": 88.2,
            "target_course_grade": 87.0,
        },
        "expected_numeric": 107.68,
        "expected_answer": "After allocating the remaining late days optimally, you would need 107.68 on the final exam, so the target is not feasible.",
        "requires_infeasible_note": True,
    },
    {
        "id": 13,
        "type": "unanswerable",
        "question": "Does the instructor allow oral exams instead of the written final exam?",
        "expected_answer": ABSTAIN_TEXT,
    },
    {
        "id": 14,
        "type": "unanswerable",
        "question": "What textbook is required for the course?",
        "expected_answer": ABSTAIN_TEXT,
    },
    {
        "id": 15,
        "type": "unanswerable",
        "question": "Are project demo videos required to be uploaded to YouTube?",
        "expected_answer": ABSTAIN_TEXT,
    },
    {
        "id": 16,
        "type": "factual_in_doc",
        "question": "Can a student use five late days on one homework if they have them saved up?",
        "expected_answer": "No. A student cannot use five late days on one homework; the maximum is 2 late days on a single homework.",
        "accepted_groups": [[
            "maximum of 2 late days",
            "max 2 late days",
            "2 late days",
            "2 late days can be used on any single homework",
            "2 late days can be used on any single homework assignment",
        ]],
    },
]


DOCS: Dict[str, str] = {}
CHUNKS: List[Dict[str, Any]] = []
CORPUS_TERMS: set[str] = set()
RUN_CACHE: Dict[Any, Dict[str, Any]] = {}
STAGE_RESULTS: Dict[str, pd.DataFrame] = {}


@dataclass(frozen=True)
class AgentConfig:
    enable_retrieve: bool = False
    enable_tool: bool = False
    enable_evidence_check: bool = False
    retrieval_k: int = 3


def configure_notebook_display() -> None:
    pd.set_option("display.max_colwidth", None)
    pd.set_option("display.max_columns", 20)
    pd.set_option("display.width", 160)


def get_api_config() -> Dict[str, Any]:
    load_dotenv()

    model = os.environ.get("OPENROUTER_MODEL", "google/gemini-2.5-flash-lite").strip()

    return {
        "api_key": (
            os.environ.get("OPENROUTER_API_KEY") or ""
        ).strip(),
        "base_url": os.environ.get(
            "OPENROUTER_BASE_URL",
            "https://openrouter.ai/api/v1",
        ).rstrip("/"),
        "backend": "openrouter",
        "model": model,
    }


def ensure_docs_loaded() -> None:
    global DOCS, CHUNKS, CORPUS_TERMS

    if DOCS:
        return

    configure_notebook_display()
    DATA_DIR.mkdir(exist_ok=True)
    docs = {
        path.name: path.read_text(encoding="utf-8")
        for path in sorted(DATA_DIR.glob("*.md"))
    }
    if not docs:
        raise RuntimeError(f"No markdown files found in {DATA_DIR.resolve()}.")

    DOCS = docs
    CHUNKS = chunk_docs(DOCS)
    CORPUS_TERMS = set(tokenize(" ".join(DOCS.values())))


def bootstrap_notebook() -> None:
    ensure_docs_loaded()
    RUN_CACHE.clear()
    STAGE_RESULTS.clear()

    api_config = get_api_config()
    print("Using data directory:", DATA_DIR.resolve())
    print("Backend:", api_config["backend"])
    print("Model:", api_config["model"])
    if api_config["api_key"]:
        print("API key: loaded")
    else:
        print("API key: missing (set OPENROUTER_API_KEY before running stage cells)")


def accuracy_badge(value: float) -> str:
    return f"{value:.1f}%"


def display_table(
    df: pd.DataFrame,
    title: Optional[str] = None,
    max_rows: Optional[int] = None,
) -> None:
    if title:
        display(Markdown(f"### {title}"))
    if df.empty:
        display(Markdown("_No rows to display._"))
        return

    table = df.head(max_rows).copy() if max_rows else df.copy()
    styler = (
        table.style
        .set_properties(**{
            "text-align": "left",
            "white-space": "pre-wrap",
            "vertical-align": "top",
            "background-color": "#ffffff",
            "color": "#111827",
            "border-color": "#e5e7eb",
        })
        .set_table_styles([
            {"selector": "table", "props": [("border-collapse", "collapse"), ("width", "100%")]},
            {"selector": "th", "props": [("text-align", "left"), ("background-color", "#f3f4f6"), ("color", "#111827"), ("border-bottom", "1px solid #e5e7eb"), ("padding", "8px 10px")]},
            {"selector": "td", "props": [("max-width", "420px"), ("background-color", "#ffffff"), ("color", "#111827"), ("border-bottom", "1px solid #f1f5f9"), ("padding", "8px 10px")]},
            {"selector": "tbody tr:nth-child(even) td", "props": [("background-color", "#f8fafc")]},
        ])
    )
    try:
        styler = styler.hide(axis="index")
    except Exception:
        pass
    display(styler)

    if max_rows is not None and len(df) > max_rows:
        display(Markdown(f"_Showing first {max_rows} of {len(df)} rows._"))


def display_markdown_doc(name: str, text: str) -> None:
    display(Markdown(f"### `{name}`\n\n{text}"))


def show_corpus() -> None:
    ensure_docs_loaded()
    for name, text in DOCS.items():
        display_markdown_doc(name, text)
        display(Markdown("---"))


def show_benchmark() -> pd.DataFrame:
    benchmark_df = pd.DataFrame(BENCHMARK)[["id", "type", "question", "expected_answer"]]
    display_table(benchmark_df, title="Benchmark questions")
    return benchmark_df


def display_stage_banner(stage_name: str, cfg: AgentConfig) -> None:
    chips = []
    chip_specs = [
        ("Retrieval", cfg.enable_retrieve),
        ("Calculator", cfg.enable_tool),
        ("Evidence check", cfg.enable_evidence_check),
    ]
    for label, enabled in chip_specs:
        bg = "#dcfce7" if enabled else "#f3f4f6"
        fg = "#166534" if enabled else "#475569"
        chips.append(
            f'<span style="display:inline-block; margin: 0 8px 8px 0; padding: 4px 10px; border-radius: 999px; background:{bg}; color:{fg}; font-size:12px; font-weight:600;">{label}: {"on" if enabled else "off"}</span>'
        )

    card = f"""
    <div style="border: 1px solid #dbe3ee; border-radius: 10px; padding: 14px 16px; margin: 8px 0 16px 0; background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%); color: #111827;">
      <div style="font-size: 18px; font-weight: 700; margin-bottom: 8px;">{html.escape(stage_name)}</div>
      <div style="margin-bottom: 6px; color: #475569;">Active capabilities in this stage</div>
      <div>{''.join(chips)}</div>
    </div>
    """
    display(HTML(card))


def display_summary_cards(summary: pd.DataFrame, title: str = "Benchmark snapshot") -> None:
    display(Markdown(f"### {title}"))
    cards = []
    for _, row in summary.iterrows():
        key = row["type"]
        label = TYPE_LABELS.get(key, key)
        color = TYPE_COLORS.get(key, "#111827")
        width = max(6, min(100, float(row["accuracy"])))
        cards.append(
            f"""
            <div style="border: 1px solid #e5e7eb; border-radius: 10px; padding: 12px; background: #ffffff; color: #111827;">
              <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.04em; color: #64748b; margin-bottom: 6px;">{html.escape(label)}</div>
              <div style="font-size: 26px; font-weight: 700; color: {color}; margin-bottom: 4px;">{accuracy_badge(float(row['accuracy']))}</div>
              <div style="font-size: 13px; color: #475569; margin-bottom: 8px;">{int(row['correct'])} / {int(row['total'])} correct</div>
              <div style="height: 8px; border-radius: 999px; background: #e5e7eb; overflow: hidden;">
                <div style="width: {width}%; height: 100%; background: {color};"></div>
              </div>
            </div>
            """
        )

    container = f"""
    <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin: 10px 0 18px 0;">
      {''.join(cards)}
    </div>
    """
    display(HTML(container))


def display_examples(
    df: pd.DataFrame,
    title: str,
    tone: str,
    limit: Optional[int] = None,
) -> None:
    display(Markdown(f"### {title}"))
    if df.empty:
        display(Markdown("_No items to display._"))
        return

    shown = df.head(limit) if limit is not None else df
    styles = {
        "success": {"border": "#15803d", "background": "#f0fdf4"},
        "failure": {"border": "#d1242f", "background": "#fff7ed"},
    }
    style = styles[tone]

    for _, row in shown.iterrows():
        card = f"""
        <div style="border-left: 4px solid {style['border']}; padding: 12px 14px; margin: 12px 0; background: {style['background']}; color: #111827; line-height: 1.5; border-radius: 0 8px 8px 0;">
          <p><strong>Benchmark item</strong>: {row['id']} ({html.escape(str(row['type']))})</p>
          <p><strong>Question</strong><br>{html.escape(str(row['question']))}</p>
          <p><strong>Expected answer</strong><br>{html.escape(str(row['expected_answer']))}</p>
          <p><strong>Model answer</strong><br>{html.escape(str(row['answer']))}</p>
          <p><strong>Retrieved documents</strong><br>{html.escape(str(row['evidence_docs']) if row['evidence_docs'] else 'None')}</p>
        </div>
        """
        display(HTML(card))

    if limit is not None and len(df) > len(shown):
        display(Markdown(f"_Showing {len(shown)} of {len(df)} items._"))


def show_stage_pseudocode(stage_name: str, cfg: AgentConfig) -> None:
    pseudocode = f"""```python
cfg = AgentConfig(
    enable_retrieve={cfg.enable_retrieve},
    enable_tool={cfg.enable_tool},
    enable_evidence_check={cfg.enable_evidence_check},
)

for item in benchmark:
    evidence = []
    tool_result = None
    answer = None

    while True:
        allowed_tools = ["finish"]
        {"allowed_tools.append('retrieve')" if cfg.enable_retrieve else "# allowed_tools.append('retrieve')"}
        {"allowed_tools.append('grade_calculator')" if cfg.enable_tool else "# allowed_tools.append('grade_calculator')"}

        if allowed_tools == ["finish"]:
            # Stage 0: there is nothing to choose, so use a direct LLM call.
            answer = llm_text(question_only_prompt)
            break

        decision = planner_llm(item, evidence, tool_result, allowed_tools)

        if decision.action == "retrieve":
            evidence = retrieve(decision.query)
            continue
        if decision.action == "grade_calculator":
            tool_result = grade_calculator(...)
            continue
        if decision.action == "finish":
            answer = render_final_answer(evidence, tool_result)
            break

    if cfg.enable_evidence_check:
        answer = enforce_evidence_gate(answer, evidence, tool_result)
    else:
        # no evidence gate in this stage
        pass

    score_answer(item, answer)
```"""
    display(Markdown(f"### {stage_name} pseudocode\n\n{pseudocode}"))


def tokenize(text: str) -> List[str]:
    tokens = [token.strip(".") for token in re.findall(r"[A-Za-z0-9\-\+\.]+", text.lower())]
    return [token for token in tokens if token not in STOPWORDS and len(token) > 1]


def chunk_docs(
    docs: Dict[str, str],
    chunk_chars: int = 450,
    overlap: int = 80,
) -> List[Dict[str, Any]]:
    chunks: List[Dict[str, Any]] = []
    for doc_name, text in docs.items():
        start = 0
        idx = 0
        while start < len(text):
            end = min(len(text), start + chunk_chars)
            chunk_text = text[start:end]
            chunks.append({
                "chunk_id": f"{doc_name}::chunk_{idx}",
                "doc_name": doc_name,
                "text": chunk_text.strip(),
            })
            if end == len(text):
                break
            start = max(start + chunk_chars - overlap, start + 1)
            idx += 1
    return chunks


def retrieve(query: str, k: int = 3) -> List[Dict[str, Any]]:
    ensure_docs_loaded()
    q_terms = set(tokenize(query))
    scored = []
    for chunk in CHUNKS:
        c_terms = tokenize(chunk["text"])
        overlap = sum(1 for term in q_terms if term in c_terms)
        bonus = 0.25 * sum(query.lower().count(term) for term in q_terms if term in chunk["text"].lower())
        score = overlap + bonus
        scored.append((score, chunk))

    ranked = [
        chunk
        for score, chunk in sorted(scored, key=lambda item: item[0], reverse=True)
        if score > 0
    ]

    selected: List[Dict[str, Any]] = []
    seen_docs = set()
    for chunk in ranked:
        if chunk["doc_name"] in seen_docs:
            continue
        selected.append(chunk)
        seen_docs.add(chunk["doc_name"])
        if len(selected) == k:
            return selected

    for chunk in ranked:
        if chunk in selected:
            continue
        selected.append(chunk)
        if len(selected) == k:
            break
    return selected


def show_retrieval(query: str, k: int = 3) -> List[Dict[str, Any]]:
    hits = retrieve(query, k=k)
    if not hits:
        display(Markdown("_No retrieval hits._"))
        return hits

    for idx, chunk in enumerate(hits, start=1):
        display(Markdown(f"#### Hit {idx}: `{chunk['doc_name']}`\n\n{chunk['text']}"))
        display(Markdown("---"))
    return hits


def weighted_grade(points: Dict[str, float], weights: Dict[str, float]) -> float:
    return sum(points[key] * weights[key] for key in points)


def apply_late_policy(
    raw_score: float,
    days_late: int = 0,
    late_days_available: int = 0,
) -> Dict[str, Any]:
    late_days_used = min(max(days_late, 0), max(late_days_available, 0), 2)
    penalty_days = max(days_late - late_days_used, 0)
    adjusted_score = 0.0 if penalty_days > 3 else max(0.0, raw_score - 10.0 * penalty_days)
    return {
        "raw_score": round(raw_score, 4),
        "days_late": int(days_late),
        "late_days_used": int(late_days_used),
        "penalty_days": int(penalty_days),
        "adjusted_score": round(adjusted_score, 4),
        "zero_credit": bool(penalty_days > 3),
    }


def optimize_late_day_allocation(
    homework_scores: List[float],
    days_late_by_homework: Dict[str, int],
    total_late_days_available: int,
) -> Dict[str, Any]:
    choices_per_assignment: List[List[int]] = []
    days_late_lookup = {str(key): int(value) for key, value in days_late_by_homework.items()}

    for idx in range(1, len(homework_scores) + 1):
        days_late = max(days_late_lookup.get(str(idx), 0), 0)
        choices_per_assignment.append(list(range(min(days_late, 2) + 1)))

    best_summary = None
    best_key = None

    def search(pos: int, allocation: List[int], used: int) -> None:
        nonlocal best_summary, best_key
        if used > total_late_days_available:
            return

        if pos == len(homework_scores):
            adjusted_scores: List[float] = []
            adjustment_details: List[Dict[str, Any]] = []
            for idx, raw_score in enumerate(homework_scores, start=1):
                late_result = apply_late_policy(
                    raw_score=float(raw_score),
                    days_late=days_late_lookup.get(str(idx), 0),
                    late_days_available=allocation[idx - 1],
                )
                adjusted_scores.append(late_result["adjusted_score"])
                adjustment_details.append({"assignment": idx, **late_result})

            dropped_score = min(adjusted_scores)
            counted_scores = sorted(adjusted_scores)[1:]
            counted_average = sum(counted_scores) / len(counted_scores)
            summary = {
                "adjusted_homework_scores": [round(score, 4) for score in adjusted_scores],
                "dropped_homework_score": round(dropped_score, 4),
                "counted_homework_average": round(counted_average, 4),
                "late_policy_details": adjustment_details,
                "optimal_late_day_allocation": {
                    str(i + 1): int(days)
                    for i, days in enumerate(allocation)
                    if days
                },
                "late_days_used_total": int(sum(allocation)),
                "total_late_days_available": int(total_late_days_available),
            }
            key = (
                round(counted_average, 8),
                round(sum(adjusted_scores), 8),
                -sum(allocation),
                tuple(-days for days in allocation),
            )
            if best_key is None or key > best_key:
                best_key = key
                best_summary = summary
            return

        for days_used in choices_per_assignment[pos]:
            allocation.append(days_used)
            search(pos + 1, allocation, used + days_used)
            allocation.pop()

    search(0, [], 0)
    if best_summary is None:
        raise RuntimeError("Failed to find a valid late-day allocation.")
    return best_summary


def homework_average_after_policy(
    homework_scores: List[float],
    late_adjustments: Optional[Dict[str, Dict[str, int]]] = None,
    days_late_by_homework: Optional[Dict[str, int]] = None,
    total_late_days_available: Optional[int] = None,
) -> Dict[str, Any]:
    if days_late_by_homework is not None and total_late_days_available is not None:
        return optimize_late_day_allocation(
            homework_scores=homework_scores,
            days_late_by_homework=days_late_by_homework,
            total_late_days_available=int(total_late_days_available),
        )

    late_adjustments = late_adjustments or {}
    adjusted_scores: List[float] = []
    adjustment_details: List[Dict[str, Any]] = []

    for idx, raw_score in enumerate(homework_scores, start=1):
        adjustment = late_adjustments.get(str(idx), {})
        late_result = apply_late_policy(
            raw_score=float(raw_score),
            days_late=int(adjustment.get("days_late", 0)),
            late_days_available=int(adjustment.get("late_days_available", 0)),
        )
        adjusted_scores.append(late_result["adjusted_score"])
        adjustment_details.append({"assignment": idx, **late_result})

    dropped_score = min(adjusted_scores)
    counted_scores = sorted(adjusted_scores)[1:]
    counted_average = sum(counted_scores) / len(counted_scores)
    return {
        "adjusted_homework_scores": [round(score, 4) for score in adjusted_scores],
        "dropped_homework_score": round(dropped_score, 4),
        "counted_homework_average": round(counted_average, 4),
        "late_policy_details": adjustment_details,
    }


def letter_grade_for_score(score: float) -> str:
    for label, threshold in LETTER_THRESHOLDS:
        if score >= threshold:
            return label
    return "Below B-"


def grade_calculator(mode: str, **payload: Any) -> Dict[str, Any]:
    if mode == "homework_average_after_policy":
        summary = homework_average_after_policy(
            homework_scores=payload["homework_scores"],
            late_adjustments=payload.get("late_adjustments"),
            days_late_by_homework=payload.get("days_late_by_homework"),
            total_late_days_available=payload.get("total_late_days_available"),
        )
        return {
            "mode": mode,
            **summary,
            "final_numeric_answer": summary["counted_homework_average"],
        }

    if mode == "needed_final_for_target":
        homework_summary = homework_average_after_policy(
            homework_scores=payload["homework_scores"],
            late_adjustments=payload.get("late_adjustments"),
            days_late_by_homework=payload.get("days_late_by_homework"),
            total_late_days_available=payload.get("total_late_days_available"),
        )
        known_scores = {
            "homework": homework_summary["counted_homework_average"],
            "midterm": float(payload["midterm_score"]),
            "project": float(payload["project_score"]),
        }
        known_weights = {
            "homework": COURSE_WEIGHTS["homework"],
            "midterm": COURSE_WEIGHTS["midterm"],
            "project": COURSE_WEIGHTS["project"],
        }
        needed = (
            float(payload["target_course_grade"])
            - weighted_grade(known_scores, known_weights)
        ) / COURSE_WEIGHTS["final_exam"]
        feasible = 0.0 <= needed <= 100.0
        return {
            "mode": mode,
            **homework_summary,
            "target_course_grade": round(float(payload["target_course_grade"]), 4),
            "needed_on_final_exam": round(needed, 4),
            "feasible": feasible,
            "final_numeric_answer": round(needed, 4),
        }

    if mode == "overall_course_grade":
        homework_summary = homework_average_after_policy(
            homework_scores=payload["homework_scores"],
            late_adjustments=payload.get("late_adjustments"),
            days_late_by_homework=payload.get("days_late_by_homework"),
            total_late_days_available=payload.get("total_late_days_available"),
        )
        overall = weighted_grade(
            {
                "homework": homework_summary["counted_homework_average"],
                "midterm": float(payload["midterm_score"]),
                "project": float(payload["project_score"]),
                "final_exam": float(payload["final_exam_score"]),
            },
            COURSE_WEIGHTS,
        )
        return {
            "mode": mode,
            **homework_summary,
            "overall_course_grade": round(overall, 4),
            "letter_grade": letter_grade_for_score(overall),
            "final_numeric_answer": round(overall, 4),
        }

    raise ValueError(f"Unknown calculator mode: {mode}")


def show_sample_calculator() -> Dict[str, Any]:
    sample_tool_result = grade_calculator(
        mode="needed_final_for_target",
        homework_scores=[88.7, 91.4, 84.2, 79.9, 95.1],
        days_late_by_homework={"2": 1, "4": 3, "5": 2},
        total_late_days_available=3,
        midterm_score=86.35,
        project_score=91.8,
        target_course_grade=90.0,
    )
    display_table(pd.json_normalize([sample_tool_result]), title="Sample calculator output")
    return sample_tool_result


def _openrouter_request(
    messages: List[Dict[str, Any]],
    max_tokens: int = 500,
    tools: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    api_config = get_api_config()
    if not api_config["api_key"]:
        raise RuntimeError(
            "Set OPENROUTER_API_KEY before running stage cells."
        )

    payload: Dict[str, Any] = {
        "model": api_config["model"],
        "messages": messages,
        "temperature": 0,
        "top_p": 1,
        "max_tokens": max_tokens,
    }
    if tools:
        payload["tools"] = tools

    request = urllib.request.Request(
        url=f"{api_config['base_url']}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_config['api_key']}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    body = None
    last_error = None
    for attempt in range(6):
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                body = json.loads(response.read().decode("utf-8"))
            break
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            last_error = RuntimeError(f"OpenRouter request failed with HTTP {exc.code}: {detail}")
            if exc.code not in {429, 500, 502, 503, 504} or attempt == 5:
                raise last_error from exc
            delay = float(2 ** attempt)
            time.sleep(max(delay, 1.0))
        except urllib.error.URLError as exc:
            last_error = RuntimeError(f"OpenRouter request failed: {exc}")
            if attempt == 5:
                raise last_error from exc
            time.sleep(2 ** attempt)

    if body is None:
        raise last_error or RuntimeError("OpenRouter request failed without a response body.")
    return body


def llm_text(system_prompt: str, user_prompt: str, max_tokens: int = 500) -> str:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    # Retry up to 3 times on empty/error responses
    for attempt in range(3):
        body = _openrouter_request(messages, max_tokens=max_tokens)
        choices = body.get("choices", [])
        if not choices:
            if attempt < 2:
                time.sleep(1)
                continue
            raise RuntimeError(f"OpenRouter returned no choices: {body}")
        finish_reason = choices[0].get("finish_reason", "")
        native_reason = choices[0].get("native_finish_reason", "")
        text = (choices[0].get("message", {}).get("content") or "").strip()
        if text:
            return text
        # Retry on malformed function call or error finish reasons
        if finish_reason == "error" or "MALFORMED" in (native_reason or ""):
            if attempt < 2:
                time.sleep(1)
                continue
        if attempt < 2:
            time.sleep(1)
            continue
        raise RuntimeError(f"OpenRouter returned no text content: {body}")
    raise RuntimeError("llm_text failed after retries")


_TOOL_DECISION_SYSTEM_PROMPT = """You are controlling a notebook assistant. Choose exactly one action for the current step.

You MUST respond with a single JSON object on one line. No markdown, no explanation, no extra text.

Available actions:
{tool_descriptions}

Response format examples:
{{"action": "retrieve", "query": "late day policy"}}
{{"action": "grade_calculator"}}
{{"action": "finish", "answer": "The answer is 42."}}
"""


def openrouter_tool_decision(user_prompt: str, available_tools: List[str]) -> Dict[str, Any]:
    tool_descriptions = []
    if "retrieve" in available_tools:
        tool_descriptions.append('- "retrieve": fetch relevant course-policy excerpts. Requires "query" field.')
    if "grade_calculator" in available_tools:
        tool_descriptions.append('- "grade_calculator": compute the authoritative numeric result for this benchmark question. No extra fields.')
    tool_descriptions.append('- "finish": return the final answer. Requires "answer" field with the user-facing answer text.')

    system_prompt = _TOOL_DECISION_SYSTEM_PROMPT.format(
        tool_descriptions="\n".join(tool_descriptions),
    )

    text = llm_text(system_prompt, user_prompt, max_tokens=300)

    # Strip markdown fences if present
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        cleaned = cleaned.strip()

    try:
        result = json.loads(cleaned)
        if isinstance(result, dict) and "action" in result:
            return result
    except json.JSONDecodeError:
        pass

    # Try to extract JSON from the text
    match = re.search(r'\{[^}]*"action"\s*:\s*"[^"]*"[^}]*\}', text)
    if match:
        try:
            result = json.loads(match.group())
            if "action" in result:
                return result
        except json.JSONDecodeError:
            pass

    return {"action": "finish", "answer": text, "reason": "json parse fallback"}


def render_evidence(evidence: List[Dict[str, Any]]) -> str:
    if not evidence:
        return "No retrieved excerpts were provided."
    parts = []
    for idx, chunk in enumerate(evidence, start=1):
        parts.append(f"[{idx}] [{chunk['doc_name']}]\n{chunk['text']}")
    return "\n\n".join(parts)


def build_user_prompt(
    question: str,
    evidence: List[Dict[str, Any]],
    tool_result: Optional[Dict[str, Any]],
) -> str:
    sections = [f"Question:\n{question}"]
    if evidence:
        sections.append("Retrieved excerpts:\n" + render_evidence(evidence))
    if tool_result is not None:
        sections.append(
            "Deterministic tool result (authoritative):\n" + json.dumps(tool_result, indent=2)
        )
    return "\n\n".join(sections)


def build_tool_selection_prompt(
    item: Dict[str, Any],
    evidence: List[Dict[str, Any]],
    tool_result: Optional[Dict[str, Any]],
    tool_trace: List[Dict[str, Any]],
    available_tools: List[str],
) -> str:
    tool_descriptions = []
    if "retrieve" in available_tools:
        tool_descriptions.append('- retrieve: fetch relevant course-policy excerpts.')
    if "grade_calculator" in available_tools:
        tool_descriptions.append('- grade_calculator: compute the authoritative numeric result for this benchmark question.')
    tool_descriptions.append('- finish: produce the final answer.')

    sections = [
        f"Question:\n{item['question']}",
        "Available tools:\n" + "\n".join(tool_descriptions),
        "Current retrieved excerpts:\n" + render_evidence(evidence),
        "Current calculator result:\n" + (
            json.dumps(tool_result, indent=2) if tool_result is not None else "No calculator result yet."
        ),
    ]
    if tool_trace:
        sections.append("Previous tool decisions:\n" + json.dumps(tool_trace, indent=2))
    else:
        sections.append("Previous tool decisions:\nNone yet.")
    return "\n\n".join(sections)


def system_prompt_for_config(cfg: AgentConfig) -> str:
    if not cfg.enable_retrieve and not cfg.enable_tool and not cfg.enable_evidence_check:
        return BASELINE_SYSTEM_PROMPT
    return GROUNDED_SYSTEM_PROMPT


def calculator_available_for_item(item: Dict[str, Any], cfg: AgentConfig) -> bool:
    return cfg.enable_tool and item.get("tool_payload") is not None


def tool_context_for_item(item: Dict[str, Any], cfg: AgentConfig) -> Optional[Dict[str, Any]]:
    if not calculator_available_for_item(item, cfg):
        return None
    return grade_calculator(**item["tool_payload"])


def render_tool_answer(item: Dict[str, Any], tool_result: Dict[str, Any]) -> str:
    mode = tool_result["mode"]
    optimization_prefix = (
        "After allocating the remaining late days optimally, "
        if "optimal_late_day_allocation" in tool_result
        else "After applying the homework and late-day rules, "
    )

    if mode == "homework_average_after_policy":
        value = tool_result["counted_homework_average"]
        if "optimal_late_day_allocation" in tool_result:
            return (
                "After allocating the remaining late days optimally and dropping the lowest homework, "
                f"the counted homework average is {value:.2f}."
            )
        return (
            "After applying the late policy and dropping the lowest homework, "
            f"the counted homework average is {value:.2f}."
        )

    if mode == "needed_final_for_target":
        needed = tool_result["needed_on_final_exam"]
        target = tool_result["target_course_grade"]
        if tool_result["feasible"]:
            return optimization_prefix + f"you need {needed:.2f} on the final exam to reach {target:.2f} overall."
        return optimization_prefix + f"you would need {needed:.2f} on the final exam, so the target is not feasible."

    if mode == "overall_course_grade":
        value = tool_result["overall_course_grade"]
        return optimization_prefix + f"the final weighted course grade is {value:.2f}."

    raise ValueError(f"Unknown tool mode: {mode}")


def extract_numbers(text: str) -> List[float]:
    return [float(match) for match in re.findall(r"-?\d+(?:\.\d+)?", text.replace(",", ""))]


def normalize(text: str) -> str:
    text = text.lower()
    contractions = {
        "aren't": "are not",
        "can't": "cannot",
        "couldn't": "could not",
        "didn't": "did not",
        "doesn't": "does not",
        "don't": "do not",
        "hasn't": "has not",
        "haven't": "have not",
        "isn't": "is not",
        "shouldn't": "should not",
        "wasn't": "was not",
        "weren't": "were not",
        "won't": "will not",
        "wouldn't": "would not",
    }
    for src, dst in contractions.items():
        text = text.replace(src, dst)
    text = re.sub(r"[^a-z0-9\.\%\+\-\s]", " ", text)
    return re.sub(r"\s+", " ", text.strip())


def find_numeric_result_candidates(answer: str, mode: Optional[str]) -> List[float]:
    text = normalize(answer)
    patterns: List[str] = []

    if mode == "homework_average_after_policy":
        patterns = [
            r"(?:counted homework average|homework average(?: counts)?|average counts|average is)[^\d-]*(-?\d+(?:\.\d+)?)",
        ]
    elif mode == "needed_final_for_target":
        patterns = [
            r"(?:you need|would need|need on the final exam|need on the final)[^\d-]*(-?\d+(?:\.\d+)?)",
        ]
    elif mode == "overall_course_grade":
        patterns = [
            r"(?:overall course grade|final weighted course grade|course grade is|finish with)[^\d-]*(-?\d+(?:\.\d+)?)",
        ]

    candidates: List[float] = []
    for pattern in patterns:
        candidates.extend(float(match) for match in re.findall(pattern, text))

    if candidates:
        return candidates

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    tail = "\n".join(lines[-3:]) if lines else text
    return extract_numbers(tail)


def any_number_matches(values: List[float], expected: float, tolerance: float = 0.01) -> bool:
    return any(abs(value - expected) <= tolerance for value in values)


def available_tools_for_step(
    item: Dict[str, Any],
    cfg: AgentConfig,
    evidence: List[Dict[str, Any]],
    tool_result: Optional[Dict[str, Any]],
) -> List[str]:
    tools = []
    if cfg.enable_retrieve and not evidence:
        tools.append("retrieve")
    if calculator_available_for_item(item, cfg) and tool_result is None:
        tools.append("grade_calculator")
    tools.append("finish")
    return tools


def merge_evidence(
    existing: List[Dict[str, Any]],
    new_hits: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    merged = {chunk["chunk_id"]: chunk for chunk in existing}
    for chunk in new_hits:
        merged[chunk["chunk_id"]] = chunk
    return list(merged.values())


def tool_trace_entry(action: str, detail: str) -> Dict[str, Any]:
    return {"action": action, "detail": detail}


def run_tool_agent(item: Dict[str, Any], cfg: AgentConfig) -> Dict[str, Any]:
    evidence: List[Dict[str, Any]] = []
    tool_result: Optional[Dict[str, Any]] = None
    tool_trace: List[Dict[str, Any]] = []

    for _ in range(4):
        step_tools = available_tools_for_step(item, cfg, evidence, tool_result)
        planner_prompt = build_tool_selection_prompt(item, evidence, tool_result, tool_trace, step_tools)
        decision = openrouter_tool_decision(planner_prompt, step_tools)
        action = decision["action"]

        if action == "retrieve":
            query = str(decision.get("query") or item["question"]).strip()
            hits = retrieve(query, k=cfg.retrieval_k)
            evidence = merge_evidence(evidence, hits)
            tool_trace.append(
                tool_trace_entry(
                    "retrieve",
                    f"query={query!r}; docs={', '.join(chunk['doc_name'] for chunk in hits) if hits else 'none'}",
                )
            )
            continue

        if action == "grade_calculator":
            tool_result = tool_context_for_item(item, cfg)
            if tool_result is None:
                tool_trace.append(tool_trace_entry("grade_calculator", "not available for this question"))
            else:
                detail = f"mode={tool_result['mode']}"
                if "final_numeric_answer" in tool_result:
                    detail += f"; numeric={tool_result['final_numeric_answer']}"
                tool_trace.append(tool_trace_entry("grade_calculator", detail))
            continue

        if action == "finish":
            if tool_result is not None and item["type"] == "numeric_requires_tool":
                answer = render_tool_answer(item, tool_result)
                tool_trace.append(tool_trace_entry("finish", "used deterministic calculator result"))
            else:
                answer = str(decision.get("answer", "")).strip()
                if not answer:
                    answer = llm_text(
                        system_prompt_for_config(cfg),
                        build_user_prompt(item["question"], evidence, tool_result),
                    )
                tool_trace.append(tool_trace_entry("finish", "returned final answer"))
            return {
                "answer": answer,
                "evidence": evidence,
                "tool_result": tool_result,
                "tool_trace": tool_trace,
            }

    if tool_result is not None and item["type"] == "numeric_requires_tool":
        answer = render_tool_answer(item, tool_result)
        tool_trace.append(tool_trace_entry("finish", "max-step fallback used deterministic calculator result"))
    else:
        answer = llm_text(
            system_prompt_for_config(cfg),
            build_user_prompt(item["question"], evidence, tool_result),
        )
        tool_trace.append(tool_trace_entry("finish", "max-step fallback direct answer"))

    return {
        "answer": answer,
        "evidence": evidence,
        "tool_result": tool_result,
        "tool_trace": tool_trace,
    }


def answer_uses_missing_question_terms(
    question: str,
    answer: str,
    evidence: List[Dict[str, Any]],
) -> bool:
    evidence_terms = set(tokenize(" ".join(chunk["text"] for chunk in evidence)))
    answer_terms = set(tokenize(answer))
    question_terms = {
        token
        for token in tokenize(question)
        if len(token) >= 5
        and token not in SUPPORT_IGNORE_TOKENS
        and token not in MISSING_TERM_IGNORE_TOKENS
        and not re.fullmatch(r"\d+(?:\.\d+)?", token)
    }
    missing_terms = {
        token
        for token in question_terms
        if token not in evidence_terms and token not in CORPUS_TERMS
    }
    return any(term in answer_terms for term in missing_terms)


def is_abstention(text: str) -> bool:
    normalized = normalize(text)
    if any(marker in normalized for marker in ABSTAIN_MARKERS):
        return True
    return any(re.search(pattern, normalized) for pattern in ABSTAIN_REGEXES)


def is_strict_abstention(text: str) -> bool:
    return normalize(text) == normalize(ABSTAIN_TEXT)


def split_into_scoring_clauses(text: str) -> List[str]:
    normalized = normalize(text)
    return [
        clause.strip()
        for clause in re.split(r"[.!?;]+|\bbut\b|\bhowever\b|\byet\b", normalized)
        if clause.strip()
    ]


def has_unsupported_conclusion(text: str) -> bool:
    for clause in split_into_scoring_clauses(text):
        if is_abstention(clause):
            continue
        if any(marker in clause for marker in UNANSWERABLE_DISQUALIFIERS):
            return True
    return False


def score_answer(item: Dict[str, Any], answer: str) -> Dict[str, Any]:
    normalized_answer = normalize(answer)

    if item["type"] == "unanswerable":
        ok = is_abstention(answer) and not has_unsupported_conclusion(answer)
        return {"correct": ok, "mode": "abstain"}

    if item["type"] == "numeric_requires_tool":
        expected = item["expected_numeric"]
        numeric_mode = item.get("tool_payload", {}).get("mode")
        candidates = find_numeric_result_candidates(answer, numeric_mode)
        ok = any_number_matches(candidates, expected)
        if ok and item.get("requires_infeasible_note"):
            ok = any(
                marker in normalized_answer
                for marker in ["not feasible", "not achievable", "cannot be reached", "impossible"]
            )
        return {
            "correct": ok,
            "mode": "numeric",
            "expected": expected,
            "found_numbers": candidates,
            "all_numbers": extract_numbers(normalized_answer),
        }

    accepted_groups = item.get("accepted_groups")
    if accepted_groups:
        ok = all(
            any(normalize(option) in normalized_answer for option in group)
            for group in accepted_groups
        )
        return {"correct": ok, "mode": "concept_groups"}

    needed = [normalize(value) for value in item.get("expected_substrings", [])]
    ok = all(value in normalized_answer for value in needed)
    return {"correct": ok, "mode": "substring"}


def run_item(item: Dict[str, Any], cfg: AgentConfig) -> Dict[str, Any]:
    ensure_docs_loaded()
    cache_key = (
        item["id"],
        item["question"],
        cfg.enable_retrieve,
        cfg.enable_tool,
        cfg.enable_evidence_check,
        cfg.retrieval_k,
    )
    if cache_key in RUN_CACHE:
        return RUN_CACHE[cache_key]

    if cfg.enable_retrieve or cfg.enable_tool:
        agent_result = run_tool_agent(item, cfg)
        answer = agent_result["answer"]
        evidence = agent_result["evidence"]
        tool_result = agent_result["tool_result"]
        tool_trace = agent_result["tool_trace"]
    else:
        evidence = []
        tool_result = None
        answer = llm_text(
            system_prompt_for_config(cfg),
            build_user_prompt(item["question"], evidence, tool_result),
        )
        tool_trace = []

    if cfg.enable_evidence_check:
        unsupported = tool_result is None and (
            not evidence or answer_uses_missing_question_terms(item["question"], answer, evidence)
        )
        if unsupported:
            answer = ABSTAIN_TEXT
            tool_trace = tool_trace + [tool_trace_entry("evidence_check", "blocked unsupported answer")]
        elif is_abstention(answer):
            fallback_cfg = AgentConfig(
                enable_retrieve=cfg.enable_retrieve,
                enable_tool=cfg.enable_tool,
                enable_evidence_check=False,
                retrieval_k=cfg.retrieval_k,
            )
            recovered = run_item(item, fallback_cfg)["answer"]
            if is_abstention(recovered):
                answer = ABSTAIN_TEXT
                tool_trace = tool_trace + [tool_trace_entry("evidence_check", "kept abstention after fallback")]
            else:
                answer = recovered
                tool_trace = tool_trace + [tool_trace_entry("evidence_check", "recovered supported answer from fallback")]
        if is_abstention(answer) and answer != ABSTAIN_TEXT:
            answer = ABSTAIN_TEXT
            tool_trace = tool_trace + [tool_trace_entry("evidence_check", "canonicalized abstention text")]

    result = {
        "id": item["id"],
        "type": item["type"],
        "question": item["question"],
        "expected_answer": item.get("expected_answer"),
        "answer": answer,
        "evidence_docs": [chunk["doc_name"] for chunk in evidence],
        "evidence": evidence,
        "tool_result": tool_result,
        "tool_trace": tool_trace,
    }
    RUN_CACHE[cache_key] = result
    return result


def evaluate_config(cfg: AgentConfig, label: str) -> pd.DataFrame:
    rows = []
    for item in BENCHMARK:
        result = run_item(item, cfg)
        score = score_answer(item, result["answer"])
        rows.append({
            "stage": label,
            "id": item["id"],
            "type": item["type"],
            "question": item["question"],
            "expected_answer": item.get("expected_answer", ""),
            "answer": result["answer"],
            "correct": bool(score["correct"]),
            "strict_abstain": is_strict_abstention(result["answer"]) if item["type"] == "unanswerable" else None,
            "semantic_abstain": is_abstention(result["answer"]) if item["type"] == "unanswerable" else None,
            "evidence_docs": ", ".join(result["evidence_docs"]),
        })
    return pd.DataFrame(rows)


def summarize_results(df: pd.DataFrame) -> pd.DataFrame:
    summary = df.groupby("type")["correct"].agg(correct="sum", total="count").reset_index()
    summary["accuracy"] = (100 * summary["correct"] / summary["total"]).round(1)
    order = {
        "factual_in_doc": 0,
        "cross_doc": 1,
        "numeric_requires_tool": 2,
        "unanswerable": 3,
        "overall": 4,
    }
    overall = pd.DataFrame([{
        "type": "overall",
        "correct": int(df["correct"].sum()),
        "total": int(len(df)),
        "accuracy": round(100 * df["correct"].mean(), 1),
    }])
    summary = pd.concat([summary, overall], ignore_index=True)
    summary["type_label"] = summary["type"].map(TYPE_LABELS).fillna(summary["type"])
    summary["accuracy_display"] = summary["accuracy"].map(accuracy_badge)
    summary["sort_key"] = summary["type"].map(order)
    summary = summary.sort_values("sort_key").drop(columns="sort_key").reset_index(drop=True)
    return summary


def summarize_for_comparison(df: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for key in ["factual_in_doc", "cross_doc", "numeric_requires_tool"]:
        subset = df[df["type"] == key]
        if len(subset) == 0:
            continue
        rows.append({
            "category": TYPE_LABELS[key],
            "metric": f"{100 * subset['correct'].mean():.1f}% ({int(subset['correct'].sum())}/{len(subset)})",
        })

    abstain_subset = df[df["type"] == "unanswerable"]
    if len(abstain_subset) > 0:
        semantic = abstain_subset["semantic_abstain"].fillna(False)
        strict = abstain_subset["strict_abstain"].fillna(False)
        rows.append({
            "category": "Unanswerable",
            "metric": f"{100 * semantic.mean():.1f}% ({int(semantic.sum())}/{len(semantic)})",
        })
        rows.append({
            "category": "Canonical abstention",
            "metric": f"{100 * strict.mean():.1f}% ({int(strict.sum())}/{len(strict)})",
        })

    answerable = df[df["type"] != "unanswerable"]
    rows.append({
        "category": "Answerable overall",
        "metric": f"{100 * answerable['correct'].mean():.1f}% ({int(answerable['correct'].sum())}/{len(answerable)})",
    })
    return pd.DataFrame(rows)


def example_type_priority(stage_name: str, tone: str) -> List[str]:
    if tone == "success":
        if "Stage 1" in stage_name:
            return ["cross_doc", "factual_in_doc", "numeric_requires_tool", "unanswerable"]
        if "Stage 2" in stage_name:
            return ["numeric_requires_tool", "cross_doc", "factual_in_doc", "unanswerable"]
        if "Stage 3" in stage_name:
            return ["unanswerable", "numeric_requires_tool", "cross_doc", "factual_in_doc"]
        return ["factual_in_doc", "cross_doc", "numeric_requires_tool", "unanswerable"]

    if "Stage 1" in stage_name:
        return ["numeric_requires_tool", "unanswerable", "cross_doc", "factual_in_doc"]
    if "Stage 2" in stage_name:
        return ["unanswerable", "cross_doc", "factual_in_doc", "numeric_requires_tool"]
    if "Stage 3" in stage_name:
        return ["unanswerable", "cross_doc", "factual_in_doc", "numeric_requires_tool"]
    return ["cross_doc", "numeric_requires_tool", "unanswerable", "factual_in_doc"]


def pick_examples(results: pd.DataFrame, stage_name: str, tone: str, limit: int) -> pd.DataFrame:
    pool = results.loc[results["correct"]] if tone == "success" else results.loc[~results["correct"]]
    if pool.empty:
        return pool

    priority = example_type_priority(stage_name, tone)
    chosen_ids: List[int] = []
    chosen_rows: List[pd.Series] = []

    for item_type in priority:
        subset = pool.loc[pool["type"] == item_type]
        if subset.empty:
            continue
        row = subset.iloc[0]
        if int(row["id"]) in chosen_ids:
            continue
        chosen_ids.append(int(row["id"]))
        chosen_rows.append(row)
        if len(chosen_rows) == limit:
            break

    if len(chosen_rows) < limit:
        for _, row in pool.iterrows():
            if int(row["id"]) in chosen_ids:
                continue
            chosen_ids.append(int(row["id"]))
            chosen_rows.append(row)
            if len(chosen_rows) == limit:
                break

    return pd.DataFrame(chosen_rows).reset_index(drop=True)


def run_stage_analysis(stage_name: str, cfg: AgentConfig) -> pd.DataFrame:
    display_stage_banner(stage_name, cfg)
    results = evaluate_config(cfg, stage_name)
    STAGE_RESULTS[stage_name] = results

    summary = summarize_results(results)
    display_summary_cards(summary, title="Benchmark snapshot")
    display_table(
        summary[["type_label", "correct", "total", "accuracy_display"]].rename(
            columns={
                "type_label": "Category",
                "correct": "Correct",
                "total": "Total",
                "accuracy_display": "Accuracy",
            }
        ),
        title="Benchmark accuracy",
    )

    example_columns = ["id", "type", "question", "expected_answer", "answer", "evidence_docs"]
    successes = pick_examples(results[example_columns + ["correct"]], stage_name, tone="success", limit=1)
    display_examples(
        successes[example_columns] if not successes.empty else successes,
        title="Representative correct answer",
        tone="success",
        limit=1,
    )

    failures = pick_examples(results[example_columns + ["correct"]], stage_name, tone="failure", limit=2)
    display_examples(
        failures[example_columns] if not failures.empty else failures,
        title="Failure cases",
        tone="failure",
        limit=2,
    )
    return results


def build_stage_comparison() -> pd.DataFrame:
    comparison_rows = []
    for stage_name, results in STAGE_RESULTS.items():
        stage_summary = summarize_for_comparison(results)
        for _, row in stage_summary.iterrows():
            comparison_rows.append({
                "stage": stage_name,
                "category": row["category"],
                "metric": row["metric"],
            })

    if not comparison_rows:
        return pd.DataFrame()

    comparison_df = pd.DataFrame(comparison_rows)
    return comparison_df.pivot(index="stage", columns="category", values="metric").reset_index()


def show_stage_comparison() -> pd.DataFrame:
    comparison_matrix = build_stage_comparison()
    display_table(comparison_matrix, title="Stage comparison")
    return comparison_matrix
