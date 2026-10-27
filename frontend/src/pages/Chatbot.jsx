import React, { useState, useEffect, useRef } from 'react'
import { useLocation } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { changeLanguage } from '../i18n'
import { 
  MessageSquare, 
  Send, 
  Mic, 
  Volume2, 
  VolumeX, 
  ShieldCheck, 
  Sparkles, 
  RefreshCw, 
  FileText,
  User,
  Bot
} from 'lucide-react'
import { sendChatMessage } from '../api/client'

export default function Chatbot() {
  const { t, i18n } = useTranslation()
  const location = useLocation()
  const currentLang = i18n.language || 'en'

  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'assistant',
      text: currentLang === 'hi'
        ? "नमस्ते किसान भाई! मैं किसानसारथी एआई सहायक हूँ। आप मुझसे फसल रोग, मंडी भाव या किसान क्रेडिट कार्ड जैसी किसी भी योजना के बारे में पूछ सकते हैं।"
        : currentLang === 'pa'
        ? "ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ ਕਿਸਾਨ ਵੀਰੋ! ਮੈਂ ਕਿਸਾਨਸਾਰਥੀ ਏਆਈ ਸਹਾਇਕ ਹਾਂ। ਤੁਸੀਂ ਮੇਰੇ ਤੋਂ ਫ਼ਸਲ ਦੀਆਂ ਬਿਮਾਰੀਆਂ, ਮੰਡੀ ਭਾਅ ਜਾਂ ਕਿਸਾਨ ਕ੍ਰੈਡਿਟ ਕਾਰਡ ਬਾਰੇ ਕੋਈ ਵੀ ਸਵਾਲ ਪੁੱਛ ਸਕਦੇ ਹੋ।"
        : "Hello Farmer friend! I am your KisanSaarthi AI assistant. You can ask me anything about crop diseases, mandi prices, or schemes like PM-KISAN & KCC.",
      sources: ['schemes.json', 'pm_kisan_guide.md'],
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ])

  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, loading])

  // Handle initial query from navigation state
  useEffect(() => {
    if (location.state?.initialQuery) {
      handleSend(location.state.initialQuery)
      window.history.replaceState({}, document.title)
    }
  }, [location.state])

  const handleSend = async (textToSend) => {
    const queryText = (textToSend || input).trim()
    if (!queryText) return

    const userMessage = {
      id: Date.now(),
      sender: 'user',
      text: queryText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }

    setMessages((prev) => [...prev, userMessage])
    if (!textToSend) setInput('')

    try {
      setLoading(true)
      const res = await sendChatMessage(queryText, currentLang)
      if (res.status === 'ok') {
        const assistantMessage = {
          id: Date.now() + 1,
          sender: 'assistant',
          text: res.data.response,
          sources: res.data.sources,
          passages: res.data.retrieved_passages,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
        setMessages((prev) => [...prev, assistantMessage])
      } else {
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now() + 1,
            sender: 'assistant',
            text: "Sorry, I encountered an issue querying the agricultural knowledge base. Please try again.",
            sources: [],
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          }
        ])
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          sender: 'assistant',
          text: "Network error connecting to KisanSaarthi AI server. Please verify your connection.",
          sources: [],
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ])
    } finally {
      setLoading(false)
    }
  }

  // Web Speech API Voice Recognition
  const handleVoiceInput = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SpeechRecognition) {
      alert("Speech recognition is not supported in this browser.")
      return
    }

    try {
      const recognition = new SpeechRecognition()
      const langMap = { hi: 'hi-IN', pa: 'pa-IN', en: 'en-IN' }
      recognition.lang = langMap[currentLang.slice(0, 2)] || 'hi-IN'
      recognition.interimResults = false

      recognition.onstart = () => setIsListening(true)
      recognition.onend = () => setIsListening(false)
      recognition.onerror = () => setIsListening(false)
      recognition.onresult = (event) => {
        const speechText = event.results[0][0].transcript
        setInput(speechText)
        handleSend(speechText)
      }
      recognition.start()
    } catch (err) {
      setIsListening(false)
    }
  }

  // Text-to-Speech Output
  const handleSpeak = (text) => {
    if (!window.speechSynthesis) return
    if (isSpeaking) {
      window.speechSynthesis.cancel()
      setIsSpeaking(false)
      return
    }

    const cleanText = text.replace(/[*#_`]/g, '')
    const utterance = new SpeechSynthesisUtterance(cleanText)
    const langMap = { hi: 'hi-IN', pa: 'hi-IN', en: 'en-IN' }
    utterance.lang = langMap[currentLang.slice(0, 2)] || 'en-IN'

    utterance.onend = () => setIsSpeaking(false)
    utterance.onerror = () => setIsSpeaking(false)

    setIsSpeaking(true)
    window.speechSynthesis.speak(utterance)
  }

  const suggestionChips = currentLang === 'hi'
    ? [
        { label: 'फसल का इलाज', q: 'गेहूं के पीले पत्तों का क्या इलाज है?' },
        { label: 'आज की मंडी कीमत', q: 'लुधियाना मंडी में गेहूं का ताजा भाव क्या है?' },
        { label: 'किसान क्रेडिट / योजना', q: 'किसान क्रेडिट कार्ड पर ब्याज दर और पात्रता क्या है?' }
      ]
    : currentLang === 'pa'
    ? [
        { label: 'ਫ਼ਸਲ ਦਾ ਇਲਾਜ', q: 'ਕਣਕ ਦੇ ਪੀਲੇ ਰੱਤੂਏ ਦਾ ਇਲਾਜ ਦੱਸੋ' },
        { label: 'ਮੰਡੀ ਭਾਅ', q: 'ਅੱਜ ਲੁਧਿਆਣਾ ਮੰਡੀ ਵਿੱਚ ਕਣਕ ਦਾ ਰੇਟ ਕੀ ਹੈ?' },
        { label: 'ਕਿਸਾਨ ਕ੍ਰੈਡਿਟ ਕਾਰਡ', q: 'ਕਿਸਾਨ ਕ੍ਰੈਡਿਟ ਕਾਰਡ 4% ਵਿਆਜ ਦਰ ' }
      ]
    : [
        { label: 'Crop Disease Cure', q: 'What is the treatment for early blight in tomato?' },
        { label: "Today's Mandi Price", q: 'What is today wheat price in Ludhiana APMC?' },
        { label: 'KCC Loan at 4%', q: 'How to apply for Kisan Credit Card loan?' }
      ]

  return (
    <div className="max-w-4xl mx-auto flex flex-col h-[calc(100vh-6rem)] pb-18 md:pb-4">
      {/* Header Matching Wireframe 6 */}
      <div className="bg-white rounded-t-3xl p-4 border border-gray-200/90 border-b-0 flex items-center justify-between shadow-2xs">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-emerald-800 to-emerald-600 flex items-center justify-center text-white shadow-xs">
            <Bot className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-base font-extrabold text-gray-900 flex items-center gap-2">
              <span>{t('chat.title')}</span>
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            </h2>
            <p className="text-[11px] font-semibold text-emerald-800">
              {t('chat.online')}
            </p>
          </div>
        </div>

        {/* Language switch buttons matching wireframe 6 */}
        <div className="flex items-center gap-1 p-1 bg-gray-100 rounded-xl text-xs font-bold">
          {[
            { code: 'hi', label: 'हिन्दी' },
            { code: 'pa', label: 'ਪੰਜਾਬੀ' },
            { code: 'en', label: 'English' }
          ].map((l) => (
            <button
              key={l.code}
              onClick={() => changeLanguage(l.code)}
              className={`px-2.5 py-1 rounded-lg transition-all ${
                currentLang.startsWith(l.code)
                  ? 'bg-emerald-700 text-white shadow-2xs'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              {l.label}
            </button>
          ))}
        </div>
      </div>

      {/* Chat Messages Stream Matching Wireframe 6 */}
      <div className="flex-1 overflow-y-auto bg-gray-50/70 p-4 md:p-6 space-y-4 border-x border-gray-200/90">
        {messages.map((msg) => {
          const isUser = msg.sender === 'user'
          return (
            <div
              key={msg.id}
              className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} max-w-[90%] md:max-w-[78%] ${
                isUser ? 'ml-auto' : 'mr-auto'
              }`}
            >
              <div
                className={`p-4 rounded-3xl text-xs sm:text-sm leading-relaxed shadow-2xs ${
                  isUser
                    ? 'bg-emerald-700 text-white rounded-br-xs'
                    : 'bg-white text-gray-800 border border-emerald-100/80 rounded-bl-xs'
                }`}
              >
                <div className="whitespace-pre-wrap">{msg.text}</div>

                {/* Grounded Sources Attribution Matching Wireframe 6 */}
                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-3 pt-2.5 border-t border-emerald-50 flex flex-wrap items-center gap-1.5 text-[10px]">
                    <span className="font-bold text-emerald-800 flex items-center gap-1">
                      <FileText className="w-3 h-3 text-emerald-600" />
                      Sources:
                    </span>
                    {msg.sources.map((s, idx) => (
                      <span
                        key={idx}
                        className="bg-emerald-50 text-emerald-900 font-semibold px-2 py-0.5 rounded-md border border-emerald-200/60"
                      >
                        {s}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Message metadata row */}
              <div className="flex items-center gap-2 mt-1 px-2 text-[10px] text-gray-400">
                <span>{msg.timestamp}</span>
                {!isUser && (
                  <button
                    onClick={() => handleSpeak(msg.text)}
                    className="hover:text-emerald-700 transition-colors flex items-center gap-0.5"
                    title={isSpeaking ? 'Stop Audio' : 'Listen with Speech Synthesis'}
                  >
                    {isSpeaking ? (
                      <VolumeX className="w-3 h-3 text-emerald-700" />
                    ) : (
                      <Volume2 className="w-3 h-3" />
                    )}
                  </button>
                )}
              </div>
            </div>
          )
        })}

        {loading && (
          <div className="flex items-center gap-2 p-3 bg-white border border-gray-200 rounded-2xl max-w-xs text-xs text-gray-500 shadow-2xs">
            <RefreshCw className="w-3.5 h-3.5 text-emerald-600 animate-spin" />
            <span>Consulting official agricultural documents...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Quick Question Chips Matching Wireframe 6 */}
      <div className="bg-white border-x border-gray-200/90 px-4 py-2 flex flex-wrap items-center gap-2">
        <span className="text-[10px] font-bold uppercase text-gray-400 tracking-wider">
          Suggested:
        </span>
        {suggestionChips.map((chip, i) => (
          <button
            key={i}
            onClick={() => handleSend(chip.q)}
            className="text-xs bg-emerald-50 hover:bg-emerald-100 text-emerald-900 border border-emerald-100 px-3 py-1 rounded-xl transition-colors font-medium cursor-pointer"
          >
            {chip.label}
          </button>
        ))}
      </div>

      {/* Input Box Matching Wireframe 6 */}
      <div className="bg-white rounded-b-3xl p-4 border border-gray-200/90 border-t-0 shadow-sm">
        <form
          onSubmit={(e) => {
            e.preventDefault()
            handleSend()
          }}
          className="relative flex items-center"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={isListening ? t('chat.listening') : t('chat.placeholder')}
            className="w-full pl-4 pr-24 py-3.5 text-xs sm:text-sm bg-gray-50 border border-gray-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600 transition-all placeholder:text-gray-400"
          />

          <div className="absolute right-2 flex items-center gap-1">
            <button
              type="button"
              onClick={handleVoiceInput}
              className={`p-2 rounded-xl transition-colors cursor-pointer ${
                isListening
                  ? 'bg-red-500 text-white animate-pulse'
                  : 'text-gray-500 hover:text-emerald-700 hover:bg-emerald-50'
              }`}
              title="Speak Question"
            >
              <Mic className="w-4 h-4" />
            </button>

            <button
              type="submit"
              disabled={!input.trim()}
              className="p-2.5 rounded-xl bg-emerald-700 text-white hover:bg-emerald-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors cursor-pointer"
              title="Send Message"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </form>

        <p className="text-[10px] text-gray-400 text-center mt-2">
          {t('chat.disclaimer')}
        </p>
      </div>
    </div>
  )
}
