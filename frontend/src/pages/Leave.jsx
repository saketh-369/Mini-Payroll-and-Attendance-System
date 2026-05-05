import { useState, useEffect } from 'react';
import api from '../api';

/**
 * Leave page — apply for leave and approve/reject existing requests.
 */
export default function Leave() {
  const [leaves, setLeaves] = useState([]);
  const [form, setForm] = useState({ employee_id: '', start_date: '', end_date: '' });
  const [message, setMessage] = useState(null);

  useEffect(() => {
    fetchLeaves();
  }, []);

  async function fetchLeaves() {
    try {
      const res = await api.get('/leave/');
      setLeaves(res.data);
    } catch (err) {
      console.error('Failed to fetch leaves', err);
    }
  }

  async function handleApply(e) {
    e.preventDefault();
    setMessage(null);
    try {
      await api.post('/leave/', {
        employee_id: parseInt(form.employee_id),
        start_date: form.start_date,
        end_date: form.end_date,
      });
      setMessage({ type: 'success', text: 'Leave applied successfully!' });
      setForm({ employee_id: '', start_date: '', end_date: '' });
      fetchLeaves();
    } catch (err) {
      setMessage({ type: 'error', text: err.response?.data?.detail || 'Failed to apply leave' });
    }
  }

  async function handleStatusUpdate(leaveId, status) {
    try {
      await api.put(`/leave/${leaveId}`, { status });
      fetchLeaves();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to update leave');
    }
  }

  return (
    <>
      {/* Apply Leave */}
      <div className="card">
        <h2>🏖️ Apply Leave</h2>
        {message && <div className={`alert alert-${message.type}`}>{message.text}</div>}
        <form onSubmit={handleApply}>
          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="leave-emp-id">Employee ID</label>
              <input id="leave-emp-id" type="number" value={form.employee_id} onChange={(e) => setForm({ ...form, employee_id: e.target.value })} required />
            </div>
            <div className="form-group">
              <label htmlFor="leave-start">Start Date</label>
              <input id="leave-start" type="date" value={form.start_date} onChange={(e) => setForm({ ...form, start_date: e.target.value })} required />
            </div>
            <div className="form-group">
              <label htmlFor="leave-end">End Date</label>
              <input id="leave-end" type="date" value={form.end_date} onChange={(e) => setForm({ ...form, end_date: e.target.value })} required />
            </div>
          </div>
          <button type="submit" className="btn btn-primary">Apply</button>
        </form>
      </div>

      {/* Leave Requests */}
      <div className="card">
        <h2>📑 Leave Requests</h2>
        {leaves.length === 0 ? (
          <p style={{ color: 'var(--text-muted)' }}>No leave requests found.</p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Employee ID</th>
                  <th>Start</th>
                  <th>End</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {leaves.map((l) => (
                  <tr key={l.id}>
                    <td>{l.id}</td>
                    <td>{l.employee_id}</td>
                    <td>{l.start_date}</td>
                    <td>{l.end_date}</td>
                    <td><span className={`badge badge-${l.status}`}>{l.status}</span></td>
                    <td>
                      {l.status === 'pending' && (
                        <div className="flex-row">
                          <button className="btn btn-success btn-sm" onClick={() => handleStatusUpdate(l.id, 'approved')}>Approve</button>
                          <button className="btn btn-danger btn-sm" onClick={() => handleStatusUpdate(l.id, 'rejected')}>Reject</button>
                        </div>
                      )}
                    </td>
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
