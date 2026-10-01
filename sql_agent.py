import argparse
import os
import warnings
from urllib.parse import quote_plus

from dotenv import load_dotenv
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watson_machine_learning.foundation_models.extensions.langchain import WatsonxLLM
from langchain.agents import AgentType
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.utilities.sql_database import SQLDatabase

warnings.filterwarnings("ignore")
load_dotenv()


class FormattedGraniteLLM(WatsonxLLM):
    """Wrap Granite prompts in the chat format expected by the model."""

    def _call(self, prompt, stop=None, run_manager=None, **kwargs):
        formatted_prompt = (
            "<|start_of_role|>user<|end_of_role|>"
            + prompt
            + "<|end_of_text|>\n"
            "<|start_of_role|>assistant<|end_of_role|>"
        )
        return super()._call(
            formatted_prompt,
            stop=stop,
            run_manager=run_manager,
            **kwargs,
        )


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            "Copy .env.example to .env and fill in your local values."
        )
    return value


def build_database() -> SQLDatabase:
    username = quote_plus(require_env("MYSQL_USERNAME"))
    password = quote_plus(require_env("MYSQL_PASSWORD"))
    host = require_env("MYSQL_HOST")
    port = os.getenv("MYSQL_PORT", "3306")
    database = require_env("MYSQL_DATABASE")

    mysql_uri = (
        f"mysql+mysqlconnector://{username}:{password}"
        f"@{host}:{port}/{database}"
    )

    return SQLDatabase.from_uri(
        mysql_uri,
        engine_args={
            "connect_args": {"connection_timeout": 10},
            "pool_pre_ping": True,
        },
    )


def build_llm() -> FormattedGraniteLLM:
    model = ModelInference(
        model_id=os.getenv("WATSONX_MODEL_ID", "ibm/granite-4-h-small"),
        params={
            GenParams.MAX_NEW_TOKENS: 1024,
            GenParams.TEMPERATURE: 0.2,
            GenParams.TOP_P: 0.95,
            GenParams.REPETITION_PENALTY: 1.2,
        },
        credentials={
            "url": os.getenv(
                "WATSONX_URL",
                "https://us-south.ml.cloud.ibm.com",
            ),
        },
        project_id=os.getenv("WATSONX_PROJECT_ID", "skills-network"),
    )
    return FormattedGraniteLLM(model=model)


def main():
    parser = argparse.ArgumentParser(
        description="Ask natural-language questions about a MySQL database."
    )
    parser.add_argument(
        "--prompt",
        required=True,
        help="Question to send to the SQL agent.",
    )
    args = parser.parse_args()

    db = build_database()
    llm = build_llm()

    agent_executor = create_sql_agent(
        llm=llm,
        db=db,
        verbose=True,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        agent_executor_kwargs={"handle_parsing_errors": True},
    )

    result = agent_executor.invoke({"input": args.prompt})
    print("\nAnswer:", result["output"])


if __name__ == "__main__":
    main()
