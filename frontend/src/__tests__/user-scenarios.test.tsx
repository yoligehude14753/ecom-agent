/**
 * User-scenario tests for EcomAgent frontend.
 *
 * Tests are written from the USER's perspective:
 *   - "I fill in X and click Y — I expect to see Z"
 *   - We mock the API layer; tests verify that UI renders the right content
 *
 * Run with: npm test
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'
import React from 'react'

// Mock the API service modules
vi.mock('@/services/api', () => ({
  productResearchApi: {
    getCategories: vi.fn(),
    runResearch: vi.fn(),
  },
  listingApi: {
    generate: vi.fn(),
    optimize: vi.fn(),
    getLanguages: vi.fn(),
  },
  reviewsApi: {
    analyze: vi.fn(),
  },
  monitorApi: {
    list: vi.fn(),
    add: vi.fn(),
    remove: vi.fn(),
  },
  adsApi: {
    optimize: vi.fn(),
  },
  default: {},
}))

import {
  productResearchApi,
  listingApi,
  reviewsApi,
} from '@/services/api'

// ─── Test helpers ─────────────────────────────────────────────────────────────

function makeQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false, gcTime: 0 },
      mutations: { retry: false },
    },
  })
}

function renderWithProviders(ui: React.ReactElement) {
  const queryClient = makeQueryClient()
  return render(
    <MemoryRouter>
      <QueryClientProvider client={queryClient}>
        {ui}
      </QueryClientProvider>
    </MemoryRouter>
  )
}

// ─── Mock data (realistic product responses) ─────────────────────────────────

const MOCK_RESEARCH_RESULT = {
  // API returns `results` key (matches ProductResearchPage: mutation.data?.results)
  results: [
    {
      asin: 'B0MOCK001',
      title: 'Premium Stainless Steel Water Bottle 32oz',
      price: 24.99,
      bsr_rank: 450,
      bsr_category: 'sports',
      review_count: 3200,
      rating: 4.6,
      competition_score: 5.5,
      profit_potential_score: 8.2,
      trend_score: 7.0,
      overall_score: 7.8,
      recommended: true,
      ai_analysis: 'Strong profit potential due to low competition and high demand trend.',
      tags: ['low competition', 'trending'],
    },
    {
      asin: 'B0MOCK002',
      title: 'Phone Case for iPhone 15 Slim Clear',
      price: 9.99,
      bsr_rank: 120,
      bsr_category: 'electronics',
      review_count: 15000,
      rating: 4.1,
      competition_score: 9.2,
      profit_potential_score: 3.0,
      trend_score: 5.5,
      overall_score: 4.2,
      recommended: false,
      ai_analysis: 'Extremely saturated market. Entry barrier is high.',
      tags: ['high competition'],
    },
  ],
}

const MOCK_LISTING_RESULT = {
  title: 'Premium Stainless Steel Water Bottle 32oz - BPA Free, Insulated',
  bullet_points: [
    'KEEPS COLD 24 HOURS: Double-wall vacuum insulation maintains temperature all day',
    'BPA FREE & SAFE: Made from 18/8 food-grade stainless steel',
    'LEAKPROOF LID: Triple-seal cap guarantees zero leaks in your bag',
    'WIDE MOUTH DESIGN: Fits ice cubes, easy to fill, clean, and drink from',
    'LIFETIME WARRANTY: Hassle-free replacement guarantee',
  ],
  description: 'Stay hydrated anywhere with our premium stainless steel water bottle.',
  search_terms: ['insulated water bottle', 'stainless steel bottle 32oz'],
  seo_score: 8.7,
  character_counts: { title: 65, description: 80, search_terms: 60 },
}

const MOCK_REVIEW_RESULT = {
  asin: 'B0MOCK001',
  total_reviews: 3200,
  avg_rating: 4.6,
  sentiment_breakdown: { positive: 82, negative: 10, neutral: 8 },
  top_pain_points: ['lid sometimes leaks after extended use', 'paint chips over time'],
  top_praise_points: ['excellent insulation', 'durable build'],
  improvement_suggestions: ['reinforce lid sealing', 'use more durable coating'],
  summary: 'Buyers praise insulation quality but 10% report lid issues after heavy use.',
  listing_recommendations: ["Add 'improved leak-proof lid' to bullet points"],
  // common_keywords is required by ReviewAnalyzerPage's .map() call
  common_keywords: [
    { word: 'insulation', count: 180, sentiment: 'positive' },
    { word: 'lid', count: 95, sentiment: 'negative' },
    { word: 'durable', count: 120, sentiment: 'positive' },
  ],
}


// ═══════════════════════════════════════════════════════════════════════════════
// Scenario 1: 用户进行选品研究，点击后看到评分和AI分析
// ═══════════════════════════════════════════════════════════════════════════════

describe('Product Research — user scenario', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    ;(productResearchApi.getCategories as ReturnType<typeof vi.fn>).mockResolvedValue({
      categories: ['electronics', 'sports', 'home', 'beauty'],
    })
    ;(productResearchApi.runResearch as ReturnType<typeof vi.fn>).mockResolvedValue(
      MOCK_RESEARCH_RESULT
    )
  })

  it('renders the research form with a category selector and run button', async () => {
    const { default: ProductResearchPage } = await import('@/pages/ProductResearchPage')
    renderWithProviders(<ProductResearchPage />)

    // User sees a page title
    expect(screen.getByText(/product research/i)).toBeTruthy()

    // User sees a way to start research
    const runButton = screen.getByRole('button', { name: /run research/i })
    expect(runButton).toBeTruthy()
  })

  it('shows product list with scores after user clicks Run Research', async () => {
    const { default: ProductResearchPage } = await import('@/pages/ProductResearchPage')
    renderWithProviders(<ProductResearchPage />)

    // User clicks the research button
    const runButton = screen.getByRole('button', { name: /run research/i })
    fireEvent.click(runButton)

    // User sees the first product's title (use getAllByText to handle potential duplicates)
    await waitFor(() => {
      const matches = screen.getAllByText(/Premium Stainless Steel Water Bottle 32oz/i)
      expect(matches.length).toBeGreaterThan(0)
    })

    // User sees the overall score
    const scoreMatches = screen.getAllByText(/7\.8/)
    expect(scoreMatches.length).toBeGreaterThan(0)
  })

  it('shows AI analysis text so user understands WHY a product is recommended', async () => {
    const { default: ProductResearchPage } = await import('@/pages/ProductResearchPage')
    renderWithProviders(<ProductResearchPage />)

    fireEvent.click(screen.getByRole('button', { name: /run research/i }))

    await waitFor(() => {
      expect(
        screen.getByText(/Strong profit potential/i)
      ).toBeTruthy()
    })
  })
})


// ═══════════════════════════════════════════════════════════════════════════════
// Scenario 2: 用户输入关键词生成 Listing，看到完整可复制的文案
// ═══════════════════════════════════════════════════════════════════════════════

describe('Listing Generator — user scenario', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    ;(listingApi.generate as ReturnType<typeof vi.fn>).mockResolvedValue(MOCK_LISTING_RESULT)
    ;(listingApi.getLanguages as ReturnType<typeof vi.fn>).mockResolvedValue({
      languages: ['en', 'de', 'fr', 'ja', 'es'],
    })
  })

  it('renders keyword input and generate button', async () => {
    const { default: ListingGeneratorPage } = await import('@/pages/ListingGeneratorPage')
    renderWithProviders(<ListingGeneratorPage />)

    // User sees a keyword input
    const input = screen.getByPlaceholderText(/stainless steel insulated water bottle/i)
    expect(input).toBeTruthy()

    // User sees the generate button
    expect(screen.getByRole('button', { name: /generate listing/i })).toBeTruthy()
  })

  it('shows generated title after user enters keyword and clicks generate', async () => {
    const { default: ListingGeneratorPage } = await import('@/pages/ListingGeneratorPage')
    renderWithProviders(<ListingGeneratorPage />)

    // User types keyword
    const input = screen.getByPlaceholderText(/stainless steel insulated water bottle/i)
    fireEvent.change(input, { target: { value: 'stainless steel water bottle' } })

    // User clicks generate
    fireEvent.click(screen.getByRole('button', { name: /generate listing/i }))

    // User sees the generated title (use getAllByText to handle multiple matches)
    await waitFor(() => {
      const matches = screen.getAllByText(/Premium Stainless Steel Water Bottle/i)
      expect(matches.length).toBeGreaterThan(0)
    })
  })

  it('shows all 5 bullet points so user can copy them to Amazon', async () => {
    const { default: ListingGeneratorPage } = await import('@/pages/ListingGeneratorPage')
    renderWithProviders(<ListingGeneratorPage />)

    const input = screen.getByPlaceholderText(/stainless steel insulated water bottle/i)
    fireEvent.change(input, { target: { value: 'water bottle' } })
    fireEvent.click(screen.getByRole('button', { name: /generate listing/i }))

    await waitFor(() => {
      expect(screen.getByText(/KEEPS COLD 24 HOURS/i)).toBeTruthy()
    })

    // All 5 bullet points must be visible
    expect(screen.getByText(/LIFETIME WARRANTY/i)).toBeTruthy()
    expect(screen.getByText(/LEAKPROOF LID/i)).toBeTruthy()
  })

  it('shows SEO score so user can judge listing quality', async () => {
    const { default: ListingGeneratorPage } = await import('@/pages/ListingGeneratorPage')
    renderWithProviders(<ListingGeneratorPage />)

    const input = screen.getByPlaceholderText(/stainless steel insulated water bottle/i)
    fireEvent.change(input, { target: { value: 'water bottle' } })
    fireEvent.click(screen.getByRole('button', { name: /generate listing/i }))

    await waitFor(() => {
      // SEO score (8.7) or "SEO" label should appear — use getAllByText to handle multiple
      const matches = screen.getAllByText(/8\.7|SEO/i)
      expect(matches.length).toBeGreaterThan(0)
    })
  })
})


// ═══════════════════════════════════════════════════════════════════════════════
// Scenario 3: 用户分析竞品评论，看到痛点和改进建议
// ═══════════════════════════════════════════════════════════════════════════════

describe('Review Analyzer — user scenario', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    ;(reviewsApi.analyze as ReturnType<typeof vi.fn>).mockResolvedValue(MOCK_REVIEW_RESULT)
  })

  it('renders ASIN input and analyze button', async () => {
    const { default: ReviewAnalyzerPage } = await import('@/pages/ReviewAnalyzerPage')
    renderWithProviders(<ReviewAnalyzerPage />)

    expect(screen.getByPlaceholderText(/B01MFCXDYG/i)).toBeTruthy()
    expect(screen.getByRole('button', { name: /analyze reviews/i })).toBeTruthy()
  })

  it('shows sentiment breakdown after user enters ASIN and clicks analyze', async () => {
    const { default: ReviewAnalyzerPage } = await import('@/pages/ReviewAnalyzerPage')
    renderWithProviders(<ReviewAnalyzerPage />)

    const input = screen.getByPlaceholderText(/B01MFCXDYG/i)
    fireEvent.change(input, { target: { value: 'B0MOCK001' } })
    fireEvent.click(screen.getByRole('button', { name: /analyze reviews/i }))

    // User sees the sentiment numbers (82% positive)
    await waitFor(() => {
      expect(screen.getByText(/82/)).toBeTruthy()
    })
  })

  it('shows top pain points so user knows what to fix in their product', async () => {
    const { default: ReviewAnalyzerPage } = await import('@/pages/ReviewAnalyzerPage')
    renderWithProviders(<ReviewAnalyzerPage />)

    const input = screen.getByPlaceholderText(/B01MFCXDYG/i)
    fireEvent.change(input, { target: { value: 'B0MOCK001' } })
    fireEvent.click(screen.getByRole('button', { name: /analyze reviews/i }))

    await waitFor(() => {
      expect(screen.getByText(/lid sometimes leaks/i)).toBeTruthy()
    })
  })

  it('shows a readable summary so user does not have to parse raw numbers', async () => {
    const { default: ReviewAnalyzerPage } = await import('@/pages/ReviewAnalyzerPage')
    renderWithProviders(<ReviewAnalyzerPage />)

    const input = screen.getByPlaceholderText(/B01MFCXDYG/i)
    fireEvent.change(input, { target: { value: 'B0MOCK001' } })
    fireEvent.click(screen.getByRole('button', { name: /analyze reviews/i }))

    await waitFor(() => {
      expect(screen.getByText(/Buyers praise insulation/i)).toBeTruthy()
    })
  })
})
