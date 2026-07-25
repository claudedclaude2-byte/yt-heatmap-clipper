# FOIA Machine — Expansion Pack

Portable data/templates for the FOIA Machine (the local himalaya/Gmail-IMAP cron system filing
public-records requests for Blackmatter Insight). This repo doesn't run the machine itself —
these files are meant to be copied into the local system's working directory.

## Layout

- `agencies/agencies.json` — agency directory (33 agencies: 11 local, 14 state, 5 federal, 3
  foreign): jurisdiction, statute, fee-waiver citation, submission channel. The original 19 came
  from confirmed correspondence; 14 more (state police for OH/PA/NY/FL/GA/WA/AZ/NC/CO/MA/MN plus
  federal ATF/US Marshals/CBP) were added via web search against each agency's official .gov
  site (Jul 2026) — their `notes` field says "Verified via ... Jul 2026" and cites the source
  site. Those 14 intentionally leave `fee_waiver_citation: null`: the statute name/citation is
  confirmed, but the specific fee-waiver subsection wasn't independently verified, so don't cite
  one in an appeal until it's added to `appeals_playbook.md`. `mailing_address` is `null` unless
  explicitly confirmed — verify before mailing anything. Three entries are marked
  `level: "foreign"` (Quebec, Costa Rica, Jordan) and explicitly do **not** use FOIA.
- `templates/` — letter templates for each stage of a request:
  - `request_initial.md` — first request
  - `appeal_fee_waiver_federal.md` / `appeal_fee_waiver_state.md` — fee waiver / denial appeals
  - `appeal_improper_closure.md` — contest a closure that skipped a required statutory step
  - `extension_acknowledgment_reply.md` — acknowledge an agency's extension, lock in the new date
  - `ag_complaint_escalation.md` — escalate to a state AG / oversight body after a missed deadline
  - `foreign_jurisdiction_clarification.md` — correct a prior message that wrongly cited U.S.
    FOIA against a non-U.S. agency (this has actually happened twice — see appeals_playbook.md)
- `docs/appeals_playbook.md` — statute/fee-waiver/precedent/escalation-path table by
  jurisdiction, pulled from appeals actually filed. Fill template placeholders from this table,
  not from memory.
- `extension_tracker.py` — reads a tracked-requests JSON file, computes each request's due date
  (statutory response days + any granted extension), and prints overdue / due-soon / tracking
  status, sorted most-urgent first.
- `tracked_requests.sample.json` — example input for the tracker; replace with the machine's live
  tracked-requests export.

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
