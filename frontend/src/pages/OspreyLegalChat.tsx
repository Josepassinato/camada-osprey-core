import React, { useState, useRef, useEffect } from 'react';

const API_URL = import.meta.env.VITE_BACKEND_URL || '';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

const QUICK_ACTIONS = [
  { label: 'RFE Response Strategy', prompt: 'I received an RFE on an H-1B petition. What is the best strategy for responding? What are the key elements I should address?' },
  { label: 'Case Assessment', prompt: 'I need to assess a new immigration case. What key factors should I evaluate for case viability and what questions should I ask the client?' },
  { label: 'Filing Checklist', prompt: 'Generate a comprehensive filing checklist for an I-485 Adjustment of Status application. Include all required forms, documents, and evidence.' },
  { label: 'Client Update Draft', prompt: 'Draft a professional client update email regarding their pending case status. Include sections for case progress, next steps, and timeline expectations.' },
  { label: 'Visa Comparison', prompt: 'Compare the H-1B and O-1A visa categories. What are the key differences in requirements, processing, and strategic advantages for the petitioner?' },
  { label: 'Compliance Review', prompt: 'What are the key compliance requirements for an employer sponsoring H-1B workers? Include LCA posting, PAF maintenance, and material change obligations.' },
];

function FormattedMessage({ content }: { content: string }) {
  const parts = content.split(/(\*\*.*?\*\*|`[^`]+`|\n)/g);
  return (
    <span>
      {parts.map((part, i) => {
        if (part.startsWith('**') && part.endsWith('**')) {
          return <strong key={i} className="font-semibold">{part.slice(2, -2)}</strong>;
        }
        if (part.startsWith('`') && part.endsWith('`')) {
          return (
            <code key={i} className="bg-black/20 px-1.5 py-0.5 rounded text-sm font-mono">
              {part.slice(1, -1)}
            </code>
          );
        }
        if (part === '\n') {
          return <br key={i} />;
        }
        return <span key={i}>{part}</span>;
      })}
    </span>
  );
}

function TypingIndicator() {
  return (
    <div className="flex items-start gap-3 animate-fade-in">
      <div className="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold shrink-0"
        style={{ backgroundColor: '#C9A84C', color: '#1a1a2e' }}>
        O
      </div>
      <div className="bg-white/5 border border-white/10 rounded-2xl rounded-tl-sm px-4 py-3">
        <div className="flex gap-1.5">
          <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '0ms' }} />
          <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '150ms' }} />
          <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '300ms' }} />
        </div>
      </div>
    </div>
  );
}

function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === 'user';
  return (
    <div className={`flex items-start gap-3 animate-fade-in ${isUser ? 'flex-row-reverse' : ''}`}>
      <div
        className="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold shrink-0"
        style={
          isUser
            ? { backgroundColor: '#2d2d4e', color: '#C9A84C', border: '1px solid rgba(201,168,76,0.3)' }
            : { backgroundColor: '#C9A84C', color: '#1a1a2e' }
        }
      >
        {isUser ? 'U' : 'O'}
      </div>
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
          isUser
            ? 'rounded-tr-sm text-white'
            : 'rounded-tl-sm text-gray-100'
        }`}
        style={
          isUser
            ? { backgroundColor: 'rgba(201,168,76,0.15)', border: '1px solid rgba(201,168,76,0.2)' }
            : { backgroundColor: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)' }
        }
      >
        <FormattedMessage content={message.content} />
        <div className="text-[10px] mt-2 opacity-40">
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>
    </div>
  );
}

