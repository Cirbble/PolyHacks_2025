import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import BiodiversityMap from './map';
import waveIcon from './assets/wave_icon.png';
import TopBar from './components/TopBar';
import DataPage from './pages/DataPage';
import CreditPage from './pages/CreditPage';

function App() {
  return (
    <Router>
      <div className="app-container">
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
              <use xlinkHref="#onda" x="48" y="1" fill="#935341" />
              <use xlinkHref="#onda" x="48" y="5" fill="#4F834F" />
              <use xlinkHref="#onda" x="48" y="10" fill="#28663F" />
            </g>
          </svg>
        </div>

        <Routes>
          <Route path="/" element={
            <>
              <main className="main-content">
                <div className="logo-container">
                  <img src={waveIcon} alt="Wave Icon" />
                </div>
                
                <h1 className="title">Marine Life Tracker</h1>
                
                <div className="content">
                  <div className="content__container">
                    <p className="content__container__text">
                      We help
                    </p>
                    
                    <ul className="content__container__list">
                      <li className="content__container__list__item">the animals !</li>
                      <li className="content__container__list__item">the plants !</li>
                      <li className="content__container__list__item">the ecosystems !</li>
                      <li className="content__container__list__item">everybody !!</li>
                      <li className="content__container__list__item">the animals !</li>
                    </ul>
                  </div>
                </div>
              </main>
            </>
          } />
          <Route path="/data" element={<DataPage />} />
          <Route path="/credit" element={<CreditPage />} />
          <Route path="/map" element={<BiodiversityMap />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
