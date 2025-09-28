import { useState } from "react";
import { useNavigate } from "react-router-dom";

const SelectFormSimple = () => {
  const navigate = useNavigate();
  const [selectedForm, setSelectedForm] = useState("");

  const forms = [
    {
      code: 'B-1/B-2',
      title: 'Visto de Turismo e Negócios',
      description: 'Para turismo, visitas familiares, reuniões de negócios'
    },
    {
      code: 'H-1B',
      title: 'Visto de Trabalho Especializado',
      description: 'Para profissionais com ensino superior'
    }
  ];

  const handleFormSelect = (formCode: string) => {
    setSelectedForm(formCode);
    navigate('/auto-application/basic-data', { 
      state: { 
        selectedForm: formCode,
        caseId: localStorage.getItem('osprey_case_id')
      } 
    });
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h1 style={{ color: 'black', marginBottom: '20px' }}>
        Selecione o Tipo de Visto
      </h1>
      
      <p style={{ marginBottom: '30px', color: '#666' }}>
        Escolha o tipo de visto americano que deseja aplicar:
      </p>

      <div style={{ display: 'grid', gap: '20px' }}>
        {forms.map((form) => (
          <div
            key={form.code}
            onClick={() => handleFormSelect(form.code)}
            style={{
              border: '2px solid black',
              borderRadius: '8px',
              padding: '20px',
              cursor: 'pointer',
              backgroundColor: selectedForm === form.code ? '#f0f0f0' : 'white',
              transition: 'all 0.2s'
            }}
          >
            <h3 style={{ margin: '0 0 10px 0', color: 'black' }}>
              {form.title}
            </h3>
            <p style={{ margin: 0, color: '#666', fontSize: '14px' }}>
              {form.description}
            </p>
            
            <button
              style={{
                marginTop: '15px',
                padding: '10px 20px',
                backgroundColor: 'black',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Começar {form.code}
            </button>
          </div>
        ))}
      </div>

      <div style={{ marginTop: '30px', textAlign: 'center' }}>
        <button
          onClick={() => navigate('/auto-application/start')}
          style={{
            padding: '10px 20px',
            backgroundColor: 'white',
            color: 'black',
            border: '2px solid black',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          ← Voltar
        </button>
      </div>
    </div>
  );
};

export default SelectFormSimple;