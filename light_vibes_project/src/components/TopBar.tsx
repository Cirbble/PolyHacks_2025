import { useNavigate } from 'react-router-dom';
import waveIcon from '../assets/wave_icon.png';

const TopBar = () => {
  const navigate = useNavigate();

  const buttonStyle = {
    backgroundColor: 'white',
    color: '#935341',
    padding: '6px 12px',
    borderRadius: '6px',
    border: 'none',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
    fontWeight: 'bold',
    fontSize: '14px',
    margin: '0 2px',
    minWidth: 'fit-content',
    whiteSpace: 'nowrap'
  };

  return (
    <div style={{
      backgroundColor: '#28663F',
      width: '100%',
      height: '70px',
      position: 'fixed',
      top: 0,
      left: 0,
      zIndex: 1000,
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: '0 16px',
      boxSizing: 'border-box'
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        cursor: 'pointer',
      }} onClick={() => navigate('/')}>
        <img 
          src={waveIcon} 
          alt="Wave Icon" 
          style={{
            height: '30px',
            width: '30px',
            marginRight: '8px',
            transition: 'opacity 0.2s'
          }}
          onMouseOver={(e) => e.currentTarget.style.opacity = '0.8'}
          onMouseOut={(e) => e.currentTarget.style.opacity = '1'}
        />
        <h1 style={{ 
          color: 'white', 
          fontSize: '20px', 
          fontWeight: 'bold',
          marginRight: '12px',
          whiteSpace: 'nowrap',
          transition: 'opacity 0.2s'
        }}>
          Marine Life Tracker
        </h1>
      </div>
      <div style={{ 
        display: 'flex', 
        gap: '4px',
        marginRight: '0',
        flexShrink: 0
      }}>
        <button 
          onClick={() => navigate('/map')}
          style={buttonStyle}
          onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#f0f0f0'}
          onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'white'}
        >
          Map
        </button>
        <button 
          onClick={() => navigate('/data')}
          style={buttonStyle}
          onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#f0f0f0'}
          onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'white'}
        >
          Data
        </button>
        <button 
          onClick={() => navigate('/credit')}
          style={buttonStyle}
          onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#f0f0f0'}
          onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'white'}
        >
          Credit
        </button>
      </div>
    </div>
  );
};

export default TopBar; 