import { useState } from 'react';
import LoginForm from './components/LoginForm';
import Dashboard from './components/Dashboard';

export default function App() {
  const [currentUser, setCurrentUser] = useState(null);

  const handleLogin = (userType, email) => {
    setCurrentUser({
      type: userType,
      name: userType === 'patient' ? 'John Doe' : userType === 'provider' ? 'City General Hospital' : 'BlueCross Insurance',
      email: email
    });
  };

  const handleLogout = () => {
    setCurrentUser(null);
  };

  if (!currentUser) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50 flex items-center justify-center p-6">
        <LoginForm onLogin={handleLogin} />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      <Dashboard user={currentUser} onLogout={handleLogout} />
    </div>
  );
}
