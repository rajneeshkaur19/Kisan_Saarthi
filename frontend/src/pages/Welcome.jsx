import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { changeLanguage } from '../i18n'
import { 
  Sprout, 
  ArrowRight, 
  Stethoscope, 
  TrendingUp, 
  Landmark, 
  MessageSquare,
  ShieldCheck,
  CheckCircle2
} from 'lucide-react'

export default function Welcome() {
  const { t, i18n } = useTranslation()
  const navigate = useNavigate()
  const currentLang = i18n.language || 'en'

  const languages = [
    { code: 'hi', label: 'हिन्दी' },
    { code: 'pa', label: 'ਪੰਜਾਬੀ' },
    { code: 'en', label: 'English' }
  ]

  const features = [
    {
      icon: Stethoscope,
      title: t('services.crop_health_title'),
      desc: t('services.crop_health_desc'),
      tag: 'AI Leaf Doctor'
    },
    {
      icon: TrendingUp,
      title: t('services.mandi_prices_title'),
      desc: t('services.mandi_prices_desc'),
      tag: 'Agmarknet APMC'
    },
    {
      icon: Landmark,
      title: t('services.schemes_title'),
      desc: t('services.schemes_desc'),
      tag: 'PM-KISAN & KCC'
    },
    {
      icon: MessageSquare,
      title: t('nav.chatbot'),
      desc: 'Ask questions in voice or text with verified official citations.',
      tag: 'Multilingual RAG'
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#eef7ee] via-[#f7faf7] to-[#e8f3e8] flex flex-col justify-between p-4 md:p-8">
      {/* Top Bar with Language Selector */}
      <header className="max-w-6xl mx-auto w-full flex items-center justify-between py-2">
        <div className="flex items-center gap-2.5">
          <div className="w-10 h-10 rounded-2xl bg-emerald-700 flex items-center justify-center text-white shadow-md">
            <Sprout className="w-6 h-6 stroke-[2.5]" />
          </div>
          <div>
            <h1 className="text-xl font-extrabold text-emerald-950 tracking-tight">
              Kisan<span className="text-emerald-600">Saarthi</span>
            </h1>
            <p className="text-[11px] font-medium text-emerald-800/80">From Farm to Finance, with AI</p>
          </div>
        </div>

        <div className="flex items-center gap-1.5 p-1 bg-white/80 backdrop-blur-md rounded-xl border border-emerald-200/80 shadow-xs">
          {languages.map((l) => (
            <button
              key={l.code}
              onClick={() => changeLanguage(l.code)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                currentLang.startsWith(l.code)
                  ? 'bg-emerald-700 text-white shadow-xs'
                  : 'text-emerald-900 hover:bg-emerald-100/60'
              }`}
            >
              {l.label}
            </button>
          ))}
        </div>
      </header>

      {/* Main Hero Card Matching Wireframe 1 */}
      <main className="max-w-4xl mx-auto w-full my-auto py-8">
        <div className="bg-white rounded-3xl p-6 md:p-10 shadow-[0_12px_40px_rgba(20,61,43,0.08)] border border-emerald-100 text-center relative overflow-hidden">
          {/* Subtle nature accent blob */}
          <div className="absolute -top-24 -right-24 w-64 h-64 bg-emerald-100/60 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute -bottom-24 -left-24 w-64 h-64 bg-green-100/60 rounded-full blur-3xl pointer-events-none" />

          {/* Logo Badge */}
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-3xl bg-gradient-to-tr from-emerald-800 to-emerald-600 text-white shadow-lg shadow-emerald-900/15 mb-6 ring-8 ring-emerald-50">
            <Sprout className="w-11 h-11 stroke-[2.5]" />
          </div>

          <h2 className="text-3xl md:text-4xl font-extrabold text-emerald-950 tracking-tight mb-2">
            Kisan<span className="text-emerald-600">Saarthi</span>
          </h2>
          <p className="text-emerald-800 font-semibold text-sm md:text-base tracking-wide mb-3">
            {t('tagline')}
          </p>
          <p className="text-gray-600 text-sm md:text-base max-w-xl mx-auto leading-relaxed mb-8">
            {t('hero_subtitle')}
          </p>

          {/* Language Selection Buttons matching wireframe */}
          <div className="mb-8">
            <p className="text-xs font-semibold uppercase tracking-wider text-emerald-900/60 mb-2.5">
              {t('select_language')}
            </p>
            <div className="inline-flex flex-wrap justify-center gap-2 p-1.5 bg-emerald-50/80 rounded-2xl border border-emerald-200/80">
              {languages.map((l) => (
                <button
                  key={l.code}
                  onClick={() => changeLanguage(l.code)}
                  className={`px-5 py-2.5 rounded-xl text-sm font-bold transition-all ${
                    currentLang.startsWith(l.code)
                      ? 'bg-emerald-700 text-white shadow-md'
                      : 'bg-white text-emerald-900 hover:bg-emerald-100 border border-emerald-100'
                  }`}
                >
                  {l.label}
                </button>
              ))}
            </div>
          </div>

          {/* Get Started Button */}
          <div className="max-w-sm mx-auto space-y-3">
            <button
              onClick={() => navigate('/home')}
              className="w-full py-4 px-6 rounded-2xl bg-gradient-to-r from-emerald-700 to-emerald-600 hover:from-emerald-800 hover:to-emerald-700 text-white font-bold text-base shadow-lg shadow-emerald-900/20 flex items-center justify-center gap-2 transition-all transform hover:-translate-y-0.5 active:translate-y-0 cursor-pointer"
            >
              <span>{t('get_started')}</span>
              <ArrowRight className="w-5 h-5 stroke-[2.5]" />
            </button>

            <button
              onClick={() => navigate('/home')}
              className="text-xs text-emerald-900/70 hover:text-emerald-800 font-semibold transition-colors block mx-auto py-1"
            >
              {t('already_account')}
            </button>
          </div>
        </div>

        {/* Feature Highlights Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4 mt-6">
          {features.map((f, i) => {
            const Icon = f.icon
            return (
              <div
                key={i}
                className="bg-white/90 backdrop-blur-sm rounded-2xl p-4 border border-emerald-100 shadow-xs flex flex-col justify-between"
              >
                <div>
                  <div className="w-9 h-9 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center mb-2.5">
                    <Icon className="w-5 h-5" />
                  </div>
                  <h3 className="text-xs font-bold text-emerald-950 mb-1">{f.title}</h3>
                  <p className="text-[11px] text-gray-500 leading-snug line-clamp-2">{f.desc}</p>
                </div>
                <div className="mt-3 pt-2 border-t border-emerald-50">
                  <span className="inline-block text-[10px] font-semibold text-emerald-800 bg-emerald-50/80 px-2 py-0.5 rounded-md">
                    {f.tag}
                  </span>
                </div>
              </div>
            )
          })}
        </div>
      </main>

      {/* Trust & Official Attribution Footer */}
      <footer className="max-w-4xl mx-auto w-full text-center text-[11px] text-gray-500 py-3 flex flex-wrap items-center justify-center gap-4 border-t border-emerald-100/60">
        <span className="flex items-center gap-1 font-medium text-emerald-900/70">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
          Verified Agricultural Knowledge
        </span>
        <span>•</span>
        <span>Agmarknet APMC Real-Time Prices</span>
        <span>•</span>
        <span>Official PM-KISAN & KCC Guidance</span>
      </footer>
    </div>
  )
}
