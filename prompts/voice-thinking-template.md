# Voice Thinking Template

For mobile voice mode — walk and talk through a problem, then paste this summary request.

## How to Use

1. Open Claude on mobile.
2. Switch to voice mode.
3. Walk for 20 minutes and talk through the problem out loud.
4. End with: "Summarize what I'm trying to figure out and the top 3 options I mentioned."
5. Paste the summary back into Claude Code for implementation.

## Voice Prompt Starters (say these out loud)

**For trading decisions:**
> "I'm looking at the NQ chart and the ribbon just flipped. Walk me through whether I should take this trade or wait."

**For debugging:**
> "The Thunder Trader bot missed 20 trades today. Here's what I saw in the logs. Help me figure out which bug caused the most damage."

**For strategy design:**
> "I want to add a HTF filter to the morning scan. Talk me through the tradeoffs of using daily vs weekly ribbon for confirmation."

**For post-trade review:**
> "I took 3 trades today. The first worked, the second stopped out, the third I missed. Let me walk through each one and figure out what I'd do differently."

## Summary Request (say at end of voice session)

> "Now summarize: what problem am I trying to solve, what are the top 2-3 options I mentioned, and what do you think I'm leaning toward based on what I said?"

## Paste Back Into Claude Code

After voice session, paste the summary and say:
```
Here's my voice thinking session summary. Based on this, let's implement [option X].
Start with [specific file or function].
```
