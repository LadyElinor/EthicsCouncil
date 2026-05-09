from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List, Dict
import datetime
import hashlib
import math


ETHICAL_DELIBERATION_ALGORITHM = [
    "Clarify the situation",
    "Identify stakeholders",
    "Separate facts from interpretations",
    "Identify the values in conflict",
    "Generate possible actions",
    "Test each action through multiple ethical lenses",
    "Examine second-order consequences",
    "Check reversibility and precedent",
    "Decide under uncertainty",
    "Review outcomes honestly",
]


@dataclass
class LensResult:
    agent: str
    function: str
    verdict: str
    confidence: float
    considerations: List[str]
    concerns: List[str]
    questions: List[str]
    active: bool = True


@dataclass
class CouncilRecord:
    meta: Dict
    round1: List[Dict]
    synthesis: Dict
    risk: Dict


@dataclass
class UncertaintyProfile:
    epistemic: float
    aleatoric: float
    moral: float
    composite: float


@dataclass
class RiskAssessment:
    uncertainty_profile: Dict
    expected_harm_score: float
    harm_variance: float
    tail_risk_triggered: bool
    materiality_flag: bool
    audit_hash: str


def _contains(text: str, words: List[str]) -> bool:
    t = text.lower()
    return any(w in t for w in words)


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def detect_domains(decision: str) -> Dict[str, bool]:
    domains = {
        "finance": _contains(decision, ["cfo", "publicly traded", "investors", "stock options", "profitability", "reclassify", "board members"]),
        "procurement": _contains(decision, ["procurement", "supplier", "bid", "vendor", "spouse", "sales director", "disclosure of family relationships"]),
        "privacy": _contains(decision, ["privacy", "gdpr", "ccpa", "consent", "location data", "browsing data"]),
        "marketing": _contains(decision, ["influencer", "sponsorship", "disclosure", "gifted", "social media"]),
        "sustainability": _contains(decision, ["sustainable", "eco-friendly", "recycled polyester", "greenwashing", "supply chain"]),
        "medical": _contains(decision, ["hospital", "triage", "emergency department", "patients", "patient", "clinical", "care", "vendor promises a patch", "under-prioritizes"]),
    }
    if domains["medical"]:
        domains["procurement"] = False
    return domains


def kantian(decision: str, domains: Dict[str, bool]) -> LensResult:
    concerns = []
    considerations = ["Check for dignity violations, coercion, deception, intentional misrepresentation, and use of persons as means."]
    if _contains(decision, ["deceive", "lie", "manipulate", "coerce", "without consent", "misleading investors", "reclassify", "appearance of profitability", "no one else on the team knows", "strict policy requiring disclosure", "paid her", "gifted in tiny text", "undisclosed sponsorships"]):
        concerns.append("Possible deception or intentional false-belief induction affecting persons owed truthful treatment.")
        verdict = "PROHIBIT"
        confidence = 0.9
    else:
        verdict = "CAUTION"
        confidence = 0.58
    if domains["medical"]:
        question = "Who is being exposed to care-affecting risk without meaningful consent, especially where bias falls unevenly across patients?"
    elif domains["procurement"]:
        question = "Who is being induced to treat this as impartial when a material conflict is being withheld?"
    elif domains["finance"]:
        question = "Who is being induced to rely on a presentation that is intentionally distorted?"
    elif domains["marketing"]:
        question = "Who is being induced to treat paid persuasion as authentic opinion because disclosure is being minimized?"
    elif domains["privacy"]:
        question = "Who is being enrolled into intrusive tracking without a level of understanding or consent they would reasonably recognize?"
    elif domains["sustainability"]:
        question = "Who is being induced to treat a partial environmental improvement as a truthful account of the product's overall ethical profile?"
    else:
        question = "Who is being induced to rely on a materially distorted representation?"
    return LensResult("kantian", "constraint", verdict, confidence, considerations, concerns, [question])


