# LegalAI — Legal Argument Generator

A FastAPI service that generates legal arguments and counter-arguments for a case, given its facts and applicable IPC sections, using a fine-tuned Microsoft Phi-2 model (LoRA adapter). Includes JWT-based auth and MySQL storage for users and generated case arguments.

## Tech Stack

- FastAPI (async, lifespan-managed model loading)
- Microsoft Phi-2 + LoRA adapter (`Microsoft Phi 2/`) for generation
- SQLAlchemy (async) + MySQL
- JWT auth (`python-jose`, `passlib`/bcrypt-style hashing)

## Project Structure

```
app/
  main.py            # FastAPI app, CORS, lifespan model loading
  auth.py            # current-user dependency, user lookup
  config.py          # settings (secret key, algorithm, ...)
  database.py        # async DB connection
  model_loader.py    # loads Phi-2 + LoRA adapter and tokenizer
  models.py          # Pydantic request/response models
  schemas.py          # SQLAlchemy table definitions
  routes/
    auth_routes.py     # signup / login / logout
    generate_routes.py # generate + fetch case arguments
Microsoft Phi 2/     # fine-tuned model + tokenizer artifacts
table_schema.sql     # MySQL schema (users, generated_arguments, blacklisted_tokens)
run.py                # uvicorn entry point
```

## Getting Started

```bash
pip install -r requirements.txt   # fastapi, uvicorn, sqlalchemy, transformers, peft, torch, python-jose, ...
mysql < table_schema.sql           # create the schema
python run.py                       # starts uvicorn on 127.0.0.1:8000
```

Set the required environment variables (DB connection, JWT secret) in `.env` before starting.

## API

| Endpoint | Description |
|---|---|
| `POST /signup` | Create a user account |
| `POST /login` | Get a bearer token |
| `POST /logout` | Blacklist the current token |
| `POST /generate` | Generate arguments/counter-arguments for a case (facts + IPC sections) |
| `GET /generated_arguments/{case_id}` | Fetch previously generated arguments for a case |
| `GET /user_case/{user_id}` | List a user's cases |
| `GET /cases/summary/{user_id}` | Total vs. unsolved case counts for a user |
| `PUT /cases/update_status` | Mark a case solved/unsolved |

All `/generate*` and case endpoints require a valid bearer token.
