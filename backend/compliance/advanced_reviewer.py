"""
Advanced Immigration Reviewer Agent
Este agente atua como um advogado especialista em imigração, revisando pacotes H-1B
para garantir qualidade profissional antes da liberação para o usuário.

Funcionalidades:
1. Lê e analisa cada página do PDF gerado
2. Valida consistência de dados contra o modelo H-1B
3. Detecta conteúdo repetitivo (páginas duplicadas)
4. Identifica texto genérico ou placeholder
5. Verifica qualidade profissional do conteúdo
6. Retorna relatório detalhado com APPROVED/REJECTED
"""

import hashlib
import logging
import os
import re
from datetime import datetime
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    logger.warning("⚠️ pdfplumber não está instalado. Instale com: pip install pdfplumber")


class AdvancedImmigrationReviewerAgent:
    """
    Agente revisor avançado que age como um advogado especialista em imigração
    """
    
    def __init__(self, h1b_data_model=None):
        """
        Inicializa o agente revisor
        
        Args:
            h1b_data_model: Instância do modelo de dados H-1B para validação
        """
        self.h1b_data = h1b_data_model
        self.min_pages = 20  # Mínimo de páginas esperado
        self.max_duplicate_threshold = 0.15  # Máximo 15% de páginas duplicadas
        self.min_content_length_per_page = 200  # Mínimo de caracteres por página
        
        # Palavras/frases que indicam conteúdo genérico ou placeholder
        self.generic_phrases = [
            "lorem ipsum",
            "placeholder",
            "[insert",
            "todo:",
            "xxx",
            "sample text",
            "test data",
            "example text",
            "this is a test",
        ]
    
    def review_package(self, pdf_path: str) -> Dict:
        """
        Revisa um pacote H-1B completo
        
        Args:
            pdf_path: Caminho para o arquivo PDF
            
        Returns:
            Dict com resultado da revisão: {
                "status": "APPROVED" ou "REJECTED",
                "score": 0-100,
                "errors": [...],
                "warnings": [...],
                "details": {...}
            }
        """
        if not PDFPLUMBER_AVAILABLE:
            return {
                "status": "ERROR",
                "score": 0,
                "errors": ["pdfplumber não está instalado"],
                "warnings": [],
                "details": {}
            }
        
        if not os.path.exists(pdf_path):
            return {
                "status": "ERROR",
                "score": 0,
                "errors": [f"Arquivo não encontrado: {pdf_path}"],
                "warnings": [],
                "details": {}
            }
        
        logger.info(f"\n{'='*80}")
        logger.info(f"🔍 INICIANDO REVISÃO AVANÇADA DO PACOTE H-1B")
        logger.info(f"{'='*80}")
        logger.info(f"📄 Arquivo: {pdf_path}")
        
        errors = []
        warnings = []
        details = {}
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                num_pages = len(pdf.pages)
                logger.info(f"📃 Total de páginas: {num_pages}")
                
                # 1. Verificar número mínimo de páginas
                if num_pages < self.min_pages:
                    errors.append(f"Pacote muito curto: {num_pages} páginas (mínimo: {self.min_pages})")
                
                # 2. Extrair texto de todas as páginas
                logger.info(f"\n📖 Extraindo texto de todas as páginas...")
                pages_text = []
                pages_hashes = []
                
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text() or ""
                    pages_text.append(text)
                    
                    # Criar hash do conteúdo para detectar duplicatas
                    text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
                    pages_hashes.append(text_hash)
                    
                    if (i + 1) % 10 == 0:
                        logger.info(f"   ✓ Processadas {i + 1} páginas...")
                
                logger.info(f"   ✅ Todas as {num_pages} páginas processadas")
                
                # 3. Detectar páginas duplicadas (exatas)
                logger.info(f"\n🔎 Detectando páginas duplicadas exatas...")
                duplicate_pages = self._find_duplicate_pages(pages_hashes)
                duplicate_percentage = (len(duplicate_pages) / num_pages) * 100
                
                logger.info(f"   📊 Páginas duplicadas exatas: {len(duplicate_pages)} ({duplicate_percentage:.1f}%)")
                
                if duplicate_percentage > (self.max_duplicate_threshold * 100):
                    errors.append(
                        f"Muitas páginas duplicadas: {len(duplicate_pages)} páginas ({duplicate_percentage:.1f}%). "
                        f"Máximo aceitável: {self.max_duplicate_threshold * 100}%"
                    )
                    # Listar algumas páginas duplicadas
                    for dup_set in list(duplicate_pages.values())[:3]:  # Mostrar até 3 exemplos
                        errors.append(f"   → Páginas idênticas: {', '.join(map(str, sorted(dup_set)))}")
                
                # 3.5. Detectar páginas SIMILARES (conteúdo repetitivo com pequenas variações)
                logger.info(f"\n🔍 Detectando páginas com conteúdo SIMILAR (repetitivo)...")
                similar_pages = self._find_similar_pages(pages_text)
                similar_percentage = (len(similar_pages) / num_pages) * 100
                
                logger.info(f"   📊 Páginas similares/repetitivas: {len(similar_pages)} ({similar_percentage:.1f}%)")
                
                if similar_percentage > (self.max_duplicate_threshold * 100):
                    errors.append(
                        f"❌ CONTEÚDO REPETITIVO DETECTADO: {len(similar_pages)} páginas ({similar_percentage:.1f}%) "
                        f"têm conteúdo muito similar. Máximo aceitável: {self.max_duplicate_threshold * 100}%"
                    )
                    # Listar exemplos de páginas similares
                    for i, (page_nums, similarity) in enumerate(similar_pages[:5]):  # Mostrar até 5 exemplos
                        errors.append(f"   → Páginas {', '.join(map(str, page_nums))} são {similarity:.0f}% similares")
                
                # 4. Detectar texto genérico ou placeholder
                logger.info(f"\n🔍 Detectando texto genérico ou placeholder...")
                generic_pages = self._find_generic_content(pages_text)
                
                if generic_pages:
                    errors.append(f"Texto genérico encontrado em {len(generic_pages)} páginas:")
                    for page_num, phrases in list(generic_pages.items())[:5]:  # Mostrar até 5 exemplos
                        errors.append(f"   → Página {page_num + 1}: {', '.join(phrases)}")
                
                # 5. Verificar conteúdo mínimo por página
                logger.info(f"\n📏 Verificando quantidade de conteúdo por página...")
                thin_pages = self._find_thin_pages(pages_text)
                
                if thin_pages:
                    warnings.append(f"Páginas com pouco conteúdo: {len(thin_pages)}")
                    for page_num, char_count in list(thin_pages.items())[:5]:
                        warnings.append(f"   → Página {page_num + 1}: apenas {char_count} caracteres")
                
                # 6. Validar consistência de dados (se modelo fornecido)
                logger.info(f"\n✅ Validando consistência de dados...")
                if self.h1b_data:
                    consistency_errors = self._validate_data_consistency(pages_text)
                    if consistency_errors:
                        errors.extend(consistency_errors)
                    else:
                        logger.info(f"   ✅ Todos os dados estão consistentes")
                else:
                    warnings.append("Modelo de dados não fornecido - validação de consistência pulada")
                
                # 7. Verificar seções obrigatórias
                logger.info(f"\n📋 Verificando seções obrigatórias...")
                missing_sections = self._check_required_sections(pages_text)
                if missing_sections:
                    errors.append(f"Seções obrigatórias faltando: {', '.join(missing_sections)}")
                
                # Preparar detalhes
                details = {
                    "total_pages": num_pages,
                    "duplicate_pages": len(duplicate_pages),
                    "duplicate_percentage": round(duplicate_percentage, 2),
                    "generic_content_pages": len(generic_pages),
                    "thin_pages": len(thin_pages),
                    "file_size_mb": round(os.path.getsize(pdf_path) / (1024 * 1024), 2),
                    "review_date": datetime.now().isoformat(),
                }
                
        except Exception as e:
            errors.append(f"Erro ao processar PDF: {str(e)}")
            import traceback
            errors.append(f"Traceback: {traceback.format_exc()}")
        
        # Calcular score
        score = self._calculate_score(errors, warnings, details)
        
        # Determinar status
        status = "APPROVED" if score >= 75 and len(errors) == 0 else "REJECTED"
        
        # Relatório final
        logger.info(f"\n{'='*80}")
        logger.info(f"📊 RESULTADO DA REVISÃO")
        logger.info(f"{'='*80}")
        logger.info(f"Status: {status}")
        logger.info(f"Score: {score}/100")
        logger.error(f"Erros: {len(errors)}")
        logger.warning(f"Avisos: {len(warnings)}")
        
        if errors:
            logger.error(f"\n❌ ERROS ENCONTRADOS:")
            for error in errors:
                logger.error(f"  • {error}")
        
        if warnings:
            logger.warning(f"\n⚠️ AVISOS:")
            for warning in warnings:
                logger.warning(f"  • {warning}")
        
        logger.info(f"{'='*80}\n")
        
        return {
            "status": status,
            "score": score,
            "errors": errors,
            "warnings": warnings,
            "details": details,
        }
    
    def _find_duplicate_pages(self, hashes: List[str]) -> Dict[str, List[int]]:
        """Encontra páginas com conteúdo idêntico"""
        hash_to_pages = {}
        for i, h in enumerate(hashes):
            if h not in hash_to_pages:
                hash_to_pages[h] = []
            hash_to_pages[h].append(i + 1)  # Página 1-indexed
        
        # Retornar apenas hashes que aparecem mais de uma vez
        return {h: pages for h, pages in hash_to_pages.items() if len(pages) > 1}
    
    def _find_similar_pages(self, pages_text: List[str], similarity_threshold: float = 0.85) -> List[Tuple[List[int], float]]:
        """
        Encontra páginas com conteúdo muito similar (mas não idêntico)
        Útil para detectar páginas que são quase iguais com pequenas variações
        
        Returns:
            Lista de tuplas: (lista de páginas similares, % de similaridade)
        """
        similar_groups = []
        checked_pairs = set()
        
        # Normalizar textos: remover números de página e espaços extras
        normalized_texts = []
        for text in pages_text:
            # Remover padrões comuns de numeração de página
            normalized = re.sub(r'Page \d+', '', text)
            normalized = re.sub(r'- Page \d+', '', normalized)
            normalized = re.sub(r'\d+\s+of\s+\d+', '', normalized)
            # Remover espaços múltiplos
            normalized = re.sub(r'\s+', ' ', normalized).strip()
            normalized_texts.append(normalized)
        
        # Comparar cada par de páginas
        for i in range(len(normalized_texts)):
            for j in range(i + 1, len(normalized_texts)):
                pair_key = (i, j)
                if pair_key in checked_pairs:
                    continue
                
                checked_pairs.add(pair_key)
                
                # Calcular similaridade usando Jaccard similarity (words)
                text1 = normalized_texts[i]
                text2 = normalized_texts[j]
                
                if len(text1) < 50 or len(text2) < 50:
                    # Ignorar páginas muito curtas
                    continue
                
                # Dividir em palavras
                words1 = set(text1.lower().split())
                words2 = set(text2.lower().split())
                
                if not words1 or not words2:
                    continue
                
                # Calcular Jaccard similarity
                intersection = len(words1 & words2)
                union = len(words1 | words2)
                similarity = intersection / union if union > 0 else 0
                
                # Se similaridade for alta, marcar como problema
                if similarity >= similarity_threshold:
                    similar_groups.append(([i + 1, j + 1], similarity * 100))
        
        return similar_groups
    
    def _find_generic_content(self, pages_text: List[str]) -> Dict[int, List[str]]:
        """Encontra páginas com texto genérico ou placeholder"""
        generic_pages = {}
        
        for i, text in enumerate(pages_text):
            text_lower = text.lower()
            found_phrases = []
            
            for phrase in self.generic_phrases:
                if phrase in text_lower:
                    found_phrases.append(phrase)
            
            if found_phrases:
                generic_pages[i] = found_phrases
        
        return generic_pages
    
    def _find_thin_pages(self, pages_text: List[str]) -> Dict[int, int]:
        """Encontra páginas com muito pouco conteúdo"""
        thin_pages = {}
        
        for i, text in enumerate(pages_text):
            # Remover espaços em branco excessivos
            clean_text = re.sub(r'\s+', ' ', text).strip()
            char_count = len(clean_text)
            
            if char_count < self.min_content_length_per_page:
                thin_pages[i] = char_count
        
        return thin_pages
    
    def _validate_data_consistency(self, pages_text: List[str]) -> List[str]:
        """Valida que os dados no PDF batem com o modelo"""
        if not self.h1b_data:
            return []
        
        errors = []
        full_text = " ".join(pages_text)
        
        # Validações críticas
        critical_data = {
            "Nome completo": self.h1b_data.beneficiary['full_name'],
            "Número de engenheiros liderados": str(self.h1b_data.beneficiary['job1_team_size']),
            "Budget gerenciado": self.h1b_data.beneficiary['job1_budget_managed'],
            "Salário anual": self.h1b_data.position['salary_annual'],
            "Anos de experiência": str(self.h1b_data.beneficiary['total_experience_years']),
            "Certificação LCA": self.h1b_data.lca['certification_number'],
        }
        
        for field_name, expected_value in critical_data.items():
            # Contar quantas vezes o valor aparece no documento
            count = full_text.count(expected_value)
            
            if count == 0:
                errors.append(f"Dado crítico ausente: {field_name} = {expected_value}")
            elif count < 3:
                # Valores críticos devem aparecer múltiplas vezes em um documento completo
                errors.append(f"Dado crítico aparece poucas vezes ({count}x): {field_name} = {expected_value}")
        
        # Verificar se há referências ao time size liderado
        # O número correto é job1_team_size (Technical Lead role)
        # Outros números podem aparecer para outras posições (job2, job3) e isso é ESPERADO
        expected_team_size = str(self.h1b_data.beneficiary['job1_team_size'])
        led_pattern = r'(led|manage[sd]?|mentor[ed]*|supervise[sd]*|oversee[s]*)\s+.*?(\d+)\s+engineers?'
        led_matches = re.findall(led_pattern, full_text, re.IGNORECASE)
        
        if led_matches:
            # Extrair apenas os números quando o contexto é sobre LIDERANÇA
            team_sizes_led = [match[1] for match in led_matches]
            unique_led_counts = set(team_sizes_led)
            
            # Verificar se o número correto aparece
            if expected_team_size not in unique_led_counts:
                errors.append(
                    f"INCONSISTÊNCIA: Número de engenheiros LIDERADOS não encontrado. "
                    f"Esperado: {expected_team_size}, encontrado em contexto de liderança: {', '.join(unique_led_counts)}"
                )
            elif len(unique_led_counts) > 1:
                # Há múltiplos números em contexto de liderança
                wrong_numbers = unique_led_counts - {expected_team_size}
                errors.append(
                    f"AVISO: Múltiplos tamanhos de equipe mencionados em contexto de liderança. "
                    f"Esperado: {expected_team_size}, também encontrado: {', '.join(wrong_numbers)}"
                )
        
        return errors
    
    def _check_required_sections(self, pages_text: List[str]) -> List[str]:
        """Verifica se todas as seções obrigatórias estão presentes"""
        full_text = " ".join(pages_text)
        
        required_sections = [
            "COVER LETTER",
            "FORM I-129",
            "LABOR CONDITION APPLICATION",
            "SUPPORT LETTER",
            "JOB DESCRIPTION",
            "RESUME",
            "EDUCATIONAL CREDENTIALS",
            "PASSPORT",
        ]
        
        missing = []
        for section in required_sections:
            if section not in full_text.upper():
                missing.append(section)
        
        return missing
    
    def _calculate_score(self, errors: List[str], warnings: List[str], details: Dict) -> int:
        """Calcula score de 0-100 baseado nos problemas encontrados"""
        score = 100
        
        # Penalidades por erros
        score -= len(errors) * 15  # -15 pontos por erro
        
        # Penalidades por avisos
        score -= len(warnings) * 3  # -3 pontos por aviso
        
        # Penalidade por duplicação excessiva
        if details.get('duplicate_percentage', 0) > 15:
            score -= (details['duplicate_percentage'] - 15) * 2
        
        # Garantir que score esteja entre 0-100
        return max(0, min(100, score))


def test_reviewer():
    """Função de teste para o revisor"""
    logger.info("🧪 Testando Advanced Immigration Reviewer Agent...")
    
    # Importar modelo de dados
    try:
        import sys
        sys.path.insert(0, '/app')
        from h1b_data_model import h1b_data
        logger.info("✅ Modelo de dados H-1B carregado")
    except ImportError as e:
        logger.warning(f"⚠️ Modelo de dados não encontrado: {e}")
        h1b_data = None
    
    # Criar instância do revisor
    reviewer = AdvancedImmigrationReviewerAgent(h1b_data)
    
    # Procurar PDF para testar
    test_files = [
        "/app/CONSISTENT_H1B_PACKAGE_FERNANDA_SANTOS.pdf",
        "/app/H1B_PACKAGE_FERNANDA_SANTOS.pdf",
    ]
    
    for test_file in test_files:
        if os.path.exists(test_file):
            logger.info(f"\n✅ Encontrado arquivo para teste: {test_file}")
            result = reviewer.review_package(test_file)
            return result
    
    logger.warning("\n⚠️ Nenhum arquivo PDF encontrado para teste")
    return None


if __name__ == "__main__":
    test_reviewer()