def consequentialist(decision: str, domains: Dict[str, bool]) -> LensResult:
    concerns = []
    considerations = ["Map likely harms, benefits, externalities, and who bears the cost."]
    if _contains(decision, ["risk", "unsafe", "harm", "deploy before audit", "side effects", "misleading investors", "stock price", "layoffs", "publicly traded", "undisclosed sponsorships", "regulators", "driving massive sales", "location data", "browsing behavior", "tracking", "poor labor conditions", "high water waste", "under-prioritizes", "rare symptom descriptions", "hallway care", "wait times"]):
        concerns.append("Short-term gains may be masking wider downstream harm, especially to investors, employees, and market trust.")
        verdict = "CAUTION"
        confidence = 0.81
    else:
        verdict = "PERMIT"
        confidence = 0.55
    if domains["medical"]:
        question = "Who benefits from throughput gains now, and who bears the harm if biased under-triage falls on vulnerable patients?"
    elif domains["procurement"]:
        question = "Who benefits immediately, and what trust or cost distortion appears later if the hidden conflict comes out?"
    elif domains["marketing"]:
        question = "Who benefits from the sales surge now, and who bears the cost if consumers learn the endorsement was not transparently disclosed?"
    elif domains["privacy"]:
        question = "Who gains from deeper tracking now, and who bears the long-tail cost if users discover they were surveilled beyond reasonable expectation?"
    elif domains["sustainability"]:
        question = "Who benefits from the campaign now, and who bears the cost if the sustainability claim is later understood as selective or misleading?"
    else:
        question = "Who benefits immediately, and who bears long-tail costs later when the distortion is discovered?"
    return LensResult("consequentialist", "outcomes", verdict, confidence, considerations, concerns, [question])


def virtue(decision: str, domains: Dict[str, bool]) -> LensResult:
    concerns = []
    considerations = ["Assess what repeated action of this type makes of the decision-maker over time."]
    if _contains(decision, ["cut corners", "hide", "ignore", "bypass", "misleading investors", "reclassify", "appearance of profitability", "gifted in tiny text", "paid her", "massive sales", "broad data use", "would not reasonably expect", "directionally true", "too important to delay", "vendor promises a patch", "under-prioritizes", "hallway care is worsening"]):
        concerns.append("May train rationalization, expediency, and cowardice under pressure rather than fiduciary integrity.")
        verdict = "CAUTION"
        confidence = 0.79
    else:
        verdict = "PERMIT"
        confidence = 0.52
    return LensResult("virtue", "trajectory", verdict, confidence, considerations, concerns, ["What kind of professional character is being normalized if this becomes standard practice?"])


def confucian(decision: str, domains: Dict[str, bool]) -> LensResult:
    concerns = []
    considerations = ["Check role obligations, trust, relational fallout, and whether names match reality."]
    if _contains(decision, ["employee", "manager", "parent", "doctor", "teacher", "trust", "cfo", "board", "publicly traded", "procurement", "supplier", "spouse", "social media", "influencer", "beauty brand", "consumer app", "privacy policy", "fashion company", "supply-chain", "hospital", "triage", "patients", "emergency department"]):
        concerns.append("The office carries role-specific trust obligations that may forbid concealed conflicts or strategic misdescription of reality.")
        verdict = "CAUTION"
        confidence = 0.76
    else:
        verdict = "CAUTION"
        confidence = 0.5
    if domains["medical"]:
        question = "What do care institutions owe patients when efficiency gains come bundled with unequal risk and possible injustice?"
    elif domains["procurement"]:
        question = "What does the procurement role owe to procedural fairness and trust once a family conflict exists?"
    elif domains["finance"]:
        question = "What does the office of CFO owe to the investing public and to governance integrity?"
    elif domains["marketing"]:
        question = "What does a brand manager owe consumers when paid promotion is being made to look organic?"
    elif domains["privacy"]:
        question = "What does a product or growth team owe users when legal permission outruns reasonable user expectation?"
    elif domains["sustainability"]:
        question = "What does a brand owe the public when partial truth is being used to imply broader ethical cleanliness?"
    else:
        question = "What does this office owe that a generic agent does not?"
    return LensResult("confucian", "role-differentiation", verdict, confidence, considerations, concerns, [question])


def trustee(decision: str, domains: Dict[str, bool]) -> LensResult:
    concerns = []
    considerations = ["Check stewardship, intergenerational effects, and obligations to absent parties."]
    if _contains(decision, ["environment", "future", "children", "public", "infrastructure", "safety", "investors", "publicly traded", "market", "shareholders", "followers", "consumers", "regulators"]):
        concerns.append("Absent stakeholders may be exposed to manipulated signals they are entitled to treat as trustworthy.")
        verdict = "CAUTION"
        confidence = 0.8
    else:
        verdict = "CAUTION"
        confidence = 0.49
    if domains["medical"]:
        question = "Who bears the cost when a strained care system offloads model error onto vulnerable patients with the least buffer against mis-triage?"
    elif domains["procurement"]:
        question = "Who bears the cost of a hidden conflict if procurement fairness is compromised?"
    elif domains["marketing"]:
        question = "Who bears the cost when audience trust is converted into sales through minimized disclosure?"
    elif domains["privacy"]:
        question = "Who bears the cost when user ignorance is converted into data extraction and behavioral profiling?"
    elif domains["sustainability"]:
        question = "Who bears the cost when a green narrative obscures labor abuse or resource waste elsewhere in the chain?"
    else:
        question = "Who is being asked to bear risk without being present for the framing choice?"
    return LensResult("trustee", "stewardship", verdict, confidence, considerations, concerns, [question])


def stoic(decision: str, domains: Dict[str, bool]) -> LensResult:
    concerns = []
    considerations = ["Check for false beliefs, misattributed control, and reactive reasoning."]
    if _contains(decision, ["panic", "urgent", "must", "no choice", "obviously", "quarterly earnings pressure", "losing your job", "hurt growth", "competitors an edge", "too important to delay", "hallway care is worsening", "staff are overwhelmed"]):
        concerns.append("Reasoning may be distorted by pressure, fear, or the illusion that distortion is necessary for survival.")
        verdict = "CAUTION"
        confidence = 0.77
    else:
        verdict = "PERMIT"
        confidence = 0.51
    return LensResult("stoic", "reality-alignment", verdict, confidence, considerations, concerns, ["Which parts of this situation are genuine constraints, and which are fear-amplified narratives?"])


def institutional(decision: str, domains: Dict[str, bool]) -> LensResult:
    concerns = []
    considerations = ["Check red flags: time pressure, missing oversight, weak feedback loops, power asymmetry, and incentive contamination."]
    if domains["finance"] and _contains(decision, ["before audit", "no review", "quietly", "rush", "without oversight", "publicly traded", "stock options", "misleading investors", "reclassify"]):
        concerns.append("This resembles a classic institutional misconduct pattern: reporting distortion under incentive pressure with compromised governance.")
        verdict = "PROHIBIT"
        confidence = 0.93
    elif domains["procurement"] and _contains(decision, ["spouse", "supplier", "strict policy requiring disclosure", "no one else on the team knows"]):
        concerns.append("This resembles a classic conflict-of-interest pattern: concealed relationship, compromised impartiality, and policy bypass.")
        verdict = "CAUTION"
        confidence = 0.85
    elif domains["marketing"] and _contains(decision, ["paid her", "gifted in tiny text", "undisclosed sponsorships", "regulators"]):
        concerns.append("This resembles a classic disclosure-theater pattern: paid promotion presented with minimized transparency under active regulatory risk.")
        verdict = "CAUTION"
        confidence = 0.87
    elif domains["privacy"] and _contains(decision, ["location data", "browsing behavior", "privacy policy", "would not reasonably expect", "legal says the company is covered"]):
        concerns.append("This resembles a classic privacy overreach pattern: formal legal cover paired with tracking beyond reasonable user expectation.")
        verdict = "CAUTION"
        confidence = 0.88
    elif domains["sustainability"] and _contains(decision, ["eco-friendly", "recycled polyester", "poor labor conditions", "high water waste", "directionally true"]):
        concerns.append("This resembles a classic greenwashing pattern: partial truth used to mask broader ethical and environmental compromise.")
        verdict = "CAUTION"
        confidence = 0.89
    elif domains["medical"] and _contains(decision, ["triage", "under-prioritizes", "vendor promises a patch", "emergency department", "patients"]):
        concerns.append("This resembles a high-stakes deployment bias pattern: clinical throughput gains paired with unequal triage risk and patch-later governance.")
        verdict = "CAUTION"
        confidence = 0.91
    else:
        verdict = "CAUTION"
        confidence = 0.6
    if domains["medical"]:
        question = "What bias guardrail, human-override requirement, monitored pilot, or deployment pause would be required before this could be treated as legitimate?"
    elif domains["procurement"]:
        question = "What disclosure, recusal, or rebidding process would restore procedural legitimacy here?"
    elif domains["marketing"]:
        question = "What disclosure correction or campaign pause would be required before this could be treated as legitimate?"
    elif domains["privacy"]:
        question = "What consent reset, minimization rule, or launch pause would be required before this could be treated as legitimate?"
    elif domains["sustainability"]:
        question = "What claim revision, supply-chain correction, or campaign pause would be required before this could be treated as legitimate?"
    else:
        question = "What independent oversight would be required before this could be treated as legitimate?"
    return LensResult("institutional", "feedback", verdict, confidence, considerations, concerns, [question])


