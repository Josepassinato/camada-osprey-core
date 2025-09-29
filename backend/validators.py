# validators.py
# Snippets: normalizador de datas, parser MRZ (passaporte) com checksum,
# validador de receipt USCIS (I-797) e verificador de SSN "válido".
from __future__ import annotations
import re
from datetime import datetime, date

# -----------------------------
# 1) Normalizador de datas
# -----------------------------
# Tenta múltiplos formatos e retorna ISO (YYYY-MM-DD).
# prefer_day_first=True => "12/05/2025" -> 2025-05-12
def normalize_date(s: str, prefer_day_first: bool = True) -> str | None:
    if not s:
        return None
    s = s.strip()
    # Aceitar "D/S" (I-94)
    if s.upper() in {"D/S", "DS"}:
        return "D/S"

    # Formatos comuns
    patterns_df = ["%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y"]  # day-first
    patterns_mdy = ["%m/%d/%Y", "%m-%d-%Y", "%m.%d.%Y"] # month-first
    patterns_text = ["%b %d, %Y", "%B %d, %Y"]          # "Jan 02, 2025"

    # Heurística: tentar ambos; se prefer_day_first, prioriza DF
    tries = (patterns_df + patterns_mdy + patterns_text) if prefer_day_first \
        else (patterns_mdy + patterns_df + patterns_text)

    for fmt in tries:
        try:
            dt = datetime.strptime(s, fmt).date()
            return dt.isoformat()
        except ValueError:
            continue

    # AAAA-MM-DD já válido?
    try:
        return datetime.strptime(s, "%Y-%m-%d").date().isoformat()
    except ValueError:
        pass
    return None


# -----------------------------
# 2) MRZ (Passaporte TD3) Parser + Checksums
# -----------------------------
# Espera duas linhas TD3 (44 chars cada). Faz parse, valida check digits
# e retorna campos normalizados (numero, DOB, validade, nacionalidade, nome).
_MRZ_WEIGHTS = [7, 3, 1]

def _mrz_char_value(c: str) -> int:
    if c.isdigit():
        return int(c)
    if "A" <= c <= "Z":
        return ord(c) - 55  # A=10 ... Z=35
    if c == "<":
        return 0
    # caracteres inesperados contam como 0
    return 0

def _mrz_checksum(field: str) -> int:
    total = 0
    for i, ch in enumerate(field):
        total += _mrz_char_value(ch) * _MRZ_WEIGHTS[i % 3]
    return total % 10

def parse_mrz_td3(line1: str, line2: str) -> dict | None:
    if len(line1) != 44 or len(line2) != 44:
        return None
    # line1: 0='P', 2-4=issuing country, rest=names
    # line2 fields (positions):
    # 0-8: passport number, 9: check
    # 10-12: nationality (3)
    # 13-18: birth YYMMDD, 19: check
    # 20: sex
    # 21-26: expiry YYMMDD, 27: check
    # 28-42: optional data, 43: composite check
    number = line2[0:9]
    number_c = line2[9]
    nationality = line2[10:13]
    dob = line2[13:19]
    dob_c = line2[19]
    sex = line2[20]
    exp = line2[21:27]
    exp_c = line2[27]
    optional = line2[28:43]
    composite_c = line2[43]

    # Valida checksums
    if _mrz_checksum(number) != (ord(number_c) - ord('0')):
        return None
    if _mrz_checksum(dob) != (ord(dob_c) - ord('0')):
        return None
    if _mrz_checksum(exp) != (ord(exp_c) - ord('0')):
        return None
    # Composite check: concat numero+check + DOB+check + sex + exp+check + optional
    composite_field = number + number_c + nationality + dob + dob_c + sex + exp + exp_c + optional
    if _mrz_checksum(composite_field) != (ord(composite_c) - ord('0')):
        return None

    # Nome (line1): P<ISS<<SURNAME<<GIVEN<NAMES<<<<
    # Extrair após os 5 primeiros chars ("P<XXX")
    raw_names = line1[5:].rstrip("<")
    parts = [p for p in raw_names.split("<<") if p]
    surname = parts[0].replace("<", " ") if len(parts) >= 1 else ""
    given = parts[1].replace("<", " ") if len(parts) >= 2 else ""

    def _yyMMdd_to_iso(yyMMdd: str) -> str | None:
        # Resolve século usando regra simples: YY >= 50 -> 19YY; senão 20YY
        try:
            yy = int(yyMMdd[0:2]); mm = int(yyMMdd[2:4]); dd = int(yyMMdd[4:6])
        except Exception:
            return None
        year = 1900 + yy if yy >= 50 else 2000 + yy
        try:
            return date(year, mm, dd).isoformat()
        except ValueError:
            return None

    return {
        "passport_number": number.replace("<", ""),
        "nationality": nationality,
        "date_of_birth": _yyMMdd_to_iso(dob),
        "expiry_date": _yyMMdd_to_iso(exp),
        "sex": sex,
        "surname": surname.strip(),
        "given_names": given.strip(),
    }


