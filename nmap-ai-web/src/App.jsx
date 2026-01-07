import React, { useState, useEffect, useRef } from 'react';
import { 
  Shield, Terminal, Activity, Cpu, Globe, Lock, 
  Zap, ChevronRight, Command, Layers, AlertTriangle, CheckCircle2, XCircle
} from 'lucide-react';

// --- Components ---
const CyberButton = ({ children, onClick, disabled, className = "" }) => (
  <button 
    onClick={onClick}
    disabled={disabled}
    className={`relative group overflow-hidden px-6 py-2 bg-blue-900/30 border border-blue-500/50 text-blue-400 font-mono uppercase tracking-widest text-xs transition-all hover:bg-blue-500 hover:text-white disabled:opacity-50 ${className}`}
  >
    <div className="absolute inset-0 w-full h-full bg-blue-500/10 group-hover:animate-pulse" />
    <span className="relative z-10 flex items-center gap-2">{children}</span>
  </button>
);

const StatusCard = ({ icon: Icon, label, value, color = "blue" }) => (
  <div className={`bg-slate-900/50 border-l-2 border-${color}-500 p-3 flex items-center gap-3`}>
    <Icon className={`text-${color}-400`} size={18} />
    <div>
      <p className="text-[10px] uppercase text-slate-500 font-bold">{label}</p>
      <p className="text-sm font-mono text-slate-200">{value}</p>
    </div>
  </div>
);

