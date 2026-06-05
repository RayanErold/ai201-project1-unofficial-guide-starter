# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->
 Domain: Universal Consumer Rights, Federal Protections, and Financial Legal Safeguards.
Value Proposition: While federal laws and consumer protection acts guarantee individuals vital rights regarding credit reporting, rental agreements, and medical billing, this statutory knowledge is typically buried inside dense, jargon-heavy government regulations and multi-page policy PDF documents. This RAG system addresses this barrier by consolidating verified regulatory clauses into an accessible repository, allowing everyday consumers to extract plain-language, actionable legal guardrails and exact source citations instantly when facing corporate or financial disputes
---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | doc_1_credit_score_rights.txt | Legal rights to dispute credit bureau report errors under the FCRA. | CFPB Credit Tool |
| 2 | doc_2_security_deposit_laws.txt | Regulations governing landlord deductions and security deposit returns. | HUD Tenant Rights |
| 3 | doc_3_airline_passenger_refunds.txt | Federal mandates guaranteeing cash refunds for canceled flights. | DOT Flight Rights |
| 4 | doc_4_medical_bill_protection.txt | Protection rules against unexpected out-of-network balance billing. | CMS No Surprises Act |
| 5 | doc_5_bank_overdraft_loopholes.txt | Opt-in requirements prohibiting unapproved bank overdraft fees. | CFPB Overdraft Policy |
| 6 | doc_6_student_loan_forgiveness.txt | Requirements and monthly tracking milestones for the federal PSLF program. | Federal Student Aid Portal |
| 7 | doc_7_subscription_cancel_laws.txt | Federal "Click to Cancel" rules restricting subscription cancellation loops. | FTC Press Release |
| 8 | doc_8_credit_card_fraud_liability.txt | Statutory laws capping maximum consumer liability for unauthorized charges. | FTC Stolen Card Guide |
| 9 | doc_9_car_lemon_laws.txt | Consumer protections and safety defect buyback options for new vehicles. | USA.gov Lemon Law Hub |
| 10 | doc_10_wage_theft_protections.txt | Federal fact sheet outlining wage theft protections and deduction limits. | DOL Wage Theft Fact Sheet |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:*Fixed-size character chunking using 500 characters with a 100 character overlap*

**Overlap:*The 100-character overlap prevents critical legal conditions (such as a timeframe or exception clause) from being split mechanically across a boundary, ensuring that whichever chunk is retrieved contains the full contextual meaning of the mandate.*

**Reasoning:*Consumer protection laws and government fact sheets are packed with specific, dense numbers (e.g., "$50 max liability," "30 days to investigate"). A small chunk size of 500 characters ensures that single legal clauses are kept highly concentrated without being diluted by adjacent, unrelated rule*

**More about chunking:*

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:*all-MiniLM-L6-v2* via sentence-transformers library running locally.

**Top-k:*4*. We will retrieve the top k=4 chunks per query. This balances providing enough context for the LLM to verify exceptions while staying safely within context limits and preventing irrelevant text from pulling the generation off-track.

**Production tradeoff reflection:*If deploying this for real-world production where cost isn't a constraint, we would weigh moving to an API model like text-embedding-3-large. This would provide a larger context window and better capture the complex, domain-specific semantic relationships found in legal terminology, though it would introduce API network latency and usage costs compared to our lightweight, zero-cost local database.*

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What is my maximum legal liability if my credit card is stolen online?| Exactly $0 under the Truth in Lending Act (TILA)|
| 2 |Can a landlord deduct money from my security deposit because the apartment paint is slightly faded? | No, landlords cannot deduct for standard "wear and tear" like faded paint under HUD guidelines.|
| 3 |How long does a credit bureau have to look into an error I dispute on my file? |Exactly 30 days under the Fair Credit Reporting Act (FCRA). |
| 4 | What happens to my flight refund if the airline cancels my flight due to a major system outage?| You are legally entitled to a full cash refund, not just a travel voucher, according to DOT mandates.|
| 5 | [Out of Scope Guardrail] What is the current interest rate for a high-yield savings account at Chase Bank?|I do not have enough information to answer that question based on the provided documents." (Tests system safety).|

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

     [10 Raw Documents (.txt)]
                  │
                  ▼
       [Document Ingestion & Cleaning]
                  │
                  ▼
       [Chunking: Character-based (500 chars, 100 overlap)]
                  │
                  ▼
       [Embedding Model: sentence-transformers/all-MiniLM-L6-v2]
                  │
                  ▼
       [Vector Store: Local ChromaDB Instance] ◄─── [User Query]
                  │                                      │
                  └───────────────► [Top-K Chunks] ──────┤
                                                         ▼
                                            [LLM System Prompt Guardrails]
                                                         │
                                                         ▼
                                            [Groq: Llama-3.3-70b-versatile]
                                                         │
                                                         ▼
                                            [Grounded Answer + Sources]

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
