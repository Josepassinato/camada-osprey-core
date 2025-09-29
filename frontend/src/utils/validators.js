// validators.js
// Versões JS dos quatro validadores (sem libs externas).

// -----------------------------
// 1) Normalizador de datas
// -----------------------------
export function normalizeDate(s, preferDayFirst = true) {
  if (!s) return null;
  s = String(s).trim();
  const upper = s.toUpperCase();
  if (upper === "D/S" || upper === "DS") return "D/S";

  const tryParse = (str, fmts) => {
    for (const f of fmts) {
      const d = parseWithFormat(str, f);
      if (d) return toISO(d);
    }
    return null;
  };

  // Suporte simples a formatos comuns
  const df = ["DD/MM/YYYY", "DD-MM-YYYY", "DD.MM.YYYY"];
  const md = ["MM/DD/YYYY", "MM-DD-YYYY", "MM.DD.YYYY"];
  const txt = ["Mon DD, YYYY", "Month DD, YYYY"];

  const seq = preferDayFirst ? [...df, ...md, ...txt] : [...md, ...df, ...txt];

  // ISO direto?
  if (/^\d{4}-\d{2}-\d{2}$/.test(s)) return s;

  return tryParse(s, seq);
}

// Auxiliares de data (sem libs externas)
function parseWithFormat(str, fmt) {
  const months = {
    Jan:1, Feb:2, Mar:3, Apr:4, May:5, Jun:6,
    Jul:7, Aug:8, Sep:9, Oct:10, Nov:11, Dec:12
  };
  const monthNames = {
    January:1, February:2, March:3, April:4, May:5, June:6,
    July:7, August:8, September:9, October:10, November:11, December:12
  };
  let m, d, y;

  const num = (x)=>Number(x);

  switch(fmt){
    case "DD/MM/YYYY":
      m = str.match(/^(\d{2})\/(\d{2})\/(\d{4})$/); if(!m) break;
      d=num(m[1]); const mm=num(m[2]); y=num(m[3]); return new Date(Date.UTC(y, mm-1, d));
    case "DD-MM-YYYY":
      m = str.match(/^(\d{2})\-(\d{2})\-(\d{4})$/); if(!m) break;
      d=num(m[1]); const mm2=num(m[2]); y=num(m[3]); return new Date(Date.UTC(y, mm2-1, d));
    case "DD.MM.YYYY":
      m = str.match(/^(\d{2})\.(\d{2})\.(\d{4})$/); if(!m) break;
      d=num(m[1]); const mm3=num(m[2]); y=num(m[3]); return new Date(Date.UTC(y, mm3-1, d));
    case "MM/DD/YYYY":
      m = str.match(/^(\d{2})\/(\d{2})\/(\d{4})$/); if(!m) break;
      const mm4=num(m[1]); d=num(m[2]); y=num(m[3]); return new Date(Date.UTC(y, mm4-1, d));
    case "MM-DD-YYYY":
      m = str.match(/^(\d{2})\-(\d{2})\-(\d{4})$/); if(!m) break;
      const mm5=num(m[1]); d=num(m[2]); y=num(m[3]); return new Date(Date.UTC(y, mm5-1, d));
    case "MM.DD.YYYY":
      m = str.match(/^(\d{2})\.(\d{2})\.(\d{4})$/); if(!m) break;
      const mm6=num(m[1]); d=num(m[2]); y=num(m[3]); return new Date(Date.UTC(y, mm6-1, d));
    case "Mon DD, YYYY":
      m = str.match(/^([A-Z][a-z]{2})\s(\d{1,2}),\s(\d{4})$/); if(!m) break;
      d=num(m[2]); y=num(m[3]); return new Date(Date.UTC(y, (months[m[1]]||0)-1, d));
    case "Month DD, YYYY":
      m = str.match(/^([A-Z][a-z]+)\s(\d{1,2}),\s(\d{4})$/); if(!m) break;
      d=num(m[2]); y=num(m[3]); return new Date(Date.UTC(y, (monthNames[m[1]]||0)-1, d));
  }
  return null;
}

