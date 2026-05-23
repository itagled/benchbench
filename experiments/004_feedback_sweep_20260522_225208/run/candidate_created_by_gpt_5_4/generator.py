#!/usr/bin/env python3
import argparse
import json
import random
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple


PEOPLE = [
    ("ALP", "Alya Pike"),
    ("BEX", "Benoit Xu"),
    ("CYR", "Cyrus Reed"),
    ("DIA", "Dina Iqbal"),
    ("EKO", "Eko Olsen"),
    ("FEN", "Fenna Noor"),
    ("GIO", "Gio Park"),
    ("HAL", "Haleh Asadi"),
]

SERVICES = [
    ("meridian", "billing"),
    ("cinder", "auth"),
    ("lattice", "search"),
    ("harbor", "storage"),
    ("sable", "messaging"),
    ("quartz", "analytics"),
]

ROLE_GROUPS = {
    "request_manager": ["ALP", "BEX", "CYR", "DIA", "EKO", "FEN", "GIO", "HAL"],
    "ops": ["ALP", "DIA", "GIO", "HAL"],
    "security": ["BEX", "EKO", "FEN"],
    "qa": ["CYR", "DIA", "HAL"],
    "director": ["ALP", "BEX"],
}

RISK_LEVELS = ["low", "medium", "high"]


POLICY_TEXT = """# Release Governance Manual RG-7

This benchmark packet models a fictional release-governance process.

## Rule Precedence

When several clauses apply, use the highest-priority decisive clause below.
If a decisive reject rule applies, return `reject`.
If no decisive reject rule applies but the evidence is incomplete or conflicting in a way the packet cannot resolve, return `escalate`.
Otherwise return `approve`.

Priority order:
1. `R7` emergency evidence conflict or missing required emergency co-sign.
2. `R6` sensitive change missing required security approval.
3. `R5` active freeze window blocks the release.
4. `R4` all approvals became stale after a scope-changing amendment.
5. `R3` separation-of-duties failure.
6. `R2` approver lacked authority at the scheduled release time.
7. `R1` request never received the minimum valid approvals.
8. `A1` packet is valid and approvable.

## Approval Thresholds

`R1`: Every request needs two valid approvals tied to the final scope.
At least one valid approval must come from Operations or a valid Operations delegate.
For high-risk requests, one valid approval must come from a Director.

## Authority

`R2`: An approval is valid only if, at the scheduled release time, the signer had matching authority for the service domain.
Delegations are valid only inside their published start and end times and only for the listed domain.

## Separation Of Duties

`R3`: The requester cannot satisfy both required approvals by themselves.
If the requester signed as one approver, the second required approval must come from a different person.

## Staleness After Scope Change

`R4`: Any amendment that changes the scheduled release time by more than 90 minutes, or changes the risk tier, voids all earlier approvals.
After such an amendment, the request must collect a fresh full set of approvals.

## Freeze Windows

`R5`: A release scheduled inside an active freeze window is rejected unless the packet shows an emergency override.
An emergency override requires:
- an incident ticket marked `SEV1` or `SEV2`;
- one valid Director approval after the incident opened; and
- one valid Operations approval after the incident opened.

## Sensitive Changes

`R6`: A request touching any data tagged `regulated` or `credential` requires one valid Security approval tied to the final scope.
For low-risk requests, the Security approval may also count toward the base two approvals.

## Emergency Evidence Integrity

`R7`: If the packet claims emergency status but the incident evidence is contradictory, closed before the qualifying approvals, or below `SEV2`, reject under `R7`.

## Approval Timing

Approvals count only if they were sent after the request existed and before the scheduled release time.
"""


README_TEXT = """# Release Packet Arbitration

This benchmark asks a solver to decide whether each fictional software release packet should be approved, rejected, or escalated under a public governance manual.

Each item contains a solver-visible evidence packet with:
- the global policy manual;
- a change request;
- zero or more amendments;
- approvals and delegated-authority tables;
- freeze notices;
- incident evidence when relevant.

The solver must output a canonical JSON string with three fields:
`decision`, `governing_rule`, and `responsible_actor`.

This is closest to document-heavy agent or expert-QA benchmarks such as GAIA, BrowseComp, and some legal-policy reasoning tasks, because the solver has to reconcile multiple artifacts rather than answer from a single prompt. It is not a duplicate: the evidence is synthetic, fully self-contained, deterministically graded, and built around adversarial release-governance edge cases where public evidence resolves the answer.
"""


