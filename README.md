# IUL Saarthi prototype

A small, local-first campus information assistant demo. It searches a curated JSON knowledge base, checks whether there is relevant evidence, sends supported questions to Gemma 4 through Ollama, and displays the source. Questions without evidence receive a fallback instead of a guessed answer.

## Demo scope

The included knowledge base contains only the Hack Day details supplied by the team. It is sample data, not an official Integral University knowledge base. Do not present answers about fees, examinations, registration policy, or course materials until verified university sources are added.

The interface includes suggested questions and an expandable evidence view that displays the retrieved passage and its source for supported answers.

## Run it

1. Install Python 3.10 or newer.
2. Install Ollama and download the Gemma 4 E2B model:

   ```powershell
   ollama run gemma4:e2b
   ```

   Leave Ollama running. The first launch downloads model files and can take time. Local model speed depends on the computer's available memory and hardware.

3. In this folder, create an environment and install the app dependency:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

4. Start the chat app:

   ```powershell
   streamlit run app.py
   ```

The app uses Ollama at `http://localhost:11434` and the model name `gemma4:e2b` by default. If needed, set `OLLAMA_HOST` or `GEMMA_MODEL` before starting Streamlit.

## Suggested demo

1. Ask: **Where is the Hack Day being held?** The assistant should answer from the event information and show its source.
2. Ask: **What is the Hack Day schedule?** It should answer with the dates and hours from the same source.
3. Ask: **What is the university's exam fee deadline?** The demo data does not contain this, so the assistant should say it cannot confirm and suggest checking with the relevant office.

## How the agent workflow works

`agent.py` acts as the controller. It calls the local TF-IDF search in `retrieval.py`, applies a minimum relevance threshold, and only then sends the question and retrieved passages to Gemma. Every passage carries its source label and optional page metadata. The model prompt instructs Gemma to answer only from that context.

This is a lightweight tool-using workflow, not an autonomous university system. It does not access student records or change university data.

## Adding verified campus information

Add passages to `data/campus_faq.json` using this shape:

```json
{
  "source": "Official document title",
  "page": 2,
  "text": "A short, verified passage from that document."
}
```

Use a page number only when the source is a paginated document. For team-provided event details without a page, use `null`. Keep the source attached to each passage so the app can show where an answer came from.

