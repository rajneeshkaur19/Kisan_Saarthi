import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import BottomNav from './components/BottomNav';

import Welcome from './pages/Welcome';
import Home from './pages/Home';
import CropDoctor from './pages/CropDoctor';
import MandiPrices from './pages/MandiPrices';
import LoanSchemes from './pages/LoanSchemes';
import Chatbot from './pages/Chatbot';

function AppLayout({ children }) {
  const location = useLocation();
  const isWelcomePage = location.pathname === '/' || location.pathname === '/welcome';

  if (isWelcomePage) {
    return <main className="min-h-screen bg-[#f7faf7]">{children}</main>;
  }

  return (
    <div className="flex min-h-screen bg-[#f8faf8] text-gray-800">
      {/* Desktop Sidebar Navigation */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <Navbar />
        <main className="flex-1 p-4 md:p-8 max-w-7xl mx-auto w-full">
          {children}
        </main>
        {/* Mobile Bottom Navigation */}
        <BottomNav />
      </div>
    </div>
  );
}

export default function App() {
  return (
    <Router>
      <AppLayout>
        <Routes>
          <Route path="/" element={<Welcome />} />
          <Route path="/welcome" element={<Welcome />} />
          <Route path="/home" element={<Home />} />
          <Route path="/doctor" element={<CropDoctor />} />
          <Route path="/prices" element={<MandiPrices />} />
          <Route path="/schemes" element={<LoanSchemes />} />
          <Route path="/chat" element={<Chatbot />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AppLayout>
    </Router>
  );
}