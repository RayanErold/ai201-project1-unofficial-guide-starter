# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

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

**Chunk size:**

**Overlap:**

**Why these choices fit your documents:**

**Final chunk count:**

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**

**Production tradeoff reflection:**

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

**How source attribution is surfaced in the response:**

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**

**What the system returned:**

**Root cause (tied to a specific pipeline stage):**

**What you would change to fix it:**

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

**One way your implementation diverged from the spec, and why:**

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

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

**Instance 2**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*
