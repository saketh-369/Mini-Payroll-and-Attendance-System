import { useState, useEffect } from 'react';
import api from '../api';

/**
 * Employees page — add a new employee and view the employee list.
 */
export default function Employees() {
  const [employees, setEmployees] = useState([]);
  const [form, setForm] = useState({
    name: '',
    role: '',
    work_type: 'Office',
    salary_type: 'monthly',
    salary_amount: '',
  });
  const [message, setMessage] = useState(null);

  // Fetch all employees on mount
  useEffect(() => {
    fetchEmployees();
  }, []);

  async function fetchEmployees() {
    try {
      const res = await api.get('/employees/');
      setEmployees(res.data);
    } catch (err) {
      console.error('Failed to fetch employees', err);
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setMessage(null);
    try {
      await api.post('/employees/', {
        ...form,
        salary_amount: parseFloat(form.salary_amount),
      });
      setMessage({ type: 'success', text: 'Employee added successfully!' });
      setForm({ name: '', role: '', work_type: 'Office', salary_type: 'monthly', salary_amount: '' });
      fetchEmployees();
    } catch (err) {
      setMessage({ type: 'error', text: err.response?.data?.detail || 'Failed to add employee' });
    }
  }

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  return (
    <>
      {/* Add Employee Form */}
      <div className="card">
        <h2>➕ Add Employee</h2>
        {message && (
          <div className={`alert alert-${message.type}`}>{message.text}</div>
        )}
        <form onSubmit={handleSubmit}>
          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="emp-name">Name</label>
              <input id="emp-name" name="name" value={form.name} onChange={handleChange} required />
            </div>
            <div className="form-group">
              <label htmlFor="emp-role">Role</label>
              <input id="emp-role" name="role" value={form.role} onChange={handleChange} required />
            </div>
            <div className="form-group">
              <label htmlFor="emp-work-type">Work Type</label>
              <select id="emp-work-type" name="work_type" value={form.work_type} onChange={handleChange}>
                <option value="Office">Office</option>
                <option value="WFH">WFH</option>
                <option value="On-site">On-site</option>
              </select>
            </div>
            <div className="form-group">
              <label htmlFor="emp-salary-type">Salary Type</label>
              <select id="emp-salary-type" name="salary_type" value={form.salary_type} onChange={handleChange}>
                <option value="monthly">Monthly</option>
                <option value="daily">Daily</option>
              </select>
            </div>
            <div className="form-group">
              <label htmlFor="emp-salary-amount">Salary Amount</label>
              <input id="emp-salary-amount" name="salary_amount" type="number" step="0.01" value={form.salary_amount} onChange={handleChange} required />
            </div>
          </div>
          <button type="submit" className="btn btn-primary">Add Employee</button>
        </form>
      </div>

      {/* Employee List */}
      <div className="card">
        <h2>👥 Employee List</h2>
        {employees.length === 0 ? (
          <p style={{ color: 'var(--text-muted)' }}>No employees found. Add one above.</p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Role</th>
                  <th>Work Type</th>
                  <th>Salary Type</th>
                  <th>Salary Amount</th>
                </tr>
              </thead>
              <tbody>
                {employees.map((emp) => (
                  <tr key={emp.id}>
                    <td>{emp.id}</td>
                    <td style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{emp.name}</td>
                    <td>{emp.role}</td>
                    <td>{emp.work_type}</td>
                    <td style={{ textTransform: 'capitalize' }}>{emp.salary_type}</td>
                    <td>₹{emp.salary_amount.toLocaleString()}</td>
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
