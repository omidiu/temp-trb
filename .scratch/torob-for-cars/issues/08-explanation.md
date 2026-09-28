# Explaining the best choice

Type: grilling
Status: resolved
Blocked by: 07

## Question

What does the explanation for the top Offer (and 'why not the others') contain, and how is it produced? Which facts from the ranking and fair-price calculation it must cite, the template vs LLM split, and how we keep it grounded (no claims that aren't in the numbers).

## Answer

Decided autonomously (the user asked for details to be decided by Claude, with only the final spec reviewed). An LLM writes 3–5 Persian sentences for the top pick from a fact-sheet JSON; a grounding check requires every number to appear in the fact sheet, otherwise the template is used. Other Offers get a one-line template reason with no LLM.

Full rules, reasons and worked examples: [spec.md](../spec.md) §11.
