import { useState, useEffect } from 'react';
import api from '../api';

/**
 * Attendance page — mark attendance (single & bulk) and view records by employee.
 */
export default function Attendance({ user }) {
  const [activeTab, setActiveTab] = useState('single'); // 'single', 'bulk', 'view'

  // Mark attendance state
  const [markForm, setMarkForm] = useState({ employee_id: user.role === 'ADMIN' ? '' : user.id, date: '', status: 'present' });
  const [markMsg, setMarkMsg] = useState(null);

  // Bulk attendance state
  const [bulkDate, setBulkDate] = useState('');
  const [employees, setEmployees] = useState([]);
  const [bulkEntries, setBulkEntries] = useState({});
  const [bulkMsg, setBulkMsg] = useState(null);

  // View attendance state
  const [viewId, setViewId] = useState(user.role === 'ADMIN' ? '' : user.id);
  const [records, setRecords] = useState([]);
  const [viewMsg, setViewMsg] = useState(null);

  // Fetch employees for bulk attendance
  useEffect(() => {
    async function fetchEmployees() {
      try {
        const res = await api.get('/employees/');
        setEmployees(res.data);
        const initialEntries = {};
        res.data.forEach(emp => {
          initialEntries[emp.id] = 'present';
        });
        setBulkEntries(initialEntries);
      } catch (err) {
        console.error('Failed to fetch employees', err);
      }
    }
    if (activeTab === 'bulk') {
      fetchEmployees();
    }
  }, [activeTab]);

  // ── Mark attendance (Single) ───────────────────────────
  async function handleMark(e) {
    e.preventDefault();
    setMarkMsg(null);
    try {
      await api.post('/attendance/', {
        employee_id: parseInt(markForm.employee_id),
        date: markForm.date,
        status: markForm.status,
      });
      setMarkMsg({ type: 'success', text: 'Attendance marked!' });
      setMarkForm({ employee_id: '', date: '', status: 'present' });
    } catch (err) {
      setMarkMsg({ type: 'error', text: err.response?.data?.detail || 'Failed to mark attendance' });
    }
  }

  // ── Mark attendance (Bulk) ───────────────────────────
  async function handleBulkMark(e) {
    e.preventDefault();
    setBulkMsg(null);
    try {
      const entries = Object.keys(bulkEntries).map(empId => ({
        employee_id: parseInt(empId),
        status: bulkEntries[empId]
      }));

      await api.post('/attendance/bulk', {
        date: bulkDate,
        entries: entries,
      });
      setBulkMsg({ type: 'success', text: 'Bulk attendance recorded successfully!' });
      setBulkDate('');
    } catch (err) {
      setBulkMsg({ type: 'error', text: err.response?.data?.detail || 'Failed to record bulk attendance' });
    }
  }

  const handleBulkStatusChange = (empId, status) => {
    setBulkEntries({ ...bulkEntries, [empId]: status });
  };

  // ── View attendance ───────────────────────────
  async function handleView(e) {
    e.preventDefault();
    setViewMsg(null);
    try {
      const res = await api.get(`/attendance/${viewId}`);
      setRecords(res.data);
      if (res.data.length === 0) {
        setViewMsg({ type: 'error', text: 'No attendance records found.' });
      }
    } catch (err) {
      setViewMsg({ type: 'error', text: err.response?.data?.detail || 'Failed to fetch records' });
      setRecords([]);
    }
  }

  return (
    <>
      <div className="tab-bar" style={{ marginBottom: '1.5rem', maxWidth: '400px' }}>
        <button className={activeTab === 'single' ? 'active' : ''} onClick={() => setActiveTab('single')}>Single Entry</button>
        {user.role === 'ADMIN' && (
          <button className={activeTab === 'bulk' ? 'active' : ''} onClick={() => setActiveTab('bulk')}>Bulk Entry</button>
        )}
        <button className={activeTab === 'view' ? 'active' : ''} onClick={() => setActiveTab('view')}>View Records</button>
      </div>

      {activeTab === 'single' && (
        <div className="card">
          <h2>📝 Mark Attendance</h2>
          {markMsg && <div className={`alert alert-${markMsg.type}`}>{markMsg.text}</div>}
          <form onSubmit={handleMark}>
            <div className="form-grid">
              {user.role === 'ADMIN' && (
                <div className="form-group">
                  <label htmlFor="att-emp-id">Employee ID</label>
                  <input id="att-emp-id" type="number" value={markForm.employee_id} onChange={(e) => setMarkForm({ ...markForm, employee_id: e.target.value })} required />
                </div>
              )}
              <div className="form-group">
                <label htmlFor="att-date">Date</label>
                <input id="att-date" type="date" value={markForm.date} onChange={(e) => setMarkForm({ ...markForm, date: e.target.value })} required />
              </div>
              <div className="form-group">
                <label htmlFor="att-status">Status</label>
                <select id="att-status" value={markForm.status} onChange={(e) => setMarkForm({ ...markForm, status: e.target.value })}>
                  <option value="present">Present</option>
                  <option value="absent">Absent</option>
                </select>
              </div>
            </div>
            <button type="submit" className="btn btn-primary">Mark</button>
          </form>
        </div>
      )}

      {activeTab === 'bulk' && (
        <div className="card">
          <h2>👥 Bulk Attendance</h2>
          {bulkMsg && <div className={`alert alert-${bulkMsg.type}`}>{bulkMsg.text}</div>}
          <form onSubmit={handleBulkMark}>
            <div className="form-grid" style={{ marginBottom: '1.5rem' }}>
              <div className="form-group">
                <label htmlFor="bulk-date">Date</label>
                <input id="bulk-date" type="date" value={bulkDate} onChange={(e) => setBulkDate(e.target.value)} required />
              </div>
            </div>

            {employees.length === 0 ? (
              <p style={{ color: 'var(--text-muted)' }}>No employees found.</p>
            ) : (
              <div className="table-wrap mb-1">
                <table>
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Name</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {employees.map((emp) => (
                      <tr key={emp.id}>
                        <td>{emp.id}</td>
                        <td style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{emp.name}</td>
                        <td>
                          <select 
                            value={bulkEntries[emp.id] || 'present'} 
                            onChange={(e) => handleBulkStatusChange(emp.id, e.target.value)}
                            style={{ padding: '0.3rem 0.5rem' }}
                          >
                            <option value="present">Present</option>
                            <option value="absent">Absent</option>
                          </select>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            <button type="submit" className="btn btn-primary mt-2" disabled={employees.length === 0}>Submit Bulk Attendance</button>
          </form>
        </div>
      )}

      {activeTab === 'view' && (
        <div className="card">
          <h2>📋 View Attendance</h2>
          {viewMsg && <div className={`alert alert-${viewMsg.type}`}>{viewMsg.text}</div>}
          <form onSubmit={handleView} className="flex-row mb-1">
            {user.role === 'ADMIN' && (
              <div className="form-group">
                <label htmlFor="view-att-id">Employee ID</label>
                <input id="view-att-id" type="number" value={viewId} onChange={(e) => setViewId(e.target.value)} required />
              </div>
            )}
            <button type="submit" className="btn btn-primary mt-2">Fetch</button>
          </form>

          {records.length > 0 && (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {records.map((r) => (
                    <tr key={r.id}>
                      <td>{r.date}</td>
                      <td><span className={`badge badge-${r.status}`}>{r.status}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </>
  );
}
