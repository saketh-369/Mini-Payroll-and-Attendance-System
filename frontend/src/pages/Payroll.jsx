import { useState, useEffect } from 'react';
import api from '../api';

/**
 * Payroll page — view the salary breakdown.
 */
export default function Payroll({ user }) {
  const [empId, setEmpId] = useState(user.role === 'ADMIN' ? '' : user.id);
  const [payroll, setPayroll] = useState(null);
  const [message, setMessage] = useState(null);

  // If employee, auto-fetch their payroll
  useEffect(() => {
    if (user.role === 'EMPLOYEE') {
      fetchPayroll(user.id);
    }
  }, [user]);

  async function fetchPayroll(idToFetch) {
    setMessage(null);
    setPayroll(null);
    try {
      const res = await api.get(`/payroll/${idToFetch}`);
      setPayroll(res.data);
    } catch (err) {
      setMessage({ type: 'error', text: err.response?.data?.detail || 'Failed to fetch payroll' });
    }
  }

  async function handleFetch(e) {
    e.preventDefault();
    fetchPayroll(empId);
  }

  return (
    <>
      {user.role === 'ADMIN' && (
        <div className="card">
          <h2>💰 Payroll Calculator</h2>
          {message && <div className={`alert alert-${message.type}`}>{message.text}</div>}
          <form onSubmit={handleFetch} className="flex-row">
            <div className="form-group">
              <label htmlFor="payroll-emp-id">Employee ID</label>
              <input id="payroll-emp-id" type="number" value={empId} onChange={(e) => setEmpId(e.target.value)} required />
            </div>
            <button type="submit" className="btn btn-primary mt-2">Calculate</button>
          </form>
        </div>
      )}

      {user.role === 'EMPLOYEE' && message && (
        <div className={`alert alert-${message.type}`}>{message.text}</div>
      )}

      {payroll && (
        <div className="card">
          <h2>Salary Breakdown — {payroll.employee_name}</h2>
          <p style={{ color: 'var(--text-muted)', marginBottom: '0.5rem', fontSize: '0.85rem' }}>
            Type: <strong style={{ color: 'var(--text-secondary)', textTransform: 'capitalize' }}>{payroll.salary_type}</strong> &nbsp;|&nbsp;
            Base: <strong style={{ color: 'var(--text-secondary)' }}>₹{payroll.salary_amount.toLocaleString()}</strong>
          </p>

          <div className="payroll-grid">
            <div className="payroll-stat">
              <div className="label">Total Days</div>
              <div className="value">{payroll.total_days}</div>
            </div>
            <div className="payroll-stat">
              <div className="label">Present Days</div>
              <div className="value" style={{ color: 'var(--success)' }}>{payroll.present_days}</div>
            </div>
            <div className="payroll-stat">
              <div className="label">Approved Leave</div>
              <div className="value" style={{ color: 'var(--info)' }}>{payroll.approved_leave_days}</div>
            </div>
            <div className="payroll-stat">
              <div className="label">Absent Days</div>
              <div className="value" style={{ color: 'var(--danger)' }}>{payroll.absent_days}</div>
            </div>
            <div className="payroll-stat" style={{ gridColumn: '1 / -1', borderColor: 'var(--accent)' }}>
              <div className="label">Net Salary</div>
              <div className="value salary">₹{payroll.salary.toLocaleString()}</div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
