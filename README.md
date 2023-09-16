# 🎯 Overview streaming with Streamlit, FastAPI, Langchain, and Azure OpenAI
Welcome to this demo which builds an assistant to answer questions in near real-time with streaming.

LLM response times can be slow, in batch mode running to several seconds and longer.

Step-in streaming, key for the best LLM UX, as it reduces percieved latency with the user seeing near real-time LLM progress.

Leverages FastAPI for the backend, with a basic Streamlit UI. FastAPI, Langchain, and OpenAI LLM model configured for streaming to send partial message deltas back to the client via websocket.

# 🛠️ Project Structure

The demo is structured into 2 components:

1. A FastAPI endpoint facilitating communication between the LLM and the UI.
2. An interactive Streamlit frontend for prompting the LLM and displaying the model response.


# 🚀 Quickstart 

1. **Set environment variables:**
- In the backend sub-folder, create a .env file and set the following environment variables
- ```AZURE_OPENAI_API_TYPE="azure"```
- ```AZURE_OPENAI_CHAT_API_BASE=your Azure OpenAI cognitive account endpoint in which your chat model is deployed```
- ```AZURE_OPENAI_CHAT_API_KEY=your Azure OpenAI cognitive account key```
- ```AZURE_OPENAI_CHAT_API_VERSION=your Azure OpenAI model deployment version```
- ```AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=your Azure OpenAI model deployment name```

> Note in testing I used the gpt-3.5-turbo model


2. **The backend:**
- In the backend folder, create a virtual environment with:
- ```python3 -m venv myenv```

- Then activate the virtual environment:
- ```source myenv/bin/activate```

- Install Python package requirements for the backend:
- ```pip install -r requirements.txt```

- Finally, launch the FastAPI backend app locally:
```uvicorn api:app --reload```


3. **The frontend:**
- In the frontend folder, create a virtual environment with:
- ```python3 -m venv myenv```

- Then activate the virtual environment:
- ```source myenv/bin/activate```

- Install Python package requirements for the backend:
- ```pip install -r requirements.txt```

- Finally, launch the Streamlit app locally:
```streamlit run app.py```