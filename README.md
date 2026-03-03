# Fetch GitHub Repo Latest Release Info

See `demo.mp4` for demonstration.

See `sample_output.json` for sample outputs.


## About

This project uses [LangGraph](https://github.com/langchain-ai/langgraph) along with OpenAI's API ([GPT-5.1 model](https://developers.openai.com/api/docs/models/gpt-5.1)).

It controls the browser to fetch the latest release information of the specified repository (openclaw in the example, see `navigate.py`) from GitHub.

## Set Up

```
cp .env.example .env
```

Edit the API key in the file `.env`.

Create Python venv and activate it (recommended).

Install requirements: 

```
pip install -r requirements.txt
```


## Usage

Run command:

```
python ./navigate.py
```

