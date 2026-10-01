# IBM watsonx SQL Agent

A small natural-language-to-SQL project built with **IBM watsonx.ai**, **IBM Granite**, **LangChain**, and **MySQL**.

The agent accepts a natural-language question, inspects the connected SQL database, chooses the relevant tables, generates SQL through LangChain's SQL tools, executes the query, and returns a human-readable answer.

## Stack

- Python
- IBM watsonx.ai
- IBM Granite
- LangChain
- SQLAlchemy
- MySQL / MySQL Connector
- python-dotenv

## Project structure

```text
watsonx-sql-agent/
├── sql_agent.py
├── .env.example
├── .gitignore
├── requirements.txt
├── LICENSE
└── README.md
```

## Setup

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it and install the dependencies:

```bash
pip install -r requirements.txt
```

Copy the environment template:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Fill in your local database values in `.env`.

## Run

```bash
python sql_agent.py --prompt "How many albums are in the database?"
```

## Security

Database credentials are loaded from environment variables and the local `.env` file is excluded by `.gitignore`.

Do **not** commit passwords, API keys, access tokens, or private connection strings to GitHub.

For production use, the SQL account should also have the minimum permissions needed by the application, ideally read-only for an analytics/query agent.

## Notes

The project uses `ZERO_SHOT_REACT_DESCRIPTION` because it matches the lab environment this implementation was tested in. LangChain APIs evolve, so newer versions may require small import or agent-construction changes.

## License

MIT
