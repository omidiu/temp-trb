# LLM provider and access

Type: grilling
Status: resolved

## Question

Which LLM does each job, and how do we cope if it's unreachable from Iran?

## Answer

Decided autonomously (graduated from Not yet specified). Claude via the Anthropic API: `claude-haiku-4-5` for Intent parsing and normalization, `claude-sonnet-5` for explanations; every call goes through one `llm` module with a prompt-hash cache so the provider can be swapped. Assumes the user can reach the API.

Detail: [spec.md](../spec.md) §13.
