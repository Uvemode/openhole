# openhole

<p align="center">
  <img src="loophole.gif" width="100%" />
</p>

A privacy proxy that lets you use Claude Code as the analysis backend while keeping confidential data out of Anthropic's infrastructure. Gemini CLI acts as the user-facing interface and anonymizes sensitive content before it reaches Claude.

## Problem

Claude is a better reasoning model for technical analysis, but your organization's data confidentiality agreement covers Gemini, not Anthropic. This project bridges the gap.

## How it works

1. You interact with Gemini CLI normally
2. Before sending anything to Claude, Gemini anonymizes sensitive values (IPs, hostnames, emails, credentials, etc.) and maintains a token mapping table in its context
3. Gemini calls the `send_to_claude` MCP tool with the anonymized content
4. The MCP server injects the message into a running Claude Code session via Zellij (`zellij action write-chars`)
5. You read Claude's response directly in its terminal pane
6. If you ask Gemini to relay or summarize Claude's response, it reverses the token substitution before displaying

Claude never sees the original values. The mapping table lives only in Gemini's context window.

## Architecture

```
Ghostty
└── Zellij (local or remote)
    ├── Pane A: Gemini CLI  ──────────────────────────────┐
    └── Pane B: Claude Code  <── zellij write-chars ──┐   │
                                                      │   │
                                              MCP Server (Python)
                                              localhost:3000
```

For remote deployments, the MCP server runs on the same host as Claude Code. An SSH tunnel (`ssh -L 3000:localhost:3000 user@host`) makes it reachable from the local machine without exposing the port.

## Requirements

- Python 3.11+
- [Zellij](https://zellij.dev)
- [Gemini CLI](https://github.com/google-gemini/gemini-cli)
- [Claude Code](https://claude.ai/code)
- A Gemini API key or Google account with Gemini access
- A Claude Pro or Max subscription

## Setup

**1. Clone and install**

```bash
git clone https://github.com/Uvemode/openhole
cd openhole/server
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

**2. Configure**

```bash
cp .env.example .env
```

Edit `.env` and set `ZELLIJ_SESSION` to the name of your Zellij session running Claude Code:

```
ZELLIJ_SESSION=claude
PORT=3000
```

**3. Start Claude Code in a named Zellij session**

```bash
zellij --session claude
# then start claude inside it
```

**4. Start the MCP server**

```bash
python3 main.py
```

**5. Register the MCP server with Gemini CLI**

```bash
gemini mcp add --transport http --scope user claude-proxy http://127.0.0.1:3000/mcp
```

**6. Load the system prompt**

Gemini CLI automatically loads `.gemini/system.md` from the project directory. The file is already in place at `.gemini/system.md` - no configuration needed.

**7. (Remote only) SSH tunnel**

If the MCP server is on a remote host:

```bash
ssh -L 3000:localhost:3000 user@host
```

Point Gemini at `http://127.0.0.1:3000/mcp` as above. The tunnel must be active while using the proxy.

## Notes

- Claude's responses are not captured or de-anonymized automatically. You read them directly in the Claude pane. Gemini only de-anonymizes if you explicitly ask it to relay the response.
- The anonymization is LLM-based (Gemini), not rule-based. It is thorough but not guaranteed to catch every sensitive value. Review what gets sent for high-stakes content.
- The MCP server binds to `127.0.0.1` only and never opens an externally reachable port.
