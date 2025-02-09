import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import waveIcon from './assets/wave_icon.png';
import './App.css';
import TopBar from './components/TopBar';
import DataPage from './pages/DataPage';
import CreditPage from './pages/CreditPage';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        <TopBar />

        <div className="ondebox">
          <svg className="onde" 
               xmlns="http://www.w3.org/2000/svg" 
               xmlnsXlink="http://www.w3.org/1999/xlink"
               viewBox="0 24 150 28" 
               preserveAspectRatio="none" 
               shapeRendering="auto">
            <defs>
              <path id="onda" d="M-160 44c30 0 58-18 88-18s 58 18 88 18 58-18 88-18 58 18 88 18 v44h-352Z" />
            </defs>
            <g className="parallaxonde">
            
              <use xlinkHref="#onda" x="48" y="1" fill="rgba(17,170,159,0.6)" />
              
              <use xlinkHref="#onda" x="48" y="3" fill="rgba(17,170,159,0.4)" />
              
              <use xlinkHref="#onda" x="48" y="5" fill="rgba(17,170,159,0.1)" />
              <use xlinkHref="#onda" x="48" y="10" fill="#3892C6" />
              
            </g>
          </svg>
        </div>

        <Routes>
          <Route path="/" element={
            <div style={{ 
              paddingTop: '170px',
              minHeight: 'calc(100vh - 70px)',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'flex-start',
              alignItems: 'center',
              gap: '40px',
              paddingBottom: '50px'
            }}>
              <img 
                src={waveIcon} 
                alt="Wave Icon"
                style={{
                  width: '200px',
                  height: '200px',
                  marginTop: '20px'
                }}
              />
              <h1 style={{
                fontSize: '2.5rem',
                color: '#3892C6',
                fontWeight: 'bold'
              }}>
                Marine Life Tracker
              </h1>
            </div>
          } />
          <Route path="/data" element={<DataPage />} />
          <Route path="/credit" element={<CreditPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
