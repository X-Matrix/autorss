import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import DailyDetail from './pages/DailyDetail'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/daily/:date" element={<DailyDetail />} />
      </Routes>
    </Layout>
  )
}

export default App
