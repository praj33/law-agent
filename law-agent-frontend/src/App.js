import { Suspense } from 'react';
import LawAgentApp from './components/LawAgentApp';
import './App.css';

function App() {
  return (
    <div className="App">
      <Suspense fallback={
        <div style={{
          minHeight: '100vh',
          background: 'linear-gradient(135deg, #1e293b 0%, #1e40af 50%, #1e293b 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
          fontSize: '1.5rem'
        }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>⚖️</div>
            <p>Loading Law Agent...</p>
          </div>
        </div>
      }>
        <LawAgentApp />
      </Suspense>
    </div>
  );
}

export default App;
