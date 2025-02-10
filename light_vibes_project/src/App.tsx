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
                
                <h1 className="title">Qwerest</h1>
                <h2 className="subtitle" style={{
                  color: '#F5F3CD',
                  fontSize: '36px',
                  padding: '15px 40px',
                  background: 'rgba(40, 102, 63, 0.8)',
                  borderRadius: '15px',
                  boxShadow: '0 4px 8px rgba(0, 0, 0, 0.2)',
                  border: '2px solid #F5F3CD',
                  textShadow: '2px 2px 4px rgba(0, 0, 0, 0.3)',
                  margin: '20px 0',
                  fontFamily: "'Quicksand', sans-serif",
                  fontWeight: 'bold',
                  letterSpacing: '1px',
                  transform: 'translateY(-10px)',
                }}>
                  Query the forest
                </h2>
                
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

                <div className="mission-statement">
                  We wanted to build a project that would have a real impact on the environment and ecosystems, as we understand how important they are for the survival of all life on Earth! We ended up settling on this idea, because not only can it raise awareness about the potential risks posed to wildlife, but also can work as an actual plan to combat the extinction of these precious beings.
                </div>

                <div className="mission-statement technical">
                  Using Gbif's dataset of animal observations, we were able to create a map to visualize the data in a convenient way to better understand the population level of various species. We then trained an AI model on data from many land species in order to predict future levels based on past data. Using this, we use an LLM (Google's Gemini) to give a report based on the graph outputted, and give the risk of extinction as well as a plan to overcome this risk.
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
