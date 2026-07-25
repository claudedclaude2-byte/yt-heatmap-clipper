<!--
State-law fee waiver / denial appeal. Fill placeholders from foia_machine/docs/appeals_playbook.md
for the target jurisdiction -- do not guess a citation that isn't in the playbook or independently verified.
Placeholders: {{AGENCY}} {{STATE_STATUTE_NAME}} {{STATE_STATUTE_CITATION}} {{FEE_WAIVER_CITATION}}
{{CASE_LAW_OR_PRECEDENT}} {{REFERENCE}} {{DENIAL_SUMMARY}} {{PUBLIC_INTEREST_BASIS}} {{REQUESTER_NAME}}
-->
This is a formal appeal of your fee estimate/denial under {{STATE_STATUTE_NAME}}.

GOVERNING LAW:
- **Statute**: {{STATE_STATUTE_CITATION}}
- **Fee Waiver**: {{FEE_WAIVER_CITATION}}
{{#if CASE_LAW_OR_PRECEDENT}}
- **Precedent**: {{CASE_LAW_OR_PRECEDENT}}
{{/if}}

BASIS FOR THIS APPEAL:
{{DENIAL_SUMMARY}}

{{PUBLIC_INTEREST_BASIS}}

REQUESTED RELIEF:
I ask that the fee determination be reversed, or that the underlying denial be reconsidered and
the responsive records released with any applicable exemptions cited specifically.

Reference: {{REFERENCE}}

{{REQUESTER_NAME}}

---
NOTE: this template is jurisdiction-generic on purpose. Pull the actual statute/case-law
citations for {{AGENCY}}'s jurisdiction from appeals_playbook.md before sending -- five different
states already have divergent citations in that file (KY, MO, IA, TX, CA, UT). Sending the wrong
state's citation undermines the appeal.