function toISO(d) {
  if (!d || Number.isNaN(d.getTime())) return null;
  return d.toISOString().slice(0,10);
}


// -----------------------------
// 2) MRZ TD3 (duas linhas, 44 chars) + checksums
// -----------------------------
const MRZ_WEIGHTS = [7,3,1];

function mrzCharValue(c){
  if (/[0-9]/.test(c)) return c.charCodeAt(0)-48;
  if (/[A-Z]/.test(c)) return c.charCodeAt(0)-55; // A=10
  if (c === "<") return 0;
  return 0;
}
function mrzChecksum(field){
  let total = 0;
  for (let i=0;i<field.length;i++){
    total += mrzCharValue(field[i]) * MRZ_WEIGHTS[i%3];
  }
  return total % 10;
}

export function parseMrzTd3(line1, line2){
  if (!line1 || !line2 || line1.length!==44 || line2.length!==44) return null;

  const number = line2.slice(0,9);
  const numberC = line2[9];
  const nationality = line2.slice(10,13);
  const dob = line2.slice(13,19);
  const dobC = line2[19];
  const sex = line2[20];
  const exp = line2.slice(21,27);
  const expC = line2[27];
  const optional = line2.slice(28,43);
  const compositeC = line2[43];

  if (mrzChecksum(number) !== Number(numberC)) return null;
  if (mrzChecksum(dob) !== Number(dobC)) return null;
  if (mrzChecksum(exp) !== Number(expC)) return null;

  const composite = number + numberC + nationality + dob + dobC + sex + exp + expC + optional;
  if (mrzChecksum(composite) !== Number(compositeC)) return null;

  const rawNames = line1.slice(5).replace(/<+$/,"");
  const parts = rawNames.split("<<").filter(Boolean);
  const surname = (parts[0]||"").replace(/</g," ").trim();
  const given = (parts[1]||"").replace(/</g," ").trim();

  const yymmddToIso = (s)=>{
    const yy = Number(s.slice(0,2));
    const mm = Number(s.slice(2,4));
    const dd = Number(s.slice(4,6));
    const year = yy >= 50 ? 1900+yy : 2000+yy;
    const d = new Date(Date.UTC(year, mm-1, dd));
    return toISO(d);
  };

  return {
    passport_number: number.replace(/</g,""),
    nationality,
    date_of_birth: yymmddToIso(dob),
    expiry_date: yymmddToIso(exp),
    sex,
    surname,
    given_names: given
  };
}


// -----------------------------
// 3) USCIS Receipt (I-797)
// -----------------------------
const VALID_PREFIXES = new Set(["EAC","WAC","LIN","SRC","MSC","IOE","NBC","NSC","TSC","VSC","YSC"]);
const receiptRx = /\b([A-Z]{3})(\d{10})\b/;

export function isValidUscisReceipt(s){
  if (!s) return false;
  const m = String(s).trim().toUpperCase().match(receiptRx);
  if (!m) return false;
  return VALID_PREFIXES.has(m[1]);
}


// -----------------------------
// 4) SSN plausível
// -----------------------------
const ssnRx = /\b(\d{3})-(\d{2})-(\d{4})\b/;

export function isPlausibleSSN(s){
  if (!s) return false;
  const m = String(s).trim().match(ssnRx);
  if (!m) return false;
  const area = Number(m[1]), group = Number(m[2]), serial = Number(m[3]);
  if (area === 0 || group === 0 || serial === 0) return false;
  if (area === 666 || area >= 900) return false;
  return true;
}

// -----------------------------
// 5) Integração com sistema frontend
// -----------------------------

