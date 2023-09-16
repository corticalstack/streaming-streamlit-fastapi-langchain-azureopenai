import os
from collections.abc import Generator
from queue import Queue, Empty
from threading import Thread
from typing import Any

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from langchain.chat_models import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate

from langchain.schema.runnable import Runnable, RunnableConfig
from langchain.schema.output_parser import StrOutputParser
from langchain.callbacks.base import BaseCallbackHandler
from langchain.callbacks.tracers.run_collector import RunCollectorCallbackHandler

from dotenv import load_dotenv

load_dotenv()
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
AZURE_OPENAI_CHAT_API_VERSION = os.getenv("AZURE_OPENAI_CHAT_API_VERSION")
AZURE_OPENAI_CHAT_API_KEY = os.getenv("AZURE_OPENAI_CHAT_API_KEY")
AZURE_OPENAI_CHAT_API_BASE = os.getenv("AZURE_OPENAI_CHAT_API_BASE")

app = FastAPI()
run_collector = RunCollectorCallbackHandler()
runnable_config = RunnableConfig(callbacks=[run_collector])
run_id = None


def create_chain(llm: AzureChatOpenAI) -> Runnable:
    """
    Creates a chain based on provided llm.

    Args:
        llm: The instantiated LLM model.

    Returns:
        Runnable: A chained object.
    """

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "{system_message}"),
            ("human", "{human_message}"),
        ]
    )

    chain = prompt | llm | StrOutputParser()
    return chain


def create_llm_instance(q: Queue) -> AzureChatOpenAI:
    return AzureChatOpenAI(
        streaming=True,
        callbacks=[QueueCallback(q)],
        deployment_name=AZURE_OPENAI_CHAT_DEPLOYMENT_NAME,
        openai_api_version=AZURE_OPENAI_CHAT_API_VERSION,
        openai_api_key=AZURE_OPENAI_CHAT_API_KEY,
        openai_api_base=AZURE_OPENAI_CHAT_API_BASE,
        temperature=0.7,
        max_tokens=2000,
    )


class QueueCallback(BaseCallbackHandler):
    """Callback handler for streaming LLM responses to a queue."""

    def __init__(self, queue: Queue) -> None:
        self.queue = queue

    def on_llm_new_token(self, token: str, **kwargs: any) -> None:
        """
        Handle new tokens from LLM.

        Args:
            token (str): The new token from LLM.
            **kwargs: Additional keyword arguments.
        """
        self.queue.put(token)

    def on_llm_end(self, *args, **kwargs: any) -> None:
        """
        Handle the end of LLM streaming.

        Args:
            *args: Additional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            bool: True if the queue is empty, False otherwise.
        """
        return self.queue.empty()


def llm_task(
    llm: AzureChatOpenAI,
    system_message: str,
    human_message: str,
    queue: Queue,
    job_done: object,
) -> None:
    chain = create_chain(llm)
    chain.invoke(
        {"system_message": system_message, "human_message": human_message},
        config=runnable_config,
    )
    queue.put(job_done)


@app.post("/chat")
async def chat_endpoint(system_message: str, human_message: str) -> StreamingResponse:
    """
    Endpoint to handle chat.
    """
    run_id = None
    run_collector.traced_runs = []

    queue = Queue()
    job_done = object()

    llm = create_llm_instance(queue)

    thread = Thread(
        target=llm_task, args=(llm, system_message, human_message, queue, job_done)
    )
    thread.start()

    def stream() -> Generator[str, None, None]:
        nonlocal run_id
        content = ""

        while True:
            try:
                next_token = queue.get(True, timeout=1)
                if next_token is job_done:
                    break
                content += next_token
                yield next_token
            except Empty:
                continue

        if not run_id and run_collector.traced_runs:
            run = run_collector.traced_runs[0]
            run_id = run.id

    return StreamingResponse(stream())
