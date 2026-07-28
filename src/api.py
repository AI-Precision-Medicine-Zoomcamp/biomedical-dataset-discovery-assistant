"""Small HTTP API for reviewer-facing dataset discovery demos."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from src.agent import run_agent
from src.tools import DEFAULT_CATALOG_PATH, search_catalog

DEFAULT_FEEDBACK_PATH = Path("data/feedback/feedback.jsonl")


def render_home_page(catalog_path: str = DEFAULT_CATALOG_PATH) -> str:
    """Return a small dependency-free browser UI for reviewers."""

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Biomedical Dataset Discovery Assistant</title>
  <style>
    :root {{
      color-scheme: light;
      --border: #d7dce2;
      --muted: #5f6b7a;
      --bg: #f6f8fa;
      --accent: #155eef;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: #111827;
      background: white;
    }}
    header {{
      padding: 28px 24px 18px;
      border-bottom: 1px solid var(--border);
      background: var(--bg);
    }}
    main {{
      max-width: 1120px;
      margin: 0 auto;
      padding: 24px;
      display: grid;
      grid-template-columns: minmax(0, 1.1fr) minmax(320px, 0.9fr);
      gap: 24px;
    }}
    h1 {{ margin: 0 0 8px; font-size: 28px; }}
    h2 {{ margin: 0 0 12px; font-size: 18px; }}
    p {{ color: var(--muted); line-height: 1.5; }}
    label {{ display: block; font-weight: 650; margin-bottom: 8px; }}
    textarea, input, select {{
      width: 100%;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 10px 12px;
      font: inherit;
      background: white;
    }}
    textarea {{ min-height: 110px; resize: vertical; }}
    button {{
      border: 0;
      border-radius: 8px;
      padding: 10px 14px;
      font-weight: 700;
      color: white;
      background: var(--accent);
      cursor: pointer;
    }}
    button.secondary {{ background: #374151; }}
    .panel {{
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px;
      margin-bottom: 16px;
    }}
    .row {{ display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }}
    .muted {{ color: var(--muted); }}
    .answer {{
      white-space: pre-wrap;
      background: #0f172a;
      color: #e5e7eb;
      border-radius: 8px;
      padding: 14px;
      overflow: auto;
      max-height: 520px;
    }}
    .result {{
      border-top: 1px solid var(--border);
      padding: 12px 0;
    }}
    .result:first-child {{ border-top: 0; }}
    .pill {{
      display: inline-block;
      border: 1px solid var(--border);
      border-radius: 999px;
      padding: 2px 8px;
      margin-right: 6px;
      color: var(--muted);
      font-size: 12px;
    }}
    @media (max-width: 820px) {{
      main {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>Biomedical Dataset Discovery Assistant</h1>
    <p>Find candidate public biomedical datasets, inspect source evidence, and avoid overclaiming unsupported mutation or case-count evidence.</p>
    <p class="muted">Catalog: <code>{catalog_path}</code></p>
  </header>
  <main>
    <section>
      <div class="panel">
        <label for="question">Research question</label>
        <textarea id="question">Are there public datasets for KRAS G12C NSCLC with RNA-seq data?</textarea>
        <div class="row" style="margin-top: 12px;">
          <label for="topK" style="margin: 0;">Top K</label>
          <select id="topK" style="width: 90px;">
            <option>3</option>
            <option selected>4</option>
            <option>5</option>
          </select>
          <button onclick="ask()">Ask</button>
          <button class="secondary" onclick="searchOnly()">Search only</button>
        </div>
      </div>
      <div class="panel">
        <h2>Answer</h2>
        <div id="answer" class="answer">Ask a question to see a grounded dataset-discovery answer.</div>
      </div>
      <div class="panel">
        <h2>Feedback</h2>
        <div class="row">
          <select id="rating" style="width: 110px;">
            <option value="5">5 - useful</option>
            <option value="4">4</option>
            <option value="3">3</option>
            <option value="2">2</option>
            <option value="1">1 - poor</option>
          </select>
          <input id="comment" placeholder="Optional comment" style="flex: 1; min-width: 220px;">
          <button onclick="sendFeedback()">Send feedback</button>
        </div>
        <p id="feedbackStatus" class="muted"></p>
      </div>
    </section>
    <aside>
      <div class="panel">
        <h2>Retrieved datasets</h2>
        <div id="results" class="muted">Search results will appear here.</div>
      </div>
      <div class="panel">
        <h2>Tool trace</h2>
        <div id="trace" class="muted">Tool calls will appear here after Ask.</div>
      </div>
    </aside>
  </main>
  <script>
    let lastQuestion = "";
    async function ask() {{
      const question = document.getElementById("question").value;
      const topK = Number(document.getElementById("topK").value);
      lastQuestion = question;
      setText("answer", "Running search and grounded answer...");
      const response = await fetch("/ask", {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify({{ question, top_k: topK }})
      }});
      const payload = await response.json();
      if (!payload.ok) {{
        setText("answer", payload.error || "Request failed.");
        return;
      }}
      setText("answer", payload.answer);
      renderTrace(payload.tool_trace || []);
      renderResults(((payload.tool_trace || [])[0] || {{ output: {{ results: [] }} }}).output.results || []);
    }}
    async function searchOnly() {{
      const question = document.getElementById("question").value;
      const topK = Number(document.getElementById("topK").value);
      lastQuestion = question;
      const response = await fetch(`/search?question=${{encodeURIComponent(question)}}&top_k=${{topK}}`);
      const payload = await response.json();
      if (!payload.ok) {{
        renderResults([]);
        setText("results", payload.error || "Search failed.");
        return;
      }}
      renderResults(payload.results || []);
    }}
    async function sendFeedback() {{
      const rating = Number(document.getElementById("rating").value);
      const comment = document.getElementById("comment").value;
      const question = lastQuestion || document.getElementById("question").value;
      const response = await fetch("/feedback", {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify({{ question, rating, comment, source: "web_ui" }})
      }});
      const payload = await response.json();
      setText("feedbackStatus", payload.ok ? "Feedback saved." : (payload.error || "Feedback failed."));
    }}
    function renderResults(results) {{
      const target = document.getElementById("results");
      if (!results.length) {{
        target.textContent = "No results.";
        return;
      }}
      target.innerHTML = results.map(item => `
        <div class="result">
          <strong>${{escapeHtml(item.dataset_id)}}</strong><br>
          <span class="pill">${{escapeHtml(item.source || "")}}</span>
          <span class="pill">${{escapeHtml(item.match_level || "candidate")}}</span>
          <p>${{escapeHtml(item.title || "")}}</p>
          <p class="muted">${{escapeHtml((item.data_types || []).join(", ") || "data types unknown")}}</p>
          ${{item.source_url ? `<a href="${{escapeAttr(item.source_url)}}" target="_blank">Open source record</a>` : ""}}
        </div>
      `).join("");
    }}
    function renderTrace(trace) {{
      const target = document.getElementById("trace");
      if (!trace.length) {{
        target.textContent = "No trace.";
        return;
      }}
      target.innerHTML = trace.map((item, index) => `
        <div class="result">
          <strong>${{index + 1}}. ${{escapeHtml(item.name)}}</strong>
          <p class="muted">${{escapeHtml(JSON.stringify(item.input || {{}}))}}</p>
        </div>
      `).join("");
    }}
    function setText(id, text) {{
      document.getElementById(id).textContent = text;
    }}
    function escapeHtml(value) {{
      return String(value).replace(/[&<>"']/g, char => ({{ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }}[char]));
    }}
    function escapeAttr(value) {{
      return escapeHtml(value).replace(/`/g, "&#96;");
    }}
  </script>
</body>
</html>
"""


