import re
from datetime import datetime, date
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ValidateResult:
    ok: bool
    errors: List[Dict[str, str]]
    missingRequired: List[str]
    suggestions: List[str]
    
    def to_dict(self):
        return {
            "ok": self.ok,
            "errors": self.errors,
            "missingRequired": self.missingRequired,
            "suggestions": self.suggestions
        }

class FormValidator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # ZIP code to state mapping (simplified)
        self.zip_to_state = {
            # Major cities - simplified mapping
            "10": "NY", "11": "NY", "12": "NY",  # NYC area
            "90": "CA", "91": "CA", "92": "CA", "93": "CA", "94": "CA",  # LA/SF area
            "60": "IL", "61": "IL", "62": "IL",  # Chicago area
            "77": "TX", "78": "TX", "79": "TX",  # Houston/Dallas area
            "33": "FL", "32": "FL", "34": "FL"   # Miami/Orlando area
        }
    
    def validate_step(self, step_id: str, form_data: Dict[str, Any]) -> ValidateResult:
        """Validate form data for a specific step"""
        try:
            errors = []
            missing_required = []
            suggestions = []
            
            if step_id == "personal":
                return self._validate_personal_info(form_data)
            elif step_id == "address":
                return self._validate_address_info(form_data)
            elif step_id == "employment":
                return self._validate_employment_info(form_data)
            elif step_id == "family":
                return self._validate_family_info(form_data)
            elif step_id == "travel":
                return self._validate_travel_info(form_data)
            else:
                return self._validate_generic(form_data)
                
        except Exception as e:
            self.logger.error(f"Error validating step {step_id}: {e}")
            return ValidateResult(
                ok=False,
                errors=[{"field": "system", "code": "validation_error", "message": "Erro interno de validação"}],
                missingRequired=[],
                suggestions=["Tente novamente ou contate suporte"]
            )
    
    def _validate_personal_info(self, data: Dict[str, Any]) -> ValidateResult:
        """Validate personal information"""
        errors = []
        missing = []
        suggestions = []
        
        # Required fields
        required_fields = ["firstName", "lastName", "dateOfBirth", "nationality"]
        for field in required_fields:
            if not data.get(field, "").strip():
                missing.append(field)
        
        # Validate names
        first_name = data.get("firstName", "").strip()
        last_name = data.get("lastName", "").strip()
        
        if first_name and not re.match(r"^[A-Za-zÀ-ÿ\s'-]+$", first_name):
            errors.append({
                "field": "firstName",
                "code": "invalid_format",
                "message": "Nome deve conter apenas letras, espaços, hífen e apostrofe"
            })
        
        if last_name and not re.match(r"^[A-Za-zÀ-ÿ\s'-]+$", last_name):
            errors.append({
                "field": "lastName", 
                "code": "invalid_format",
                "message": "Sobrenome deve conter apenas letras, espaços, hífen e apostrofe"
            })
        
        # Validate date of birth
        dob = data.get("dateOfBirth", "")
        if dob:
            try:
                birth_date = datetime.strptime(dob, "%Y-%m-%d").date()
                today = date.today()
                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                
                if birth_date > today:
                    errors.append({
                        "field": "dateOfBirth",
                        "code": "future_date",
                        "message": "Data de nascimento não pode ser no futuro"
                    })
                elif age > 120:
                    errors.append({
                        "field": "dateOfBirth",
                        "code": "invalid_age", 
                        "message": "Data de nascimento parece incorreta (idade muito alta)"
                    })
                elif age < 16:
                    suggestions.append("Menores de 16 anos podem precisar de documentação adicional")
                    
            except ValueError:
                errors.append({
                    "field": "dateOfBirth",
                    "code": "invalid_format",
                    "message": "Data deve estar no formato YYYY-MM-DD"
                })
        
        # Validate nationality
        nationality = data.get("nationality", "").strip()
        if nationality and len(nationality) < 2:
            errors.append({
                "field": "nationality",
                "code": "too_short",
                "message": "Nacionalidade deve ter pelo menos 2 caracteres"
            })
        
        return ValidateResult(
            ok=len(errors) == 0 and len(missing) == 0,
            errors=errors,
            missingRequired=missing,
            suggestions=suggestions
        )
    
    def _validate_address_info(self, data: Dict[str, Any]) -> ValidateResult:
        """Validate address information"""
        errors = []
        missing = []
        suggestions = []
        
        # Required fields
        required_fields = ["currentAddress", "city", "zipCode"]
        for field in required_fields:
            if not data.get(field, "").strip():
                missing.append(field)
        
        # Validate ZIP code
        zip_code = data.get("zipCode", "").strip()
        if zip_code:
            # Remove any non-digits
            clean_zip = re.sub(r'\D', '', zip_code)
            
            if len(clean_zip) == 5:
                # Check if ZIP matches state
                state = data.get("state", "").strip().upper()
                zip_prefix = clean_zip[:2]
                
                expected_state = self.zip_to_state.get(zip_prefix)
                if expected_state and state and expected_state != state:
                    errors.append({
                        "field": "zipCode",
                        "code": "state_mismatch",
                        "message": f"CEP {zip_code} não parece ser de {state}"
                    })
            elif len(clean_zip) == 9:
                # ZIP+4 format is ok
                pass
            else:
                errors.append({
                    "field": "zipCode",
                    "code": "invalid_format", 
                    "message": "CEP americano deve ter 5 dígitos (ex: 12345)"
                })
        
        # Validate phone number
        phone = data.get("phone", "").strip()
        if phone:
            # Remove all non-digits
            clean_phone = re.sub(r'\D', '', phone)
            
            if len(clean_phone) == 10:
                # US domestic format
                pass
            elif len(clean_phone) == 11 and clean_phone.startswith('1'):
                # US format with country code
                pass
            elif len(clean_phone) >= 10:
                # International format
                pass
            else:
                errors.append({
                    "field": "phone",
                    "code": "invalid_format",
                    "message": "Telefone deve ter pelo menos 10 dígitos"
                })
        
        # Validate email
        email = data.get("email", "").strip()
        if email and not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            errors.append({
                "field": "email",
                "code": "invalid_format",
                "message": "Email deve ter formato válido (ex: nome@email.com)"
            })
        
        return ValidateResult(
            ok=len(errors) == 0 and len(missing) == 0,
            errors=errors,
            missingRequired=missing,
            suggestions=suggestions
        )
    
    def _validate_employment_info(self, data: Dict[str, Any]) -> ValidateResult:
        """Validate employment information"""
        errors = []
        missing = []
        suggestions = []
        
        # Check if currently employed
        is_employed = data.get("currentlyEmployed", False)
        
        if is_employed:
            required_fields = ["employerName", "jobTitle", "startDate"]
            for field in required_fields:
                if not data.get(field, "").strip():
                    missing.append(field)
        
        # Validate dates
        start_date_str = data.get("startDate", "")
        end_date_str = data.get("endDate", "")
        
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                if start_date > date.today():
                    errors.append({
                        "field": "startDate",
                        "code": "future_date",
                        "message": "Data de início não pode ser no futuro"
                    })
                    
                # Check for reasonable employment duration
                if end_date_str:
                    try:
                        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
                        if end_date < start_date:
                            errors.append({
                                "field": "endDate",
                                "code": "date_order",
                                "message": "Data de término deve ser após data de início"
                            })
                    except ValueError:
                        errors.append({
                            "field": "endDate",
                            "code": "invalid_format",
                            "message": "Data deve estar no formato YYYY-MM-DD"
                        })
                        
            except ValueError:
                errors.append({
                    "field": "startDate",
                    "code": "invalid_format",
                    "message": "Data deve estar no formato YYYY-MM-DD"
                })
        
        return ValidateResult(
            ok=len(errors) == 0 and len(missing) == 0,
            errors=errors,
            missingRequired=missing,
            suggestions=suggestions
        )
    
    def _validate_family_info(self, data: Dict[str, Any]) -> ValidateResult:
        """Validate family information"""
        errors = []
        missing = []
        suggestions = []
        
        marital_status = data.get("maritalStatus", "")
        
        # If married, spouse info is required
        if marital_status in ["Married", "Casado", "Casada"]:
            spouse_required = ["spouseName", "spouseDateOfBirth"]
            for field in spouse_required:
                if not data.get(field, "").strip():
                    missing.append(field)
        
        # If has children, validate children info
        children_count = data.get("childrenCount", 0)
        if isinstance(children_count, str) and children_count.isdigit():
            children_count = int(children_count)
        
        if children_count and children_count > 0:
            # Should have children details
            children_info = data.get("childrenInfo", [])
            if len(children_info) < children_count:
                suggestions.append(f"Informações de {children_count} filhos são necessárias")
        
        return ValidateResult(
            ok=len(errors) == 0 and len(missing) == 0,
            errors=errors,
            missingRequired=missing,
            suggestions=suggestions
        )
    
    def _validate_travel_info(self, data: Dict[str, Any]) -> ValidateResult:
        """Validate travel history"""
        errors = []
        missing = []
        suggestions = []
        
        trips = data.get("trips", [])
        
        for i, trip in enumerate(trips):
            departure_date = trip.get("departureDate", "")
            return_date = trip.get("returnDate", "")
            
            if departure_date and return_date:
                try:
                    dep_date = datetime.strptime(departure_date, "%Y-%m-%d").date()
                    ret_date = datetime.strptime(return_date, "%Y-%m-%d").date()
                    
                    if ret_date < dep_date:
                        errors.append({
                            "field": f"trip_{i}_returnDate",
                            "code": "date_order",
                            "message": f"Data de retorno da viagem {i+1} deve ser após partida"
                        })
                    
                    # Check if trip is more than 10 years ago
                    years_ago = (date.today() - dep_date).days / 365
                    if years_ago > 10:
                        suggestions.append(f"Viagem {i+1} foi há mais de 10 anos - pode não ser necessária")
                        
                except ValueError:
                    errors.append({
                        "field": f"trip_{i}_dates",
                        "code": "invalid_format",
                        "message": f"Datas da viagem {i+1} devem estar no formato YYYY-MM-DD"
                    })
        
        return ValidateResult(
            ok=len(errors) == 0 and len(missing) == 0,
            errors=errors,
            missingRequired=missing,
            suggestions=suggestions
        )
    
    def _validate_generic(self, data: Dict[str, Any]) -> ValidateResult:
        """Generic validation for unknown step types"""
        errors = []
        missing = []
        suggestions = []
        
        # Basic validation for any form data
        for key, value in data.items():
            if isinstance(value, str) and value.strip() == "":
                # Check if it looks like a required field
                if key.lower() in ["name", "email", "phone", "address", "date"]:
                    missing.append(key)
        
        return ValidateResult(
            ok=len(errors) == 0 and len(missing) == 0,
            errors=errors,
            missingRequired=missing,
            suggestions=suggestions
        )

# Global validator instance
form_validator = FormValidator()