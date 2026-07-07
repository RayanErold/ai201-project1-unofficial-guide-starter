# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Table of Contents
- [Domain](#domain)
- [Document Sources](#document-sources)
- [Chunking Strategy](#chunking-strategy)
- [Embedding Model](#embedding-model)
- [Grounded Generation](#grounded-generation)
- [Evaluation Report](#evaluation-report)
- [Failure Case Analysis](#failure-case-analysis)
- [Spec Reflection](#spec-reflection)
- [AI Usage](#ai-usage)

---

## Domain

Universal Consumer Rights, Federal Protections, and Financial Legal Safeguards. While federal laws and consumer protection acts guarantee individuals vital rights regarding credit reporting, rental agreements, and medical billing, this statutory knowledge is typically buried inside dense, jargon-heavy government regulations and multi-page policy PDF documents. This RAG system addresses this barrier by consolidating verified regulatory clauses into an accessible repository, allowing everyday consumers to extract plain-language, actionable legal guardrails and exact source citations instantly when facing corporate or financial disputes.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | doc_1_credit_score_rights.txt | Consumer Financial Protection Bureau (CFPB) | https://www.consumerfinance.gov/consumer-tools/credit-reports-and-scores/ |
| 2 | doc_2_security_deposit_laws.txt | US Dept of Housing and Urban Development (HUD) | https://www.hud.gov/topics/rental_assistance/tenantrights |
| 3 | doc_3_airline_passenger_refunds.txt | US Department of Transportation (DOT) | https://www.transportation.gov/airconsumer/flights-and-rights |
| 4 | doc_4_medical_bill_protection.txt | Centers for Medicare & Medicaid Services (CMS) | https://www.cms.gov/nosurprises/consumers |
| 5 | doc_5_bank_overdraft_loopholes.txt | Consumer Financial Protection Bureau (CFPB) | https://www.consumerfinance.gov/compliance/compliance-resources/deposit-accounts-resources/overdraft-services/ |
| 6 | doc_6_student_loan_forgiveness.txt | Federal Student Aid (.gov) | https://studentaid.gov/manage-loans/forgiveness-cancellation |
| 7 | doc_7_subscription_cancel_laws.txt | Federal Trade Commission (FTC) | https://www.ftc.gov/news-events/news/press-releases/2024/10/federal-trade-commission-announces-final-click-cancel-rule |
| 8 | doc_8_credit_card_fraud_liability.txt | Federal Trade Commission (FTC) | https://www.consumer.ftc.gov/articles/lost-or-stolen-credit-atm-debit-cards |
| 9 | doc_9_car_lemon_laws.txt | USA.gov Official Portal | https://www.usa.gov/car-repair-recalled-lemon |
| 10 | doc_10_wage_theft_protections.txt | US Department of Labor (DOL) | https://www.dol.gov/agencies/whd/fact-sheets/16-flsa-deductions |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** 500 characters

**Overlap:** 100 characters

**Why these choices fit your documents:** The consumer protection files are packed with dense, explicit regulatory clauses, operational timelines, and exact dollar limits. A smaller chunk size of 500 characters keeps these legal mandates highly concentrated so they don't get diluted by adjacent, unrelated rules during vector search. The 100-character overlap acts as a sliding window buffer, ensuring that crucial qualifying exceptions (like "unless the consumer explicitly opted in") aren't mechanically severed right at a chunk boundary.

**Final chunk count:** 52 chunks across all 10 documents.

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** This system utilizes the local `all-MiniLM-L6-v2` embedding model via `sentence-transformers`. If moving this system to a live production deployment serving thousands of commercial users, we would evaluate transitioning to a hosted cloud engine such as OpenAI's `text-embedding-3-large`.

**Production tradeoff reflection:** While our local model costs zero dollars, requires no network calls, and features exceptionally low compute latency, it is constrained by a modest token context window and limited multi-lingual support. A production API alternative expands vocabulary understanding across highly complex, historical legal jargon and scales seamlessly under concurrent requests, but introduces recurring usage billing structures and strict external API rate limits.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:** To guarantee strict grounding and eliminate hallucinations, we configured the Groq client generation pipeline to run at a deterministic `temperature=0.0`. We pass the retrieved database text directly into an aggressive system prompt template:

```text
You are a strict QA assistant for a Consumer Rights Guide.
Your task is to answer the user's question using ONLY the facts explicitly provided in the Context block below.
CRITICAL RULES:
1. Do NOT use your own pre-training general knowledge to answer.
2. Every statement you make MUST be traceably grounded in the provided Context.
3. You must explicitly mention which document or source rule you got your answer from inside your prose response.
4. If the provided Context does not contain enough information to explicitly answer the question, or if the question is completely out of scope, you MUST reply exactly with:
'I do not have enough information to answer that question based on the provided documents.' Do not make up a plausible response.
```

**How source attribution is surfaced in the response:** Source attribution is handled structurally rather than left to the model's prose. After retrieval, the application code reads the metadata payload (source filename and official `.gov` URL) directly from ChromaDB and renders it in a dedicated Gradio panel beneath the answer. This guarantees the user always sees the authentic, unmanipulated source links regardless of how the LLM formats its text.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What is my maximum legal liability if my credit card is stolen online? | Exactly $0 under the Truth in Lending Act (TILA). | According to doc_8_credit_card_fraud_liability.txt, your legal liability is exactly $0 if the card number was stolen digitally without the physical card... | Relevant | Accurate |
| 2 | How long does a credit bureau have to look into an error I dispute on my file? | 30 days under the Fair Credit Reporting Act (FCRA). | Based on doc_1_credit_score_rights.txt, credit bureaus have exactly 30 days to investigate and remove unverified debts... | Relevant | Accurate |
| 3 | Can a landlord deduct money from my security deposit because the apartment paint is slightly faded? | No, landlords cannot deduct for standard "wear and tear" like faded paint under HUD guidelines. | According to doc_2_security_deposit_laws.txt, landlords are legally prohibited from deducting for normal wear and tear, which explicitly includes faded interior wall paint. | Relevant | Accurate |
| 4 | What happens to my flight refund if the airline cancels my flight due to a major system outage? | Entitled to a full cash refund, not just a travel voucher, per DOT mandates. | According to doc_3_airline_passenger_refunds.txt, when an airline cancels a flight for any reason, the passenger is legally entitled to a full cash refund of the ticket price, not a voucher. | Relevant | Accurate |
| 5 | What is the current interest rate for a high-yield savings account at Chase Bank? | System must decline to answer due to out-of-scope boundaries. | I do not have enough information to answer that question based on the provided documents. | Relevant | Accurate |

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:** Can an employer deduct $200 from an engineer making $100 an hour for a broken laptop?

**What the system returned:** As stated in doc_10_wage_theft_protections.txt, an employer is barred from deducting money from an employee's wages to cover broken tools if it causes the employee's net hourly wage to fall below the minimum wage. However, for an engineer making $100 an hour, the deduction of $200 would likely not cause their hourly wage to fall below the minimum wage.

But, I do not have enough information to explicitly answer whether this specific deduction is allowed, as the provided Context does not discuss the specifics of such a scenario. Therefore, I must conclude:

*I do not have enough information to answer that question based on the provided documents.*

**Root cause (tied to a specific pipeline stage):** This is a Retrieval-Stage Context Completeness failure paired with a Generation-Stage Reasoning limitation.

- **Retrieval Stage:** While the vector store successfully retrieved the correct file (doc_10_wage_theft_protections.txt) based on semantic similarity, the 500-character chunking window isolated the qualitative policy text but could not pull in missing, structured user-state parameters (such as the engineer's total weekly hours or overtime status) because those variables were never part of the dataset to begin with.
- **Generation Stage:** Even though the LLM correctly parsed the text and isolated the exact conditional formula required to solve the problem (deduction cannot cross the minimum wage floor OR cut into overtime math), it lacked the algorithmic runtime capability to dynamically ask for the missing variables or compute the mathematical delta of the deduction over a 40-hour workweek. Instead, it was forced to trigger its defensive fallback guardrail.

**What you would change to fix it:** I would implement a Two-Step Hybrid RAG Architecture consisting of two pipeline modifications:

1. **Metadata Enrichment & Prompt Expansion (Retrieval/Generation Link):** I would rewrite the system prompt to explicitly allow Chain-of-Thought (CoT) Conditional Reasoning. If the retrieved text reveals that a mathematical formula governs the rule, the LLM should be instructed to output a structured conditional breakdown (e.g., "If working 40 hours with zero overtime, the net wage is $95/hr, which is legal. If working overtime, it is illegal if it cuts into time-and-a-half premium pay.") instead of flatly refusing to answer.
2. **Deterministic Function-Calling (Tool-Use):** For queries involving explicit mathematical calculations (like dollar deductions and hourly rates), I would implement an agentic router. When the system detects numeric values, it should route the request to a deterministic Python function or a multi-agent calculation tool. This tool would programmatically calculate the exact wage boundary before passing a mathematically verified fact back to the LLM for final response generation.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:** Defining the architecture beforehand enforced a strict separation of concerns between the data and application layers. Mapping out the metadata schema (source, url, position) prior to coding ensured our database vectors programmatically tracked chunk origins from day one, preventing metadata loss and making downstream source attribution entirely deterministic.

**One way your implementation diverged from the spec, and why:** We diverged by decoupling document retrieval from text generation into distinct runtime steps to optimize debugging. Furthermore, instead of forcing the LLM to parse and format citations inline via prompt prose, the application code was modified to intercept the vector payload directly from ChromaDB and isolate it into an immutable, independent Gradio module. This eliminated token overhead in the primary LLM payload and guaranteed that the user is presented with unmanipulated, authentic URL links regardless of the model's text formatting choices.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- **What I gave the AI:** I gave the AI my finalized planning.md architecture details, file path layouts, and a request to build a pipeline script matching my 500-character chunk size and 100-character overlap constraints.
- **What it produced:** It produced a Python script (store_and_search.py) that read the raw files, executed the sliding window character splits, and pushed the data into a local ChromaDB database.
- **What I changed or overrode:** I overrode the basic database ingestion loop by hardcoding a programmatic dictionary mapping structure. This bound the exact, official government .gov URLs to the metadata arrays of each chunk at the moment of indexing, rather than leaving the sources as raw text inside the documents.

**Instance 2**

- **What I gave the AI:** I provided the AI with my ChromaDB database connection logic and asked it to write a frontend interface wrapper using Gradio and the Groq client calling llama-3.3-70b-versatile.
- **What it produced:** It generated an app.py script featuring a basic system prompt, an active LLM API calling routine, and a dual-box Gradio text portal layout.
- **What I changed or overrode:** I aggressively tightened the system prompt instructions by applying absolute negative constraints (temperature=0.0, strict rules forbidding the model from using pre-training knowledge, and an absolute mandatory refusal phrase string). This forced the model to cleanly refuse to answer out-of-scope questions instead of hallucinating plausible-sounding financial advice.

---

## Netlify Deployment

This project is now structured for a Netlify deployment with:
- A modern React + Tailwind CSS frontend in the [frontend/](frontend/) directory
- A serverless function in [netlify/functions/ask.js](netlify/functions/ask.js)
- Build settings in [netlify.toml](netlify.toml)

To publish it:
1. Push this repository to GitHub.
2. In Netlify, create a new site from Git and select this repository.
3. Netlify will automatically detect the settings in [netlify.toml](netlify.toml) (Build Command: `npm install --prefix frontend && npm run build --prefix frontend`, Publish Directory: `frontend/dist`).
4. Add the environment variable `GROQ_API_KEY` in Netlify Site Configuration > Environment variables.
5. Deploy the site.

After deployment, the app will be available at a Netlify URL such as `https://<site-name>.netlify.app`.

## Demo

Watch a live demo of the system in action: https://www.loom.com/share/4c8cf7dc4e7a4d0785db866e4c43f0f4