import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Header } from './components/Header';
import Footer from './components/Footer';
import Home from './pages/Home';
import DayView from './pages/DayView';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-white dark:bg-zinc-950 text-zinc-900 dark:text-zinc-100 flex flex-col font-sans transition-colors duration-300">
        <Header />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/day/:date" element={<DayView />} />
        </Routes>
        <Footer />
      </div>
    </Router>
  );
}

export default App;
