# Appeals Playbook

Statutory basis for fee-waiver / denial appeals, by jurisdiction. Compiled from appeals actually
filed by the FOIA Machine (July 2026 cycle). Use this to fill `{{...}}` placeholders in
`templates/appeal_fee_waiver_state.md` and `templates/ag_complaint_escalation.md` -- do not
improvise a citation for a jurisdiction not listed here without independently verifying it first.

| Jurisdiction | Statute | Fee waiver clause | Precedent / advisory | Escalation path |
|---|---|---|---|---|
| Federal | 5 U.S.C. § 552 | 5 U.S.C. § 552(a)(4)(A)(iii) | — | Appeal to agency's FOIA appeals office, then federal court |
| Kentucky (KY) | KRS 61.870–61.884 | KRS 61.874(3) | KRS 61.870(10)(f) — news-gathering orgs qualify as "resident" | Appeal to KY AG Open Records Division under KRS 61.880(2) |
| Missouri (MO) | RSMo 610.010 et seq. | RSMo 610.026.1 | *Shields*, 771 S.W.2d 107 (Mo. 1989) — search/review not chargeable | Mandamus under RSMo 610.027 if waiver refused |
| Iowa (IA) | Iowa Code Ch. 22 | Iowa Code 22.3(2) | Iowa PIB Advisory Opinion 19-02 — redaction cost is agency's, not requester's | Iowa Public Information Board (PIB) complaint |
| Texas (TX) | Tex. Gov't Code Ch. 552 | Tex. Gov't Code 552.267 | — | TX AG Open Records Division complaint under Tex. Gov't Code 552.301 (file within 10 business days of the missed deadline) |
| California (CA) | Cal. Gov't Code 6250 et seq. (CPRA) | Cal. Gov't Code 6253(c), 6253.9 | — | Superior Court petition (CPRA has no administrative appeal body) |
| Utah (UT) | Utah Code 63G-2 (GRAMA) | Utah Code 63G-2-203 | *Media One v. State* — news media / public-interest basis | State Records Committee appeal |
| Illinois (IL) | 5 ILCS 140 | 5 ILCS 140/6(c) | — | Illinois Public Access Counselor (PAC), Office of the AG |
| Michigan (MI) | MCL 15.231–15.246 | MCL 15.234 | — | Circuit court action or written appeal to head of the public body |
| Alaska (AK) | AS 40.25.100 et seq. | AS 40.25.115 | — | Superior court action |
| Delaware (DE) | 29 Del. C. 10001 et seq. | 29 Del. C. 10003(g) | — | DE Attorney General FOIA petition |

## Non-FOIA jurisdictions (do not cite 5 U.S.C. § 552)

| Jurisdiction | Correct law | Notes |
|---|---|---|
| Quebec, Canada | Act respecting Access to documents held by public bodies, CQLR c A-2.1 | Prior mistake: cited FOIA in error, corrected in thread VQ-26-2815 |
| Costa Rica | Ley No. 8220 | Prior mistake: cited FOIA in error, corrected twice in thread CR-3244-20260719 |
| Jordan | Verify Jordan's own access law before citing anything | Flagged risk of repeating the Costa Rica/Quebec mistake in thread JO-3199-20260719 |
| Mexico | LGTAIP -- but do NOT cite INAI. INAI was dissolved by the Nov 28, 2024 constitutional reform; functions moved to "Transparencia para el Pueblo" (Secretaria Anticorrupcion y Buen Gobierno), effective Mar 21, 2025, with narrower appeal rights | No current intake contact confirmed yet -- verify via gob.mx before sending anything; check whether the incident needs a state Fiscalia instead of the federal body |
| Spain | Ley 19/2013, Art. 17.2 | Send initial requests to the agency holding the records (e.g. Ministerio del Interior) via transparencia.gob.es. `ctbg@consejodetransparencia.es` is CONFIRMED but is the appeals/oversight body only -- do not send an initial request there |
| France | Code des relations entre le public et l'administration (CRPA), Livre III, Titre Ier | Initial requests go directly to the administration/prefecture holding the documents. CADA (cada.fr) is appeals-only, filed within 2 months of a refusal, free |
| Germany | Informationsfreiheitsgesetz (IFG) -- federal only | Most policing is state (Land) business with its own separate information-freedom law -- confirm federal (Bundespolizei: borders/rail/aviation) vs. state jurisdiction before picking a statute |
| Brazil | Lei de Acesso a Informacao (LAI), Lei 12.527/2011 | Submitted per-agency via e-SIC portals, not open email. Policia Federal has its own e-SIC (gov.br/pf); each state's Policia Militar has a SEPARATE e-SIC -- don't default to the federal PF portal for a state incident |

Before sending any appeal to a jurisdiction not in the top table, add it here first with a
verified citation -- don't reuse the federal template against a state or foreign agency.

## Escalation triggers observed in practice

- **Extension not honored**: if the agency misses even its extended deadline, send
  `appeal_improper_closure.md` or the jurisdiction's escalation path above, not another
  extension acknowledgment.
- **Fee waiver ignored**: if an agency closes a request for non-payment without ever ruling on a
  pending fee waiver, that's a procedural defect -- use `appeal_improper_closure.md`.
- **Wrong intake channel**: some agencies (e.g. FBI) bounce direct-email FOIA requests and
  require portal resubmission. Check `submission_method` / `portal_type` in `agencies.json`
  before assuming an email is the right channel.
