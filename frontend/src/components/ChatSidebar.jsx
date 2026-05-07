import React, { useState, useRef } from 'react';
import { Mic, Send, Volume2, Square, Loader2 } from 'lucide-react';

const ChatSidebar = ({ setMapData }) => {
  const [messages, setMessages] = useState([
    { id: 1, text: 'مرحباً بك في المساعد المكاني الذكي لهيئة تطوير منطقة مكة المكرمة. كيف يمكنني مساعدتك؟', sender: 'ai' }
  ]);
  const [input, setInput] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  // عنوان السيرفر الأساسي
  const API_BASE_URL = 'http://localhost:8000';

  const handleSendText = async () => {
    if (!input.trim() || isLoading) return;
    
    const currentInput = input;
    setInput('');
    setIsLoading(true);
    setMessages(prev => [...prev, { id: Date.now(), text: currentInput, sender: 'user' }]);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: currentInput, session_id: 'session_default' })
      });
      
      const data = await response.json();
      
      // إضافة رد الـ AI للمحادثة
      setMessages(prev => [...prev, { 
        id: Date.now(), 
        text: data.answer || 'تمت معالجة طلبك بنجاح.', 
        sender: 'ai',
        hasAudio: !!data.audio_url,
        audio_url: data.audio_url ? `${API_BASE_URL}/api/v1/download?path=${data.audio_url}` : null
      }]);
      
      // 🚀 التحديث الجوهري: تمرير البيانات الجغرافية المباشرة للخريطة
      if (data.geojson || data.points || data.has_geometry) {
          // نرسل الكائن كاملاً مع إضافة timestamp لإجبار React-Leaflet على إعادة الرسم
          setMapData({
              ...data,
              timestamp: Date.now()
          });
      } 
      else if (data.region_id) {
          const layer = data.layer_type || 'governorate';
          const geoRes = await fetch(`${API_BASE_URL}/api/v1/geometry/${layer}/${data.region_id}`);
          const geoJsonData = await geoRes.json();
          setMapData({ geojson: geoJsonData, timestamp: Date.now() });
      }

    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, { id: Date.now(), text: 'حدث خطأ في الاتصال بالخادم.', sender: 'ai'}]);
    } finally {
      setIsLoading(false);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = e => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };
      
      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        setIsLoading(true);
        setMessages(prev => [...prev, { id: Date.now(), text: '🎤 جاري معالجة الصوت...', sender: 'user' }]);
        
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.wav');
        formData.append('session_id', 'session_default');
        
        try {
          const response = await fetch(`${API_BASE_URL}/api/v1/query/audio`, {
            method: 'POST',
            body: formData
          });
          const data = await response.json();
          
          setMessages(prev => {
             const newMsgs = [...prev];
             if(data.transcribed_text) {
                 newMsgs[newMsgs.length - 1].text = data.transcribed_text;
             }
             newMsgs.push({
                id: Date.now(), 
                text: data.answer || 'تمت المعالجة بنجاح.', 
                sender: 'ai',
                hasAudio: !!data.audio_url,
                audio_url: data.audio_url ? `${API_BASE_URL}/api/v1/download?path=${data.audio_url}` : null
             });
             return newMsgs;
          });
          
          // 🚀 تحديث الخريطة في حالة الرد الصوتي أيضاً
          if (data.geojson || data.points || data.has_geometry) {
              setMapData({ ...data, timestamp: Date.now() });
          } else if (data.region_id) {
              const layer = data.layer_type || 'governorate';
              const geoRes = await fetch(`${API_BASE_URL}/api/v1/geometry/${layer}/${data.region_id}`);
              const geoJsonData = await geoRes.json();
              setMapData({ geojson: geoJsonData, timestamp: Date.now() });
          }
          
          if (data.audio_url) {
              new Audio(`${API_BASE_URL}/api/v1/download?path=${data.audio_url}`).play();
          }
        } catch (err) {
          console.error(err);
          setMessages(prev => [...prev, { id: Date.now(), text: 'حدث خطأ أثناء معالجة الصوت.', sender: 'ai'}]);
        } finally {
          setIsLoading(false);
        }
      };
      
      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (err) {
      alert('يجب السماح بالوصول للمايكروفون!');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      setIsRecording(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* 🟢 الشعار المكبر (Header) */}
      <div className="header-banner" style={{ 
        display: 'flex', alignItems: 'center', justifyContent: 'center', 
        backgroundColor: '#FFFFFF', borderBottom: '3px solid var(--accent-gold)', 
        height: '110px', padding: '0', flexShrink: 0, overflow: 'hidden', position: 'relative'
      }}>
        <img 
          src="/logo.svg" 
          alt="الهيئة" 
          style={{ 
            width: '100%', height: '100%', objectFit: 'contain',
            transform: 'scale(1.8)', transformOrigin: 'center'
          }} 
        />
      </div>
      
      {/* منطقة الرسائل */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '20px', display: 'flex', flexDirection: 'column', gap: '20px', background: 'var(--panel-bg)' }}>
        {messages.map(msg => (
          <div key={msg.id} style={{
            alignSelf: msg.sender === 'user' ? 'flex-start' : 'flex-end',
            background: msg.sender === 'user' ? 'var(--grad-accent)' : '#F7F5F0',
            padding: '14px 18px', borderRadius: '16px', maxWidth: '85%',
            color: msg.sender === 'user' ? '#FFFFFF' : '#003B38',
            border: msg.sender === 'ai' ? '1px solid var(--accent-gold)' : 'none',
            boxShadow: msg.sender === 'ai' ? '0 4px 15px rgba(0,0,0,0.2)' : 'none',
            lineHeight: '1.6', direction: 'rtl'
          }}>
            <p style={{ margin: 0, fontWeight: '500' }}>{msg.text}</p>
            {msg.hasAudio && msg.audio_url && (
               <button onClick={() => { new Audio(msg.audio_url).play(); }} style={{ 
                 marginTop: '10px', background: 'transparent', border: '1px solid var(--accent-gold)', 
                 color: '#003B38', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', 
                 padding: '6px 12px', borderRadius: '20px', fontSize: '0.85rem'
               }}>
                 <Volume2 size={16} /> استماع
               </button>
            )}
          </div>
        ))}
        {isLoading && (
          <div style={{ alignSelf: 'flex-end', display: 'flex', alignItems: 'center', gap: '10px', color: 'var(--accent-gold)' }}>
            <Loader2 size={20} className="animate-spin" />
            <span style={{ fontSize: '0.9rem' }}>جاري المعالجة...</span>
          </div>
        )}
      </div>

      {/* منطقة الإدخال */}
      <div style={{ padding: '20px', backgroundColor: 'var(--bg-dark-green)', borderTop: '1px solid var(--accent-gold)' }}>
        <div style={{ display: 'flex', gap: '10px', background: '#F4F1EA', padding: '12px', borderRadius: '30px', border: '1px solid var(--accent-gold)' }}>
          {isRecording ? (
             <button onClick={stopRecording} style={{ background: '#e74c3c', border: 'none', color: '#FFF', borderRadius: '50%', width: '40px', height: '40px', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>
               <Square size={18} />
             </button>
          ) : (
             <button onClick={startRecording} disabled={isLoading} style={{ background: 'transparent', border: 'none', color: '#003B38', cursor: 'pointer', opacity: isLoading ? 0.5 : 1 }}>
               <Mic size={22} />
             </button>
          )}
          
          <input 
            type="text" 
            placeholder={isRecording ? "جاري التسجيل..." : "اسأل المساعد المكاني الذكي للهيئة..."} 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSendText()}
            disabled={isRecording || isLoading}
            style={{ flex: 1, background: 'transparent', border: 'none', color: '#003B38', outline: 'none', direction: 'rtl', fontWeight: '500' }}
          />
          <button 
            onClick={handleSendText} 
            disabled={isRecording || isLoading || !input.trim()} 
            style={{ background: 'var(--grad-accent)', border: 'none', color: '#003B38', borderRadius: '50%', width: '40px', height: '40px', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', opacity: (isLoading || !input.trim()) ? 0.5 : 1 }}
          >
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatSidebar;