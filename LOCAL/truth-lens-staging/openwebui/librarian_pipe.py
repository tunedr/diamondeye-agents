"""
---
name: librarian-pipe
type: pipe
display_name: Librarian — DiamondEye Knowledge Steward
description: >
  Research pipe with AnythingLLM knowledge-base pre-check.
  Auto-generates search variants, runs sequential SearXNG search for gaps,
  synthesizes evidence via Agent Zero Librarian.
  Asks for clarification when the request is too vague to act on.
---
"""
from __future__ import annotations

import re
import sys
import time
from typing import Union, Generator, Iterator

import requests

SEARXNG_URL      = "http://192.168.1.2:8081/search"
LIBRARIAN_URL    = "http://192.168.1.107:7071/message"
ANYTHINGLLM_URL  = "http://192.168.1.107:3001"
ANYTHINGLLM_KEY  = "474d5ff9ba9a4db2b9430b506a07de81"

SEARCH_TOP_N     = 10
SEARCH_DELAY     = 2
LIBRARIAN_TIMEOUT = 600
MAX_VARIANTS     = 8

_OWUI_TASK_PREFIXES = (
    "### Task:\nSuggest",
    "### Task:\nGenerate",
    "### Task:\nCreate",
    "### Task:\nProvide",
)

_SIMULATION_PHRASES = (
    "simulated access",
    "simulated public records",
    "simulated search",
    "simulated results",
    "in a real system with live search",
    "as a language model i cannot access",
)

# ---------------------------------------------------------------------------
# Workspace routing
# ---------------------------------------------------------------------------

_WORKSPACE_KEYWORDS: dict[str, list[str]] = {
    "infrastructure": [
        "vm","container","docker","proxmox","truenas","unraid","tailscale",
        "network","server","disk","storage","cpu","ram","gpu","port","ip",
        "ssh","vpn","firewall","pfsense","nginx","n8n","cron","service",
        "agent zero","ollama","openwebui",
    ],
    "mediamind": [
        "plex","sonarr","radarr","tdarr","arr","movie","tv","show","episode",
        "transcode","media","video","audio","subtitle","mkv","iso","bluray",
        "mediamind","media mind",
    ],
    "publishing": [
        "book","publish","author","amazon","kdp","postiz","social","post",
        "content","blog","article","affiliate","marketing","campaign",
        "cover","manuscript","isbn","niche",
    ],
    "inspections": [
        "inspection","property","home","house","report","client","defect",
        "hvac","electrical","plumbing","roof","foundation","inspector",
    ],
}

def _select_workspace(msg: str) -> str:
    low = msg.lower()
    scores: dict[str, int] = {}
    for ws, kws in _WORKSPACE_KEYWORDS.items():
        score = sum(1 for kw in kws if kw in low)
        if score:
            scores[ws] = score
    if not scores:
        return "diamondeye-research"
    return max(scores, key=lambda k: scores[k])