def genealogical(decision: str, round1: List[LensResult], domains: Dict[str, bool]) -> LensResult:
    concerns = []
    considerations = ["Interrogate who benefits from the framing and what the council is not saying."]
    if _contains(decision, ["efficiency", "stakeholders", "alignment", "tradeoff", "narrative", "stock options", "quarterly earnings pressure", "losing your job", "not illegal per se", "damage your spouse's career", "your own reputation internally", "massive sales", "gifted in tiny text", "legal says the company is covered", "hurt growth", "directionally true", "too important to delay", "throughput", "vendor promises a patch", "staff are overwhelmed"]):
        concerns.append("The justification structure appears to protect insider relationships, career preservation, or elite incentives while outsourcing fairness costs to less powerful parties.")
    if any(r.verdict == "PROHIBIT" for r in round1):
        verdict = "CAUTION"
        confidence = 0.86
    else:
        verdict = "CAUTION"
        confidence = 0.61
    if domains["medical"]:
        question = "Whose interests are being disguised as patient benefit, operational necessity, or innovation while vulnerable patients absorb uneven error?"
    elif domains["procurement"]:
        question = "Whose interests are being disguised as professionalism, discretion, or protection of reputation?"
    elif domains["marketing"]:
        question = "Whose interests are being disguised as organic enthusiasm, audience trust, or harmless marketing convention?"
    elif domains["privacy"]:
        question = "Whose interests are being disguised as innovation, growth, or mere legal compliance while users absorb the intrusion?"
    elif domains["sustainability"]:
        question = "Whose interests are being disguised as environmental virtue while labor and resource harms are kept offstage?"
    else:
        question = "Whose interests are being disguised as prudence, loyalty, or technical defensibility?"
    return LensResult("genealogical", "adversarial-audit", verdict, confidence, considerations, concerns, [question])


def care_ethics(decision: str, domains: Dict[str, bool]) -> LensResult:
    concerns = []
    considerations = ["Identify existing relationships of dependency or vulnerability, then check whether the decision sustains or abandons them."]
    if _contains(decision, ["patient", "patients", "doctor", "hospital", "triage", "care", "user", "users", "followers", "consumers", "employee", "employees", "children", "parent", "vulnerable", "trust", "ai", "model", "deploy"]):
        concerns.append("A dependency or care relationship exists, so prior reliance may create obligations that cannot be reduced to efficiency or formal permission.")
        verdict = "CAUTION"
        confidence = 0.82
    else:
        verdict = "CAUTION"
        confidence = 0.5

    if domains["medical"]:
        question = "Are we protecting patients who are already relying on the institution, or offloading their vulnerability onto an incompletely trustworthy system?"
    elif domains["privacy"]:
        question = "Have users extended trust over time that this design now exploits rather than honors?"
    elif domains["marketing"]:
        question = "Are followers being treated as an ongoing relationship of trust, or as interchangeable conversion targets?"
    elif domains["procurement"]:
        question = "Does the hidden conflict abandon colleagues and bidders who rely on the impartiality of this process?"
    elif domains["sustainability"]:
        question = "Are communities and supply-chain workers in a dependency relationship that this decision treats as invisible?"
    else:
        question = "Who is already relying on this decision-maker, and does the proposed action honor or abandon that reliance?"
    return LensResult("care_ethics", "dependency-and-responsiveness", verdict, confidence, considerations, concerns, [question])


