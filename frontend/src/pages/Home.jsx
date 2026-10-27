import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import {
  Stethoscope,
  TrendingUp,
  Landmark,
  MessageSquare,
  Mic,
  Send,
  ArrowRight,
  Sparkles,
  AlertCircle,
  CheckCircle,
  Wheat,
  CloudSun,
  Droplets,
  Wind,
  ShieldCheck,
  Compass
} from 'lucide-react'
import { getWeather } from '../api/client'

export default function Home() {
  const { t, i18n } = useTranslation()
  const navigate = useNavigate()
  const [query, setQuery] = useState('')
  const [isListening, setIsListening] = useState(false)
  const [weather, setWeather] = useState(null)

  useEffect(() => {
    getWeather('ludhiana')
      .then((res) => {
        if (res.status === 'ok') setWeather(res.data)
      })
      .catch((err) => console.log('Weather fetch notice:', err))
  }, [])

  const handleSearchSubmit = (e) => {
    e.preventDefault()
    if (query.trim()) {
      navigate('/chat', { state: { initialQuery: query.trim() } })
    }
  }

  const handleVoiceInput = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SpeechRecognition) {
      alert("Voice recognition is not supported in this browser. Please type your query.")
      return
    }

    try {
      const recognition = new SpeechRecognition()
      const langMap = { hi: 'hi-IN', pa: 'pa-IN', en: 'en-IN' }
      recognition.lang = langMap[i18n.language?.slice(0, 2)] || 'hi-IN'
      recognition.interimResults = false

      recognition.onstart = () => setIsListening(true)
      recognition.onend = () => setIsListening(false)
      recognition.onerror = () => setIsListening(false)
      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript
        setQuery(transcript)
        navigate('/chat', { state: { initialQuery: transcript } })
      }
      recognition.start()
    } catch (err) {
      setIsListening(false)
    }
  }

  const cards = [
    {
      title: t('services.crop_health_title'),
      desc: t('services.crop_health_desc'),
      btnText: t('services.crop_health_btn'),
      icon: Stethoscope,
      to: '/doctor',
      color: 'bg-emerald-50 text-emerald-800 border-emerald-200 hover:border-emerald-400',
      btnColor: 'bg-emerald-700 hover:bg-emerald-800 text-white'
    },
    {
      title: t('services.mandi_prices_title'),
      desc: t('services.mandi_prices_desc'),
      btnText: t('services.mandi_prices_btn'),
      icon: TrendingUp,
      to: '/prices',
      color: 'bg-green-50 text-green-900 border-green-200 hover:border-green-400',
      btnColor: 'bg-green-700 hover:bg-green-800 text-white'
    },
    {
      title: t('services.schemes_title'),
      desc: t('services.schemes_desc'),
      btnText: t('services.schemes_btn'),
      icon: Landmark,
      to: '/schemes',
      color: 'bg-teal-50 text-teal-900 border-teal-200 hover:border-teal-400',
      btnColor: 'bg-teal-700 hover:bg-teal-800 text-white'
    }
  ]

  const demoTourSteps = [
    {
      step: '1',
      title: 'Diagnose Leaf',
      desc: 'MobileNetV2 Early Blight test',
      action: () => navigate('/doctor')
    },
    {
      step: '2',
      title: 'Mandi Rates',
      desc: 'Ludhiana Wheat +2.1% Hold',
      action: () => navigate('/prices?crop=Wheat&mandi=ludhiana')
    },
    {
      step: '3',
      title: 'Credit Score',
      desc: 'Score 97/100 & PDF Checklist',
      action: () => navigate('/schemes')
    },
    {
      step: '4',
      title: 'Ask Saarthi',
      desc: 'Multilingual RAG with citations',
      action: () => navigate('/chat', { state: { initialQuery: 'ਕਿਸਾਨ ਕ੍ਰੈਡਿਟ ਕਾਰਡ ਲਈ ਕਿਹੜੇ ਕਾਗਜ਼ ਚਾਹੀਦੇ ਹਨ?' } })
    }
  ]

  return (
    <div className="space-y-6 pb-20 md:pb-8">
      {/* Top Banner Greeting */}
      <div className="bg-gradient-to-r from-emerald-800 via-emerald-700 to-green-700 rounded-3xl p-6 md:p-8 text-white shadow-md relative overflow-hidden">
        <div className="relative z-10 max-w-2xl">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/15 backdrop-blur-md text-emerald-100 text-xs font-semibold mb-3">
            <Wheat className="w-3.5 h-3.5 text-amber-300" />
            <span>KisanSaarthi AI Portal</span>
          </div>
          <h2 className="text-2xl md:text-3xl font-extrabold tracking-tight mb-2">
            {t('good_morning')}
          </h2>
          <p className="text-emerald-100/90 text-sm md:text-base font-normal">
            {t('how_can_help')}
          </p>
        </div>

        {/* Ambient graphic */}
        <div className="absolute right-0 bottom-0 translate-x-8 translate-y-8 w-60 h-60 bg-emerald-600/30 rounded-full blur-2xl pointer-events-none" />
      </div>

      {/* Hackathon Interactive Demo Tour Banner */}
      <div className="bg-gradient-to-r from-amber-50 to-emerald-50 rounded-2xl p-4 md:p-5 border border-amber-200/80 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
          <div className="flex items-center gap-2">
            <span className="p-1 rounded-lg bg-amber-500 text-white font-bold text-xs">
              <Compass className="w-4 h-4" />
            </span>
            <h4 className="text-sm font-extrabold text-gray-900 tracking-tight">
              Judge & Evaluator 3-Minute Demo Walkthrough
            </h4>
          </div>
          <span className="text-[11px] font-semibold text-amber-800 bg-amber-100/80 px-2.5 py-0.5 rounded-full self-start sm:self-auto">
            Interactive Test Flow
          </span>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-2.5">
          {demoTourSteps.map((st, i) => (
            <button
              key={i}
              onClick={st.action}
              className="bg-white/90 hover:bg-white rounded-xl p-3 border border-amber-100 text-left transition-all hover:shadow-xs group cursor-pointer"
            >
              <div className="flex items-center gap-1.5 mb-1">
                <span className="w-5 h-5 rounded-full bg-emerald-700 text-white font-bold text-[10px] flex items-center justify-center">
                  {st.step}
                </span>
                <span className="text-xs font-bold text-gray-900 group-hover:text-emerald-700 transition-colors">
                  {st.title}
                </span>
              </div>
              <p className="text-[10px] text-gray-500 line-clamp-1">{st.desc}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Prominent Talk to AI Assistant Search Box */}
      <div className="bg-white rounded-2xl p-5 md:p-6 shadow-sm border border-emerald-100">
        <div className="flex items-center gap-2 mb-1">
          <div className="w-7 h-7 rounded-lg bg-emerald-100 text-emerald-800 flex items-center justify-center">
            <MessageSquare className="w-4 h-4" />
          </div>
          <h3 className="text-base font-bold text-gray-900">{t('search.title')}</h3>
        </div>
        <p className="text-xs text-gray-500 mb-4 pl-9">{t('search.subtitle')}</p>

        <form onSubmit={handleSearchSubmit} className="relative flex items-center">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={isListening ? t('search.listening') : t('search.placeholder')}
            className="w-full pl-4 pr-24 py-3.5 text-sm bg-gray-50/80 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500/30 focus:border-emerald-600 transition-all placeholder:text-gray-400"
          />

          <div className="absolute right-2 flex items-center gap-1.5">
            <button
              type="button"
              onClick={handleVoiceInput}
              className={`p-2 rounded-lg transition-colors ${
                isListening
                  ? 'bg-red-500 text-white animate-pulse'
                  : 'text-gray-500 hover:text-emerald-700 hover:bg-emerald-50'
              }`}
              title="Voice Input (Speech-to-Text)"
            >
              <Mic className="w-4 h-4" />
            </button>

            <button
              type="submit"
              disabled={!query.trim()}
              className="p-2 rounded-lg bg-emerald-700 text-white hover:bg-emerald-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors cursor-pointer"
              title={t('search.send')}
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </form>

        {/* Quick Suggestion Chips */}
        <div className="flex flex-wrap items-center gap-2 mt-3 pt-3 border-t border-gray-100">
          <span className="text-[11px] font-semibold text-gray-400 uppercase tracking-wide">
            Try:
          </span>
          {[
            { label: 'Wheat Yellow Leaf Cure', q: 'गेहूं के पीले पत्तों का क्या इलाज है?' },
            { label: 'Ludhiana Mandi Rates', q: 'लुधियाना मंडी में गेहूं का आज का भाव क्या है?' },
            { label: 'PM-KISAN ₹6000 Info', q: 'How to register for PM-KISAN?' },
            { label: 'KCC 4% Interest Loan', q: 'ਕਿਸਾਨ ਕ੍ਰੈਡਿਟ ਕਾਰਡ 4% ਵਿਆਜ ਦਰ ਬਾਰੇ ਦੱਸੋ' }
          ].map((chip, i) => (
            <button
              key={i}
              type="button"
              onClick={() => navigate('/chat', { state: { initialQuery: chip.q } })}
              className="text-xs bg-emerald-50 hover:bg-emerald-100 text-emerald-900 border border-emerald-100 px-2.5 py-1 rounded-lg transition-colors font-medium cursor-pointer"
            >
              {chip.label}
            </button>
          ))}
        </div>
      </div>

      {/* 3 Core Services Hero Grid */}
      <div>
        <h3 className="text-base font-bold text-gray-900 mb-3 px-1">
          Core Agricultural Services
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {cards.map((c, i) => {
            const Icon = c.icon
            return (
              <div
                key={i}
                className="bg-white rounded-2xl p-6 border border-gray-200/80 shadow-xs hover:shadow-md transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-800 flex items-center justify-center mb-4">
                    <Icon className="w-6 h-6 stroke-[2.2]" />
                  </div>
                  <h4 className="text-lg font-bold text-gray-900 mb-1.5">{c.title}</h4>
                  <p className="text-sm text-gray-600 leading-relaxed mb-6">{c.desc}</p>
                </div>

                <button
                  onClick={() => navigate(c.to)}
                  className={`w-full py-2.5 px-4 rounded-xl font-bold text-sm shadow-xs flex items-center justify-center gap-2 transition-all cursor-pointer ${c.btnColor}`}
                >
                  <span>{c.btnText}</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            )
          })}
        </div>
      </div>

      {/* Snapshot Cards: Mandi, Weather Spray Advisory, Credit */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Mandi Snapshot */}
        <div className="bg-white rounded-2xl p-5 border border-gray-200/80 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-emerald-700" />
                <h4 className="text-sm font-bold text-gray-900">Today's Mandi Highlight</h4>
              </div>
              <button
                onClick={() => navigate('/prices')}
                className="text-xs font-semibold text-emerald-700 hover:text-emerald-800 cursor-pointer"
              >
                View →
              </button>
            </div>
            <div className="p-3 bg-emerald-50/60 rounded-xl border border-emerald-100 flex items-center justify-between">
              <div>
                <p className="text-xs text-emerald-900/70 font-semibold">Wheat (PBW 826)</p>
                <p className="text-lg font-black text-emerald-950">₹ 2,350 <span className="text-xs font-medium text-gray-500">/ q</span></p>
                <p className="text-[10px] text-gray-500">Ludhiana APMC</p>
              </div>
              <div className="text-right">
                <span className="inline-block px-2 py-0.5 rounded-full text-xs font-bold bg-emerald-600 text-white">
                  HOLD (+2.1%)
                </span>
                <p className="text-[9px] text-gray-500 mt-0.5">Firming demand</p>
              </div>
            </div>
          </div>
          <p className="text-[10px] text-gray-400 mt-2">
            Agmarknet APMC Modal Rate
          </p>
        </div>

        {/* Agromet Weather & Spray Advisory */}
        <div className="bg-white rounded-2xl p-5 border border-gray-200/80 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <CloudSun className="w-4 h-4 text-amber-600" />
                <h4 className="text-sm font-bold text-gray-900">Agromet Spray Advisory</h4>
              </div>
              <span className="text-[10px] font-bold text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded">
                Ludhiana
              </span>
            </div>
            {weather ? (
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs font-semibold text-gray-700">
                  <span className="flex items-center gap-1">
                    <CloudSun className="w-3.5 h-3.5 text-amber-500" /> {weather.temperature_c}°C
                  </span>
                  <span className="flex items-center gap-1">
                    <Droplets className="w-3.5 h-3.5 text-blue-500" /> {weather.humidity_percent}%
                  </span>
                  <span className="flex items-center gap-1">
                    <Wind className="w-3.5 h-3.5 text-gray-400" /> {weather.wind_speed_kmh} km/h
                  </span>
                </div>
                <div className="p-2.5 bg-emerald-50 rounded-xl border border-emerald-100">
                  <span className="inline-block text-[10px] font-extrabold text-emerald-800 bg-emerald-200/80 px-2 py-0.5 rounded mb-1">
                    {weather.spray_advisory_status}
                  </span>
                  <p className="text-[11px] text-emerald-950 leading-tight">
                    {weather.spray_advisory_text}
                  </p>
                </div>
              </div>
            ) : (
              <p className="text-xs text-gray-400">Loading agromet advisory...</p>
            )}
          </div>
          <p className="text-[10px] text-gray-400 mt-2">
            IMD Gramin Krishi Mausam Sewa
          </p>
        </div>

        {/* Credit & Schemes Advisory */}
        <div className="bg-white rounded-2xl p-5 border border-gray-200/80 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Landmark className="w-4 h-4 text-teal-700" />
                <h4 className="text-sm font-bold text-gray-900">Farmer Credit Support</h4>
              </div>
              <button
                onClick={() => navigate('/schemes')}
                className="text-xs font-semibold text-teal-700 hover:text-teal-800 cursor-pointer"
              >
                Check →
              </button>
            </div>
            <p className="text-xs text-gray-600 leading-relaxed mb-2">
              Avail subsidized short-term crop loans up to <strong>₹3 Lakh at just 4% interest rate</strong> with timely repayment under KCC.
            </p>
          </div>
          <div className="flex items-center gap-2 text-[10px] text-emerald-800 bg-emerald-50 px-2.5 py-1.5 rounded-lg border border-emerald-100 font-medium">
            <CheckCircle className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
            <span>PM-KISAN + KCC DBT Verification</span>
          </div>
        </div>
      </div>
    </div>
  )
}