# -----------------------------
# 3) Receipt USCIS (I-797) Validator
# -----------------------------
# Formato: 3 letras + 10 dígitos (ex.: SRC1234567890), com prefixos conhecidos.
_VALID_PREFIXES = {
    "EAC", "WAC", "LIN", "SRC", "MSC", "IOE", "NBC", "NSC", "TSC", "VSC", "YSC"
}

_receipt_rx = re.compile(r"\b([A-Z]{3})(\d{10})\b")

def is_valid_uscis_receipt(s: str) -> bool:
    if not s:
        return False
    m = _receipt_rx.search(s.strip().upper())
    if not m:
        return False
    prefix = m.group(1)
    return prefix in _VALID_PREFIXES


# -----------------------------
# 4) SSN (padrões válidos)
# -----------------------------
# Regras básicas: AAA-GG-SSSS
# - Área AAA != 000, 666, 900-999
# - Grupo GG != 00
# - Série SSSS != 0000
_ssn_rx = re.compile(r"\b(\d{3})-(\d{2})-(\d{4})\b")

def is_plausible_ssn(s: str) -> bool:
    if not s:
        return False
    m = _ssn_rx.search(s.strip())
    if not m:
        return False
    area, group, serial = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if area == 0 or group == 0 or serial == 0:
        return False
    if area == 666 or area >= 900:
        return False
    return True

# -----------------------------
# 5) Validadores adicionais baseados no sistema atual
# -----------------------------

def validate_passport_number_with_nationality(number: str, nationality: str) -> tuple[bool, float, str]:
    """
    Valida número de passaporte baseado na nacionalidade
    Integra com sistema existente
    """
    if not number:
        return False, 0.0, "Passport number is missing"
    
    # Normalize number (remove spaces, uppercase)
    normalized = re.sub(r'[^\w]', '', number.upper())
    
    # Country-specific patterns
    country_patterns = {
        'BR': r'^[A-Z]{2}\d{6}$',  # Brazilian passport
        'BRA': r'^[A-Z]{2}\d{6}$',
        'US': r'^\d{9}$',          # US passport
        'USA': r'^\d{9}$'
    }
    
    # Get country code from nationality
    country_code = None
    if nationality:
        nat_lower = nationality.lower()
        if 'brazil' in nat_lower or 'brasil' in nat_lower:
            country_code = 'BR'
        elif 'united states' in nat_lower or 'american' in nat_lower:
            country_code = 'US'
    
    # Validate against country pattern
    if country_code and country_code in country_patterns:
        pattern = country_patterns[country_code]
        if re.match(pattern, normalized):
            return True, 0.98, "Valid passport number format"
        else:
            return False, 0.3, f"Invalid {country_code} passport number format"
    
    # Generic validation for unknown countries
    if 6 <= len(normalized) <= 12 and normalized.isalnum():
        return True, 0.85, "Valid generic passport number format"
    
    return False, 0.2, "Invalid passport number format"

def validate_date_with_context(date_str: str, field_type: str = 'general') -> tuple[bool, float, str, str]:
    """
    Valida data com contexto específico do campo
    Returns: (is_valid, confidence, normalized_date, error_message)
    """
    if not date_str:
        return False, 0.0, '', 'Date is missing'
    
    # Try to normalize using the robust normalizer
    normalized = normalize_date(date_str.strip())
    
    if not normalized:
        return False, 0.0, '', 'Invalid date format'
    
    if normalized == "D/S":
        return True, 1.0, "D/S", ""  # Valid for I-94
    
    try:
        parsed_date = datetime.strptime(normalized, '%Y-%m-%d')
        current_date = datetime.now()
        
        # Field-specific validation
        if field_type == 'birth_date':
            if parsed_date.year < 1900:
                return False, 0.3, normalized, 'Birth year too old'
            if parsed_date > current_date:
                return False, 0.1, normalized, 'Birth date in future'
            
        elif field_type == 'expiry_date':
            if parsed_date < current_date:
                return False, 0.5, normalized, 'Document has expired'
            
        elif field_type == 'issue_date':
            if parsed_date > current_date:
                return False, 0.3, normalized, 'Issue date in future'
        
        return True, 0.95, normalized, ""
        
    except ValueError:
        return False, 0.0, '', 'Invalid date value'

