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
        
        <Routes>
          <Route path="/" element={
            <>
              <div className="wave-container">
                <div className="wave"></div>
                <div className="wave"></div>
                <div className="wave"></div>
              </div>
              
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