// --- Main App ---
function App() {
  const [messages, setMessages] = useState([]);
  const [intent, setIntent] = useState('');
  const [target, setTarget] = useState('');
  const [loading, setLoading] = useState(false);
  const [systemStatus, setSystemStatus] = useState('READY');
  const chatEndRef = useRef(null);

  // --- Chat Logic ---
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!intent || !target) return;
    setSystemStatus('PROCESSING');
    
    const userMessage = { type: 'user', intent, target, timestamp: new Date().toLocaleTimeString() };
    setMessages(prev => [...prev, userMessage]);
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ intent, target })
      });
      const data = await response.json();
      setMessages(prev => [...prev, { type: 'bot', ...data, timestamp: new Date().toLocaleTimeString() }]);
      setSystemStatus('READY');
    } catch (error) {
      setMessages(prev => [...prev, { type: 'error', text: 'SYSTEM_ERROR: API_UNREACHABLE' }]);
      setSystemStatus('ERROR');
    } finally {
      setLoading(false);
      setIntent('');
    }
  };

  return (
    <div className="h-screen bg-[#020617] text-slate-300 font-sans selection:bg-blue-500/30 overflow-hidden flex flex-col">
      {/* Futuristic Background Grid */}
      <div className="fixed inset-0 bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')] opacity-20 pointer-events-none" />
      
      {/* Top Navigation / Status Bar */}
      <nav className="relative z-20 border-b border-blue-900/50 bg-slate-950/80 backdrop-blur-md p-4 flex justify-between items-center">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-500/10 rounded-lg border border-blue-500/20">
            <Shield className="text-blue-500 animate-pulse" size={24} />
          </div>
          <div>
            <h1 className="text-lg font-black tracking-tighter text-white uppercase">NMAP-AI <span className="text-blue-500">Command Center</span></h1>
            <div className="flex items-center gap-2 text-[10px] font-mono text-slate-500">
              <span className="w-2 h-2 rounded-full bg-green-500 animate-ping" />
              SYSTEM_STATUS: {systemStatus} // V4.2.0-STABLE
            </div>
          </div>
        </div>
        <div className="hidden md:flex gap-6">
          <StatusCard icon={Activity} label="Network" value="Active" color="green" />
          <StatusCard icon={Cpu} label="Agent Load" value={loading ? "88%" : "12%"} color="blue" />
          <StatusCard icon={Globe} label="Region" value="Global" color="purple" />
        </div>
      </nav>

      <div className="relative z-10 flex flex-1 overflow-hidden">
        {/* Sidebar - System Metrics */}
        <aside className="hidden lg:block w-64 border-r border-blue-900/30 bg-slate-950/50 p-4 space-y-6">
          <div className="space-y-2">
            <h3 className="text-[10px] font-bold text-blue-500 uppercase tracking-widest">Active Modules</h3>
            <div className="space-y-1">
              {['KG-RAG Engine', 'LoRA Specialist', 'Diffusion Synthesizer', 'MCP Validator'].map(m => (
                <div key={m} className="flex items-center gap-2 text-xs p-2 bg-slate-900/50 rounded border border-slate-800">
                  <div className="w-1 h-1 bg-blue-400 rounded-full" /> {m}
                </div>
              ))}
            </div>
          </div>
          <div className="p-4 bg-blue-900/10 border border-blue-500/20 rounded-lg">
            <Lock className="text-blue-400 mb-2" size={20} />
            <p className="text-[10px] text-blue-300 font-mono leading-relaxed uppercase tracking-tighter">
              Open Access Mode Enabled.
            </p>
          </div>
        </aside>

        {/* Main Chat Area */}
        <main className="flex-1 flex flex-col relative bg-slate-950/20">
          <div className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar">
            {messages.length === 0 && (
              <div className="h-full flex flex-col items-center justify-center text-center space-y-4 opacity-40">
                <Command size={64} className="text-blue-500" />
                <p className="font-mono text-sm uppercase tracking-widest">Awaiting Operator Commands...</p>
              </div>
            )}
            
            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-4 duration-300`}>
                <div className={`max-w-[85%] space-y-1 ${msg.type === 'user' ? 'items-end' : 'items-start'}`}>
                  <div className={`p-4 rounded-xl shadow-2xl ${
                    msg.type === 'user' 
                      ? 'bg-blue-600 text-white rounded-tr-none' 
                      : 'bg-slate-900 border border-blue-900/50 rounded-tl-none'
                  }`}>
                    {msg.type === 'user' ? (
                      <div className="space-y-1">
                        <p className="text-xs font-bold opacity-70 uppercase">Target: {msg.target}</p>
                        <p className="text-sm">{msg.intent}</p>
                      </div>
                    ) : msg.type === 'error' ? (
                      <p className="text-red-400 font-mono text-xs flex items-center gap-2">
                        <AlertTriangle size={14} /> {msg.text}
                      </p>
                    ) : msg.category === 'Irrelevant' ? (
                      <div className="space-y-2">
                        <div className="flex items-center gap-2 text-[10px] font-mono text-red-400">
                          <XCircle size={12} /> OUT_OF_CONTEXT
                        </div>
                        <p className="text-sm text-slate-400 italic">{msg.error}</p>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        <div className="flex justify-between items-center border-b border-slate-800 pb-2">
                          <div className="flex items-center gap-2 text-[10px] font-mono text-blue-400">
                            <Layers size={12} /> {msg.category} AGENT
                          </div>
                          <div className="text-[10px] font-mono text-slate-500">{msg.timestamp}</div>
                        </div>
                        <div className="relative group">
                          <div className="absolute -inset-1 bg-gradient-to-r from-blue-500 to-cyan-500 rounded blur opacity-20 group-hover:opacity-40 transition duration-1000"></div>
                          <div className="relative bg-black p-3 rounded border border-blue-500/30 font-mono text-green-400 text-sm break-all">
                            <span className="text-slate-500 mr-2">$</span>{msg.command}
                          </div>
                        </div>
                        <div className="grid grid-cols-2 gap-2">
                          <div className="flex items-center gap-2 text-[10px] font-mono bg-slate-950 p-2 rounded border border-slate-800">
                            {msg.is_valid ? <CheckCircle2 size={12} className="text-green-500" /> : <AlertTriangle size={12} className="text-red-500" />}
                            SEMANTIC: {msg.is_valid ? 'PASSED' : 'FAILED'}
                          </div>
                          <div className="flex items-center gap-2 text-[10px] font-mono bg-slate-950 p-2 rounded border border-slate-800">
                            <Zap size={12} className="text-yellow-500" />
                            FUNCTIONAL: VERIFIED
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                  <p className="text-[8px] font-mono text-slate-600 uppercase px-2">{msg.timestamp}</p>
                </div>
              </div>
            ))}
            <div ref={chatEndRef} />
          </div>

          {/* Input Console - FIXED */}
          <div className="p-6 bg-slate-950/90 backdrop-blur-xl border-t border-blue-900/30">
            <div className="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="md:col-span-1 relative">
                <Globe className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={16} />
                <input
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg py-3 pl-10 pr-4 text-sm focus:outline-none focus:border-blue-500 transition-all font-mono text-white placeholder-slate-500"
                  placeholder="TARGET_IP"
                  value={target}
                  onChange={(e) => setTarget(e.target.value)}
                />
              </div>
              <div className="md:col-span-3 flex gap-3">
                <div className="flex-1 relative">
                  <Terminal className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={16} />
                  <input
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg py-3 pl-10 pr-4 text-sm focus:outline-none focus:border-blue-500 transition-all text-white placeholder-slate-500"
                    placeholder="ENTER_SCAN_INTENT..."
                    value={intent}
                    onChange={(e) => setIntent(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                  />
                </div>
                <CyberButton onClick={handleSend} disabled={loading || !intent || !target}>
                  {loading ? <Activity className="animate-spin" size={16} /> : <ChevronRight size={16} />}
                  Execute
                </CyberButton>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;