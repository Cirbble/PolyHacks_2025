const CreditPage = () => {
  return (
    <div style={{
      padding: '90px 20px 20px',
      maxWidth: '800px',
      margin: '0 auto'
    }}>
      <h1 style={{
        fontSize: '24px',
        fontWeight: 'bold',
        marginBottom: '24px',
        color: '#384BC7',
        borderRadius:'8px',
        borderColor:'black'
      }}>
        Credits
      </h1>

      <div style={{
        backgroundColor: 'white',
        borderRadius: '8px',
        padding: '24px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        marginBottom: '20px'
      }}>
        <h2 style={{
          color:'#3892C6',
          fontSize: '20px',
          fontWeight: 'bold',
          marginBottom: '16px'
        }}>
          Data Source
        </h2>
        <p style={{ marginBottom: '16px', color:'#3892C6' }}>
          Global Biodiversity Information Facility (GBIF) - An international network and data infrastructure providing open access to data about all types of life on Earth.
        </p>
        <a 
          href="https://www.gbif.org" 
          target="_blank" 
          rel="noopener noreferrer"
          style={{
            color: '#3892C6',
            textDecoration: 'none',
            fontWeight: 'bold'
          }}
        >
          Visit GBIF Website →
        </a>
      </div>

      <div style={{
        backgroundColor: 'white',
        borderRadius: '8px',
        padding: '24px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }}>
        <h2 style={{
          color:'#3892C6',
          fontSize: '20px',
          fontWeight: 'bold',
          marginBottom: '16px'
        }}>
          Development Assistant
        </h2>
        <p style={{ marginBottom: '16px' , color:"#3892C6"}}>
          Claude AI (Anthropic) - An AI assistant that helped with code development, debugging, and implementation of various features in this project.
        </p>
        <a 
          href="https://www.anthropic.com/claude" 
          target="_blank" 
          rel="noopener noreferrer"
          style={{
            color: '#3892C6',
            textDecoration: 'none',
            fontWeight: 'bold'
          }}
        >
          Learn About Claude →
        </a>
      </div>
    </div>
  );
};

export default CreditPage; 