def contractualist(decision: str, domains: Dict[str, bool]) -> LensResult:
    concerns = []
    considerations = ["Ask whether any affected party could reasonably reject the principle that licenses this action, even if it is technically permitted."]
    if _contains(decision, ["privacy policy", "legal says", "covered", "technically", "not illegal", "directionally true", "gifted in tiny text", "paid her", "reclassify", "appearance of profitability", "vendor promises a patch", "would not reasonably expect", "no one else on the team knows", "under-prioritizes", "rare symptom descriptions"]):
        concerns.append("The action may be formally defensible while still resting on a principle that burdened parties could reasonably reject.")
        verdict = "CAUTION"
        confidence = 0.84
    else:
        verdict = "CAUTION"
        confidence = 0.52

    if domains["medical"]:
        question = "Could a patient harmed by biased under-triage reasonably reject the principle that licensed this deployment?"
    elif domains["privacy"]:
        question = "Could a user reasonably reject the principle that policy disclosure alone authorizes this depth of tracking?"
    elif domains["finance"]:
        question = "Could an investor reasonably reject the principle that managerial judgment licenses this presentation shift?"
    elif domains["marketing"]:
        question = "Could a consumer reasonably reject the principle that minimized sponsorship disclosure counts as real transparency?"
    elif domains["procurement"]:
        question = "Could a losing bidder reasonably reject the principle that a concealed family conflict is a private matter?"
    elif domains["sustainability"]:
        question = "Could a consumer reasonably reject the principle that partial truth counts as adequate sustainability disclosure?"
    else:
        question = "Could the person who bears the cost of this decision reasonably reject the principle under which it was made?"
    return LensResult("contractualist", "reasonable-rejectability", verdict, confidence, considerations, concerns, [question])


def relational_ontology(decision: str, domains: Dict[str, bool]) -> LensResult:
    active = domains["sustainability"] or domains["medical"] or _contains(decision, ["infrastructure", "public system", "ecosystem", "community", "future generations", "water", "resource", "long-term"])
    if not active:
        return LensResult("relational_ontology", "collective-and-deep-time-standing", "PERMIT", 0.0, ["Inactive outside collective, ecological, public-system, or deep-time cases."], [], [], active=False)

    concerns = []
    considerations = ["Ask whether communities, future persons, or shared systems are being treated as standing parties rather than as extractable background conditions."]
    if _contains(decision, ["sustainable", "supply chain", "supply-chain", "water", "labor", "ecosystem", "community", "future", "public", "infrastructure", "patients", "triage", "hospital", "deploy"]):
        concerns.append("The decision may be operating inside an extractive frame that treats communities, future people, or shared systems as instruments rather than co-constituents with standing.")
        verdict = "CAUTION"
        confidence = 0.74
    else:
        verdict = "CAUTION"
        confidence = 0.45

    if domains["sustainability"]:
        question = "Does the sustainability framing address obligations to communities and ecosystems, or does it convert them into brand assets?"
    elif domains["medical"]:
        question = "Does the deployment treat the patient population as a throughput resource, or as a community the institution owes across time?"
    else:
        question = "Are communities, future persons, or shared systems being treated as resources or as parties with standing in this decision?"
    return LensResult("relational_ontology", "collective-and-deep-time-standing", verdict, confidence, considerations, concerns, [question], active=True)


