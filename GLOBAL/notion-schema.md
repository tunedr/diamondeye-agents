# Notion Key Page IDs and Schema

## Core Pages
- Master Hub: 30e6d271-f21c-8141-b74d-f62f14ad1e6a
- Tasks DB: 30d6d271-f21c-81b0-9e67-db1bb90e026d
- Projects DB: 30d6d271-f21c-819c-a139-ced03ca6feee
- Active Session State: 33d6d271-f21c-8104-9696-d20c95fe8eb8
- Global System Facts: 3406d271-f21c-8119-9420-f4ac4537112a
- Global Infrastructure Standard: 33e6d271-f21c-8126-837c-ef1b9bde3b3f
- Master Architecture Principles: 33e6d271-f21c-8137-8ab5-fdb9cd7e3c7a

## Revenue Pages
- DiamondEye Inspections Hub: 33d6d271-f21c-814c-b3cd-e57299a3d751
- Publishing Hub: 33d6d271-f21c-817c-b3ca-db0293f83a2b

## Task DB Field Names
- Name, Status, Priority, Assigned To, System, Phase, Blocked, Notes, Last Updated
- Status values: Ready to Execute, In Progress, Done, Blocked

## Notion API Rules
- UUID format: hyphenated (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)
- Minimum 400ms delay between consecutive write calls
- HTTP 429 = wait 10 seconds before retry
- Every page must lead with: Current Status, Next Action, Blocked/Decision Needed

## Credentials
- Notion API key location: CREDENTIALS.env on pop-ollama at /home/tunedr/CREDENTIALS.env
- See LOCAL/credentials-ref.md for this machine's credential file path
