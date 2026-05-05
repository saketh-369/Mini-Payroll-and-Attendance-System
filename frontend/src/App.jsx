import { useState } from 'react';
import Employees from './pages/Employees';
import Attendance from './pages/Attendance';
import Leave from './pages/Leave';
import Payroll from './pages/Payroll';

const TABS = [
  { key: 'employees', label: '👥 Employees', Component: Employees },
  { key: 'attendance', label: '📝 Attendance', Component: Attendance },
  { key: 'leave', label: '🏖️ Leave', Component: Leave },
  { key: 'payroll', label: '💰 Payroll', Component: Payroll },
];

/**
 * Root application shell — header + tab navigation + active page.
 */
export default function App() {
  const [activeTab, setActiveTab] = useState('employees');
  const ActivePage = TABS.find((t) => t.key === activeTab).Component;

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Mini Payroll & Attendance System</h1>
      </header>

      <nav className="tab-bar" role="tablist">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            role="tab"
            aria-selected={activeTab === tab.key}
            className={activeTab === tab.key ? 'active' : ''}
            onClick={() => setActiveTab(tab.key)}
          >
            {tab.label}
          </button>
        ))}
      </nav>

      <main>
        <ActivePage />
      </main>
    </div>
  );
}