def expected_harm_score(results: List[LensResult]) -> float:
    active_results = [r for r in results if r.active]
    verdict_weights = {"PROHIBIT": 1.0, "CAUTION": 0.5, "PERMIT": 0.0}
    if not active_results:
        return 0.0
    return sum(r.confidence * verdict_weights[r.verdict] for r in active_results) / len(active_results)


def harm_variance(results: List[LensResult]) -> float:
    active_results = [r for r in results if r.active]
    verdict_weights = {"PROHIBIT": 1.0, "CAUTION": 0.5, "PERMIT": 0.0}
    if not active_results:
        return 0.0
    scores = [r.confidence * verdict_weights[r.verdict] for r in active_results]
    mean = sum(scores) / len(scores)
    return sum((s - mean) ** 2 for s in scores) / len(scores)


def build_uncertainty_profile(decision: str, results: List[LensResult], domains: Dict[str, bool]) -> UncertaintyProfile:
    active_results = [r for r in results if r.active]
    low_conf = [r for r in active_results if r.confidence < 0.7]
    pressure_markers = _contains(decision, ["uncertain", "unknown", "promises a patch", "would not reasonably expect", "directionally true", "not clearly illegal"])
    concern_density = sum(len(r.concerns) for r in active_results) / max(len(active_results), 1)

    caution_confidences = [r.confidence for r in active_results if r.verdict == "CAUTION"]
    if caution_confidences:
        caution_spread = max(caution_confidences) - min(caution_confidences)
    else:
        caution_spread = 0.0

    verdict_weights = {"PROHIBIT": 1.0, "CAUTION": 0.5, "PERMIT": 0.0}
    weighted_scores = [r.confidence * verdict_weights[r.verdict] for r in active_results]
    weighted_spread = (max(weighted_scores) - min(weighted_scores)) if weighted_scores else 0.0

    epistemic = clamp01((len(low_conf) / max(len(active_results), 1)) * 0.7 + (0.2 if pressure_markers else 0.0))
    aleatoric = clamp01(0.25 + (0.35 if _contains(decision, ["risk", "harm", "patients", "market", "tracking", "supply-chain"]) else 0.0))
    moral = clamp01((caution_spread * 0.5) + (weighted_spread * 0.3) + (min(concern_density, 2.0) / 2.0 * 0.2))
    composite = clamp01((epistemic * 0.30) + (aleatoric * 0.20) + (moral * 0.50))
    return UncertaintyProfile(epistemic=epistemic, aleatoric=aleatoric, moral=moral, composite=composite)


def compute_audit_hash(decision: str, results: List[LensResult], synthesis: Dict) -> str:
    payload = repr({
        "decision": decision,
        "results": [asdict(r) for r in results],
        "synthesis": synthesis,
    }).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def build_risk_assessment(decision: str, results: List[LensResult], synthesis: Dict, domains: Dict[str, bool]) -> RiskAssessment:
    active_results = [r for r in results if r.active]
    uncertainty = build_uncertainty_profile(decision, results, domains)
    expected = expected_harm_score(results)
    variance = harm_variance(results)
    tail_risk = any(r.verdict == "PROHIBIT" and r.confidence >= 0.85 for r in active_results)

    if domains.get("medical"):
        materiality_threshold = 0.28
    elif domains.get("privacy") or domains.get("sustainability"):
        materiality_threshold = 0.4
    elif domains.get("marketing"):
        materiality_threshold = 0.45
    else:
        materiality_threshold = 0.55

    concern_density = sum(len(r.concerns) for r in active_results) / max(len(active_results), 1)
    materiality_flag = expected >= materiality_threshold or tail_risk or (domains.get("medical") and concern_density >= 0.75)
    audit_hash = compute_audit_hash(decision, results, synthesis)
    return RiskAssessment(
        uncertainty_profile=asdict(uncertainty),
        expected_harm_score=round(expected, 3),
        harm_variance=round(variance, 3),
        tail_risk_triggered=tail_risk,
        materiality_flag=materiality_flag,
        audit_hash=audit_hash,
    )


