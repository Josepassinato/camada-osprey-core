"""
I-129 Overlay Form Filler
Preenche formulário I-129 usando sistema de overlay com coordenadas fixas
Resolve o problema de PDFs não-editáveis (O-1, H-1B, L-1)
"""

import io
import logging
from typing import Dict, Any, Optional
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter
import fitz  # PyMuPDF

logger = logging.getLogger(__name__)


class I129OverlayFiller:
    """
    Sistema de overlay para I-129
    Usa coordenadas fixas para posicionar texto sobre o PDF
    """
    
    def __init__(self):
        # Coordenadas para campos do I-129 (x, y, página)
        # Baseado no template oficial do USCIS (Edition 04/02/24)
        self.field_coordinates = {
            # PART 1: BASIS FOR CLASSIFICATION
            "classification_type": {
                # Checkboxes para tipo de classificação
                "o1": (52, 704, 0),  # O-1A or O-1B checkbox
                "h1b": (52, 688, 0),  # H-1B checkbox
                "l1a": (52, 672, 0),  # L-1A checkbox
                "l1b": (52, 656, 0),  # L-1B checkbox
            },
            
            # PART 2: INFORMATION ABOUT THE PETITIONER
            "petitioner_name": (120, 620, 0),
            "petitioner_trade_name": (120, 604, 0),
            "petitioner_address_street": (120, 588, 0),
            "petitioner_city": (120, 572, 0),
            "petitioner_state": (350, 572, 0),
            "petitioner_zip": (450, 572, 0),
            "petitioner_country": (120, 556, 0),
            "petitioner_ein": (120, 540, 0),
            "petitioner_phone": (120, 524, 0),
            "petitioner_email": (120, 508, 0),
            
            # PART 3: INFORMATION ABOUT THE BENEFICIARY
            "beneficiary_family_name": (120, 470, 0),
            "beneficiary_given_name": (120, 454, 0),
            "beneficiary_middle_name": (120, 438, 0),
            "beneficiary_other_names": (120, 422, 0),
            "beneficiary_date_of_birth": (120, 406, 0),  # MM/DD/YYYY
            "beneficiary_country_of_birth": (120, 390, 0),
            "beneficiary_country_of_citizenship": (120, 374, 0),
            "beneficiary_gender": (120, 358, 0),  # Male/Female
            
            # Passport Information
            "beneficiary_passport_number": (120, 330, 0),
            "beneficiary_passport_country": (350, 330, 0),
            "beneficiary_passport_expiry": (120, 314, 0),
            
            # US Social Security Number (if any)
            "beneficiary_ssn": (120, 298, 0),
            
            # A-Number (if any)
            "beneficiary_alien_number": (120, 282, 0),
            
            # I-94 Arrival/Departure Record Number
            "beneficiary_i94_number": (120, 266, 0),
            
            # Current Nonimmigrant Status
            "beneficiary_current_status": (120, 250, 0),
            "beneficiary_status_expires": (350, 250, 0),
            
            # US Address
            "beneficiary_us_address_street": (120, 220, 1),  # Page 2
            "beneficiary_us_city": (120, 204, 1),
            "beneficiary_us_state": (350, 204, 1),
            "beneficiary_us_zip": (450, 204, 1),
            
            # Foreign Address
            "beneficiary_foreign_address": (120, 170, 1),
            "beneficiary_foreign_city": (120, 154, 1),
            "beneficiary_foreign_country": (120, 138, 1),
            
            # PART 4: PROCESSING INFORMATION
            "requested_action": {
                "extend_stay": (52, 100, 1),  # Checkbox
                "change_status": (52, 84, 1),  # Checkbox
                "new_employment": (52, 68, 1),  # Checkbox
            },
            
            "requested_start_date": (120, 52, 1),  # MM/DD/YYYY
            "requested_validity_from": (120, 36, 1),
            "requested_validity_to": (350, 36, 1),
            
            # PART 5: ADDITIONAL INFORMATION FOR BENEFICIARY
            "total_workers": (120, 700, 2),  # Page 3
            
            # Employment Information
            "job_title": (120, 670, 2),
            "detailed_description": (120, 640, 2),  # Large text area
            "nontechnical_description": (120, 520, 2),  # Large text area
            
            "job_start_date": (120, 490, 2),
            "job_end_date": (350, 490, 2),
            
            # Wage Information
            "wage_rate_per_hour": (120, 474, 2),
            "wage_rate_per_week": (250, 474, 2),
            "wage_rate_per_year": (380, 474, 2),
            
            # Work Location
            "work_address_street": (120, 440, 2),
            "work_city": (120, 424, 2),
            "work_state": (350, 424, 2),
            "work_zip": (450, 424, 2),
        }
        
        # Font settings
        self.font_name = "Helvetica"
        self.font_size = 9
        self.checkbox_size = 12
    
    def fill_i129(
        self,
        template_path: str,
        output_path: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Preenche I-129 usando overlay
        
        Args:
            template_path: Caminho para PDF template I-129 em branco
            output_path: Caminho para salvar PDF preenchido
            data: Dicionário com dados mapeados
        
        Returns:
            {
                "success": bool,
                "filled_fields": int,
                "total_fields": int,
                "output_path": str
            }
        """
        try:
            logger.info("🖊️ Iniciando preenchimento I-129 com overlay...")
            
            # Abrir PDF template
            template_pdf = fitz.open(template_path)
            filled_fields = 0
            total_fields = len(self.field_coordinates)
            
            # Criar overlay para cada página
            for page_num in range(len(template_pdf)):
                page = template_pdf[page_num]
                
                # Adicionar texto para cada campo nesta página
                for field_name, field_data in self.field_coordinates.items():
                    # Skip se for dict (checkboxes)
                    if isinstance(field_data, dict):
                        # Processar checkboxes
                        for checkbox_name, coords in field_data.items():
                            if coords[2] == page_num:  # Página correta
                                value = data.get(checkbox_name, False)
                                if value:
                                    self._draw_checkbox(page, coords[0], coords[1])
                                    filled_fields += 1
                        continue
                    
                    # Campos de texto normais
                    if field_data[2] != page_num:
                        continue  # Não é página correta
                    
                    x, y = field_data[0], field_data[1]
                    value = data.get(field_name)
                    
                    if value:
                        # Adicionar texto ao PDF
                        self._draw_text(page, x, y, str(value))
                        filled_fields += 1
            
            # Salvar PDF preenchido
            template_pdf.save(output_path)
            template_pdf.close()
            
            fill_rate = (filled_fields / total_fields * 100) if total_fields > 0 else 0
            
            logger.info(f"✅ I-129 preenchido: {filled_fields}/{total_fields} campos ({fill_rate:.1f}%)")
            
            return {
                "success": True,
                "filled_fields": filled_fields,
                "total_fields": total_fields,
                "fill_rate": fill_rate,
                "output_path": output_path,
                "message": f"Formulário I-129 preenchido com sucesso ({fill_rate:.1f}% completo)"
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao preencher I-129: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Erro ao preencher formulário I-129"
            }
    
    def _draw_text(self, page: fitz.Page, x: float, y: float, text: str):
        """Desenha texto na página"""
        try:
            # Ajustar coordenadas (PyMuPDF usa origem no canto superior esquerdo)
            # Converter de pontos PDF para coordenadas PyMuPDF
            page_height = page.rect.height
            adjusted_y = page_height - y
            
            # Inserir texto
            page.insert_text(
                (x, adjusted_y),
                text,
                fontname=self.font_name,
                fontsize=self.font_size,
                color=(0, 0, 0)  # Preto
            )
        except Exception as e:
            logger.warning(f"Erro ao desenhar texto: {str(e)}")
    
    def _draw_checkbox(self, page: fitz.Page, x: float, y: float):
        """Desenha um X no checkbox"""
        try:
            page_height = page.rect.height
            adjusted_y = page_height - y
            
            # Desenhar X
            size = self.checkbox_size
            page.draw_line(
                (x, adjusted_y),
                (x + size, adjusted_y + size),
                color=(0, 0, 0),
                width=2
            )
            page.draw_line(
                (x + size, adjusted_y),
                (x, adjusted_y + size),
                color=(0, 0, 0),
                width=2
            )
        except Exception as e:
            logger.warning(f"Erro ao desenhar checkbox: {str(e)}")
    
    def map_friendly_data_to_i129(self, friendly_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mapeia dados do formulário amigável para campos do I-129
        
        Args:
            friendly_data: Dados do formulário amigável
        
        Returns:
            Dicionário mapeado para I-129
        """
        mapped = {}
        
        # Determinar tipo de classificação
        visa_type = friendly_data.get("visa_type", "").upper()
        if "O-1" in visa_type or "O1" in visa_type:
            mapped["o1"] = True
        elif "H-1B" in visa_type or "H1B" in visa_type:
            mapped["h1b"] = True
        elif "L-1A" in visa_type or "L1A" in visa_type:
            mapped["l1a"] = True
        elif "L-1B" in visa_type or "L1B" in visa_type:
            mapped["l1b"] = True
        
        # Beneficiary (Applicant) Information
        mapped["beneficiary_family_name"] = friendly_data.get("last_name") or friendly_data.get("sobrenome")
        mapped["beneficiary_given_name"] = friendly_data.get("first_name") or friendly_data.get("nome")
        mapped["beneficiary_middle_name"] = friendly_data.get("middle_name") or friendly_data.get("nome_do_meio")
        
        mapped["beneficiary_date_of_birth"] = friendly_data.get("date_of_birth") or friendly_data.get("data_nascimento")
        mapped["beneficiary_country_of_birth"] = friendly_data.get("country_of_birth") or friendly_data.get("pais_nascimento")
        mapped["beneficiary_country_of_citizenship"] = friendly_data.get("citizenship") or friendly_data.get("nacionalidade")
        mapped["beneficiary_gender"] = friendly_data.get("gender") or friendly_data.get("sexo")
        
        # Passport
        mapped["beneficiary_passport_number"] = friendly_data.get("passport_number") or friendly_data.get("numero_passaporte")
        mapped["beneficiary_passport_country"] = friendly_data.get("passport_country") or friendly_data.get("pais_passaporte")
        mapped["beneficiary_passport_expiry"] = friendly_data.get("passport_expiry") or friendly_data.get("validade_passaporte")
        
        # SSN and A-Number (if any)
        mapped["beneficiary_ssn"] = friendly_data.get("ssn")
        mapped["beneficiary_alien_number"] = friendly_data.get("alien_number") or friendly_data.get("numero_a")
        
        # I-94
        mapped["beneficiary_i94_number"] = friendly_data.get("i94_number") or friendly_data.get("numero_i94")
        
        # Current Status
        mapped["beneficiary_current_status"] = friendly_data.get("current_status") or friendly_data.get("status_atual")
        mapped["beneficiary_status_expires"] = friendly_data.get("status_expires") or friendly_data.get("status_expira")
        
        # US Address
        mapped["beneficiary_us_address_street"] = friendly_data.get("us_address") or friendly_data.get("endereco_eua")
        mapped["beneficiary_us_city"] = friendly_data.get("us_city") or friendly_data.get("cidade_eua")
        mapped["beneficiary_us_state"] = friendly_data.get("us_state") or friendly_data.get("estado_eua")
        mapped["beneficiary_us_zip"] = friendly_data.get("us_zip") or friendly_data.get("cep_eua")
        
        # Petitioner (Employer) Information
        mapped["petitioner_name"] = friendly_data.get("employer_name") or friendly_data.get("nome_empregador")
        mapped["petitioner_address_street"] = friendly_data.get("employer_address") or friendly_data.get("endereco_empregador")
        mapped["petitioner_city"] = friendly_data.get("employer_city") or friendly_data.get("cidade_empregador")
        mapped["petitioner_state"] = friendly_data.get("employer_state") or friendly_data.get("estado_empregador")
        mapped["petitioner_zip"] = friendly_data.get("employer_zip") or friendly_data.get("cep_empregador")
        mapped["petitioner_ein"] = friendly_data.get("employer_ein") or friendly_data.get("ein_empregador")
        mapped["petitioner_phone"] = friendly_data.get("employer_phone") or friendly_data.get("telefone_empregador")
        mapped["petitioner_email"] = friendly_data.get("employer_email") or friendly_data.get("email_empregador")
        
        # Employment Information
        mapped["job_title"] = friendly_data.get("job_title") or friendly_data.get("cargo")
        mapped["detailed_description"] = friendly_data.get("job_description") or friendly_data.get("descricao_cargo")
        mapped["job_start_date"] = friendly_data.get("job_start_date") or friendly_data.get("data_inicio_trabalho")
        mapped["job_end_date"] = friendly_data.get("job_end_date") or friendly_data.get("data_fim_trabalho")
        
        # Wage
        mapped["wage_rate_per_year"] = friendly_data.get("salary") or friendly_data.get("salario_anual")
        
        # Work location
        mapped["work_address_street"] = friendly_data.get("work_address") or friendly_data.get("endereco_trabalho")
        mapped["work_city"] = friendly_data.get("work_city") or friendly_data.get("cidade_trabalho")
        mapped["work_state"] = friendly_data.get("work_state") or friendly_data.get("estado_trabalho")
        mapped["work_zip"] = friendly_data.get("work_zip") or friendly_data.get("cep_trabalho")
        
        # Requested action
        action = friendly_data.get("requested_action", "").lower()
        if "extend" in action or "extensão" in action:
            mapped["extend_stay"] = True
        elif "change" in action or "mudança" in action:
            mapped["change_status"] = True
        elif "new" in action or "novo" in action:
            mapped["new_employment"] = True
        
        # Dates
        mapped["requested_start_date"] = friendly_data.get("requested_start_date") or friendly_data.get("data_inicio_pedido")
        mapped["requested_validity_from"] = friendly_data.get("validity_from") or friendly_data.get("validade_de")
        mapped["requested_validity_to"] = friendly_data.get("validity_to") or friendly_data.get("validade_ate")
        
        return mapped


# Global instance
i129_filler = I129OverlayFiller()


# Helper function
def fill_i129_form(template_path: str, output_path: str, friendly_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Helper function para preencher I-129
    
    Args:
        template_path: Caminho do template I-129
        output_path: Onde salvar PDF preenchido
        friendly_data: Dados do formulário amigável
    
    Returns:
        Resultado do preenchimento
    """
    # Mapear dados
    mapped_data = i129_filler.map_friendly_data_to_i129(friendly_data)
    
    # Preencher formulário
    return i129_filler.fill_i129(template_path, output_path, mapped_data)