def render_monitoring_page(feedback_path: Path | str = DEFAULT_FEEDBACK_PATH) -> str:
    """Return a reviewer-facing feedback summary page."""

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Dataset Discovery Monitoring</title>
  <style>
    :root {{
      --border: #d7dce2;
      --muted: #5f6b7a;
      --bg: #f6f8fa;
      --good: #166534;
      --warn: #92400e;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: #111827;
      background: white;
    }}
    header {{
      padding: 28px 24px 18px;
      border-bottom: 1px solid var(--border);
      background: var(--bg);
    }}
    main {{
      max-width: 1120px;
      margin: 0 auto;
      padding: 24px;
    }}
    h1 {{ margin: 0 0 8px; font-size: 28px; }}
    h2 {{ margin: 0 0 12px; font-size: 18px; }}
    p {{ color: var(--muted); line-height: 1.5; }}
    a {{ color: #155eef; }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 14px;
      margin-bottom: 20px;
    }}
    .card {{
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px;
    }}
    .value {{ font-size: 28px; font-weight: 750; }}
    .muted {{ color: var(--muted); }}
    .event {{
      border-top: 1px solid var(--border);
      padding: 12px 0;
    }}
    .event:first-child {{ border-top: 0; }}
    .rating-good {{ color: var(--good); font-weight: 700; }}
    .rating-warn {{ color: var(--warn); font-weight: 700; }}
    @media (max-width: 820px) {{
      .grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}
    @media (max-width: 520px) {{
      .grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>Monitoring</h1>
    <p>Feedback summary for the Biomedical Dataset Discovery Assistant.</p>
    <p class="muted">Feedback log: <code>{feedback_path}</code> · <a href="/">Back to assistant</a></p>
  </header>
  <main>
    <section class="grid">
      <div class="card">
        <div class="muted">Total feedback</div>
        <div id="total" class="value">0</div>
      </div>
      <div class="card">
        <div class="muted">Average rating</div>
        <div id="average" class="value">n/a</div>
      </div>
      <div class="card">
        <div class="muted">Positive rate</div>
        <div id="positive" class="value">n/a</div>
      </div>
      <div class="card">
        <div class="muted">Low-rating count</div>
        <div id="low" class="value">0</div>
      </div>
    </section>
    <section class="card">
      <h2>Rating Distribution</h2>
      <div id="distribution" class="muted">Loading...</div>
    </section>
    <section class="card" style="margin-top: 16px;">
      <h2>Recent Feedback</h2>
      <div id="events" class="muted">Loading...</div>
    </section>
  </main>
  <script>
    async function loadSummary() {{
      const response = await fetch("/feedback/summary");
      const payload = await response.json();
      if (!payload.ok) {{
        document.getElementById("events").textContent = payload.error || "Could not load feedback.";
        return;
      }}
      document.getElementById("total").textContent = payload.total_events;
      document.getElementById("average").textContent = payload.average_rating === null ? "n/a" : payload.average_rating.toFixed(2);
      document.getElementById("positive").textContent = payload.positive_rate === null ? "n/a" : `${{Math.round(payload.positive_rate * 100)}}%`;
      document.getElementById("low").textContent = payload.low_rating_count;
      document.getElementById("distribution").innerHTML = [5, 4, 3, 2, 1].map(rating => {{
        const count = payload.rating_counts[String(rating)] || 0;
        return `<p><strong>${{rating}}</strong>: ${{count}}</p>`;
      }}).join("");
      const events = payload.recent_events || [];
      document.getElementById("events").innerHTML = events.length ? events.map(event => {{
        const ratingClass = Number(event.rating) >= 4 ? "rating-good" : "rating-warn";
        return `<div class="event">
          <div class="${{ratingClass}}">Rating ${{escapeHtml(event.rating)}}</div>
          <p><strong>${{escapeHtml(event.question || "")}}</strong></p>
          <p>${{escapeHtml(event.comment || "No comment")}}</p>
          <p class="muted">${{escapeHtml(event.created_at || "time unknown")}} · ${{escapeHtml(event.source || "source unknown")}}</p>
        </div>`;
      }}).join("") : "No feedback has been submitted yet.";
    }}
    function escapeHtml(value) {{
      return String(value).replace(/[&<>"']/g, char => ({{ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }}[char]));
    }}
    loadSummary();
  </script>
</body>
</html>
"""


def ask_payload(
    question: str,
    catalog_path: str = DEFAULT_CATALOG_PATH,
    top_k: int = 4,
) -> dict[str, Any]:
    """Return the same tool-grounded answer used by the local agent."""

    if not question.strip():
        return {
            "ok": False,
            "error": "question is required",
        }

    result = run_agent(question, catalog_path=catalog_path, top_k=top_k)
    return {
        "ok": True,
        "question": question,
        "catalog_path": catalog_path,
        "top_k": top_k,
        "answer": result["final_answer"],
        "tool_trace": result["tool_trace"],
    }


def search_payload(
    question: str,
    catalog_path: str = DEFAULT_CATALOG_PATH,
    top_k: int = 5,
) -> dict[str, Any]:
    """Return raw search results without generating the final answer text."""

    if not question.strip():
        return {
            "ok": False,
            "error": "question is required",
        }

    result = search_catalog(question, catalog_path=catalog_path, top_k=top_k)
    return {
        "ok": True,
        "question": question,
        "catalog_path": catalog_path,
        "top_k": top_k,
        "results": result.output["results"],
    }


def feedback_payload(
    feedback: dict[str, Any],
    feedback_path: Path | str = DEFAULT_FEEDBACK_PATH,
) -> dict[str, Any]:
    """Append a user feedback event for monitoring and review."""

    question = str(feedback.get("question", "")).strip()
    rating = feedback.get("rating")
    if not question:
        return {"ok": False, "error": "question is required"}
    if rating is None:
        return {"ok": False, "error": "rating is required"}

    try:
        rating_value = int(rating)
    except (TypeError, ValueError):
        return {"ok": False, "error": "rating must be an integer from 1 to 5"}
    if rating_value < 1 or rating_value > 5:
        return {"ok": False, "error": "rating must be an integer from 1 to 5"}

    event = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "question": question,
        "rating": rating_value,
        "answer_id": str(feedback.get("answer_id", "")),
        "comment": str(feedback.get("comment", "")),
        "source": str(feedback.get("source", "api")),
    }
    path = Path(feedback_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event, sort_keys=True) + "\n")

    return {
        "ok": True,
        "feedback_path": str(path),
        "event": event,
    }


def load_feedback_events(feedback_path: Path | str = DEFAULT_FEEDBACK_PATH) -> list[dict[str, Any]]:
    """Load valid feedback events from the JSONL feedback log."""

    path = Path(feedback_path)
    if not path.exists():
        return []

    events: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(event, dict) and isinstance(event.get("rating"), int):
                events.append(event)
    return events


def feedback_summary_payload(
    feedback_path: Path | str = DEFAULT_FEEDBACK_PATH,
    recent_limit: int = 10,
) -> dict[str, Any]:
    """Summarize feedback events for lightweight monitoring."""

    events = load_feedback_events(feedback_path)
    rating_counts = {str(rating): 0 for rating in range(1, 6)}
    for event in events:
        rating = event.get("rating")
        if isinstance(rating, int) and 1 <= rating <= 5:
            rating_counts[str(rating)] += 1

    total = sum(rating_counts.values())
    rating_sum = sum(int(rating) * count for rating, count in rating_counts.items())
    positive_count = rating_counts["4"] + rating_counts["5"]
    low_rating_count = rating_counts["1"] + rating_counts["2"]
    average_rating = round(rating_sum / total, 2) if total else None
    positive_rate = round(positive_count / total, 4) if total else None

    return {
        "ok": True,
        "feedback_path": str(feedback_path),
        "total_events": total,
        "average_rating": average_rating,
        "positive_rate": positive_rate,
        "low_rating_count": low_rating_count,
        "rating_counts": rating_counts,
        "recent_events": list(reversed(events[-recent_limit:])),
    }


class DatasetDiscoveryHandler(BaseHTTPRequestHandler):
    catalog_path = DEFAULT_CATALOG_PATH

    def _write_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _write_html(self, html: str, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if not length:
            return {}
        body = self.rfile.read(length).decode("utf-8")
        return json.loads(body)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)

        if parsed.path == "/":
            self._write_html(render_home_page(self.catalog_path))
            return

        if parsed.path == "/monitoring":
            self._write_html(render_monitoring_page())
            return

        if parsed.path == "/health":
            self._write_json(
                {
                    "ok": True,
                    "service": "biomedical-dataset-discovery-api",
                    "catalog_path": self.catalog_path,
                }
            )
            return

        if parsed.path == "/feedback/summary":
            self._write_json(feedback_summary_payload())
            return

        if parsed.path == "/search":
            question = query.get("question", [""])[0]
            top_k = int(query.get("top_k", ["5"])[0])
            payload = search_payload(
                question,
                catalog_path=self.catalog_path,
                top_k=top_k,
            )
            status = HTTPStatus.OK if payload["ok"] else HTTPStatus.BAD_REQUEST
            self._write_json(payload, status)
            return

        self._write_json(
            {
                "ok": False,
                "error": "not found",
                "routes": [
                    "GET /health",
                    "GET /monitoring",
                    "GET /feedback/summary",
                    "GET /search?question=...",
                    "POST /ask",
                    "POST /feedback",
                ],
            },
            HTTPStatus.NOT_FOUND,
        )

    def do_POST(self) -> None:
        parsed = urlparse(self.path)

        try:
            body = self._read_json_body()

            if parsed.path == "/feedback":
                payload = feedback_payload(body)
                status = HTTPStatus.OK if payload["ok"] else HTTPStatus.BAD_REQUEST
                self._write_json(payload, status)
                return

            if parsed.path != "/ask":
                self._write_json({"ok": False, "error": "not found"}, HTTPStatus.NOT_FOUND)
                return

            question = str(body.get("question", ""))
            catalog_path = str(body.get("catalog_path") or self.catalog_path)
            top_k = int(body.get("top_k", 4))
            payload = ask_payload(question, catalog_path=catalog_path, top_k=top_k)
            status = HTTPStatus.OK if payload["ok"] else HTTPStatus.BAD_REQUEST
            self._write_json(payload, status)
        except json.JSONDecodeError:
            self._write_json(
                {"ok": False, "error": "invalid JSON body"},
                HTTPStatus.BAD_REQUEST,
            )


def run_server(host: str, port: int, catalog_path: str) -> None:
    DatasetDiscoveryHandler.catalog_path = catalog_path
    server = ThreadingHTTPServer((host, port), DatasetDiscoveryHandler)
    print(f"Serving dataset discovery API at http://{host}:{port}")
    print(f"Catalog: {catalog_path}")
    server.serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--catalog", default=DEFAULT_CATALOG_PATH)
    args = parser.parse_args()
    run_server(args.host, args.port, args.catalog)


if __name__ == "__main__":
    main()