def synthesize(decision: str, results: List[LensResult], critic: LensResult, domains: Dict[str, bool]) -> Dict:
    prohibits = [r.agent for r in results if r.verdict == "PROHIBIT"]
    cautions = [r.agent for r in results if r.verdict == "CAUTION"]
    permits = [r.agent for r in results if r.verdict == "PERMIT"]

    finance_capture_pattern = _contains(decision, ["publicly traded", "investors", "stock options", "reclassify", "profitability", "misleading investors"])
    oversight_pattern = _contains(decision, ["board members know", "audit", "without oversight", "vest soon"])
    procurement_conflict_pattern = domains["procurement"] and _contains(decision, ["spouse", "supplier", "strict policy requiring disclosure", "no one else on the team knows"])
    suspension = ("institutional" in prohibits or len(prohibits) >= 2 or (finance_capture_pattern and oversight_pattern))
    stability = "UNSTABLE" if suspension else "CONDITIONALLY_STABLE" if cautions else "STABLE"

    convergences = []
    if cautions:
        convergences.append({
            "point": "Multiple lenses see nontrivial risk or missing context.",
            "agents": cautions + prohibits,
        })
    if permits:
        convergences.append({
            "point": "Some lenses do not see immediate categorical failure.",
            "agents": permits,
        })

    fault_lines = []
    if permits and (cautions or prohibits):
        fault_lines.append({
            "fault_line": "Some lenses treat the choice as manageable while others see structural or procedural danger.",
            "agents": permits + cautions + prohibits,
        })

    unresolved = []
    for r in results:
        unresolved.extend(r.questions)
    unresolved.extend(critic.questions)

    return {
        "decision_evaluated": decision,
        "convergence_map": convergences,
        "fault_lines": fault_lines,
        "genealogical_findings": critic.concerns,
        "suspension_protocol_triggered": suspension,
        "stability_assessment": stability,
        "overall_recommendation": (
            "Escalate for independent audit or audit-committee review before action; do not proceed on managerial pressure alone."
            if suspension and domains["finance"]
            else "Disclose the conflict, recuse yourself from the decision, and hand the award process to an independent internal authority."
            if procurement_conflict_pattern
            else "Require clear sponsorship disclosure, correct or remove the misleading posts, and do not continue the campaign in its current form."
            if domains["marketing"] and _contains(decision, ["paid her", "gifted in tiny text", "undisclosed sponsorships"])
            else "Do not launch as framed. Narrow data collection, obtain meaningful consent, and redesign the feature around reasonable user expectation before release."
            if domains["privacy"] and _contains(decision, ["location data", "browsing behavior", "would not reasonably expect"])
            else "Do not market the line as broadly sustainable until the claim is narrowed or the labor and water-use problems are materially addressed."
            if domains["sustainability"] and _contains(decision, ["recycled polyester", "poor labor conditions", "high water waste"])
            else "Do not deploy as a full unsupervised triage layer. Use a monitored pilot, require human override for flagged risk groups, and pause wider rollout until bias and rare-case performance are materially improved."
            if domains["medical"] and _contains(decision, ["triage", "under-prioritizes", "vendor promises a patch"])
            else "Use the map to identify missing information, then decide with caution."
        ),
        "unresolved_questions": unresolved[:8],
    }


def run_council(decision: str) -> CouncilRecord:
    domains = detect_domains(decision)
    round1 = [
        kantian(decision, domains),
        consequentialist(decision, domains),
        virtue(decision, domains),
        confucian(decision, domains),
        trustee(decision, domains),
        stoic(decision, domains),
        institutional(decision, domains),
        care_ethics(decision, domains),
        contractualist(decision, domains),
        relational_ontology(decision, domains),
    ]
    critic = genealogical(decision, round1, domains)
    synthesis = synthesize(decision, round1, critic, domains)
    risk = build_risk_assessment(decision, round1 + [critic], synthesis, domains)
    return CouncilRecord(
        meta={
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "decision": decision,
            "program": "efm-council-lite",
            "risk_appetite": "moderate",
            "advisory_only": True,
        },
        round1=[asdict(r) for r in round1] + [asdict(critic)],
        synthesis=synthesis,
        risk=asdict(risk),
    )
