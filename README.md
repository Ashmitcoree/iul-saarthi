# IUL Saarthi prototype

A small, local-first campus information assistant demo. It searches a curated JSON knowledge base, checks whether there is relevant evidence, sends supported questions to Gemma 4 through Ollama, and displays the source. Questions without evidence receive a fallback instead of a guessed answer.

## Demo scope

The knowledge base contains team-provided Hack Day details and short, bilingual guides that point to official Integral University admissions, contacts, noticeboard, and admission-policy pages. It is not an official university knowledge base and does not continuously sync live information or student records. Always confirm changing fees, eligibility, notices, and deadlines on the linked university page or with the relevant office.

The interface includes English/Hindi reply selection, suggested questions, an expandable evidence view with official source links and page-check dates, a campus office finder, and a session-only helpfulness control. The office finder uses public university details; only locations explicitly published by the university are shown as exact rooms. Its map link points to the general campus pin, not an indoor route. Hindi retrieval is supported for Hindi written in Devanagari; choose Hindi in the sidebar for romanized Hindi input. Feedback is not saved after the browser session ends.

The notice reader accepts one PNG, JPG, or WebP image up to 8 MB. It checks that each checklist item includes a quote found in the model's transcription and lets the student inspect the text it read. The image is not added to the shared FAQ knowledge base or verified against live university sources. Students should compare results with the original notice. In local mode, image processing uses Ollama on the same machine. In Render mode, the image is sent to Google's Gemma API; use public notices and avoid private student information. The hosted API uses Gemma 4 26B by default, while local mode stays on Gemma 4 E2B.

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

## Deploy on Render

The `render.yaml` Blueprint runs the Streamlit app on Render and selects the hosted Gemma API only for that deployment. The local default remains Ollama. Before deploying, create a Google AI Studio API key and add it to the Render service as the secret environment variable `GEMMA_API_KEY`; never commit the key to this repository. The free API tier has usage limits and Google may use free-tier requests to improve its products, so do not upload private student records or confidential notices.

To deploy, push the desired project version to GitHub, open Render, choose **New → Blueprint**, connect this repository, and apply the `render.yaml` configuration. Enter the API key when Render prompts for it. Render deploys the branch configured in the Blueprint and can redeploy later pushes to that branch. The free Render service may sleep when idle, so its first response after a quiet period can take longer.

## Suggested demo

1. Ask: **Where is the Hack Day being held?** The assistant should answer from the event information and show its source.
2. Ask: **What is the Hack Day schedule?** It should answer with the dates and hours from the same source.
3. Ask in Hindi: **हैक डे कहाँ होगा?** The assistant should answer in Hindi from the Hindi event summary and show its source.
4. Ask: **Where can I find current program fees?** It should point to the official Programs and Fee Structure page.
5. Ask: **What is the university's exam fee deadline?** The demo does not contain this, so the assistant should say it cannot confirm and suggest checking with the relevant office.
6. Upload a clear campus notice image in **Turn a campus notice into next steps**. Show the checklist and source text, then try an unrelated photo to demonstrate the fallback.

## How the agent workflow works

`agent.py` acts as the controller. It calls the local TF-IDF search in `retrieval.py`, applies a minimum relevance threshold, and only then sends the question and retrieved passages to Gemma. Every passage carries its source label and optional page metadata. The model prompt instructs Gemma to answer only from that context.

This is a lightweight tool-using workflow, not an autonomous university system. It does not access student records or change university data.

## Adding verified campus information

Add passages to `data/campus_faq.json` using this shape:

```json
{
  "source": "Official document title",
  "page": 2,
  "url": "https://www.iul.ac.in/example",
  "language": "en",
  "verified_on": "2026-10-16",
  "text": "A short, verified passage from that document."
}
```

Use a page number only when the source is a paginated document. For web pages and team-provided event details, use `null`. Add a `hi` passage for an approved Hindi summary, and keep the source, official URL, and date the page was checked so the app can show where an answer came from and how fresh its summary is. These dates are recorded by the project team and are not updated automatically. Update office details in `data/campus_offices.json`; do not guess room numbers or building locations.

