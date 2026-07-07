const fs = require('fs');
const path = require('path');

const RAW_DIR = path.join(__dirname, '..', '..', 'documents', 'data', 'raw');

function getSourceUrl(fileName) {
  const map = {
    doc_1_credit_score_rights: 'https://www.consumerfinance.gov/consumer-tools/credit-reports-and-scores/',
    doc_2_security_deposit_laws: 'https://www.hud.gov/topics/rental_assistance/tenantrights',
    doc_3_airline_passenger_refunds: 'https://www.transportation.gov/airconsumer/flights-and-rights',
    doc_4_medical_bill_protection: 'https://www.cms.gov/nosurprises/consumers',
    doc_5_bank_overdraft_loopholes: 'https://www.consumerfinance.gov/compliance/compliance-resources/deposit-accounts-resources/overdraft-services/',
    doc_6_student_loan_forgiveness: 'https://studentaid.gov/manage-loans/forgiveness-cancellation',
    doc_7_subscription_cancel_laws: 'https://www.ftc.gov/news-events/news/press-releases/2024/10/federal-trade-commission-announces-final-click-cancel-rule',
    doc_8_credit_card_fraud_liability: 'https://www.consumer.ftc.gov/articles/lost-or-stolen-credit-atm-debit-cards',
    doc_9_car_lemon_laws: 'https://www.usa.gov/car-repair-recalled-lemon',
    doc_10_wage_theft_protections: 'https://www.dol.gov/agencies/whd/fact-sheets/16-flsa-deductions'
  };

  return map[fileName] || '';
}

function loadDocuments() {
  if (!fs.existsSync(RAW_DIR)) {
    return [];
  }

  return fs.readdirSync(RAW_DIR)
    .filter((fileName) => fileName.endsWith('.txt'))
    .map((fileName) => {
      const fullPath = path.join(RAW_DIR, fileName);
      const text = fs.readFileSync(fullPath, 'utf8');
      const baseName = path.basename(fileName, '.txt');
      return {
        fileName,
        baseName,
        text,
        url: getSourceUrl(baseName)
      };
    })
    .filter((doc) => doc.text && doc.text.trim());
}

function normalize(text) {
  return text.toLowerCase().replace(/[^a-z0-9\s]/g, ' ').split(/\s+/).filter(Boolean);
}

function retrieveDocuments(query, documents, topK = 3) {
  const queryTerms = normalize(query);
  const scored = documents.map((document) => {
    const textTerms = normalize(document.text);
    const overlap = queryTerms.filter((term) => term.length > 2 && textTerms.includes(term)).length;
    const phraseHit = document.text.toLowerCase().includes(query.toLowerCase()) ? 2 : 0;
    return {
      ...document,
      score: overlap + phraseHit
    };
  });

  return scored.sort((a, b) => b.score - a.score).slice(0, topK);
}

async function callGroq(question, context) {
  if (!process.env.GROQ_API_KEY) {
    throw new Error('Missing GROQ_API_KEY environment variable.');
  }

  const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.GROQ_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      model: 'llama-3.3-70b-versatile',
      temperature: 0.0,
      messages: [
        {
          role: 'system',
          content: 'You are a strict consumer-rights assistant. Answer only from the provided context. If the context does not contain enough information, say so clearly and do not invent facts. Mention the source file name in your answer.'
        },
        {
          role: 'user',
          content: `Context:\n${context}\n\nQuestion: ${question}\n\nAnswer:`
        }
      ]
    })
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`Groq request failed: ${response.status} ${detail}`);
  }

  const data = await response.json();
  return data.choices?.[0]?.message?.content || 'No answer returned.';
}

exports.handler = async (event) => {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
  };

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers, body: '' };
  }

  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, headers, body: JSON.stringify({ error: 'Method not allowed' }) };
  }

  let body = {};
  try {
    body = JSON.parse(event.body || '{}');
  } catch (error) {
    return { statusCode: 400, headers, body: JSON.stringify({ error: 'Invalid JSON body.' }) };
  }

  const question = (body.question || '').trim();
  if (!question) {
    return { statusCode: 400, headers, body: JSON.stringify({ error: 'Please enter a question.' }) };
  }

  try {
    const documents = loadDocuments();
    const relevantDocs = retrieveDocuments(question, documents, 3);
    const context = relevantDocs.map((doc, index) => `[Source ${index + 1}: ${doc.fileName}] ${doc.text}`).join('\n\n');
    const answer = await callGroq(question, context);
    const sources = relevantDocs.map((doc) => `${doc.fileName} — ${doc.url || 'No URL available'}`);

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ answer, sources })
    };
  } catch (error) {
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ error: error.message || 'Unexpected server error.' })
    };
  }
};
