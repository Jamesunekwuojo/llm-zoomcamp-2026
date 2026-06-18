# Module 1 Review: From Simple RAG to Agentic RAG

Congratulations on completing Module 1! This document serves as a comprehensive breakdown of everything you've built, the concepts you've mastered, and the technical hurdles you overcame.

---

## 1. The Journey of the Implementation

### Phase 1: Simple RAG (Retrieval-Augmented Generation)
We started by building a traditional RAG pipeline.
* **The Process**: 
  1. We ingested knowledge base documents (`documents.json`).
  2. We built a local search index using `minsearch`.
  3. When a user asked a question, our Python code explicitly performed a keyword search against the index.
  4. The results were packaged into a context prompt and sent to the LLM to generate an answer.
* **The Limitation**: The LLM was entirely passive. If a user made a typo (e.g., asking about "Olama" instead of "Ollama"), our hardcoded search failed to find relevant context. Because the LLM wasn't allowed to search for itself, it failed to answer the question, even though it possessed the reasoning capability to fix the typo.

### Phase 2: Function Calling (Tool Calling)
To fix the passive LLM problem, we introduced Function Calling.
* **The Concept**: Instead of forcing the search upfront, we provided the LLM with a JSON schema describing our `search` function. 
* **The Shift**: The LLM became an active participant. It would read the user's prompt, realize it needed more information, and pause its text generation to emit a **Tool Call** (a JSON string requesting us to run the `search` function with specific, often corrected, keywords).
* **The Execution**: Our Python code executed the local search, and then we fed the raw database results back to the LLM (using `"role": "tool"`) so it could read the facts and formulate a final answer.

### Phase 3: The Agentic Loop
A single function call isn't enough if the LLM needs to make multiple searches or refine its keywords after a bad result.
* **The Implementation**: We wrapped the API calls in a `while True` loop.
* **The Outcome**: You created an autonomous **Agent**. The LLM could iteratively call tools, analyze the output, and decide on its own whether it needed to search again or if it finally had enough information to respond to the user.

---

## 2. The Sandbox Environment & Tools

* **Backend Provider**: You utilized the OpenAI Python SDK but pointed the `base_url` to **Groq** (`https://api.groq.com/openai/v1`) to run fast, open-source models (like `gpt-oss-20b`).
* **Package Management**: We transitioned to managing project dependencies using standard Python packaging (`pyproject.toml`) and modern, ultra-fast tools like `uv`.
* **Git**: Ensured the repository remained clean by instructing `.gitignore` to ignore Python build artifacts (`*.egg-info/`, `__pycache__/`).

---

## 3. Error Log & Resolutions

Building real-world AI pipelines involves a lot of debugging. Here is a definitive log of the errors we encountered and how we solved them:

### API SDK Migration Errors
* **`TypeError: 'Completions' object is not callable`**
  * **Cause**: Attempting to use the legacy OpenAI v0.x syntax (`openai.ChatCompletion.create`).
  * **Fix**: Updated to the v1.x syntax (`client.chat.completions.create`).
* **`AttributeError: 'ChatCompletion' object has no attribute 'output' / 'messages'`**
  * **Cause**: Incorrectly accessing the response object.
  * **Fix**: Accessed the text response properly via `response.choices[0].message.content`.

### Function Calling Structure Errors
* **`BadRequestError: tools[0].function.name is required`**
  * **Cause**: The JSON schema defining the `search_tool` was missing the required `"name"` key.
  * **Fix**: Added `"name": "search"` inside the `"function"` object block.
* **`AttributeError: 'NoneType' object has no attribute 'arguments'`**
  * **Cause**: Trying to read arguments from `message.content`, but when an LLM makes a tool call, `content` is `None`.
  * **Fix**: Extracted the arguments from `response.choices[0].message.tool_calls[0].function`.
* **`AttributeError: 'Function' object has no attribute 'call_id'`**
  * **Cause**: Looking for the tool call ID on the `.function` property instead of the parent `tool_call` object.
  * **Fix**: Used `tool_call.id`.

### Network & Dependency Errors
* **`SSLError: UNEXPECTED_EOF_WHILE_READING`**
  * **Cause**: The old `datatalks.club` FAQ URL stopped working and dropped the connection.
  * **Fix**: Refactored `ingest.py` to directly fetch the compiled `documents.json` from the official LLM Zoomcamp GitHub repository.
* **`OpenAIError: Missing credentials`**
  * **Cause**: The `toyaikit` framework tried to instantiate a default `OpenAI()` client because we didn't pass it our Groq credentials.
  * **Fix**: Explicitly passed our pre-configured `openai_client` into `OpenAIClient(model=MODEL, client=openai_client)`.

### The Jupyter Notebook State Errors
* **`NameError: name 'index' is not defined`**
  * **Cause**: Attempting to run the `search` function without initializing the index in memory.
  * **Fix**: Added a cell to import `load_faq_data` and `build_index`, creating the index globally.
* **`TypeError: 'NoneType' object is not iterable`**
  * **Cause**: Using `.extend(message.content)` when `content` was `None` (due to a tool call).
* **`BadRequestError: value must be an object with the discriminator property: 'role'`** & **`AttributeError: 'tuple' object has no attribute 'type'`**
  * **Cause**: Using `.extend(response.choices[0].message)`. Because Pydantic models iterate as tuples, `.extend()` shredded the message object into key-value pairs (like `('role', 'assistant')`) and permanently corrupted the global `messages` list.
  * **Fix**: Switched to using `.append()`. More importantly, moved the `messages = [...]` initialization into the **exact same cell** as the execution loop so the state is reset fresh on every run.

### Provider & Model Quirks
* **`BadRequestError: Failed to parse tool call arguments as JSON`**
  * **Cause**: The open-source model hallucinated malformed JSON (printing `","}` instead of `"}`). 
  * **Fix**: Simply re-ran the cell. (Smaller LLMs occasionally fail at strict JSON generation).
* **`BadRequestError: property 'annotations' is unsupported`**
  * **Cause**: The OpenAI Python SDK appended new properties (`annotations`, `audio`, `refusal`) when dumping the message to a dictionary. Groq's API rejected these unknown fields.
  * **Fix**: We intercepted the `.model_dump()`, scrubbed the unsupported keys (`assistant_dict.pop("annotations", None)`), and safely appended the cleaned dictionary to the history.
