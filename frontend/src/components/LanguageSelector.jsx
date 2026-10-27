import React from 'react'
import { useTranslation } from 'react-i18next'
import { changeLanguage } from '../i18n'
import { Globe } from 'lucide-react'

export default function LanguageSelector({ variant = 'pills' }) {
  const { i18n } = useTranslation()
  const currentLang = i18n.language || 'en'

  const languages = [
    { code: 'hi', label: 'हिन्दी' },
    { code: 'pa', label: 'ਪੰਜਾਬੀ' },
    { code: 'en', label: 'English' }
  ]

  if (variant === 'select') {
    return (
      <div className="flex items-center gap-1.5 text-xs bg-emerald-50 border border-emerald-200 rounded-lg px-2.5 py-1 text-emerald-900">
        <Globe className="w-3.5 h-3.5 text-emerald-700" />
        <select
          value={currentLang.slice(0, 2)}
          onChange={(e) => changeLanguage(e.target.value)}
          className="bg-transparent font-medium cursor-pointer focus:outline-none"
        >
          {languages.map((l) => (
            <option key={l.code} value={l.code}>
              {l.label}
            </option>
          ))}
        </select>
      </div>
    )
  }

  return (
    <div className="flex items-center gap-1.5 p-1 bg-emerald-950/20 backdrop-blur-sm rounded-xl border border-emerald-800/30">
      {languages.map((lang) => {
        const isActive = currentLang.startsWith(lang.code)
        return (
          <button
            key={lang.code}
            onClick={() => changeLanguage(lang.code)}
            className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all duration-150 ${
              isActive
                ? 'bg-emerald-600 text-white shadow-sm'
                : 'text-emerald-900 hover:bg-emerald-100/60'
            }`}
          >
            {lang.label}
          </button>
        )
      })}
    </div>
  )
}
