import { useNavigate } from 'react-router-dom';

const TopBar = () => {
  const navigate = useNavigate();

  return (
    <div style={{
      backgroundColor: '#3892C6',
      width: '100%',
      height: '60px',
      position: 'fixed',
      top: 0,
      left: 0,
      zIndex: 1000,
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: '0 20px'
    }}>
      <h1 style={{ color: 'white', fontSize: '20px', fontWeight: 'bold' }}>
        Marine Life Tracker
      </h1>
      <button 
        onClick={() => navigate('/data')}
        style={{
          backgroundColor: 'white',
          color: '#76B6C4',
          padding: '8px 16px',
          borderRadius: '8px',
          border: 'none',
          cursor: 'pointer',
          transition: 'background-color 0.2s',
          fontWeight: 'bold'
        }}
        onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#f0f0f0'}
        onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'white'}
      >
        View Data
      </button>
    </div>
  );
};

export default TopBar; 