# ---------------------------------------------------------------------------
# Name-spelling variant table (lowercase keys and values)
# ---------------------------------------------------------------------------
_NAME_VARIANTS: dict[str, list[str]] = {
    "madelin":   ["madelin","madelyn","madeline","madeleine"],
    "madelyn":   ["madelyn","madelin","madeline","madeleine"],
    "madeline":  ["madeline","madelyn","madelin","madeleine"],
    "madeleine": ["madeleine","madeline","madelyn","madelin"],
    "caitlin":   ["caitlin","kaitlyn","katelyn","caitlyn","kaitlin"],
    "kaitlyn":   ["kaitlyn","caitlin","katelyn","caitlyn"],
    "katelyn":   ["katelyn","kaitlyn","caitlin","caitlyn"],
    "katherine": ["katherine","kathryn","catherine","katharine"],
    "kathryn":   ["kathryn","katherine","catherine"],
    "catherine": ["catherine","katherine","kathryn","catharine"],
    "kristin":   ["kristin","kristen","kristine","christine"],
    "kristen":   ["kristen","kristin","kristine"],
    "kristine":  ["kristine","kristin","kristen","christine"],
    "christine": ["christine","kristine","christina"],
    "christina": ["christina","christine","kristina"],
    "kristina":  ["kristina","christina","cristina"],
    "jennifer":  ["jennifer","jeniffer","jenifer"],
    "ashley":    ["ashley","ashlee","ashleigh","ashlie"],
    "brittany":  ["brittany","brittney","britney","britany"],
    "brittney":  ["brittney","brittany","britney","britany"],
    "britney":   ["britney","brittney","brittany","britany"],
    "haley":     ["haley","hailey","hayley","haleigh"],
    "hailey":    ["hailey","haley","hayley"],
    "hayley":    ["hayley","haley","hailey"],
    "megan":     ["megan","meghan","meagan"],
    "meghan":    ["meghan","megan","meagan"],
    "stephanie": ["stephanie","stefanie","stephany"],
    "lindsey":   ["lindsey","lindsay","lyndsey","lyndsay"],
    "lindsay":   ["lindsay","lindsey","lyndsey"],
    "courtney":  ["courtney","kortney","kortnie"],
    "erica":     ["erica","erika","ericka"],
    "alyssa":    ["alyssa","alissa","alysa","alisa"],
    "tiffany":   ["tiffany","tiffanie"],
    "emily":     ["emily","emilee","emilie","emely"],
    "kelsey":    ["kelsey","kelsie","kelcie"],
    "alexis":    ["alexis","alexus"],
    "amy":       ["amy","aimee","amie"],
    "sarah":     ["sarah","sara"],
    "sara":      ["sara","sarah"],
    "hannah":    ["hannah","hanna"],
    "hanna":     ["hanna","hannah"],
    "rachael":   ["rachael","rachel"],
    "rachel":    ["rachel","rachael"],
    "brian":     ["brian","bryan"],
    "bryan":     ["bryan","brian"],
    "stephen":   ["stephen","steven","stefan"],
    "steven":    ["steven","stephen"],
    "jeffrey":   ["jeffrey","jeffery"],
    "jeffery":   ["jeffery","jeffrey"],
    "michael":   ["michael","micheal"],
    "nicholas":  ["nicholas","nicolas","nickolas"],
    "nicolas":   ["nicolas","nicholas"],
    "zachary":   ["zachary","zachery","zackary"],
    "phillip":   ["phillip","philip"],
    "philip":    ["philip","phillip"],
    "aaron":     ["aaron","aron"],
    "eric":      ["eric","erik","erick"],
    "erik":      ["erik","eric","erick"],
    "jacob":     ["jacob","jakob"],
}

_STATES: dict[str, str] = {
    "alabama":"AL","alaska":"AK","arizona":"AZ","arkansas":"AR",
    "california":"CA","colorado":"CO","connecticut":"CT","delaware":"DE",
    "florida":"FL","georgia":"GA","hawaii":"HI","idaho":"ID",
    "illinois":"IL","indiana":"IN","iowa":"IA","kansas":"KS",
    "kentucky":"KY","louisiana":"LA","maine":"ME","maryland":"MD",
    "massachusetts":"MA","michigan":"MI","minnesota":"MN","mississippi":"MS",
    "missouri":"MO","montana":"MT","nebraska":"NE","nevada":"NV",
    "new hampshire":"NH","new jersey":"NJ","new mexico":"NM","new york":"NY",
    "north carolina":"NC","north dakota":"ND","ohio":"OH","oklahoma":"OK",
    "oregon":"OR","pennsylvania":"PA","rhode island":"RI","south carolina":"SC",
    "south dakota":"SD","tennessee":"TN","texas":"TX","utah":"UT",
    "vermont":"VT","virginia":"VA","washington":"WA","west virginia":"WV",
    "wisconsin":"WI","wyoming":"WY",
}
_STATE_ABBREVS: dict[str, str] = {v: k.title() for k, v in _STATES.items()}

