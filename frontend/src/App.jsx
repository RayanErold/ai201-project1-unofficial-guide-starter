import { useState } from 'react';
import { 
  Send, 
  RotateCcw, 
  Copy, 
  Check, 
  BookOpen, 
  AlertTriangle, 
  Scale, 
  HelpCircle, 
  Sparkles, 
  ShieldCheck, 
  ExternalLink,
  ChevronRight,
  Info
} from 'lucide-react';

const SAMPLE_QUESTIONS = [
  {
    text: "What is my maximum liability if my credit card is stolen online?",
    category: "Credit Card Fraud"
  },
  {
    text: "Can a landlord deduct money from my deposit for slightly faded paint?",
    category: "Tenant Rights"
  },
  {
    text: "How long does a credit bureau have to investigate a disputed error?",
    category: "Credit Scores"
  },
  {
    text: "What happens to my refund if the airline cancels my flight?",
    category: "Travel Rights"
  },
  {
    text: "What are common bank overdraft fee loopholes I should know about?",
    category: "Banking Fees"
  },
  {
    text: "What is the PSLF monthly tracking milestone for student loan forgiveness?",
    category: "Student Loans"
  }
];

export default function App() {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [answer, setAnswer] = useState('');
  const [sources, setSources] = useState([]);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState('');
  const [searchTime, setSearchTime] = useState(null);

  const handleSampleClick = (qText) => {
    setQuestion(qText);
  };

  const handleClear = () => {
    setQuestion('');
    setAnswer('');
    setSources([]);
    setError('');
    setSearchTime(null);
  };

  const handleCopy = () => {
    if (!answer) return;
    navigator.clipboard.writeText(answer);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const trimmedQuestion = question.trim();
    if (!trimmedQuestion) {
      setError('Please enter a question first.');
      return;
    }

    setLoading(true);
    setError('');
    setAnswer('');
    setSources([]);
    setSearchTime(null);
    const startTime = performance.now();

    try {
      // Resolve API endpoint: in dev, if opened on port 5173 (Vite), fallback to port 8888 (Netlify Dev proxy)
      let apiUrl = '/.netlify/functions/ask';
      if (import.meta.env.DEV && window.location.port !== '8888') {
        apiUrl = 'http://localhost:8888/.netlify/functions/ask';
      }

      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: trimmedQuestion })
      });

      if (!response.ok) {
        let errorMsg = 'Failed to retrieve an answer.';
        try {
          const errData = await response.json();
          errorMsg = errData.error || errorMsg;
        } catch {
          try {
            const rawText = await response.text();
            if (rawText && rawText.length < 200) {
              errorMsg = rawText;
            } else {
              errorMsg = `Server returned status code ${response.status}`;
            }
          } catch {}
        }
        throw new Error(errorMsg);
      }

      const data = await response.json();
      setAnswer(data.answer || 'No answer returned.');
      setSources(data.sources || []);
      setSearchTime(((performance.now() - startTime) / 1000).toFixed(2));
    } catch (err) {
      console.error(err);
      setError(err.message || 'An unexpected connection error occurred.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans selection:bg-indigo-500 selection:text-white">
      {/* Background Gradients for Aesthetics */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-indigo-500/10 rounded-full filter blur-3xl pointer-events-none" />
      <div className="absolute top-1/3 right-1/4 w-96 h-96 bg-cyan-500/10 rounded-full filter blur-3xl pointer-events-none" />

      {/* Outer wrapper */}
      <div className="max-w-6xl mx-auto px-4 py-8 relative z-10">
        
        {/* Header */}
        <header className="text-center mb-12">
          <div className="inline-flex items-center gap-2 bg-indigo-950/40 border border-indigo-800/40 px-3 py-1 rounded-full text-indigo-400 text-xs font-semibold tracking-wide uppercase mb-4">
            <Scale size={14} className="text-indigo-400" />
            Legal & Regulatory RAG Guide
          </div>
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-white mb-4 bg-gradient-to-r from-white via-slate-100 to-indigo-300 bg-clip-text text-transparent">
            Consumer Rights Assistant
          </h1>
          <p className="max-w-2xl mx-auto text-base md:text-lg text-slate-400">
            Get instant, grounded answers from verified federal protection acts (FCRA, TILA, HUD, DOT, CMS, FTC) and consumer safety regulations.
          </p>
        </header>

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          {/* Left panel - Query Box and Examples */}
          <div className="lg:col-span-7 space-y-6">
            <div className="bg-slate-900/40 backdrop-blur-xl border border-slate-800/80 rounded-2xl p-6 shadow-xl">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                  <Sparkles size={18} className="text-indigo-400" />
                  Ask a Question
                </h2>
                {(question || answer) && (
                  <button 
                    onClick={handleClear}
                    className="text-xs text-slate-500 hover:text-slate-300 flex items-center gap-1 transition-colors"
                  >
                    <RotateCcw size={12} />
                    Reset
                  </button>
                )}
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="relative">
                  <textarea
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="e.g. What is my maximum legal liability if my credit card is stolen online?"
                    rows={4}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-4 text-slate-200 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all resize-none text-sm md:text-base"
                    disabled={loading}
                  />
                  <div className="absolute right-3 bottom-3 flex items-center gap-2">
                    <button
                      type="submit"
                      disabled={loading || !question.trim()}
                      className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 disabled:hover:bg-indigo-600 text-white font-medium text-sm px-4 py-2 rounded-lg flex items-center gap-2 transition-all shadow-lg shadow-indigo-950/50"
                    >
                      {loading ? (
                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      ) : (
                        <Send size={14} />
                      )}
                      {loading ? 'Analyzing...' : 'Ask'}
                    </button>
                  </div>
                </div>
              </form>

              {error && (
                <div className="mt-4 bg-red-950/20 border border-red-800/40 p-4 rounded-xl flex items-start gap-3">
                  <AlertTriangle className="text-red-500 shrink-0 mt-0.5" size={18} />
                  <div>
                    <h4 className="text-sm font-semibold text-red-400">Request Error</h4>
                    <p className="text-xs text-slate-400 mt-1">{error}</p>
                  </div>
                </div>
              )}
            </div>

            {/* Example Questions */}
            <div className="bg-slate-900/20 border border-slate-800/40 rounded-2xl p-6">
              <h3 className="text-sm font-medium text-slate-400 mb-4 flex items-center gap-2">
                <HelpCircle size={16} className="text-slate-500" />
                Example Questions (Click to Ask)
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {SAMPLE_QUESTIONS.map((sample, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => handleSampleClick(sample.text)}
                    className="text-left bg-slate-900/50 hover:bg-slate-900 border border-slate-850 hover:border-slate-700/60 p-3 rounded-xl transition-all group flex flex-col justify-between"
                  >
                    <span className="text-xs text-slate-200 group-hover:text-indigo-300 transition-colors line-clamp-2">
                      {sample.text}
                    </span>
                    <span className="text-[10px] text-slate-500 font-semibold mt-2 inline-block px-1.5 py-0.5 bg-slate-950 rounded">
                      {sample.category}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Right panel - Answer Output & Sources */}
          <div className="lg:col-span-5 space-y-6">
            
            {/* Answer Display */}
            <div className="bg-slate-900/40 backdrop-blur-xl border border-slate-800/80 rounded-2xl p-6 shadow-xl min-h-[280px] flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between border-b border-slate-800/60 pb-3 mb-4">
                  <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                    <ShieldCheck size={18} className="text-emerald-400" />
                    Verified Answer
                  </h3>
                  {answer && (
                    <button
                      onClick={handleCopy}
                      className="text-slate-400 hover:text-white transition-colors p-1.5 hover:bg-slate-800 rounded-lg flex items-center gap-1.5 text-xs"
                      title="Copy response to clipboard"
                    >
                      {copied ? <Check size={14} className="text-emerald-400" /> : <Copy size={14} />}
                      {copied ? 'Copied!' : 'Copy'}
                    </button>
                  )}
                </div>

                {loading ? (
                  <div className="space-y-3 py-4 animate-pulse">
                    <div className="h-4 bg-slate-800 rounded w-3/4"></div>
                    <div className="h-4 bg-slate-800 rounded w-full"></div>
                    <div className="h-4 bg-slate-800 rounded w-5/6"></div>
                    <div className="h-4 bg-slate-800 rounded w-2/3"></div>
                  </div>
                ) : answer ? (
                  <div className="text-slate-300 text-sm md:text-base leading-relaxed whitespace-pre-line prose prose-invert max-w-none">
                    {answer}
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center text-slate-500 py-12 text-center">
                    <BookOpen size={48} className="text-slate-700 mb-3 animate-pulse" />
                    <p className="text-sm">Submit a question to receive a grounded legal explanation.</p>
                  </div>
                )}
              </div>

              {searchTime && !loading && (
                <div className="mt-6 pt-3 border-t border-slate-800/60 flex items-center justify-between text-[11px] text-slate-500">
                  <span className="flex items-center gap-1">
                    <Info size={12} />
                    Strict Grounding Active
                  </span>
                  <span>Processed in {searchTime}s</span>
                </div>
              )}
            </div>

            {/* Sources List */}
            {sources.length > 0 && !loading && (
              <div className="bg-slate-900/40 backdrop-blur-xl border border-slate-800/80 rounded-2xl p-6 shadow-xl">
                <h3 className="text-sm font-semibold text-white flex items-center gap-2 border-b border-slate-800/60 pb-3 mb-3">
                  <BookOpen size={16} className="text-indigo-400" />
                  Source Documents Cited
                </h3>
                <ul className="space-y-2 text-xs">
                  {sources.map((source, idx) => {
                    const parts = source.split(' — ');
                    const title = parts[0] || source;
                    const url = parts[1] || '';
                    const isLinkable = url && url.startsWith('http');

                    return (
                      <li key={idx} className="flex items-start gap-2 bg-slate-950/40 border border-slate-800/50 p-2.5 rounded-lg">
                        <ChevronRight size={14} className="text-indigo-400 shrink-0 mt-0.5" />
                        <div className="min-w-0 flex-1">
                          <p className="font-medium text-slate-200 truncate">{title}</p>
                          {isLinkable ? (
                            <a 
                              href={url} 
                              target="_blank" 
                              rel="noopener noreferrer" 
                              className="text-[10px] text-indigo-400 hover:text-indigo-300 hover:underline flex items-center gap-1 mt-1 truncate"
                            >
                              Official Government Link <ExternalLink size={10} />
                            </a>
                          ) : (
                            <span className="text-[10px] text-slate-500 mt-1 block">No external link available</span>
                          )}
                        </div>
                      </li>
                    );
                  })}
                </ul>
              </div>
            )}

          </div>

        </div>

        {/* Footer */}
        <footer className="text-center text-xs text-slate-600 mt-16 border-t border-slate-900/60 pt-6">
          <p>© 2026 RAG Guide. Powered by Llama-3.3-70b-versatile & Netlify Functions.</p>
        </footer>

      </div>
    </div>
  );
}
