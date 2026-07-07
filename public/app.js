const form = document.getElementById('ask-form');
const questionInput = document.getElementById('question');
const statusEl = document.getElementById('status');
const answerEl = document.getElementById('answer');
const sourcesEl = document.getElementById('sources');
const sampleBtn = document.getElementById('sample-btn');

const sampleQuestion = 'What is my maximum liability if my credit card is stolen online?';

sampleBtn.addEventListener('click', () => {
  questionInput.value = sampleQuestion;
  questionInput.focus();
});

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const question = questionInput.value.trim();
  if (!question) {
    statusEl.textContent = 'Please enter a question first.';
    return;
  }

  statusEl.textContent = 'Thinking…';
  answerEl.textContent = '';
  sourcesEl.innerHTML = '';

  try {
    const response = await fetch('/.netlify/functions/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question })
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || 'Unable to get an answer right now.');
    }

    statusEl.textContent = 'Answer ready.';
    answerEl.textContent = data.answer || 'No answer returned.';
    if (data.sources && data.sources.length) {
      sourcesEl.innerHTML = '<strong>Sources:</strong><ul>' + data.sources.map((source) => `<li>${source}</li>`).join('') + '</ul>';
    }
  } catch (error) {
    statusEl.textContent = 'The request failed.';
    answerEl.textContent = error.message || 'Unknown error';
  }
});
