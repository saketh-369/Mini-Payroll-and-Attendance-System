import { useState, useEffect } from 'react';
import Employees from './pages/Employees';
import Attendance from './pages/Attendance';
import Leave from './pages/Leave';
import Payroll from './pages/Payroll';
import Login from './pages/Login';

const ALL_TABS = [
  { key: 'employees', label: '👥 Employees', Component: Employees, roles: ['ADMIN'] },
  { key: 'attendance', label: '📝 Attendance', Component: Attendance, roles: ['ADMIN', 'EMPLOYEE'] },
  { key: 'leave', label: '🏖️ Leave', Component: Leave, roles: ['ADMIN', 'EMPLOYEE'] },
  { key: 'payroll', label: '💰 Payroll', Component: Payroll, roles: ['ADMIN', 'EMPLOYEE'] },
];

/**
 * Root application shell — header + tab navigation + active page.
 */
export default function App() {
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('attendance');

  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  };

  if (!user) {
    return (
      <div className="app-container">
        <header className="app-header">
          <h1>Mini Payroll & Attendance System</h1>
        </header>
        <Login onLogin={setUser} />
      </div>
    );
  }

  const allowedTabs = ALL_TABS.filter(t => t.roles.includes(user.role));
  
  // Make sure activeTab is valid for the user's role
  const isValidTab = allowedTabs.find(t => t.key === activeTab);
  if (!isValidTab && allowedTabs.length > 0) {
    setActiveTab(allowedTabs[0].key);
    return null; // will re-render
  }

  const ActivePage = allowedTabs.find((t) => t.key === activeTab)?.Component || (() => <div>No page available</div>);

  return (
    <div className="app-container">
      <header className="app-header" style={{ position: 'relative' }}>
        <h1>Mini Payroll & Attendance System</h1>
        <div style={{ position: 'absolute', top: 0, right: 0, display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            Welcome, <strong>{user.name}</strong> ({user.role})
          </span>
          <button onClick={handleLogout} className="btn btn-sm btn-danger">Logout</button>
        </div>
      </header>

      <nav className="tab-bar" role="tablist">
        {allowedTabs.map((tab) => (
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
        <ActivePage user={user} />
      </main>
    </div>
  );
}