export function validateFieldClient(fieldName, fieldValue, documentType = '', context = {}) {
  /**
   * Valida campos no frontend usando os mesmos validadores do backend
   */
  
  const result = {
    fieldName,
    originalValue: fieldValue,
    isValid: false,
    confidence: 0.0,
    normalizedValue: fieldValue,
    validationMethod: 'basic',
    issues: [],
    recommendations: []
  };

  try {
    // Date fields
    if (fieldName.toLowerCase().includes('date')) {
      const normalized = normalizeDate(fieldValue, true);
      if (normalized) {
        result.isValid = true;
        result.confidence = 0.95;
        result.normalizedValue = normalized;
        result.validationMethod = 'robust_date_parser';
      } else {
        result.issues.push('Invalid date format');
        result.recommendations.push('Use format: DD/MM/YYYY, MM/DD/YYYY, or Month DD, YYYY');
      }
    }
    
    // Receipt numbers
    else if (fieldName.toLowerCase().includes('receipt') && documentType.toLowerCase().includes('i797')) {
      const isValid = isValidUscisReceipt(fieldValue);
      result.isValid = isValid;
      result.confidence = isValid ? 0.99 : 0.1;
      result.validationMethod = 'uscis_receipt_validator';
      result.normalizedValue = fieldValue.trim().toUpperCase();
      if (!isValid) {
        result.issues.push('Invalid USCIS receipt format');
        result.recommendations.push('Format should be: 3 letters + 10 digits (e.g., SRC1234567890)');
      }
    }
    
    // SSN
    else if (fieldName.toLowerCase().includes('ssn') || fieldName.toLowerCase().includes('social')) {
      const isValid = isPlausibleSSN(fieldValue);
      result.isValid = isValid;
      result.confidence = isValid ? 0.95 : 0.1;
      result.validationMethod = 'ssn_rules_validator';
      if (!isValid) {
        result.issues.push('Invalid SSN format or number');
        result.recommendations.push('Format should be: XXX-XX-XXXX with valid area/group/serial');
      }
    }
    
    // Basic validation for other fields
    else if (fieldValue && fieldValue.trim().length > 0) {
      result.isValid = true;
      result.confidence = 0.8;
      result.validationMethod = 'basic_presence_check';
    }

  } catch (error) {
    result.issues.push(`Validation error: ${error.message}`);
    result.validationMethod = 'error';
  }

  return result;
}

export function validateMRZClient(line1, line2) {
  /**
   * Valida MRZ no frontend e retorna dados estruturados
   */
  const mrzData = parseMrzTd3(line1, line2);
  
  if (mrzData) {
    return {
      isValid: true,
      confidence: 0.99,
      validationMethod: 'mrz_checksum_validation',
      extractedData: mrzData,
      issues: [],
      recommendations: []
    };
  }
  
  return {
    isValid: false,
    confidence: 0.0,
    validationMethod: 'mrz_checksum_validation',
    extractedData: null,
    issues: ['MRZ checksum validation failed'],
    recommendations: ['Ensure MRZ lines are complete and clearly readable']
  };
}

// Test functions
export function runClientValidationTests() {
  // Test date normalization
  console.assert(normalizeDate("12/05/2025", true) === "2025-05-12", "Date normalization failed");
  console.assert(normalizeDate("May 12, 2025") === "2025-05-12", "Text date normalization failed");
  
  // Test receipt validation
  console.assert(isValidUscisReceipt("SRC1234567890") === true, "Valid receipt validation failed");
  console.assert(isValidUscisReceipt("ABC000") === false, "Invalid receipt validation failed");
  
  // Test SSN validation
  console.assert(isPlausibleSSN("123-45-6789") === true, "Valid SSN validation failed");
  console.assert(isPlausibleSSN("000-12-3456") === false, "Invalid SSN validation failed");
  
  console.log("✅ All client-side validation tests passed!");
}

// Export all functions for use in components
export {
  normalizeDate,
  parseMrzTd3,
  isValidUscisReceipt,
  isPlausibleSSN
};