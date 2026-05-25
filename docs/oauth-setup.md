# Google OAuth & Remote Access

## OAuth for Gemini CLI
Gemini CLI/Hermes might require a callback URL for Google OAuth. 

## Configuration
- **Port**: 8080 exposed in `docker-compose.yml`.
- **Redirect URI**: If the CLI asks for one, use `http://localhost:8080` (if on same machine) or your server's IP.

## Process
1. Run `hermes` (or `gemini` login command).
2. Follow link in terminal.
3. OAuth provider will redirect to `localhost:8080`.
4. Container receives token.

## Tunneling (Optional)
If running on remote server without public IP, use SSH tunneling:
```bash
ssh -L 8080:localhost:8080 user@your-server-ip
```
Now OAuth can redirect to your local browser at `localhost:8080`.
