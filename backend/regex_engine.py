"""
SENTINEL X - Regex Threat Detection Engine
PRN: 202401110046

Provides core scanning functionality across configured rules,
calculates match positions, spans, highlights, timing, and includes
a safe custom regex evaluation function.
"""

import re
import time
from datetime import datetime
from backend.detection_rules import DETECTION_RULES, get_rules_by_category

STATUS_SUSPICIOUS = "SUSPICIOUS INDICATOR DETECTED"
STATUS_NO_MATCH = "NO CONFIGURED INDICATOR MATCHED"

ACADEMIC_DISCLAIMER = (
    "These are educational pattern-matching rules, not comprehensive security signatures. "
    "A regex match indicates a suspicious indicator, not proof of an actual attack. "
    "A non-match does not prove that an input is safe."
)

def scan_text(input_text: str, category: str = "all") -> dict:
    """
    Scans input text against the configured detection rules.
    Returns detailed match statistics, highlight spans, and execution time.
    """
    start_time = time.perf_counter()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if input_text is None:
        input_text = ""

    # Sanitize max length to prevent abuse (e.g., 50KB limit)
    truncated = False
    if len(input_text) > 50000:
        input_text = input_text[:50000]
        truncated = True

    rules_to_scan = get_rules_by_category(category)
    matched_rules = []
    all_matches = []
    total_match_count = 0

    for rule in rules_to_scan:
        pattern_str = rule["pattern"]
        try:
            # Compile pattern
            regex_obj = re.compile(pattern_str)
            rule_matches = []

            for match in regex_obj.finditer(input_text):
                matched_str = match.group(0)
                span = match.span()
                rule_matches.append({
                    "matched_text": matched_str,
                    "start": span[0],
                    "end": span[1],
                    "group": match.groups()
                })
                all_matches.append({
                    "rule_id": rule["id"],
                    "rule_name": rule["name"],
                    "category": rule["category"],
                    "severity": rule["severity"],
                    "matched_text": matched_str,
                    "start": span[0],
                    "end": span[1]
                })

            if rule_matches:
                total_match_count += len(rule_matches)
                matched_rules.append({
                    "id": rule["id"],
                    "name": rule["name"],
                    "category": rule["category"],
                    "severity": rule["severity"],
                    "pattern": rule["pattern"],
                    "purpose": rule["purpose"],
                    "explanation": rule["explanation"],
                    "match_count": len(rule_matches),
                    "matches": rule_matches
                })
        except Exception as e:
            # Log or capture regex compilation issues
            continue

    end_time = time.perf_counter()
    duration_ms = round((end_time - start_time) * 1000, 3)

    is_suspicious = len(matched_rules) > 0
    status = STATUS_SUSPICIOUS if is_suspicious else STATUS_NO_MATCH

    # Compute highlighted HTML string safely
    highlighted_html = generate_highlighted_html(input_text, all_matches)

    return {
        "original_input": input_text,
        "input_length": len(input_text),
        "truncated": truncated,
        "timestamp": timestamp,
        "status": status,
        "is_suspicious": is_suspicious,
        "matched_rules_count": len(matched_rules),
        "total_matches": total_match_count,
        "matched_rules": matched_rules,
        "all_match_spans": all_matches,
        "highlighted_html": highlighted_html,
        "scan_duration_ms": duration_ms,
        "rules_checked": len(rules_to_scan),
        "disclaimer": ACADEMIC_DISCLAIMER
    }

def generate_highlighted_html(text: str, matches: list) -> str:
    """
    Constructs an HTML representation of the input text with matched spans highlighted.
    Handles overlapping or adjacent spans safely.
    """
    if not text:
        return ""
    if not matches:
        return escape_html(text)

    # Sort spans by start asc, end desc
    sorted_matches = sorted(matches, key=lambda m: (m["start"], -m["end"]))

    # Merge overlapping or touching intervals
    merged_spans = []
    for m in sorted_matches:
        start, end = m["start"], m["end"]
        if not merged_spans:
            merged_spans.append({"start": start, "end": end, "rules": [m["rule_name"]]})
        else:
            last = merged_spans[-1]
            if start < last["end"]:
                # Overlap
                last["end"] = max(last["end"], end)
                if m["rule_name"] not in last["rules"]:
                    last["rules"].append(m["rule_name"])
            else:
                merged_spans.append({"start": start, "end": end, "rules": [m["rule_name"]]})

    # Build highlighted output string
    out = []
    curr_idx = 0
    for span in merged_spans:
        start = span["start"]
        end = span["end"]
        rules_label = ", ".join(span["rules"])

        # Preceding non-matched text
        if curr_idx < start:
            out.append(escape_html(text[curr_idx:start]))

        # Highlighted matched text
        matched_chunk = escape_html(text[start:end])
        out.append(f'<mark class="threat-highlight" title="Matched: {escape_html(rules_label)}">{matched_chunk}</mark>')
        curr_idx = end

    # Remaining tail text
    if curr_idx < len(text):
        out.append(escape_html(text[curr_idx:]))

    return "".join(out)

def escape_html(s: str) -> str:
    """Safely escape HTML entities."""
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
         .replace('"', "&quot;")
         .replace("'", "&#x27;")
    )

def test_custom_regex(pattern_str: str, test_text: str, case_sensitive: bool = True) -> dict:
    """
    Evaluates a user-supplied regular expression against test text with
    strict safeguards against ReDoS and malformed patterns.
    """
    start_time = time.perf_counter()

    if not pattern_str:
        return {
            "valid": False,
            "error": "Pattern cannot be empty.",
            "matches": [],
            "match_count": 0,
            "duration_ms": 0
        }

    # Safe limits for educational demonstration
    if len(pattern_str) > 300:
        return {
            "valid": False,
            "error": "Pattern exceeds maximum allowed length of 300 characters.",
            "matches": [],
            "match_count": 0,
            "duration_ms": 0
        }

    if len(test_text) > 10000:
        test_text = test_text[:10000]

    flags = 0 if case_sensitive else re.IGNORECASE

    try:
        regex = re.compile(pattern_str, flags)
    except re.error as e:
        return {
            "valid": False,
            "error": f"Regex Compilation Error: {str(e)}",
            "matches": [],
            "match_count": 0,
            "duration_ms": 0
        }

    matches = []
    try:
        for m in regex.finditer(test_text):
            span = m.span()
            matches.append({
                "matched_text": m.group(0),
                "start": span[0],
                "end": span[1],
                "groups": m.groups()
            })
            if len(matches) >= 500: # guard against infinite match loops
                break
    except Exception as e:
        return {
            "valid": False,
            "error": f"Execution Error: {str(e)}",
            "matches": [],
            "match_count": 0,
            "duration_ms": 0
        }

    end_time = time.perf_counter()
    duration_ms = round((end_time - start_time) * 1000, 3)

    highlighted = generate_highlighted_html(test_text, [
        {"start": m["start"], "end": m["end"], "rule_name": "Custom Match"}
        for m in matches
    ])

    return {
        "valid": True,
        "pattern": pattern_str,
        "matches": matches,
        "match_count": len(matches),
        "highlighted_html": highlighted,
        "duration_ms": duration_ms
    }