export default function OspreyLegalChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [firmName, setFirmName] = useState('Your Law Firm');
  const [isEditingFirm, setIsEditingFirm] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const sendMessage = async (content: string) => {
    if (!content.trim() || isLoading) return;

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: content.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const res = await fetch(`${API_URL}/api/osprey-chat/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: content.trim(),
          conversation_id: conversationId,
          firm_name: firmName,
        }),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();

      if (!conversationId) {
        setConversationId(data.conversation_id);
      }

      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: data.response,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: 'I apologize, but I encountered an error processing your request. Please try again or contact support if the issue persists.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  const clearChat = () => {
    setMessages([]);
    setConversationId(null);
  };

  return (
    <div className="min-h-screen flex flex-col" style={{ backgroundColor: '#0f0f23', color: '#e2e8f0' }}>
      {/* Header */}
      <header
        className="border-b px-6 py-4 flex items-center justify-between"
        style={{ borderColor: 'rgba(201,168,76,0.2)', backgroundColor: 'rgba(15,15,35,0.95)' }}
      >
        <div className="flex items-center gap-3">
          <div
            className="w-10 h-10 rounded-lg flex items-center justify-center font-bold text-lg"
            style={{ backgroundColor: '#C9A84C', color: '#1a1a2e' }}
          >
            O
          </div>
          <div>
            <h1 className="text-lg font-semibold tracking-tight" style={{ fontFamily: "'Playfair Display', serif" }}>
              Osprey Legal Chat
            </h1>
            <div className="flex items-center gap-2">
              {isEditingFirm ? (
                <input
                  className="text-xs bg-transparent border-b outline-none"
                  style={{ borderColor: '#C9A84C', color: '#C9A84C' }}
                  value={firmName}
                  onChange={e => setFirmName(e.target.value)}
                  onBlur={() => setIsEditingFirm(false)}
                  onKeyDown={e => e.key === 'Enter' && setIsEditingFirm(false)}
                  autoFocus
                />
              ) : (
                <button
                  className="text-xs opacity-60 hover:opacity-100 transition-opacity"
                  onClick={() => setIsEditingFirm(true)}
                  title="Click to edit firm name"
                >
                  Chief of Staff — {firmName}
                </button>
              )}
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 text-xs opacity-60">
            <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
            Online
          </div>
          {messages.length > 0 && (
            <button
              onClick={clearChat}
              className="text-xs px-3 py-1.5 rounded-lg border transition-colors hover:bg-white/5"
              style={{ borderColor: 'rgba(255,255,255,0.1)' }}
            >
              Clear Chat
            </button>
          )}
        </div>
      </header>

      {/* Messages */}
      <main className="flex-1 overflow-y-auto px-6 py-6 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center py-20">
            <div
              className="w-16 h-16 rounded-2xl flex items-center justify-center text-2xl font-bold mb-6"
              style={{ backgroundColor: 'rgba(201,168,76,0.15)', color: '#C9A84C', border: '1px solid rgba(201,168,76,0.2)' }}
            >
              O
            </div>
            <h2
              className="text-2xl font-semibold mb-2"
              style={{ fontFamily: "'Playfair Display', serif" }}
            >
              Osprey Legal Chat
            </h2>
            <p className="text-sm opacity-50 mb-8 max-w-md">
              Your AI Chief of Staff for immigration law. Ask about case strategy, filing procedures,
              compliance requirements, or draft client communications.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 max-w-3xl w-full">
              {QUICK_ACTIONS.map(action => (
                <button
                  key={action.label}
                  onClick={() => sendMessage(action.prompt)}
                  className="text-left text-sm px-4 py-3 rounded-xl transition-all hover:scale-[1.02]"
                  style={{
                    backgroundColor: 'rgba(255,255,255,0.03)',
                    border: '1px solid rgba(201,168,76,0.15)',
                  }}
                >
                  <span style={{ color: '#C9A84C' }}>{action.label}</span>
                  <p className="text-xs opacity-40 mt-1 line-clamp-2">{action.prompt}</p>
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map(msg => <MessageBubble key={msg.id} message={msg} />)
        )}
        {isLoading && <TypingIndicator />}
        <div ref={messagesEndRef} />
      </main>

      {/* Input */}
      <footer
        className="border-t px-6 py-4"
        style={{ borderColor: 'rgba(201,168,76,0.2)', backgroundColor: 'rgba(15,15,35,0.95)' }}
      >
        <div className="max-w-4xl mx-auto flex gap-3">
          <textarea
            ref={inputRef}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about immigration law, case strategy, filing procedures..."
            rows={1}
            className="flex-1 bg-white/5 border rounded-xl px-4 py-3 text-sm resize-none outline-none focus:ring-1 placeholder:opacity-30"
            style={{
              borderColor: 'rgba(255,255,255,0.1)',
              focusRingColor: '#C9A84C',
            }}
            disabled={isLoading}
          />
          <button
            onClick={() => sendMessage(input)}
            disabled={!input.trim() || isLoading}
            className="px-5 py-3 rounded-xl text-sm font-medium transition-all disabled:opacity-30"
            style={{
              backgroundColor: '#C9A84C',
              color: '#1a1a2e',
            }}
          >
            Send
          </button>
        </div>
        <p className="text-center text-[10px] opacity-30 mt-3">
          AI assistant for legal professionals. Not a substitute for attorney judgment. Review all outputs before use.
        </p>
      </footer>

      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');
        @keyframes fade-in {
          from { opacity: 0; transform: translateY(8px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in { animation: fade-in 0.3s ease-out; }
      `}</style>
    </div>
  );
}
