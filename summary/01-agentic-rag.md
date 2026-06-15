

### What is RAG (Retrieval-Augmented Generation)?

At its core, RAG is a technique to give a Large Language Model (LLM) access to external, up-to-date, or private knowledge that it wasn't trained on. 

LLMs are like incredibly smart people who have been locked in a room without internet since their training ended. If you ask them a question about your specific company documents or a course (like your "llm-zoomcamp"), they won't know the answer. 

RAG solves this by turning the interaction into an **open-book exam**.

Here is how RAG works, step-by-step, mapping directly to the `RAGBase` class in your `rag_helper.py`:

**1. Retrieval (`self.search()`)**
When a user asks a question, we don't send it straight to the LLM. Instead, we use a search engine (an "Index") to find documents relevant to the user's query.
*In your code:* Your `search()` method searches an index (likely Elasticsearch or a vector database) for the course documents, boosting results where the question matches.

**2. Augmentation (`self.build_prompt()`)**
Once we retrieve the relevant documents, we "augment" (combine) the user's original question with the retrieved documents. 
*In your code:* Your `build_context()` formats the retrieved Q&A documents into text. Then `build_prompt()` combines the user's `query` with this `context` using your `PROMPT_TEMPLATE`.

**3. Generation (`self.llm()`)**
Finally, we send this combined prompt—along with strict instructions—to the LLM. 
*In your code:* You pass the prompt to `openai/gpt-oss-20b`. Notice your `INSTRUCTIONS` tell the model: *"Use the context to find relevant information... If the answer is not found in the context, respond with 'I don't know'."* This forces the LLM to only use the retrieved data to generate the answer.

***

### How Does RAG Differ from Fine-Tuning?

If RAG is taking an **open-book exam**, Fine-Tuning is **studying hard for a closed-book exam**. 

In Fine-Tuning, you take an existing model and train it further on thousands of examples to actually change its internal "brain" (its neural network weights). 

Here is a clear-cut breakdown of how they differ:

| Feature | RAG (Retrieval-Augmented Gen) | Model Fine-Tuning |
| :--- | :--- | :--- |
| **How Knowledge is Stored** | Knowledge is stored externally in a database (like an Index). | Knowledge is baked directly into the model's neural network weights. |
| **Updating Knowledge** | **Very Easy.** Just add, delete, or update documents in your database. The LLM instantly knows the new info. | **Hard.** If a fact changes, you have to retrain/fine-tune the model all over again to "unlearn" the old fact. |
| **Hallucinations** | **Low.** Because you force the model to look at the retrieved context (and say "I don't know" if it's missing). | **Higher.** The model relies on its memory, which can lead it to confidently state false or outdated information. |
| **Data Requirements** | Requires raw text documents to put into a search index. | Requires thousands of carefully structured `{"prompt": ..., "response": ...}` training pairs. |
| **Cost & Effort** | Cheaper and much faster to build and maintain. | High compute cost to train, and requires a lot of effort to curate a good training dataset. |

### When should you use which?

*   **Use RAG when:** You need the model to answer questions based on a specific knowledge base, proprietary documents, or fast-changing data (like customer support docs, company wikis, or course material).
*   **Use Fine-Tuning when:** You want to change the model's *behavior*, *tone*, or *format*. For example, if you want the model to speak like Shakespeare, or if you need the model to consistently output valid JSON in a very specific, complex schema without needing massive prompts.

In modern AI development, **RAG is almost always the first step** when you want an LLM to "know" your data. Fine-tuning is usually reserved for teaching the model a specific skill or style rather than injecting facts.