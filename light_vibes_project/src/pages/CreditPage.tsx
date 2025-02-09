const CreditPage = () => {
  return (
    
    <div style={{
      minHeight: '100vh',

      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      position: 'relative',
      paddingTop: '170px'
    }}>
      <div style={{
        width: '95%',
        maxWidth: '800px',
        display: 'flex',
        flexDirection: 'column',
        gap: '24px',
        position: 'absolute',
        top: '50%',
        transform: 'translateY(-50%)'
      }}>
        <h1 style={{
          fontSize: '32px',
          fontWeight: 'bold',
          color: '#FDFBD4',
          textAlign: 'center',
          marginBottom: '20px'
        }}>
          Credits
        </h1>

        <div style={{
          backgroundColor: '#68392E',
          borderRadius: '8px',
          padding: '24px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          marginBottom: '20px',
          textAlign: 'center'
        }}>
          <h2 style={{
            color:'#FDFBD4',
            fontSize: '20px',
            fontWeight: 'bold',
            marginBottom: '16px'
          }}>
            Data Source
          </h2>
          <p style={{ marginBottom: '16px', color:'#FDFBD4' }}>
            Global Biodiversity Information Facility (GBIF) - An international network and data infrastructure providing open access to data about all types of life on Earth.
          </p>
          <a 
            href="https://www.gbif.org" 
            target="_blank" 
            rel="noopener noreferrer"
            style={{
              color: '#FDFBD4',
              textDecoration: 'none',
              fontWeight: 'bold'
            }}
          >
            Visit GBIF Website →
          </a>
        </div>

        <div style={{
          backgroundColor: '#68392E',
          borderRadius: '8px',
          padding: '24px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          textAlign: 'center'
        }}>
          <h2 style={{
            color:'#FDFBD4',
            fontSize: '20px',
            fontWeight: 'bold',
            marginBottom: '16px'
          }}>
            Development Assistant
          </h2>
          <p style={{ marginBottom: '16px' , color:"#FDFBD4"}}>
            Claude AI (Anthropic) - An AI assistant that helped with code development, debugging, and implementation of various features in this project.
          </p>
          <a 
            href="https://www.anthropic.com/claude" 
            target="_blank" 
            rel="noopener noreferrer"
            style={{
              color: '#FDFBD4',
              textDecoration: 'none',
              fontWeight: 'bold'
            }}
          >
            Learn About Claude →
          </a>
        </div>
      </div>
    </div>
  );
};

export default CreditPage; 