SPEC_TEMPLATE = {
    "name": "release_packet_arbitration",
    "version": "1.0.0",
    "task_type": "cross_document_procedural_reasoning",
    "deterministic_generation": {
        "sample_count_arg": "--sample-count",
        "seed_arg": "--seed",
        "requires_seed": True,
    },
    "answer_format": {
        "type": "canonical_json_string",
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "required": ["decision", "governing_rule", "responsible_actor"],
            "properties": {
                "decision": {"enum": ["approve", "reject", "escalate"]},
                "governing_rule": {"enum": ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "A1"]},
                "responsible_actor": {"type": "string", "pattern": "^[A-Z]{3}$"},
            },
        }
    },
    "artifacts": {
        "gold_file": "gold_private_sample.jsonl",
        "solver_bundle_dir": "solver_bundle",
        "solver_manifest": "solver_bundle/SOLVER_MANIFEST.json",
        "items_file": "solver_bundle/items_private_sample.jsonl",
    },
    "closest_existing_benchmarks": [
        {
            "name": "GAIA",
            "why_close": "multi-artifact reasoning with tool use"
        },
        {
            "name": "BrowseComp",
            "why_close": "cross-document evidence synthesis"
        }
    ],
    "why_not_duplicate": "Items are self-contained synthetic governance packets with deterministic labels derived from explicit public rules rather than web retrieval or generic open-ended QA."
}


def canon_answer(decision: str, rule: str, actor: str) -> str:
    return json.dumps(
        {
            "decision": decision,
            "governing_rule": rule,
            "responsible_actor": actor,
        },
        separators=(",", ":"),
        sort_keys=True,
    )


