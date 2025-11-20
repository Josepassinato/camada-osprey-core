"""
Repositório de Formulários Oficiais do USCIS
Mantém uma biblioteca de todos os formulários oficiais para cada tipo de visto
"""

import os
import requests
from pathlib import Path

class OfficialFormsRepository:
    """Gerencia acesso aos formulários oficiais do USCIS"""
    
    FORMS_DIR = Path("/app/official_forms/uscis_forms")
    
    # Mapeamento de formulários oficiais por tipo de visto
    FORMS_CATALOG = {
        "H-1B": {
            "I-129": {
                "name": "Petition for a Nonimmigrant Worker",
                "url": "https://www.uscis.gov/sites/default/files/document/forms/i-129.pdf",
                "direct_download": "https://www.reginfo.gov/public/do/DownloadDocument?objectID=4578401",
                "filename": "i-129.pdf",
                "pages": 20,
                "required": True
            },
            "I-129-H": {
                "name": "H Classification Supplement",
                "url": "https://www.uscis.gov/sites/default/files/document/forms/i-129h.pdf",
                "filename": "i-129h.pdf",
                "pages": 4,
                "required": True
            },
            "LCA": {
                "name": "Labor Condition Application (ETA-9035)",
                "url": "https://www.dol.gov/sites/dolgov/files/ETA/oflc/pdfs/ETA_Form_9035.pdf",
                "filename": "eta-9035-lca.pdf",
                "pages": 10,
                "required": True
            }
        },
        "F-1": {
            "I-20": {
                "name": "Certificate of Eligibility for Nonimmigrant Student Status",
                "note": "Issued by school, not downloadable",
                "required": True
            },
            "I-539": {
                "name": "Application to Extend/Change Nonimmigrant Status",
                "url": "https://www.uscis.gov/sites/default/files/document/forms/i-539.pdf",
                "filename": "i-539.pdf",
                "required": False
            }
        },
        "I-539": {
            "I-539": {
                "name": "Application to Extend/Change Nonimmigrant Status",
                "url": "https://www.uscis.gov/sites/default/files/document/forms/i-539.pdf",
                "filename": "i-539.pdf",
                "pages": 12,
                "required": True
            }
        },
        "Green_Card": {
            "I-485": {
                "name": "Application to Register Permanent Residence",
                "url": "https://www.uscis.gov/sites/default/files/document/forms/i-485.pdf",
                "filename": "i-485.pdf",
                "pages": 18,
                "required": True
            },
            "I-130": {
                "name": "Petition for Alien Relative",
                "url": "https://www.uscis.gov/sites/default/files/document/forms/i-130.pdf",
                "filename": "i-130.pdf",
                "pages": 12,
                "required": False
            },
            "I-140": {
                "name": "Immigrant Petition for Alien Workers",
                "url": "https://www.uscis.gov/sites/default/files/document/forms/i-140.pdf",
                "filename": "i-140.pdf",
                "pages": 8,
                "required": False
            },
            "I-864": {
                "name": "Affidavit of Support",
                "url": "https://www.uscis.gov/sites/default/files/document/forms/i-864.pdf",
                "filename": "i-864.pdf",
                "pages": 11,
                "required": False
            }
        },
        "Citizenship": {
            "N-400": {
                "name": "Application for Naturalization",
                "url": "https://www.uscis.gov/sites/default/files/document/forms/n-400.pdf",
                "filename": "n-400.pdf",
                "pages": 21,
                "required": True
            }
        }
    }
    
    def __init__(self):
        """Inicializa o repositório"""
        self.forms_dir = self.FORMS_DIR
        self.forms_dir.mkdir(parents=True, exist_ok=True)
        
    def get_form(self, visa_type: str, form_code: str) -> str:
        """
        Obtém o caminho de um formulário específico
        Baixa se não existir localmente
        
        Args:
            visa_type: Tipo de visto (H-1B, F-1, Green_Card, etc.)
            form_code: Código do formulário (I-129, I-539, etc.)
        
        Returns:
            Caminho do arquivo PDF do formulário
        """
        
        if visa_type not in self.FORMS_CATALOG:
            raise ValueError(f"Tipo de visto não suportado: {visa_type}")
        
        if form_code not in self.FORMS_CATALOG[visa_type]:
            raise ValueError(f"Formulário {form_code} não encontrado para {visa_type}")
        
        form_info = self.FORMS_CATALOG[visa_type][form_code]
        
        # Se formulário não tem URL (ex: I-20 é emitido pela escola)
        if "url" not in form_info:
            raise ValueError(f"{form_code} não é baixável: {form_info.get('note', 'Não disponível')}")
        
        form_path = self.forms_dir / form_info["filename"]
        
        # Verificar se já existe localmente
        if form_path.exists():
            print(f"✅ Formulário {form_code} encontrado localmente: {form_path}")
            return str(form_path)
        
        # Baixar formulário
        print(f"📥 Baixando {form_code} - {form_info['name']}...")
        
        try:
            # Tentar URL alternativa primeiro se existir
            download_url = form_info.get('direct_download', form_info['url'])
            
            response = requests.get(download_url, timeout=30)
            response.raise_for_status()
            
            # Salvar arquivo
            with open(form_path, 'wb') as f:
                f.write(response.content)
            
            file_size = os.path.getsize(form_path)
            print(f"✅ {form_code} baixado: {file_size:,} bytes")
            
            return str(form_path)
            
        except Exception as e:
            print(f"❌ Erro ao baixar {form_code}: {e}")
            # Tentar URL alternativa
            if 'direct_download' in form_info and download_url == form_info['direct_download']:
                try:
                    response = requests.get(form_info['url'], timeout=30)
                    response.raise_for_status()
                    with open(form_path, 'wb') as f:
                        f.write(response.content)
                    print(f"✅ {form_code} baixado via URL alternativa")
                    return str(form_path)
                except:
                    pass
            
            return None
    
    def get_required_forms_for_visa(self, visa_type: str) -> list:
        """
        Retorna lista de formulários obrigatórios para um tipo de visto
        """
        if visa_type not in self.FORMS_CATALOG:
            return []
        
        required_forms = []
        for form_code, form_info in self.FORMS_CATALOG[visa_type].items():
            if form_info.get('required', False):
                required_forms.append({
                    'code': form_code,
                    'name': form_info['name'],
                    'filename': form_info.get('filename', ''),
                    'downloadable': 'url' in form_info
                })
        
        return required_forms
    
    def download_all_forms_for_visa(self, visa_type: str):
        """Baixa todos os formulários para um tipo de visto"""
        print(f"\n{'='*80}")
        print(f"📥 BAIXANDO FORMULÁRIOS PARA {visa_type}")
        print(f"{'='*80}")
        
        forms = self.FORMS_CATALOG.get(visa_type, {})
        downloaded = []
        skipped = []
        
        for form_code, form_info in forms.items():
            if 'url' not in form_info:
                skipped.append(f"{form_code} - {form_info.get('note', 'Não baixável')}")
                continue
            
            try:
                path = self.get_form(visa_type, form_code)
                if path:
                    downloaded.append(f"{form_code} - {form_info['name']}")
            except Exception as e:
                print(f"   ⚠️ {form_code}: {e}")
        
        print(f"\n✅ Baixados: {len(downloaded)}")
        for item in downloaded:
            print(f"   • {item}")
        
        if skipped:
            print(f"\n⚠️ Pulados: {len(skipped)}")
            for item in skipped:
                print(f"   • {item}")
        
        print(f"{'='*80}")
    
    def list_available_forms(self):
        """Lista todos os formulários disponíveis no repositório"""
        print(f"\n{'='*80}")
        print(f"📋 FORMULÁRIOS DISPONÍVEIS NO REPOSITÓRIO")
        print(f"{'='*80}")
        
        for visa_type, forms in self.FORMS_CATALOG.items():
            print(f"\n{visa_type}:")
            for form_code, form_info in forms.items():
                required = "✓ OBRIGATÓRIO" if form_info.get('required') else "  Opcional"
                downloadable = "📥 Baixável" if 'url' in form_info else "⚠️ Não baixável"
                print(f"   {required} | {downloadable} | {form_code}: {form_info['name']}")
        
        print(f"\n{'='*80}")


if __name__ == "__main__":
    # Teste
    repo = OfficialFormsRepository()
    
    # Listar todos os formulários
    repo.list_available_forms()
    
    # Baixar formulários H-1B
    repo.download_all_forms_for_visa("H-1B")
    
    # Verificar o que foi baixado
    print(f"\n📁 Formulários salvos em: {repo.forms_dir}")
    for f in repo.forms_dir.glob("*.pdf"):
        size = os.path.getsize(f)
        print(f"   • {f.name}: {size:,} bytes ({size/1024:.1f} KB)")
