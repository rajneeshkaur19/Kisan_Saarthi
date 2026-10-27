import React, { useState, useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { 
  Landmark, 
  CheckCircle, 
  Download, 
  ShieldCheck, 
  FileText, 
  HelpCircle, 
  AlertCircle, 
  X,
  ExternalLink,
  ChevronRight,
  TrendingUp,
  RefreshCw,
  Sparkles,
  MessageSquare
} from 'lucide-react'
import { checkEligibility, downloadChecklist } from '../api/client'

export default function LoanSchemes() {
  const { t, i18n } = useTranslation()
  const location = useLocation()
  const navigate = useNavigate()
  const currentLang = i18n.language || 'en'

  const [activeTab, setActiveTab] = useState('check') // 'check' | 'all'
  const [landHolding, setLandHolding] = useState('3.5')
  const [annualIncome, setAnnualIncome] = useState('1 - 3 lakh')
  const [primaryCrop, setPrimaryCrop] = useState('Wheat')
  const [existingLoan, setExistingLoan] = useState('no_active_loan')
  const [bankAccount, setBankAccount] = useState('aadhaar_linked_dbt')

  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [errorMsg, setErrorMsg] = useState(null)

  // Checklist modal state
  const [modalScheme, setModalScheme] = useState(null)
  const [checklistLoading, setChecklistLoading] = useState(false)
  const [checklistData, setChecklistData] = useState(null)

  useEffect(() => {
    if (location.state?.prefilledCrop) {
      setPrimaryCrop(location.state.prefilledCrop)
    }
  }, [location.state])

  const handleEvaluate = async (e) => {
    e.preventDefault()
    try {
      setLoading(true)
      setErrorMsg(null)
      const acres = parseFloat(landHolding) || 0
      const res = await checkEligibility({
        land_holding_acres: acres,
        annual_income: annualIncome,
        primary_crop: primaryCrop,
        existing_loan_status: existingLoan,
        bank_account_status: bankAccount,
        language: currentLang
      })
      if (res.status === 'ok') {
        setResult(res.data)
      } else {
        setErrorMsg(res.error?.message || 'Eligibility calculation failed.')
      }
    } catch (err) {
      setErrorMsg('Could not connect to eligibility service.')
    } finally {
      setLoading(false)
    }
  }

  const handleOpenChecklist = async (scheme) => {
    setModalScheme(scheme)
    setChecklistData(null)
    try {
      setChecklistLoading(true)
      const res = await downloadChecklist({
        scheme_id: scheme.code || scheme.id,
        language: currentLang,
        farmer_name: 'Farmer Partner',
        include_pdf_base64: true
      })
      if (res.status === 'ok') {
        setChecklistData(res.data)
      }
    } catch (err) {
      console.error(err)
    } finally {
      setChecklistLoading(false)
    }
  }

  const handleDownloadPDF = () => {
    if (!checklistData?.pdf_base64) return
    const linkSource = `data:application/pdf;base64,${checklistData.pdf_base64}`
    const downloadLink = document.createElement('a')
    downloadLink.href = linkSource
    downloadLink.download = `${checklistData.scheme_id}_Document_Checklist.pdf`
    downloadLink.click()
  }

  const readiness = result?.readiness_score

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-20 md:pb-8">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 mb-1">
          <div className="w-8 h-8 rounded-xl bg-teal-100 text-teal-800 flex items-center justify-center">
            <Landmark className="w-5 h-5" />
          </div>
          <h2 className="text-2xl font-extrabold text-gray-900 tracking-tight">
            {t('schemes.title')}
          </h2>
        </div>
        <p className="text-sm text-gray-500 pl-10">
          {t('schemes.subtitle')}
        </p>
      </div>

      {/* Connected Journey Banner if navigated from Crop Doctor */}
      {location.state?.prefilledCrop && (
        <div className="p-3.5 bg-emerald-50 border border-emerald-200 rounded-2xl flex items-center justify-between gap-3 text-xs text-emerald-950 animate-fadeIn">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>
              <strong>Connected Farmer Journey:</strong> Form auto-configured for your diagnosed crop: <strong>{location.state.prefilledCrop}</strong> {location.state.sourceDisease ? `(${location.state.sourceDisease})` : ''}
            </span>
          </div>
          <span className="text-[10px] font-bold bg-emerald-200/70 text-emerald-900 px-2 py-0.5 rounded">
            Auto-Synced
          </span>
        </div>
      )}

      {/* Form Card Matching Wireframe 5 */}
      <div className="bg-white rounded-3xl p-6 md:p-8 border border-gray-200/90 shadow-xs">
        <form onSubmit={handleEvaluate} className="space-y-5">
          <h3 className="text-base font-bold text-gray-900 pb-2 border-b border-gray-100">
            Farmer Profile & Farm Parameters
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Land Holding */}
            <div>
              <label className="block text-xs font-bold text-gray-700 mb-1.5">
                {t('schemes.land_holding')}
              </label>
              <div className="relative">
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  value={landHolding}
                  onChange={(e) => setLandHolding(e.target.value)}
                  placeholder="e.g. 3.5"
                  className="w-full px-3.5 py-2.5 text-sm bg-gray-50 border border-gray-200 rounded-xl font-medium text-gray-800 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-600 transition-all"
                  required
                />
                <span className="absolute right-3.5 top-2.5 text-xs text-gray-400 font-semibold pointer-events-none">
                  acres
                </span>
              </div>
            </div>

            {/* Annual Income */}
            <div>
              <label className="block text-xs font-bold text-gray-700 mb-1.5">
                {t('schemes.annual_income')}
              </label>
              <select
                value={annualIncome}
                onChange={(e) => setAnnualIncome(e.target.value)}
                className="w-full px-3.5 py-2.5 text-sm bg-gray-50 border border-gray-200 rounded-xl font-medium text-gray-800 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-600 transition-all cursor-pointer"
              >
                <option value="< 1 lakh">&lt; ₹ 1 Lakh</option>
                <option value="1 - 3 lakh">₹ 1 - 3 Lakh</option>
                <option value="3 - 6 lakh">₹ 3 - 6 Lakh</option>
                <option value="> 6 lakh">&gt; ₹ 6 Lakh</option>
              </select>
            </div>

            {/* Primary Crop */}
            <div>
              <label className="block text-xs font-bold text-gray-700 mb-1.5">
                {t('schemes.primary_crop')}
              </label>
              <select
                value={primaryCrop}
                onChange={(e) => setPrimaryCrop(e.target.value)}
                className="w-full px-3.5 py-2.5 text-sm bg-gray-50 border border-gray-200 rounded-xl font-medium text-gray-800 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-600 transition-all cursor-pointer"
              >
                <option value="Wheat">Wheat</option>
                <option value="Paddy">Paddy / Rice</option>
                <option value="Cotton">Cotton</option>
                <option value="Potato">Potato</option>
                <option value="Tomato">Tomato</option>
                <option value="Maize">Maize</option>
                <option value="Mustard">Mustard</option>
                <option value="Soybean">Soybean</option>
              </select>
            </div>

            {/* Bank Account Status */}
            <div>
              <label className="block text-xs font-bold text-gray-700 mb-1.5">
                {t('schemes.bank_account')}
              </label>
              <select
                value={bankAccount}
                onChange={(e) => setBankAccount(e.target.value)}
                className="w-full px-3.5 py-2.5 text-sm bg-gray-50 border border-gray-200 rounded-xl font-medium text-gray-800 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-600 transition-all cursor-pointer"
              >
                <option value="aadhaar_linked_dbt">Aadhaar Linked with DBT enabled (Ready)</option>
                <option value="bank_account_no_dbt">Bank Account without Aadhaar DBT</option>
                <option value="no_formal_account">No Formal Bank Account</option>
              </select>
            </div>

            {/* Existing Loan Status */}
            <div className="sm:col-span-2">
              <label className="block text-xs font-bold text-gray-700 mb-1.5">
                {t('schemes.existing_loans')}
              </label>
              <select
                value={existingLoan}
                onChange={(e) => setExistingLoan(e.target.value)}
                className="w-full px-3.5 py-2.5 text-sm bg-gray-50 border border-gray-200 rounded-xl font-medium text-gray-800 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-600 transition-all cursor-pointer"
              >
                <option value="no_active_loan">No active formal loans (Clean slate)</option>
                <option value="active_kcc_loan_good_standing">Active KCC loan (Regular repayment, Good track)</option>
                <option value="active_formal_loan">Other bank term loan active</option>
                <option value="informal_debt">Informal village debt / Money lender loan</option>
              </select>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3.5 px-6 rounded-2xl bg-teal-700 hover:bg-teal-800 text-white font-bold text-sm shadow-md shadow-teal-900/15 flex items-center justify-center gap-2 disabled:opacity-50 transition-all cursor-pointer"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>{t('schemes.evaluating')}</span>
              </>
            ) : (
              <>
                <ShieldCheck className="w-4 h-4" />
                <span>{t('schemes.check_btn')}</span>
              </>
            )}
          </button>
        </form>

        {errorMsg && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-xl text-red-800 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-red-600 shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}
      </div>

      {/* Credit Readiness Score Card Matching Wireframe 5 */}
      {readiness && (
        <div className="bg-white rounded-3xl p-6 md:p-8 border border-emerald-100 shadow-sm space-y-6 animate-fadeIn">
          <div className="flex flex-col sm:flex-row items-center gap-6">
            {/* Circular Gauge */}
            <div className="relative w-32 h-32 shrink-0 flex items-center justify-center">
              <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                <path
                  className="text-gray-100"
                  strokeWidth="3.5"
                  stroke="currentColor"
                  fill="none"
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                />
                <path
                  className="text-emerald-600 transition-all duration-1000 ease-out"
                  strokeDasharray={`${readiness.score}, 100`}
                  strokeWidth="3.5"
                  strokeLinecap="round"
                  stroke="currentColor"
                  fill="none"
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                />
              </svg>
              <div className="absolute flex flex-col items-center justify-center text-center">
                <span className="text-2xl font-black text-gray-900 leading-none">
                  {readiness.score}
                </span>
                <span className="text-[10px] font-bold text-gray-400 mt-0.5">/ 100</span>
              </div>
            </div>

            {/* Score Text Summary Matching Wireframe 5 */}
            <div className="flex-1 text-center sm:text-left">
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-extrabold bg-emerald-100 text-emerald-900 mb-2">
                <CheckCircle className="w-3.5 h-3.5 text-emerald-700" />
                <span>Score: {readiness.label}</span>
              </div>
              <h4 className="text-base font-bold text-gray-900 mb-1">
                {t('schemes.readiness_score')}
              </h4>
              <p className="text-xs text-gray-600 leading-relaxed mb-3">
                {readiness.summary}
              </p>

              {/* Actionable improvement tips */}
              <div className="space-y-1">
                {readiness.improvement_tips?.map((tip, i) => (
                  <p key={i} className="text-[11px] text-emerald-800 font-semibold flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-600" />
                    {tip}
                  </p>
                ))}
              </div>
            </div>
          </div>

          {/* Recommended Schemes Matching Wireframe 5 */}
          <div className="pt-4 border-t border-gray-100">
            <h4 className="text-sm font-bold text-gray-900 mb-3">
              {t('schemes.recommended_schemes')}
            </h4>

            <div className="space-y-3">
              {result.recommended_schemes?.map((scheme) => (
                <div
                  key={scheme.id}
                  className="p-4 rounded-2xl border border-emerald-100 bg-emerald-50/30 hover:bg-emerald-50/70 transition-colors flex flex-col sm:flex-row sm:items-center justify-between gap-4"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 rounded-md bg-emerald-700 text-white text-[10px] font-bold">
                        {scheme.short_name || scheme.code}
                      </span>
                      <h5 className="text-sm font-bold text-gray-900">{scheme.name}</h5>
                    </div>
                    <p className="text-xs font-semibold text-emerald-900">
                      {scheme.financial_benefit}
                    </p>
                    <p className="text-[11px] text-gray-500 leading-snug">
                      {scheme.match_reason}
                    </p>
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    <button
                      onClick={() => handleOpenChecklist(scheme)}
                      className="px-3.5 py-2 rounded-xl bg-white hover:bg-emerald-50 text-emerald-800 text-xs font-bold border border-emerald-200 shadow-2xs flex items-center gap-1.5 transition-colors cursor-pointer"
                    >
                      <FileText className="w-3.5 h-3.5 text-emerald-700" />
                      <span>{t('schemes.view_details')}</span>
                    </button>

                    <button
                      onClick={() => navigate('/chat', { state: { initialQuery: `What are the full eligibility and documentation rules for ${scheme.short_name || scheme.name} in simple terms?` } })}
                      className="px-3 py-2 rounded-xl bg-teal-50 hover:bg-teal-100 text-teal-800 text-xs font-bold border border-teal-200 flex items-center gap-1 transition-colors cursor-pointer"
                      title="Ask Saarthi AI Assistant"
                    >
                      <MessageSquare className="w-3.5 h-3.5 text-teal-700" />
                      <span>Ask AI</span>
                    </button>

                    <button
                      onClick={() => handleOpenChecklist(scheme)}
                      className="px-3.5 py-2 rounded-xl bg-emerald-700 hover:bg-emerald-800 text-white text-xs font-bold shadow-xs flex items-center gap-1.5 transition-colors cursor-pointer"
                    >
                      <Download className="w-3.5 h-3.5" />
                      <span>Checklist</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Document Checklist Modal */}
      {modalScheme && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-lg w-full max-h-[90vh] overflow-y-auto p-6 md:p-8 space-y-5 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-gray-100">
              <div>
                <span className="text-[10px] font-bold text-teal-700 uppercase tracking-wider bg-teal-50 px-2 py-0.5 rounded">
                  Document Checklist
                </span>
                <h3 className="text-lg font-bold text-gray-900 mt-1">
                  {checklistData?.title || modalScheme.name}
                </h3>
              </div>
              <button
                onClick={() => setModalScheme(null)}
                className="p-1.5 rounded-full hover:bg-gray-100 text-gray-500"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {checklistLoading ? (
              <div className="py-12 text-center">
                <RefreshCw className="w-6 h-6 text-teal-600 animate-spin mx-auto mb-2" />
                <p className="text-xs text-gray-500">{t('schemes.downloading')}</p>
              </div>
            ) : checklistData ? (
              <div className="space-y-4">
                <div className="p-3 bg-teal-50/60 rounded-xl text-xs text-teal-950 flex justify-between items-center">
                  <span><strong>Portal:</strong> {checklistData.portal}</span>
                  <span><strong>Helpline:</strong> {checklistData.official_helpline}</span>
                </div>

                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-2">
                    {t('schemes.documents_needed')}
                  </h4>
                  <div className="space-y-2">
                    {checklistData.required_documents?.map((doc, idx) => (
                      <div
                        key={idx}
                        className="p-3 bg-gray-50 rounded-xl border border-gray-100 text-xs"
                      >
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-bold text-gray-900">
                            {idx + 1}. {doc.name}
                          </span>
                          <span
                            className={`text-[10px] px-2 py-0.5 rounded font-bold ${
                              doc.mandatory
                                ? 'bg-emerald-100 text-emerald-800'
                                : 'bg-gray-200 text-gray-600'
                            }`}
                          >
                            {doc.mandatory ? 'MANDATORY' : 'OPTIONAL'}
                          </span>
                        </div>
                        <p className="text-gray-500 text-[11px] leading-relaxed">
                          {doc.description}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>

                {checklistData.pdf_base64 && (
                  <button
                    onClick={handleDownloadPDF}
                    className="w-full py-3 px-4 rounded-xl bg-emerald-700 hover:bg-emerald-800 text-white text-xs font-bold shadow-xs flex items-center justify-center gap-2 transition-colors cursor-pointer"
                  >
                    <Download className="w-4 h-4" />
                    <span>{t('schemes.download_checklist')}</span>
                  </button>
                )}
              </div>
            ) : null}
          </div>
        </div>
      )}
    </div>
  )
}
