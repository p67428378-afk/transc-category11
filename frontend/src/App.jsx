import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [loanApplications, setLoanApplications] = useState([]);
  const [newApplication, setNewApplication] = useState({
    applicant_id: '',
    loan_type: '',
    amount_requested: 0,
    kyc: {
      first_name: '',
      last_name: '',
      date_of_birth: '',
      address: '',
      ssn: '',
      identification_document_id: ''
    }
  });

  useEffect(() => {
    // Fetch loan applications on component mount
    // This would typically be a GET request to /api/v1/loans
    // For now, we'll simulate it or leave it for future implementation
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    if (name.startsWith('kyc.')) {
      const kycField = name.split('.')[1];
      setNewApplication(prev => ({
        ...prev,
        kyc: {
          ...prev.kyc,
          [kycField]: value
        }
      }));
    } else {
      setNewApplication(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/v1/loans/application', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newApplication),
      });
      if (response.ok) {
        const data = await response.json();
        alert('Application submitted successfully!');
        setLoanApplications(prev => [...prev, data]);
        // Clear form
        setNewApplication({
          applicant_id: '',
          loan_type: '',
          amount_requested: 0,
          kyc: {
            first_name: '',
            last_name: '',
            date_of_birth: '',
            address: '',
            ssn: '',
            identification_document_id: ''
          }
        });
      } else {
        const errorData = await response.json();
        alert(`Error submitting application: ${errorData.detail || response.statusText}`);
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Network error or unexpected issue.');
    }
  };

  return (
    <div className="App">
      <h1>Loan Officer Dashboard</h1>

      <section>
        <h2>Submit New Loan Application</h2>
        <form onSubmit={handleSubmit}>
          <input type="text" name="applicant_id" placeholder="Applicant ID" value={newApplication.applicant_id} onChange={handleInputChange} required />
          <input type="text" name="loan_type" placeholder="Loan Type" value={newApplication.loan_type} onChange={handleInputChange} required />
          <input type="number" name="amount_requested" placeholder="Amount Requested" value={newApplication.amount_requested} onChange={handleInputChange} required />
          
          <h3>KYC Details</h3>
          <input type="text" name="kyc.first_name" placeholder="First Name" value={newApplication.kyc.first_name} onChange={handleInputChange} required />
          <input type="text" name="kyc.last_name" placeholder="Last Name" value={newApplication.kyc.last_name} onChange={handleInputChange} required />
          <input type="date" name="kyc.date_of_birth" placeholder="Date of Birth" value={newApplication.kyc.date_of_birth} onChange={handleInputChange} required />
          <input type="text" name="kyc.address" placeholder="Address" value={newApplication.kyc.address} onChange={handleInputChange} required />
          <input type="text" name="kyc.ssn" placeholder="SSN" value={newApplication.kyc.ssn} onChange={handleInputChange} required />
          <input type="text" name="kyc.identification_document_id" placeholder="Identification Document ID" value={newApplication.kyc.identification_document_id} onChange={handleInputChange} />
          
          <button type="submit">Submit Application</button>
        </form>
      </section>

      <section>
        <h2>Existing Loan Applications</h2>
        {loanApplications.length === 0 ? (
          <p>No applications submitted yet.</p>
        ) : (
          <ul>
            {loanApplications.map(app => (
              <li key={app.application_id}>
                {app.loan_type} - {app.amount_requested} - Status: {app.status}
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

export default App;
