import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Layout from '@/components/Layout'
import DashboardPage from '@/pages/DashboardPage'
import ProductResearchPage from '@/pages/ProductResearchPage'
import ListingGeneratorPage from '@/pages/ListingGeneratorPage'
import ReviewAnalyzerPage from '@/pages/ReviewAnalyzerPage'
import CompetitorMonitorPage from '@/pages/CompetitorMonitorPage'
import AdOptimizerPage from '@/pages/AdOptimizerPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="research" element={<ProductResearchPage />} />
          <Route path="listing" element={<ListingGeneratorPage />} />
          <Route path="reviews" element={<ReviewAnalyzerPage />} />
          <Route path="monitor" element={<CompetitorMonitorPage />} />
          <Route path="ads" element={<AdOptimizerPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
