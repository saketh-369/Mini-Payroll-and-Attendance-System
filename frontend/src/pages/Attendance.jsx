import { useState } from 'react';
import api from '../api';

/**
 * Attendance page — mark attendance (single) and view records by employee.
 */
export default function Attendance() {
  // Mark attendance state
  const [markForm, setMarkForm] = useState({ employee_id: '', date: '', status: 'present' });
  const [markMsg, setMarkMsg] = useState(null);

  // View attendance state
  const [viewId, setViewId] = useState('');
  const [records, setRecords] = useState([]);
  const [viewMsg, setViewMsg] = useState(null);

  // ── Mark attendance ───────────────────────────
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
      {/* Mark Attendance */}
      <div className="card">
        <h2>📝 Mark Attendance</h2>
        {markMsg && <div className={`alert alert-${markMsg.type}`}>{markMsg.text}</div>}
        <form onSubmit={handleMark}>
          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="att-emp-id">Employee ID</label>
              <input id="att-emp-id" type="number" value={markForm.employee_id} onChange={(e) => setMarkForm({ ...markForm, employee_id: e.target.value })} required />
            </div>
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

      {/* View Attendance */}
      <div className="card">
        <h2>📋 View Attendance</h2>
        {viewMsg && <div className={`alert alert-${viewMsg.type}`}>{viewMsg.text}</div>}
        <form onSubmit={handleView} className="flex-row mb-1">
          <div className="form-group">
            <label htmlFor="view-att-id">Employee ID</label>
            <input id="view-att-id" type="number" value={viewId} onChange={(e) => setViewId(e.target.value)} required />
          </div>
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
    </>
  );
}
