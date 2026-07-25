# FOIA Machine — Expansion Pack

Portable data/templates for the FOIA Machine (the local himalaya/Gmail-IMAP cron system filing
public-records requests for Blackmatter Insight). This repo doesn't run the machine itself —
these files are meant to be copied into the local system's working directory.

## Layout

- `agencies/agencies.json` — agency directory (54 agencies: 15 local, 26 state, 5 federal, 8
  foreign): jurisdiction, statute, fee-waiver citation, submission channel. The original 19 came
  from confirmed correspondence; 35 more were added via `WebSearch` against official sources
  (Jul 2026) in three rounds — round one covered state police for
  OH/PA/NY/FL/GA/WA/AZ/NC/CO/MA/MN plus federal ATF/US Marshals/CBP; round two added
  VA/NJ/IN/TN/WI/OR/NV/MD state police, four major city PDs (LAPD, Houston, Philadelphia,
  Seattle), and SC/OK/LA/CT; round three added five non-US jurisdictions (Mexico, Spain, France,
  Germany, Brazil) with native-language templates in `templates/intl/`. Their `notes` field says
  "Verified via ... Jul 2026" and cites the source. Most of round two/three intentionally leave
  `fee_waiver_citation: null` and/or `submission_method: "unknown-verify"`: the statute is
  confirmed, but the specific fee-waiver subsection or exact intake address wasn't independently
  verified, so don't guess — check `appeals_playbook.md` or the agency's current site first. A
  few (`sc-sled`) had a contact email come back masked/obfuscated by the source page. The five
  round-three foreign entries needed extra care: **Mexico's INAI was dissolved** in the
  Nov 2024–Mar 2025 constitutional reform (its functions moved to a new body with narrower appeal
  rights — citing INAI today would itself be a wrong-citation mistake), and **Spain/France's only
  confirmed contacts (CTBG, CADA) are appeals/oversight bodies, not initial-request intake** — do
  not send a first request to either of them. `mailing_address` is `null` unless explicitly
  confirmed — verify before mailing anything. Eight entries are marked `level: "foreign"`
  (Quebec, Costa Rica, Jordan, Mexico, Spain, France, Germany, Brazil) and explicitly do **not**
  use FOIA.
- `templates/` — letter templates for each stage of a request:
  - `request_initial.md` — first request
  - `appeal_fee_waiver_federal.md` / `appeal_fee_waiver_state.md` — fee waiver / denial appeals
  - `appeal_improper_closure.md` — contest a closure that skipped a required statutory step
  - `extension_acknowledgment_reply.md` — acknowledge an agency's extension, lock in the new date
  - `ag_complaint_escalation.md` — escalate to a state AG / oversight body after a missed deadline
  - `foreign_jurisdiction_clarification.md` — correct a prior message that wrongly cited U.S.
    FOIA against a non-U.S. agency (this has actually happened twice — see appeals_playbook.md)
  - `intl/` — native-language initial-request templates for non-US jurisdictions:
    `mexico_solicitud_es.md`, `spain_solicitud_es.md`, `france_demande_fr.md`,
    `germany_antrag_de.md`, `brazil_solicitacao_pt.md`. Each has a comment block at the top
    explaining that country's correct submission channel — several of these are portal/form-only,
    not open email, so don't improvise a recipient address.
- `docs/appeals_playbook.md` — statute/fee-waiver/precedent/escalation-path table by
  jurisdiction, pulled from appeals actually filed. Fill template placeholders from this table,
  not from memory.
- `extension_tracker.py` — reads a tracked-requests JSON file, computes each request's due date
  (statutory response days + any granted extension), and prints overdue / due-soon / tracking
  status, sorted most-urgent first.
- `tracked_requests.sample.json` — example input for the tracker; replace with the machine's live
  tracked-requests export.
- `scraper/verify_agency_contact.py` — Camoufox-based verifier: renders an agency's contact page
  in a real (stealth) browser and pulls out `mailto:` links / emails, for cases where a plain
  fetch or search snippet gets an obfuscated result (this happened with Arizona DPS below).
  **Cannot run inside this repo's own claude-code-remote session** — that session's egress proxy
  allowlists only pypi/npm/its own GitHub repo, so `camoufox fetch` can't download the browser
  binary and even a plain `curl` to an arbitrary `.gov` site 403s. Run it somewhere with normal
  internet access instead — e.g. wherever the FOIA Machine's own cron job runs. See
  `scraper/requirements.txt` for setup.

## Extending

**Adding an agency**: append to `agencies.json` only with a submission channel you've actually
confirmed (an email/portal seen in real correspondence, or independently verified on the
agency's official site). Leave `mailing_address` null and `submission_method: "unknown-verify"`
rather than guessing — a wrong address misdirects a real legal filing.

**Adding a jurisdiction's statute**: add a row to `appeals_playbook.md` before using
`appeal_fee_waiver_state.md` or `ag_complaint_escalation.md` for that jurisdiction.

**Tracking deadlines**: run

```
python3 extension_tracker.py tracked_requests.sample.json --within-days 7
```

against the machine's live export (or wire it into the existing cron cycle to fold this report
into the `[FOIA MACHINE] Cron Report` emails).
