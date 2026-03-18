# GenAI Logs

This directory contains logs of AI-assisted development conversations for **COMP3011 Coursework 1** (Web Services and Web Data, University of Leeds, 2025--26).

Two sources are represented:

- **Claude Code sessions** --- exported from local JSONL logs (`~/.claude/projects/`), converted to Markdown by [`convert_jsonl_to_md.py`](convert_jsonl_to_md.py).
- **Claude.ai web conversations** --- shared links; stub files record the URL and topic summary.

---

## Regenerating Claude Code Logs

```bash
cd docs/genai-logs
python convert_jsonl_to_md.py
```

This reads all `.jsonl` files from the project's Claude Code session store and writes one Markdown file per session into this directory.

---

## External (Claude.ai web) Dialogs

| File | Topic | URL |
| --- | --- | --- |
| [external-overview-idea.md](external-overview-idea.md) | Initial project overview and idea | [Shared conversation](https://claude.ai/share/c7370728-7d81-42d8-8041-56501efca1b2) |
| [external-dataset.md](external-dataset.md) | Dataset selection and ingestion planning | [Shared conversation](https://claude.ai/share/51e1ce39-726b-4ad3-ba2a-003814e54336) |
| [external-design.md](external-design.md) | System and API design | [Shared conversation](https://claude.ai/share/f21e3b36-9194-4388-95a5-ab973bbde60a) |
| [external-deployment.md](external-deployment.md) | Deployment configuration | [Shared conversation](https://claude.ai/share/6af3f0e2-cd9b-4eaa-a159-d3cc85965720) |

---

## Claude Code Session Logs

<!-- session-logs-start -->

| File | Topic |
| --- | --- |
| [session-3cd69ba2-26c3-4139-b446-ffd60281df2f.md](session-3cd69ba2-26c3-4139-b446-ffd60281df2f.md) | Read coursework brief --- initial scaffolding |
| [session-4e42dca1-aec2-47b4-8538-ceb82f7f9c8b.md](session-4e42dca1-aec2-47b4-8538-ceb82f7f9c8b.md) | Read coursework brief --- continued setup |
| [session-c9a91f07-0d75-4208-a025-b0cc268c81eb.md](session-c9a91f07-0d75-4208-a025-b0cc268c81eb.md) | Read coursework brief --- further scaffolding |
| [session-593822d1-4ef7-48ff-9344-55932e00715d.md](session-593822d1-4ef7-48ff-9344-55932e00715d.md) | Fix PostCSS config error in frontend |
| [session-a02a9776-9a53-4d04-b472-b5c8dc268a22.md](session-a02a9776-9a53-4d04-b472-b5c8dc268a22.md) | Run backend tests and fix bugs |
| [session-b2fd7706-afd3-4d83-a31b-99e03242b31a.md](session-b2fd7706-afd3-4d83-a31b-99e03242b31a.md) | Debug issue (reported by user) |
| [session-5d2a718d-4de9-4b7e-8694-f9d471bfb392.md](session-5d2a718d-4de9-4b7e-8694-f9d471bfb392.md) | Explorer page --- show all countries/commodities by default |
| [session-13c34a6b-5203-4965-9a1b-7a112cfe8569.md](session-13c34a6b-5203-4965-9a1b-7a112cfe8569.md) | Add default admin credentials to README |
| [session-acb4fc44-34d3-4fec-878f-2f599983bfff.md](session-acb4fc44-34d3-4fec-878f-2f599983bfff.md) | Show country full name on map |
| [session-6f5ece28-dc4c-4593-8ab6-62a2e8b776df.md](session-6f5ece28-dc4c-4593-8ab6-62a2e8b776df.md) | Evaluate Vercel deployment feasibility |
| [session-572660ca-4c98-465a-a6e2-9f68a2f559d0.md](session-572660ca-4c98-465a-a6e2-9f68a2f559d0.md) | Check FastAPI definitions and type coverage |
| [session-0409a872-1994-4c55-b4ec-d63473e85aab.md](session-0409a872-1994-4c55-b4ec-d63473e85aab.md) | Add full country name to frontend selections |
| [session-c7359d98-51d2-4652-997c-15131777b8fe.md](session-c7359d98-51d2-4652-997c-15131777b8fe.md) | Fix Docker build node module loader error |
| [session-26118e51-0c09-4d2f-96db-d0584e1c1d5e.md](session-26118e51-0c09-4d2f-96db-d0584e1c1d5e.md) | How to test MCP server |
| [session-0abe2c1a-e610-4851-b106-cd48c2c55859.md](session-0abe2c1a-e610-4851-b106-cd48c2c55859.md) | MCP server usage / README updates |
| [session-09de10d5-7820-4e14-b719-3b7c96689944.md](session-09de10d5-7820-4e14-b719-3b7c96689944.md) | Generate genai-logs and conversion script |

<!-- session-logs-end -->