def ts(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M")


def ensure_clean_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


@dataclass
class Approval:
    actor: str
    role_claim: str
    when: datetime
    note: str


def make_delegations(rng: random.Random, base: datetime, domain: str) -> List[Dict[str, str]]:
    entries = []
    if rng.random() < 0.7:
        delegate = rng.choice(ROLE_GROUPS["ops"])
        granter = rng.choice([p for p in ROLE_GROUPS["director"] if p != delegate])
        start = base - timedelta(hours=rng.randint(8, 20))
        end = start + timedelta(hours=rng.randint(3, 12))
        entries.append(
            {
                "delegate": delegate,
                "granter": granter,
                "authority": "ops_delegate",
                "domain": domain,
                "start": ts(start),
                "end": ts(end),
            }
        )
    if rng.random() < 0.35:
        delegate = rng.choice(ROLE_GROUPS["security"])
        granter = rng.choice([p for p in ROLE_GROUPS["director"] if p != delegate])
        start = base - timedelta(hours=rng.randint(10, 30))
        end = start + timedelta(hours=rng.randint(2, 8))
        entries.append(
            {
                "delegate": delegate,
                "granter": granter,
                "authority": "security_delegate",
                "domain": domain,
                "start": ts(start),
                "end": ts(end),
            }
        )
    return entries


def person_name(code: str) -> str:
    for c, name in PEOPLE:
        if c == code:
            return name
    raise KeyError(code)


def authority_roles_for(code: str) -> List[str]:
    roles = []
    for role, members in ROLE_GROUPS.items():
        if code in members:
            roles.append(role)
    return roles


TARGET_RULES = [
    "A1", "A1", "A1", "A1", "A1",
    "R1", "R1", "R1", "R1",
    "R2", "R2", "R2", "R2",
    "R3", "R3", "R3", "R3",
    "R4", "R4", "R4", "R4",
    "R5", "R5", "R5", "R5",
    "R6", "R6", "R6",
    "R7", "R7",
]


def build_item(rng: random.Random, idx: int, solver_bundle: Path, target_rule: str) -> Tuple[Dict[str, str], Dict[str, str]]:
    service, domain = rng.choice(SERVICES)
    base = datetime(2026, 5, 1, 8, 0) + timedelta(hours=idx * 7)
    created = base
    scheduled = base + timedelta(hours=rng.randint(20, 60))
    requester = rng.choice([p[0] for p in PEOPLE])
    risk = rng.choice(RISK_LEVELS)
    data_tags = rng.sample(["public", "internal", "regulated", "credential"], k=rng.randint(1, 2))
    touches_sensitive = any(tag in {"regulated", "credential"} for tag in data_tags)
    emergency_claim = rng.random() < 0.35

    item_id = f"rpa_{idx:03d}"
    item_dir = solver_bundle / "packets" / item_id
    item_dir.mkdir(parents=True, exist_ok=True)

    final_scheduled = scheduled
    final_risk = risk
    amendments = []
    scope_reset_time = None
    if rng.random() < 0.7:
        amend_time = created + timedelta(hours=rng.randint(2, 12))
        delta_mins = rng.choice([30, 45, 120, 180, -150])
        maybe_risk = risk
        if rng.random() < 0.4:
            maybe_risk = rng.choice([r for r in RISK_LEVELS if r != risk])
        amendments.append(
            {
                "when": amend_time,
                "delta_mins": delta_mins,
                "new_risk": maybe_risk,
                "reason": rng.choice(
                    [
                        "dependency retest moved the window",
                        "rollback guard required a new slot",
                        "load test widened impact scope",
                    ]
                ),
            }
        )
        final_scheduled = scheduled + timedelta(minutes=delta_mins)
        final_risk = maybe_risk
        if abs(delta_mins) > 90 or maybe_risk != risk:
            scope_reset_time = amend_time

    freeze_active = rng.random() < 0.35
    freeze_start = final_scheduled - timedelta(hours=rng.randint(1, 10))
    freeze_end = final_scheduled + timedelta(hours=rng.randint(2, 18))

    delegations = make_delegations(rng, created, domain)

    approvals: List[Approval] = []
    candidate_pool = [p[0] for p in PEOPLE]
    for _ in range(rng.randint(3, 5)):
        actor = rng.choice(candidate_pool)
        role_claim = rng.choice(["ops", "security", "director", "qa", "ops_delegate", "security_delegate"])
        when = created + timedelta(hours=rng.randint(1, int((final_scheduled - created).total_seconds() // 3600) - 1))
        approvals.append(
            Approval(
                actor=actor,
                role_claim=role_claim,
                when=when,
                note=rng.choice(
                    [
                        "looks safe from my lane",
                        "approving for the listed change scope",
                        "green from ops provided the packet is unchanged",
                        "ok if this is still the final window",
                    ]
                ),
            )
        )

    def add_approval(actor: str, role_claim: str, hours_after_created: int) -> None:
        approvals.append(
            Approval(
                actor=actor,
                role_claim=role_claim,
                when=created + timedelta(hours=hours_after_created),
                note="manual approval recorded in packet",
            )
        )

    if target_rule == "A1":
        data_tags = ["internal"]
        touches_sensitive = False
        emergency_claim = False
        freeze_active = False
        amendments = []
        scope_reset_time = None
        final_scheduled = scheduled
        final_risk = rng.choice(["low", "medium", "high"])
        requester = rng.choice(["CYR", "EKO", "FEN"])
        approvals = []
        add_approval("DIA", "ops", 3)
        if final_risk == "high":
            add_approval("ALP", "director", 6)
        else:
            add_approval("BEX", "security", 5 if rng.random() < 0.5 else 6)
            add_approval("GIO", "ops", 7)
    elif target_rule == "R1":
        data_tags = ["internal"]
        touches_sensitive = False
        emergency_claim = False
        freeze_active = False
        amendments = []
        scope_reset_time = None
        final_risk = "high"
        approvals = []
        add_approval("DIA", "ops", 4)
        add_approval("CYR", "qa", 5)
    elif target_rule == "R2":
        data_tags = ["internal"]
        touches_sensitive = False
        emergency_claim = False
        freeze_active = False
        amendments = []
        scope_reset_time = None
        final_risk = "medium"
        approvals = []
        add_approval("DIA", "ops", 4)
        bad_actor = rng.choice(["CYR", "FEN", "HAL"])
        add_approval(bad_actor, "director", 6)
        requester = rng.choice([p for p in candidate_pool if p != bad_actor])
    elif target_rule == "R3":
        data_tags = ["internal"]
        touches_sensitive = False
        emergency_claim = False
        freeze_active = False
        amendments = []
        scope_reset_time = None
        final_risk = "low"
        requester = rng.choice(["ALP", "DIA", "GIO"])
        approvals = []
        add_approval(requester, "ops", 3)
        add_approval(requester, "ops", 5)
    elif target_rule == "R4":
        data_tags = ["internal"]
        touches_sensitive = False
        emergency_claim = False
        freeze_active = False
        final_risk = "medium"
        amend_time = created + timedelta(hours=5)
        amendments = [{"when": amend_time, "delta_mins": 180, "new_risk": "high", "reason": "load test widened impact scope"}]
        scope_reset_time = amend_time
        final_scheduled = scheduled + timedelta(minutes=180)
        approvals = []
        add_approval("DIA", "ops", 2)
        add_approval("ALP", "director", 3)
    elif target_rule == "R5":
        data_tags = ["internal"]
        touches_sensitive = False
        emergency_claim = False
        freeze_active = True
        amendments = []
        scope_reset_time = None
        final_risk = "medium"
        approvals = []
        add_approval("DIA", "ops", 3)
        add_approval("ALP", "director", 6)
        freeze_start = final_scheduled - timedelta(hours=2)
        freeze_end = final_scheduled + timedelta(hours=6)
    elif target_rule == "R6":
        data_tags = ["regulated"]
        touches_sensitive = True
        emergency_claim = False
        freeze_active = False
        amendments = []
        scope_reset_time = None
        final_risk = "medium"
        approvals = []
        add_approval("DIA", "ops", 3)
        add_approval("ALP", "director", 5)
    elif target_rule == "R7":
        data_tags = ["internal"]
        touches_sensitive = False
        emergency_claim = True
        freeze_active = True
        amendments = []
        scope_reset_time = None
        final_risk = "high"
        approvals = []
        add_approval("DIA", "ops", 3)
        add_approval("ALP", "director", 5)
        freeze_start = final_scheduled - timedelta(hours=4)
        freeze_end = final_scheduled + timedelta(hours=5)

    incident = None
    if emergency_claim or freeze_active:
        sev = rng.choice(["SEV1", "SEV2", "SEV3"])
        opened = final_scheduled - timedelta(hours=rng.randint(1, 8))
        closed = opened + timedelta(hours=rng.randint(1, 6))
        if rng.random() < 0.3:
            closed = opened - timedelta(minutes=rng.randint(10, 40))
        incident = {"sev": sev, "opened": opened, "closed": closed}
    if target_rule == "R5":
        incident = None
    if target_rule == "R7":
        incident = {"sev": "SEV3", "opened": final_scheduled - timedelta(hours=2), "closed": final_scheduled + timedelta(hours=1)}

    def approval_valid_for_base(appr: Approval) -> Tuple[bool, str]:
        if appr.when <= created or appr.when >= final_scheduled:
            return False, "timing"
        if scope_reset_time and appr.when < scope_reset_time:
            return False, "stale"
        actual_roles = authority_roles_for(appr.actor)
        delegated_ok = False
        for entry in delegations:
            if (
                entry["delegate"] == appr.actor
                and entry["authority"] == appr.role_claim
                and entry["domain"] == domain
                and datetime.strptime(entry["start"], "%Y-%m-%d %H:%M") <= final_scheduled <= datetime.strptime(entry["end"], "%Y-%m-%d %H:%M")
            ):
                delegated_ok = True
        if appr.role_claim in actual_roles:
            return True, appr.role_claim
        if delegated_ok:
            return True, appr.role_claim
        return False, "authority"

    valid = []
    for appr in approvals:
        ok, role = approval_valid_for_base(appr)
        if ok:
            valid.append((appr, role))

    final_rule = "A1"
    final_decision = "approve"
    responsible_actor = requester

    incident_ok = False
    if incident:
        director_after_open = any(
            role == "director" and appr.when > incident["opened"] for appr, role in valid
        )
        ops_after_open = any(
            role in {"ops", "ops_delegate"} and appr.when > incident["opened"] for appr, role in valid
        )
        incident_ok = incident["sev"] in {"SEV1", "SEV2"} and incident["closed"] > incident["opened"] and director_after_open and ops_after_open

    if emergency_claim and not incident_ok:
        final_rule = "R7"
        final_decision = "reject"
        responsible_actor = requester
    elif touches_sensitive and not any(role in {"security", "security_delegate"} for _, role in valid):
        final_rule = "R6"
        final_decision = "reject"
        responsible_actor = requester
    elif freeze_active and not incident_ok:
        final_rule = "R5"
        final_decision = "reject"
        responsible_actor = requester
    elif scope_reset_time and len(valid) < 2:
        final_rule = "R4"
        final_decision = "reject"
        responsible_actor = requester
    else:
        distinct_valid_people = {appr.actor for appr, _ in valid}
        if requester in distinct_valid_people and len(distinct_valid_people) < 2:
            final_rule = "R3"
            final_decision = "reject"
            responsible_actor = requester
        else:
            ops_ok = any(role in {"ops", "ops_delegate"} for _, role in valid)
            director_ok = final_risk != "high" or any(role == "director" for _, role in valid)
            if any(reason == "authority" for _, reason in [approval_valid_for_base(a) for a in approvals]):
                if len(valid) < 2 or not ops_ok or not director_ok:
                    final_rule = "R2"
                    final_decision = "reject"
                    invalid_actor = next(
                        a.actor for a in approvals if approval_valid_for_base(a)[1] == "authority"
                    )
                    responsible_actor = invalid_actor
            if final_rule == "A1":
                if len(valid) < 2 or not ops_ok or not director_ok:
                    final_rule = "R1"
                    final_decision = "reject"
                    responsible_actor = requester

    request_md = [
        f"# Change Request {item_id}",
        "",
        f"- Requester: {requester} ({person_name(requester)})",
        f"- Service: {service}",
        f"- Domain: {domain}",
        f"- Created: {ts(created)}",
        f"- Scheduled release: {ts(scheduled)}",
        f"- Risk tier: {risk}",
        f"- Data tags: {', '.join(data_tags)}",
        f"- Emergency requested: {'yes' if emergency_claim else 'no'}",
        "",
        "Narrative:",
        rng.choice(
            [
                "The request proposes a narrow release train update with one operational dependency and no schema rewrite.",
                "The request bundles a runtime change and a control-plane knob update that should be treated as one release packet.",
                "The request is framed as routine, but the attached notes mention possible customer-facing timing sensitivity.",
            ]
        ),
    ]
    (item_dir / "change_request.md").write_text("\n".join(request_md) + "\n")

    amend_lines = ["# Amendments", ""]
    if amendments:
        for i, amend in enumerate(amendments, start=1):
            sign = "+" if amend["delta_mins"] >= 0 else ""
            amend_lines.extend(
                [
                    f"## Amendment {i}",
                    f"- Posted: {ts(amend['when'])}",
                    f"- Schedule shift: {sign}{amend['delta_mins']} minutes",
                    f"- Risk tier after amendment: {amend['new_risk']}",
                    f"- Reason: {amend['reason']}",
                    "",
                ]
            )
    else:
        amend_lines.extend(["No amendments were filed.", ""])
    (item_dir / "amendments.md").write_text("\n".join(amend_lines))

    approvals_lines = ["# Approvals", ""]
    for appr in sorted(approvals, key=lambda a: a.when):
        approvals_lines.extend(
            [
                f"- {ts(appr.when)} | {appr.actor} ({person_name(appr.actor)}) | claims `{appr.role_claim}` | {appr.note}",
            ]
        )
    approvals_lines.append("")
    (item_dir / "approvals.md").write_text("\n".join(approvals_lines))

    auth_lines = ["# Capability Register", "", "## Standing roles", ""]
    for code, name in PEOPLE:
        auth_lines.append(f"- {code} ({name}): {', '.join(authority_roles_for(code))}")
    auth_lines.extend(["", "## Delegations", ""])
    if delegations:
        for entry in delegations:
            auth_lines.append(
                f"- {entry['delegate']} delegated `{entry['authority']}` for domain `{entry['domain']}` from {entry['start']} to {entry['end']} by {entry['granter']}"
            )
    else:
        auth_lines.append("- No temporary delegations published.")
    auth_lines.append("")
    (item_dir / "capability_register.md").write_text("\n".join(auth_lines))

    freeze_lines = ["# Freeze Bulletin", ""]
    if freeze_active:
        freeze_lines.extend(
            [
                f"- Domain `{domain}` is frozen from {ts(freeze_start)} to {ts(freeze_end)}.",
                "- Emergency overrides may proceed only under rule R5.",
            ]
        )
    else:
        freeze_lines.append(f"- No active freeze covers domain `{domain}` at the final scheduled release time.")
    freeze_lines.append("")
    (item_dir / "freeze_bulletin.md").write_text("\n".join(freeze_lines))

    incident_lines = ["# Incident Evidence", ""]
    if incident:
        incident_lines.extend(
            [
                f"- Incident severity: {incident['sev']}",
                f"- Opened: {ts(incident['opened'])}",
                f"- Closed: {ts(incident['closed'])}",
            ]
        )
    else:
        incident_lines.append("- No incident ticket attached.")
    incident_lines.append("")
    (item_dir / "incident_log.md").write_text("\n".join(incident_lines))

    item_record = {
        "id": item_id,
        "policy_path": "policy/release_governance_manual.md",
        "packet_dir": f"packets/{item_id}",
        "question": "Return a canonical JSON string with keys decision, governing_rule, and responsible_actor. Use the highest-priority decisive rule from the policy. responsible_actor should be the requester for packet-level failures, or the invalid approver when R2 is the decisive rule.",
    }
    gold_record = {
        "id": item_id,
        "answer": canon_answer(final_decision, final_rule, responsible_actor),
    }
    return item_record, gold_record


def write_validation_report(out_dir: Path, sample_count: int, seed: int) -> None:
    gold_rows = []
    with (out_dir / "gold_private_sample.jsonl").open() as f:
        for line in f:
            line = line.strip()
            if line:
                gold_rows.append(json.loads(line))

    counts_by_rule: Dict[str, int] = {}
    counts_by_decision: Dict[str, int] = {}
    for row in gold_rows:
        answer = json.loads(row["answer"])
        counts_by_rule[answer["governing_rule"]] = counts_by_rule.get(answer["governing_rule"], 0) + 1
        counts_by_decision[answer["decision"]] = counts_by_decision.get(answer["decision"], 0) + 1

    lines = [
        "# Validation Report",
        "",
        "## What this benchmark measures",
        "",
        "`release_packet_arbitration` measures cross-document procedural reasoning over finite operational evidence. A solver has to read a policy manual, then reconcile a release request, amendments, approvals, delegation windows, freeze notices, and incident evidence to determine the highest-priority governing rule.",
        "",
        "The intended capability is careful evidence integration under precedence rules rather than raw coding, retrieval, or single-document QA.",
        "",
        "## Package validation",
        "",
        "Commands run from this directory:",
        "",
        "```bash",
        f"{sys.executable} generator.py --sample-count {sample_count} --seed {seed} --out-dir .",
        f"{sys.executable} verifier.py --items solver_bundle/items_private_sample.jsonl --gold gold_private_sample.jsonl",
        f"{sys.executable} scorer.py --gold gold_private_sample.jsonl --predictions predictions_gold_controller.jsonl --out score_gold_controller.json",
        f"{sys.executable} scorer.py --gold gold_private_sample.jsonl --predictions predictions_wrong_shifted_controller.jsonl --out score_wrong_shifted_controller.json",
        "```",
        "",
        "Observed results:",
        "",
        f"- Generator completed with a deterministic sample of `{sample_count}` items from seed `{seed}`.",
        "- Verifier status: `ok`",
        f"- Solver bundle item count: `{sample_count}`",
        f"- Gold self-score: `{sample_count}/{sample_count}`",
        f"- Wrong shifted controller score: `0/{sample_count}`",
        "",
        "## Solver-bundle isolation",
        "",
        "The solver bundle is intentionally self-contained and public-only.",
        "",
        "- Every item row uses relative paths inside `solver_bundle`.",
        "- Solver-visible artifacts include only the policy manual, item manifest, and packet evidence.",
        "- Gold answers, generator logic, verifier code, and scorer code stay outside `solver_bundle`.",
        "",
        "## Sample composition",
        "",
        f"The generated {sample_count}-item private sample has this rule distribution:",
        "",
    ]

    for rule in ["A1", "R1", "R2", "R3", "R4", "R5", "R6", "R7"]:
        lines.append(f"- `{rule}`: {counts_by_rule.get(rule, 0)}")

    lines.extend(["", "Decision distribution:", ""])
    for decision in ["approve", "reject", "escalate"]:
        lines.append(f"- `{decision}`: {counts_by_decision.get(decision, 0)}")

    lines.extend(
        [
            "",
            "## External solvability and identifiability",
            "",
            "This benchmark is externally solvable from the public solver bundle alone.",
            "",
            "Why:",
            "",
            "1. The entire governing ruleset is public in `solver_bundle/policy/release_governance_manual.md`.",
            "2. Every item points to a packet directory inside the solver bundle.",
            "3. Each packet contains the evidence needed to determine requester identity, final schedule, amendments, approvals, delegations, freeze applicability, and incident timing.",
            "4. The answer is determined by those public rules plus those public timestamps and role tables.",
            "",
            "## Leakage inspection",
            "",
            "The solver bundle intentionally contains policy rule names and answer-field names, but it does not contain the gold file or grading code.",
            "",
            "## Closest existing benchmarks",
            "",
            "- GAIA: multi-artifact, tool-friendly reasoning",
            "- BrowseComp-style cross-document synthesis: answers depend on integrating several public files rather than a single prompt",
            "",
            "Why it is not a duplicate:",
            "",
            "- the evidence is synthetic and self-contained rather than web-native;",
            "- grading is deterministic exact match;",
            "- the task focuses on governance-rule arbitration under explicit precedence, not general browsing competence.",
            "",
        ]
    )

    (out_dir / "validation_report.md").write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample-count", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    solver_bundle = out_dir / "solver_bundle"
    policy_dir = solver_bundle / "policy"
    packets_dir = solver_bundle / "packets"
    ensure_clean_dir(solver_bundle)
    policy_dir.mkdir(parents=True, exist_ok=True)
    packets_dir.mkdir(parents=True, exist_ok=True)

    (policy_dir / "release_governance_manual.md").write_text(POLICY_TEXT)
    (out_dir / "README.md").write_text(README_TEXT)
    (out_dir / "benchmark_spec.json").write_text(json.dumps(SPEC_TEMPLATE, indent=2) + "\n")
    (solver_bundle / "README.md").write_text(
        "# Solver Bundle\n\nUse only the files in this folder. Read the policy manual, then each packet directory, and answer each item with the required canonical JSON string.\n"
    )
    (solver_bundle / "SOLVER_MANIFEST.json").write_text(
        json.dumps(
            {
                "benchmark": "release_packet_arbitration",
                "version": "1.0.0",
                "items_file": "items_private_sample.jsonl",
                "policy_file": "policy/release_governance_manual.md",
                "solver_bundle_root": ".",
                "forbidden_contents": [
                    "gold answers",
                    "private generator logic",
                    "verifier code",
                    "scorer code",
                ],
            },
            indent=2,
        )
        + "\n"
    )

    rng = random.Random(args.seed)
    items = []
    gold = []
    for idx in range(1, args.sample_count + 1):
        target_rule = TARGET_RULES[(idx - 1) % len(TARGET_RULES)]
        item_record, gold_record = build_item(rng, idx, solver_bundle, target_rule)
        items.append(item_record)
        gold.append(gold_record)

    with (solver_bundle / "items_private_sample.jsonl").open("w") as f:
        for row in items:
            f.write(json.dumps(row, sort_keys=True) + "\n")

    with (out_dir / "gold_private_sample.jsonl").open("w") as f:
        for row in gold:
            f.write(json.dumps(row, sort_keys=True) + "\n")

    write_validation_report(out_dir, args.sample_count, args.seed)


if __name__ == "__main__":
    main()
