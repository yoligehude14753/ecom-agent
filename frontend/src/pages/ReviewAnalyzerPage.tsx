import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Star, ThumbsUp, ThumbsDown, Lightbulb, Loader2, BarChart3 } from 'lucide-react'
import { reviewsApi } from '@/services/api'
import { cn } from '@/lib/utils'

interface ReviewAnalysis {
  asin: string
  total_reviews: number
  avg_rating: number
  sentiment_breakdown: { positive: number; negative: number; neutral: number }
  top_pain_points: string[]
  top_praise_points: string[]
  improvement_suggestions: string[]
  common_keywords: Array<{ word: string; count: number; sentiment: string }>
  rating_distribution: Record<string, number>
  verified_purchase_ratio: number
  summary: string
  listing_recommendations: string[]
}

export default function ReviewAnalyzerPage() {
  const [asin, setAsin] = useState('')
  const [maxPages, setMaxPages] = useState(3)

  const mutation = useMutation({
    mutationFn: () => reviewsApi.analyze({ asin, max_pages: maxPages }),
  })

  const data: ReviewAnalysis | undefined = mutation.data

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Star className="w-6 h-6 text-amber-400" />
          Review Analyzer
        </h1>
        <p className="text-slate-400 mt-1">Extract customer insights and improvement opportunities from Amazon reviews.</p>
      </div>

      {/* Input */}
      <div className="flex gap-4 flex-wrap p-5 bg-slate-900 rounded-xl border border-slate-800 mb-6">
        <div className="flex-1 min-w-48">
          <label className="text-xs text-slate-400 font-medium mb-1 block">ASIN</label>
          <input
            value={asin}
            onChange={e => setAsin(e.target.value.toUpperCase())}
            placeholder="B01MFCXDYG"
            maxLength={10}
            className="w-full bg-slate-800 border border-slate-700 text-white text-sm rounded-lg px-3 py-2.5 focus:ring-1 focus:ring-amber-500 outline-none placeholder:text-slate-600 font-mono"
          />
        </div>
        <div>
          <label className="text-xs text-slate-400 font-medium mb-1 block">Review pages</label>
          <select
            value={maxPages}
            onChange={e => setMaxPages(Number(e.target.value))}
            className="bg-slate-800 border border-slate-700 text-white text-sm rounded-lg px-3 py-2.5 focus:ring-1 focus:ring-amber-500 outline-none"
          >
            {[1, 3, 5, 10].map(n => <option key={n} value={n}>{n} pages (~{n * 10} reviews)</option>)}
          </select>
        </div>
        <div className="flex items-end">
          <button
            onClick={() => mutation.mutate()}
            disabled={mutation.isPending || !asin}
            className="flex items-center gap-2 px-6 py-2 bg-amber-600 hover:bg-amber-500 disabled:opacity-50 text-white font-medium rounded-lg transition-colors"
          >
            {mutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Star className="w-4 h-4" />}
            {mutation.isPending ? 'Analyzing...' : 'Analyze Reviews'}
          </button>
        </div>
      </div>

      {mutation.isError && (
        <div className="mb-4 p-4 bg-red-900/30 border border-red-700 rounded-xl text-red-300 text-sm">
          {(mutation.error as Error).message}
        </div>
      )}

      {data && (
        <div className="space-y-4">
          {/* Overview */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {[
              { label: 'Total Reviews', value: data.total_reviews.toLocaleString() },
              { label: 'Avg Rating', value: `${data.avg_rating.toFixed(1)} ★` },
              { label: 'Verified', value: `${(data.verified_purchase_ratio * 100).toFixed(0)}%` },
              { label: 'Positive', value: `${data.sentiment_breakdown.positive}%`, color: 'text-emerald-400' },
            ].map(({ label, value, color }) => (
              <div key={label} className="p-4 bg-slate-900 rounded-xl border border-slate-800">
                <p className="text-xs text-slate-500 mb-1">{label}</p>
                <p className={cn('text-2xl font-bold text-white', color)}>{value}</p>
              </div>
            ))}
          </div>

          {/* Summary */}
          <div className="p-5 bg-slate-900 rounded-xl border border-slate-800">
            <h3 className="text-white font-semibold mb-3 flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-amber-400" /> Executive Summary
            </h3>
            <p className="text-slate-300 text-sm leading-relaxed">{data.summary}</p>
          </div>

          {/* Sentiment grid */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="p-5 bg-slate-900 rounded-xl border border-slate-800">
              <h3 className="text-red-400 font-semibold mb-3 flex items-center gap-2 text-sm">
                <ThumbsDown className="w-4 h-4" /> Top Pain Points
              </h3>
              <ul className="space-y-2">
                {data.top_pain_points.map((p, i) => (
                  <li key={i} className="text-slate-400 text-xs flex items-start gap-2">
                    <span className="text-red-600 mt-0.5">•</span>{p}
                  </li>
                ))}
              </ul>
            </div>
            <div className="p-5 bg-slate-900 rounded-xl border border-slate-800">
              <h3 className="text-emerald-400 font-semibold mb-3 flex items-center gap-2 text-sm">
                <ThumbsUp className="w-4 h-4" /> Top Praise Points
              </h3>
              <ul className="space-y-2">
                {data.top_praise_points.map((p, i) => (
                  <li key={i} className="text-slate-400 text-xs flex items-start gap-2">
                    <span className="text-emerald-600 mt-0.5">•</span>{p}
                  </li>
                ))}
              </ul>
            </div>
            <div className="p-5 bg-slate-900 rounded-xl border border-slate-800">
              <h3 className="text-blue-400 font-semibold mb-3 flex items-center gap-2 text-sm">
                <Lightbulb className="w-4 h-4" /> Improvement Ideas
              </h3>
              <ul className="space-y-2">
                {data.improvement_suggestions.map((s, i) => (
                  <li key={i} className="text-slate-400 text-xs flex items-start gap-2">
                    <span className="text-blue-600 mt-0.5">•</span>{s}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Listing recommendations */}
          <div className="p-5 bg-slate-900 rounded-xl border border-slate-800">
            <h3 className="text-purple-400 font-semibold mb-3 text-sm">Listing Optimization Recommendations</h3>
            <ul className="space-y-2">
              {data.listing_recommendations.map((r, i) => (
                <li key={i} className="text-slate-300 text-sm flex items-start gap-2">
                  <span className="text-purple-400 font-bold mt-0.5">{i + 1}.</span>{r}
                </li>
              ))}
            </ul>
          </div>

          {/* Keywords */}
          <div className="p-5 bg-slate-900 rounded-xl border border-slate-800">
            <h3 className="text-white font-semibold mb-3 text-sm">Common Keywords</h3>
            <div className="flex flex-wrap gap-2">
              {data.common_keywords.map(({ word, count, sentiment }) => (
                <span
                  key={word}
                  className={cn(
                    'text-xs px-2 py-1 rounded-full font-medium',
                    sentiment === 'positive' ? 'bg-emerald-900/40 text-emerald-300' :
                    sentiment === 'negative' ? 'bg-red-900/40 text-red-300' :
                    'bg-slate-800 text-slate-400',
                  )}
                >
                  {word} <span className="opacity-60">×{count}</span>
                </span>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