def extract_and_validate_mrz(document_text: str) -> dict | None:
    """
    Extrai e valida MRZ de texto OCR
    """
    lines = document_text.split('\n')
    
    # Look for two consecutive lines of 44 characters (TD3 format)
    for i in range(len(lines) - 1):
        line1 = lines[i].strip()
        line2 = lines[i + 1].strip()
        
        if len(line1) == 44 and len(line2) == 44:
            # Check if it looks like MRZ (starts with P< for passport)
            if line1.startswith('P<'):
                mrz_data = parse_mrz_td3(line1, line2)
                if mrz_data:
                    return {
                        'mrz_found': True,
                        'mrz_valid': True,
                        'mrz_data': mrz_data,
                        'confidence': 0.99
                    }
    
    return None

# -----------------------------
# 6) Função de integração com sistema atual
# -----------------------------

def enhance_field_validation(field_name: str, field_value: str, document_type: str, context: dict = None) -> dict:
    """
    Aplica validadores específicos baseados no campo e tipo de documento
    Integra com o sistema de alta precisão existente
    """
    context = context or {}
    
    result = {
        'field_name': field_name,
        'original_value': field_value,
        'is_valid': False,
        'confidence': 0.0,
        'normalized_value': field_value,
        'validation_method': 'basic',
        'issues': [],
        'recommendations': []
    }
    
    try:
        # Date fields
        if 'date' in field_name.lower():
            field_type = 'general'
            if 'birth' in field_name.lower():
                field_type = 'birth_date'
            elif 'expiry' in field_name.lower() or 'expire' in field_name.lower():
                field_type = 'expiry_date'
            elif 'issue' in field_name.lower():
                field_type = 'issue_date'
            
            is_valid, confidence, normalized, error = validate_date_with_context(field_value, field_type)
            result.update({
                'is_valid': is_valid,
                'confidence': confidence,
                'normalized_value': normalized,
                'validation_method': 'robust_date_parser',
                'issues': [error] if error else [],
                'recommendations': ['Check date format and readability'] if error else []
            })
        
        # Passport number
        elif field_name.lower() in ['passport_number', 'passport_no']:
            nationality = context.get('nationality', '')
            is_valid, confidence, message = validate_passport_number_with_nationality(field_value, nationality)
            result.update({
                'is_valid': is_valid,
                'confidence': confidence,
                'validation_method': 'nationality_aware_passport',
                'issues': [message] if not is_valid else [],
                'recommendations': ['Verify passport number format'] if not is_valid else []
            })
        
        # USCIS Receipt Number
        elif field_name.lower() in ['receipt_number', 'case_number'] and 'i797' in document_type.lower():
            is_valid = is_valid_uscis_receipt(field_value)
            result.update({
                'is_valid': is_valid,
                'confidence': 0.99 if is_valid else 0.1,
                'validation_method': 'uscis_receipt_validator',
                'normalized_value': field_value.upper().strip(),
                'issues': [] if is_valid else ['Invalid USCIS receipt number format or prefix'],
                'recommendations': [] if is_valid else ['Verify receipt number: 3 letters + 10 digits']
            })
        
        # SSN
        elif field_name.lower() in ['ssn', 'social_security_number']:
            is_valid = is_plausible_ssn(field_value)
            result.update({
                'is_valid': is_valid,
                'confidence': 0.95 if is_valid else 0.1,
                'validation_method': 'ssn_rules_validator',
                'issues': [] if is_valid else ['Invalid SSN format or implausible number'],
                'recommendations': [] if is_valid else ['Check SSN format: XXX-XX-XXXX with valid area/group/serial']
            })
        
        else:
            # Basic validation for other fields
            if field_value and len(field_value.strip()) > 0:
                result.update({
                    'is_valid': True,
                    'confidence': 0.8,
                    'validation_method': 'basic_presence_check'
                })
    
    except Exception as e:
        result.update({
            'is_valid': False,
            'confidence': 0.0,
            'issues': [f'Validation error: {str(e)}'],
            'validation_method': 'error'
        })
    
    return result


# Test functions for verification
def run_validation_tests():
    """Executa testes dos validadores para verificação"""
    
    # Test date normalization
    assert normalize_date("12/05/2025", prefer_day_first=True) == "2025-05-12"
    assert normalize_date("May 12, 2025") == "2025-05-12"
    assert normalize_date("D/S") == "D/S"
    
    # Test receipt validation
    assert is_valid_uscis_receipt("SRC1234567890") is True
    assert is_valid_uscis_receipt("ABC000") is False
    assert is_valid_uscis_receipt("MSC9876543210") is True
    
    # Test SSN validation
    assert is_plausible_ssn("123-45-6789") is True
    assert is_plausible_ssn("000-12-3456") is False
    assert is_plausible_ssn("666-12-3456") is False
    assert is_plausible_ssn("900-12-3456") is False
    
    print("✅ All validation tests passed!")

if __name__ == "__main__":
    run_validation_tests()