_MONTHS = {
    "january","february","march","april","may","june",
    "july","august","september","october","november","december",
    "jan","feb","mar","apr","jun","jul","aug","sep","sept","oct","nov","dec",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _name_variants(first: str) -> list[str]:
    key = first.lower()
    raw = _NAME_VARIANTS.get(key)
    if raw:
        return [v.title() for v in raw]
    result = [key]
    if key.endswith("y"):
        result += [key[:-1]+"ie", key[:-1]+"i"]
    elif key.endswith("ie"):
        result += [key[:-2]+"y", key[:-2]+"i"]
    elif key.endswith("i") and len(key) > 3:
        result += [key[:-1]+"y", key[:-1]+"ie"]
    if key.endswith("ine"):
        result.append(key[:-3]+"yn")
    elif key.endswith("yn"):
        result.append(key[:-2]+"ine")
    if key.startswith("k") and len(key) > 2:
        result.append("c"+key[1:])
    elif key.startswith("c") and len(key) > 2 and key[1] not in "aeiou":
        result.append("k"+key[1:])
    seen: set[str] = set()
    out: list[str] = []
    for v in result:
        if v not in seen:
            seen.add(v)
            out.append(v.title())
    return out[:5]


def _extract_dob(msg: str) -> str:
    for pat in [
        r'(?:dob|born|birth(?:date|day)?)\s*[:\-]?\s*(\w+\.?\s+\d{1,2},?\s+\d{4})',
        r'(?:dob|born|birth(?:date|day)?)\s*[:\-]?\s*(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})',
        r'\b(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})\b',
    ]:
        m = re.search(pat, msg, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return ""


_CITY_REJECT = (
    frozenset(_STATES) | frozenset(k.lower() for k in _STATE_ABBREVS) | _MONTHS
    | {"llc","inc","corp","ltd","dba","co","the","of","at","a","an","county"}
)

def _valid_city(candidate: str) -> str:
    words = candidate.strip().split()
    if not words or len(words) > 3:
        return ""
    if any(w.lower() in _CITY_REJECT for w in words):
        return ""
    return " ".join(w.title() for w in words)

def _extract_location(msg: str) -> tuple[str, str, str]:
    city = state = county = ""

    m = re.search(r'\b([A-Z][a-z]+)\s+[Cc]ounty\b', msg)
    if m:
        county = m.group(1).strip() + " County"

    msg_lower = msg.lower()
    state_pos = -1

    for sname in sorted(_STATES, key=len, reverse=True):
        idx = msg_lower.find(sname)
        if idx >= 0:
            state = sname.title()
            state_pos = idx
            break

    if not state:
        for mabb in re.finditer(r'\b([A-Z]{2})\b', msg):
            abbr = mabb.group(1)
            if abbr in _STATE_ABBREVS:
                state = _STATE_ABBREVS[abbr]
                state_pos = mabb.start()
                break

    if state and state_pos > 0:
        before = msg[:state_pos].rstrip(" ,")
        words = before.split()
        for n in (2, 1):
            if len(words) >= n:
                result = _valid_city(" ".join(words[-n:]))
                if result:
                    city = result
                    break

    if not city:
        m = re.search(r'\b(?:in|from)\s+([A-Za-z]+(?:\s[A-Za-z]+){0,1})', msg, re.IGNORECASE)
        if m:
            city = _valid_city(m.group(1))

    return city, state, county


def _extract_person_name(msg: str, city: str, state: str, county: str) -> tuple[str, str]:
    skip: set[str] = _MONTHS | set(_STATES) | set(_STATE_ABBREVS)
    skip.update({
        "subject","name","person","individual","find","search","look","locate",
        "background","check","research","investigate","osint","verify",
        "legal","paralegal","court","county","public","record","that","this",
        "the","girl","boy","guy","woman","man","lady","dude","them","they",
        "someone","somebody","anyone","anybody","people","who","what","when",
    })
    for word in (city, state, county):
        skip.update(w.lower() for w in word.split())

    def valid(first: str, last: str) -> bool:
        return (first.lower() not in skip and last.lower() not in skip
                and len(first) >= 2 and len(last) >= 2)

    def tc(s: str) -> str:
        return s.title()

    m = re.search(
        r'(?:subject|name|person|individual)\s*[:\-]\s*([A-Za-z]+)\s+([A-Za-z]+)',
        msg, re.IGNORECASE)
    if m and valid(m.group(1), m.group(2)):
        return tc(m.group(1)), tc(m.group(2))

    m = re.search(r'"([A-Za-z]+)\s+([A-Za-z]+)"', msg)
    if m and valid(m.group(1), m.group(2)):
        return tc(m.group(1)), tc(m.group(2))

    m = re.search(
        r'(?:find|look\s+up|search(?:\s+for)?|locate|check(?:\s+on)?|'
        r'investigate|background\s+on|run\s+a|pull(?:\s+up)?|research(?:\s+on)?)\s+'
        r'([A-Za-z]+)\s+([A-Za-z]+)',
        msg, re.IGNORECASE)
    if m and valid(m.group(1), m.group(2)):
        return tc(m.group(1)), tc(m.group(2))

    for m in re.finditer(r'([A-Z][a-z]{1,})\s+([A-Z][a-z]{1,})', msg):
        f, l = m.group(1), m.group(2)
        if valid(f, l):
            return tc(f), tc(l)

    return "", ""


# ---------------------------------------------------------------------------
# Plan builders
# ---------------------------------------------------------------------------

def _plan_person(msg: str, city: str, state: str, county: str, dob: str) -> dict:
    first, last = _extract_person_name(msg, city, state, county)

    if not last:
        q = ("I need a full name (first and last) to start. What is the subject's full name?"
             if not first
             else f"I found a first name ({first!r}) but no last name. What is the last name?")
        return {"search_type":"person","needs_clarification":True,
                "clarification":q,"entities":{},"variants":[]}

    fvariants = _name_variants(first)
    variants: list[str] = []
    seen: set[str] = set()

    def add(q: str) -> None:
        if q not in seen:
            seen.add(q)
            variants.append(q)

    for fn in fvariants[:4]:
        full = f'"{fn} {last}"'
        if city:   add(f'{full} "{city}"')
        if county: add(f'{full} "{county}"')
        if state and state != city: add(f'{full} {state}')
        if not city and not state:  add(f'{full}')

    init = f'"{first[0]}. {last}"'
    if city:  add(f'{init} "{city}"')
    elif state: add(f'{init} {state}')

    add(f'"{first} {last}" site:facebook.com')
    add(f'"{first} {last}" site:linkedin.com')

    loc = f'"{city}"' if city else (state or "")
    if loc:
        add(f'"{first} {last}" {loc} (arrest OR court OR warrant OR sentence)')

    if not city and not state:
        for fn in fvariants[1:3]:
            add(f'"{fn} {last}"')

    nc = not city and not state
    clar = ("What city, state, or county is this person associated with?" if nc else None)

    return {
        "search_type": "person",
        "needs_clarification": nc,
        "clarification": clar,
        "entities": {
            "primary_name": f"{first} {last}",
            "first_name": first,
            "last_name": last,
            "dob": dob or None,
            "location_city": city or None,
            "location_state": state or None,
            "location_county": county or None,
        },
        "variants": variants[:MAX_VARIANTS],
    }


def _plan_company(msg: str, city: str, state: str) -> dict:
    m = re.search(
        r'([A-Z][A-Za-z&\.\,\s]{2,50}?)\s*'
        r'(?:inc\.?|llc\.?|corp\.?|ltd\.?|co\.?|company|corporation|'
        r'group|partners|associates|services|solutions|enterprises)',
        msg, re.IGNORECASE)
    company = m.group(0).strip() if m else ""

    if not company:
        m = re.search(
            r'(?:find|look\s+up|search(?:\s+for)?|check(?:\s+on)?|research(?:\s+on)?)\s+'
            r'([A-Z][A-Za-z\s&]{2,50})',
            msg, re.IGNORECASE)
        company = m.group(1).strip() if m else ""

    if not company:
        return {"search_type":"company","needs_clarification":True,
                "clarification":"What is the name of the company or entity to research?",
                "entities":{},"variants":[]}

    variants: list[str] = []
    seen: set[str] = set()

    def add(q: str) -> None:
        if q not in seen:
            seen.add(q)
            variants.append(q)

    if city:  add(f'"{company}" "{city}"')
    if state: add(f'"{company}" {state}')
    add(f'"{company}"')
    base = re.sub(
        r'\s*(?:inc\.?|llc\.?|corp\.?|ltd\.?|co\.?|company|corporation)$',
        '', company, flags=re.IGNORECASE).strip()
    if base != company:
        for sfx in ("Inc","LLC","Corp","Company"):
            add(f'"{base} {sfx}"' + (f' {state}' if state else ''))
    if state:
        add(f'"{company}" "{state}" "secretary of state" OR "registered agent"')
    add(f'"{company}" site:linkedin.com')

    return {
        "search_type": "company",
        "needs_clarification": False,
        "clarification": None,
        "entities": {"primary_name":company,"location_city":city or None,"location_state":state or None},
        "variants": variants[:MAX_VARIANTS],
    }


def _plan_general(msg: str, city: str, state: str) -> dict:
    explicit = re.findall(r'"([^"]{3,})"', msg)
    if explicit:
        return {"search_type":"general","needs_clarification":False,"clarification":None,
                "entities":{"primary_name":explicit[0]},
                "variants":[f'"{q}"' for q in explicit[:MAX_VARIANTS]]}
    filler = re.compile(
        r'\b(?:please|can you|could you|help me|i need|i want|'
        r'find me|look up|search for|research|look into|check on|archive|file|catalog)\b',
        re.IGNORECASE)
    cleaned = filler.sub("", msg).strip()
    if len(cleaned) < 5:
        return {"search_type":"general","needs_clarification":True,
                "clarification":"What topic, entity, or subject should I research and archive?",
                "entities":{},"variants":[]}
    loc = f' "{city}"' if city else (f' {state}' if state else "")
    return {"search_type":"general","needs_clarification":False,"clarification":None,
            "entities":{"primary_name":cleaned},
            "variants":[f'"{cleaned}"{loc}', cleaned+loc]}


def _parse_request(message: str, history: list[dict]) -> dict:
    msg = message.strip()
    if len(history) >= 3:
        prev = history[-2].get("content","")
        if "LIBRARIAN needs clarification:" in prev:
            original = history[-3].get("content","")
            msg = f"{original} {msg}"
    dob = _extract_dob(msg)
    city, state, county = _extract_location(msg)
    msg_lower = msg.lower()
    if any(s in msg_lower for s in {
        "company","corp","llc","inc","ltd","business","entity",
        "firm","dba","registered agent","organization"}):
        return _plan_company(msg, city, state)
    if any(s in msg_lower for s in {
        "property","address","deed","parcel","land record",
        "real estate","assessor","apn"}):
        return _plan_general(msg, city, state)
    if any(s in msg_lower for s in {
        "vm","container","docker","proxmox","server","network","service",
        "plex","sonarr","radarr","tdarr","media","publish","inspection"}):
        return _plan_general(msg, city, state)
    return _plan_person(msg, city, state, county, dob)


# ---------------------------------------------------------------------------
# AnythingLLM
# ---------------------------------------------------------------------------

def _query_anythingllm(workspace: str, query: str) -> str:
    try:
        resp = requests.post(
            f"{ANYTHINGLLM_URL}/api/v1/workspace/{workspace}/chat",
            json={"message": query, "mode": "query"},
            headers={"Authorization": f"Bearer {ANYTHINGLLM_KEY}"},
            timeout=30,
        )
        if resp.status_code != 200:
            print(f"[librarian-pipe] AnythingLLM {resp.status_code}", file=sys.stderr)
            return ""
        data = resp.json()
        text = data.get("textResponse","").strip()
        if "no relevant information" in text.lower():
            return ""
        return text
    except Exception as exc:
        print(f"[librarian-pipe] AnythingLLM error: {exc}", file=sys.stderr)
        return ""


# ---------------------------------------------------------------------------
# SearXNG
# ---------------------------------------------------------------------------

def _fetch_searxng(query: str) -> list[dict]:
    try:
        resp = requests.post(SEARXNG_URL, data={"q":query,"format":"json"}, timeout=15)
        if resp.status_code != 200:
            print(f"[librarian-pipe] SearXNG {resp.status_code} for {query!r}", file=sys.stderr)
            return []
        out = []
        for item in resp.json().get("results",[])[:SEARCH_TOP_N]:
            url = item.get("url","")
            if not url or not url.startswith("http"):
                continue
            out.append({
                "title":   item.get("title","").strip(),
                "url":     url,
                "snippet": item.get("content","").strip()[:350],
            })
        return out
    except Exception as exc:
        print(f"[librarian-pipe] SearXNG error {query!r}: {exc}", file=sys.stderr)
        return []


# ---------------------------------------------------------------------------
# Evidence block
# ---------------------------------------------------------------------------

def _build_evidence_block(
    existing_knowledge: str,
    results: list[dict],
    original: str,
    plan: dict,
    query_map: dict[str, str],
    workspace: str,
) -> str:
    ent   = plan.get("entities", {})
    stype = plan.get("search_type","general").upper()
    lines = [
        "LIBRARIAN MULTI-VARIANT RESEARCH PACKAGE",
        f"Search type: {stype}",
        f"AnythingLLM workspace: {workspace}",
        f"Original request: {original[:300]}",
    ]
    if ent.get("primary_name"):
        lines.append(f"Subject: {ent['primary_name']}")
    if ent.get("dob"):
        lines.append(f"DOB: {ent['dob']}")
    if ent.get("location_city"):
        loc = ent["location_city"]
        if ent.get("location_state"):
            loc += f", {ent['location_state']}"
        lines.append(f"Location: {loc}")
    if ent.get("location_county"):
        lines.append(f"County: {ent['location_county']}")
    lines.append("")

    if existing_knowledge:
        lines += [
            "=== EXISTING KNOWLEDGE (AnythingLLM) ===",
            existing_knowledge,
            "",
        ]
    else:
        lines += ["=== EXISTING KNOWLEDGE (AnythingLLM) ===", "Nothing found in knowledge base.", ""]

    lines += [f"=== NEW SEARCH RESULTS ({len(results)} unique URLs) ===", ""]

    for i, r in enumerate(results, 1):
        lines += [
            f"[{i}] Query: {query_map.get(r['url'],'')}",
            f"     Title: {r['title']}",
            f"     URL: {r['url']}",
        ]
        if r.get("snippet"):
            lines.append(f"     Snippet: {r['snippet']}")
        lines.append("")

    lines += [
        "MANDATORY LIBRARIAN RULES:",
        "- Cite ONLY URLs provided in this package. Do not invent sources.",
        "- Compare new findings against existing knowledge. Note what changed or is new.",
        "- Classify each finding: CONFIRMED (matches existing knowledge), NEW (not previously known), CONTRADICTS (conflicts).",
        "- If existing knowledge is empty, state clearly that this is first-time research.",
        "- Do not store credentials, passwords, API keys, or private tokens in any output.",
        "- Include: SOURCE URL and DATE for every finding.",
        "- Close with three sections: CONFIRMED / NEW FINDINGS / GAPS REMAINING.",
        "- End with a FILING NOTE: which workspace and category this should be archived to.",
        "- Never write 'simulated', 'in a real system', or 'as a language model'.",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Pipe class
# ---------------------------------------------------------------------------

class Pipe:
    def __init__(self):
        self.type = "pipe"
        self.name = "Librarian — DiamondEye Knowledge Steward"
        self.id   = "librarian-pipe"

    def pipe(self, body: dict) -> Union[str, Generator, Iterator]:
        messages = body.get("messages", [])
        user_message = messages[-1]["content"] if messages else ""
        if not user_message:
            return "LIBRARIAN requires a user message."

        for prefix in _OWUI_TASK_PREFIXES:
            if user_message.startswith(prefix):
                return ""

        history = [{"role": m.get("role"), "content": m.get("content","")}
                   for m in messages]

        print(f"[librarian-pipe] request ({len(user_message)} chars): {user_message[:80]!r}",
              file=sys.stderr)

        def _stream():
            yield "LIBRARIAN — parsing request...\n\n"

            plan     = _parse_request(user_message, history)
            variants = plan.get("variants", [])
            nc       = plan.get("needs_clarification", False)
            stype    = plan.get("search_type", "general")

            if nc and not variants:
                clar = plan.get("clarification",
                                "Could you provide more details? (topic, entity, location, date range)")
                yield f"LIBRARIAN needs clarification: {clar}"
                return

            workspace = _select_workspace(user_message)
            primary   = plan.get("entities",{}).get("primary_name","")
            atl_query = primary if primary else user_message[:200]

            yield f"LIBRARIAN — checking knowledge base (workspace: {workspace})...\n"
            existing = _query_anythingllm(workspace, atl_query)
            if existing:
                yield f"  Found existing knowledge ({len(existing)} chars)\n"
            else:
                yield "  Nothing found in knowledge base — will search for all.\n"
            yield "\n"

            yield f"LIBRARIAN — {stype.upper()} | {len(variants)} variant(s)\n"
            for i, v in enumerate(variants, 1):
                yield f"  [{i}] {v}\n"
            if nc:
                yield f"\n  Note: will also ask — {plan['clarification']}\n"
            yield "\n"

            all_results: dict[str, list[dict]] = {}
            for i, query in enumerate(variants, 1):
                yield f"[{i}/{len(variants)}] {query[:80]}\n"
                hits = _fetch_searxng(query)
                all_results[query] = hits
                print(f"[librarian-pipe] variant {i}: {len(hits)} results", file=sys.stderr)
                if i < len(variants):
                    time.sleep(SEARCH_DELAY)

            yield "\n"

            seen_urls: set[str] = set()
            merged:    list[dict] = []
            query_map: dict[str, str] = {}
            for query, results in all_results.items():
                for r in results:
                    url = r.get("url","")
                    if url and url.startswith("http") and url not in seen_urls:
                        seen_urls.add(url)
                        merged.append(r)
                        query_map[url] = query

            if not merged and not existing:
                yield ("LIBRARIAN — SearXNG returned no results and AnythingLLM had no existing knowledge.\n"
                       "Verify SearXNG at http://192.168.1.2:8081 and the knowledge base is populated.")
                return

            yield (f"LIBRARIAN — {len(merged)} unique results + knowledge base context. "
                   "Sending to Agent Zero Librarian...\n\n")

            evidence = _build_evidence_block(existing, merged, user_message, plan, query_map, workspace)

            try:
                resp = requests.post(
                    LIBRARIAN_URL,
                    json={"text": evidence, "context": ""},
                    timeout=LIBRARIAN_TIMEOUT,
                )
                print(f"[librarian-pipe] Librarian HTTP {resp.status_code}", file=sys.stderr)

                if resp.status_code != 200:
                    yield f"LIBRARIAN Error: HTTP {resp.status_code}\n\n{resp.text[:500]}"
                    return

                data = resp.json()
                result_text = data.get("message", str(data))

                for phrase in _SIMULATION_PHRASES:
                    if phrase in result_text.lower():
                        print(f"[librarian-pipe] SIMULATION DETECTED: {phrase!r}", file=sys.stderr)
                        yield ("LIBRARIAN ERROR: simulated output detected.\nPhrase: " + repr(phrase))
                        return

                print(f"[librarian-pipe] clean response: {len(result_text)} chars", file=sys.stderr)

                if nc and plan.get("clarification"):
                    result_text += (
                        "\n\n---\n"
                        f"To improve future research: {plan['clarification']}"
                    )

                yield result_text

            except requests.exceptions.Timeout:
                yield "LIBRARIAN Error: Agent Zero timed out after 600s"
            except requests.exceptions.ConnectionError as exc:
                yield f"LIBRARIAN Error: cannot reach Agent Zero at {LIBRARIAN_URL} — {exc}"
            except Exception as exc:
                yield f"LIBRARIAN Error: {type(exc).__name__}: {exc}"

        return _stream()
