#!/usr/bin/env python3
"""
🎯 TESTE END-TO-END COMPLETO - USERsimulator-DISCIPLINA SESSION
METODOLOGIA DE TESTE: Teste rigoroso e estruturado em 10 ETAPAS sequenciais

Testing I-539 Extension of Stay complete flow with detailed validation
Focus: P0 Bug verification - PDF field filling after pypdf migration
"""

import requests
import json
import time
import os
import base64
import hashlib
from pathlib import Path
from datetime import datetime
import pypdf
import io

# Get backend URL from frontend .env
BACKEND_URL = "https://formfiller-26.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def disciplina_i539_complete_e2e_test():
    """
    🎯 TESTE END-TO-END COMPLETO - USERsimulator-DISCIPLINA SESSION
    
    METODOLOGIA DE TESTE: Teste rigoroso e estruturado em 10 ETAPAS sequenciais
    
    ETAPAS:
    1. CRIAÇÃO DE CASO I-539 (Extension of Stay)
    2. SUBMISSÃO DO FORMULÁRIO AMIGÁVEL EM PORTUGUÊS
    3. VERIFICAÇÃO DE PERSISTÊNCIA DOS DADOS
    4. GERAÇÃO DO PDF OFICIAL I-539 (⭐ VALIDAÇÃO BUG P0)
    5. DOWNLOAD DO PDF
    6. ⭐ VALIDAÇÃO CRÍTICA DO BUG P0 - CAMPOS PREENCHIDOS NO PDF
    7. VERIFICAÇÃO DE INTEGRIDADE DO ARQUIVO
    8. TESTE DE EXTRAÇÃO DE TEXTO
    9. COMPARAÇÃO: DADOS ENVIADOS vs DADOS NO PDF
    10. VERIFICAÇÃO FINAL DO FLUXO E2E
    
    SUCCESS CRITERIA:
    - Taxa de sucesso geral >= 8/10 etapas
    - BUG P0 CORRIGIDO: >= 7 de 10 campos preenchidos no PDF
    - Tempo total de execução < 30 segundos
    - Sem erros 500 durante todo o fluxo
    """
    
    print("🎯 TESTE END-TO-END COMPLETO - USERsimulator-DISCIPLINA SESSION")
    print("📋 METODOLOGIA DE TESTE: Rigoroso e estruturado em 10 ETAPAS sequenciais")
    print("🎯 FOCUS: Validação completa do sistema I-539 Extension of Stay")
    print("⭐ CRÍTICO: Verificação do Bug P0 - PDF field filling")
    print("=" * 100)
    
    # Initialize results structure
    results = {
        "etapa1_criacao_caso": {},
        "etapa2_formulario_amigavel": {},
        "etapa3_persistencia_dados": {},
        "etapa4_geracao_pdf": {},
        "etapa5_download_pdf": {},
        "etapa6_validacao_bug_p0": {},
        "etapa7_integridade_arquivo": {},
        "etapa8_extracao_texto": {},
        "etapa9_comparacao_dados": {},
        "etapa10_verificacao_final": {},
        "summary": {}
    }
    
    start_time = time.time()
    case_id = None
    
    # ETAPA 1: CRIAÇÃO DE CASO I-539 (Extension of Stay)
    print("\n" + "="*80)
    print("📋 ETAPA 1: CRIAÇÃO DE CASO I-539 (Extension of Stay)")
    print("="*80)
    
    try:
        print("📝 Request: POST /api/auto-application/start")
        print("📤 Body: {\"visa_type\": \"I-539\", \"form_code\": \"I-539\"}")
        
        response = requests.post(
            f"{API_BASE}/auto-application/start",
            json={"visa_type": "I-539", "form_code": "I-539"},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        # Validações Obrigatórias
        validacoes_etapa1 = {
            "status_code_200_ou_201": response.status_code in [200, 201],
            "response_contem_case_id": False,
            "case_id_formato_osp": False,
            "caso_persistido_mongodb": False
        }
        
        if response.status_code in [200, 201]:
            case_data = response.json()
            case_info = case_data.get("case", {})
            case_id = case_info.get("case_id")
            
            if case_id:
                validacoes_etapa1["response_contem_case_id"] = True
                validacoes_etapa1["case_id_formato_osp"] = case_id.startswith("OSP-") and len(case_id) == 12
                print(f"✅ Case ID gerado: {case_id}")
                print(f"✅ Timestamp de criação: {datetime.utcnow().isoformat()}")
                print(f"✅ Estrutura da resposta: {json.dumps(case_data, indent=2)}")
                
                # Verify case persisted in MongoDB
                verify_response = requests.get(
                    f"{API_BASE}/auto-application/case/{case_id}",
                    timeout=30
                )
                if verify_response.status_code == 200:
                    verify_data = verify_response.json()
                    case_info = verify_data.get("case", {})
                    if (case_info.get("form_code") == "I-539" and 
                        case_info.get("progress_percentage") == 0):
                        validacoes_etapa1["caso_persistido_mongodb"] = True
                        print(f"✅ Caso persistido no MongoDB com form_code=I-539, progress=0%")
        
        print(f"\n🎯 VALIDAÇÕES OBRIGATÓRIAS ETAPA 1:")
        for validacao, passou in validacoes_etapa1.items():
            status = "✅" if passou else "❌"
            print(f"  {status} {validacao}: {passou}")
        
        etapa1_sucesso = all(validacoes_etapa1.values())
        results["etapa1_criacao_caso"] = {
            "success": etapa1_sucesso,
            "case_id": case_id,
            "validacoes": validacoes_etapa1,
            "status_code": response.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if not etapa1_sucesso:
            print("❌ ETAPA 1 FALHOU - Interrompendo teste")
            return results
            
    except Exception as e:
        print(f"❌ Exception na ETAPA 1: {str(e)}")
        results["etapa1_criacao_caso"] = {"success": False, "exception": str(e)}
        return results
    
    # ETAPA 2: SUBMISSÃO DO FORMULÁRIO AMIGÁVEL EM PORTUGUÊS
    print("\n" + "="*80)
    print("📋 ETAPA 2: SUBMISSÃO DO FORMULÁRIO AMIGÁVEL EM PORTUGUÊS")
    print("="*80)
    
    # Dados EXATOS da review request
    formulario_dados = {
        "friendly_form_data": {
            "nome_completo": "Roberto Carlos Mendes Silva",
            "data_nascimento": "1988-11-25",
            "endereco_eua": "2580 Ocean Drive Apt 305",
            "cidade_eua": "Orlando",
            "estado_eua": "FL",
            "cep_eua": "32801",
            "email": "roberto.mendes@testqa.com",
            "telefone": "+1-407-555-1234",
            "numero_passaporte": "BR111222333",
            "pais_nascimento": "Brazil",
            "status_atual": "B-2",
            "status_solicitado": "B-2 Extension",
            "data_entrada_eua": "2024-06-10",
            "numero_i94": "12345678901"
        },
        "basic_data": {}
    }
    
    try:
        print(f"📝 Request: POST /api/case/{case_id}/friendly-form")
        print(f"📤 Body: {json.dumps(formulario_dados, indent=2, ensure_ascii=False)}")
        
        response = requests.post(
            f"{API_BASE}/case/{case_id}/friendly-form",
            json=formulario_dados,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        # Validações Obrigatórias
        validacoes_etapa2 = {
            "status_code_200": response.status_code == 200,
            "response_success_true": False,
            "completion_percentage_90_plus": False,
            "validation_status_approved": False,
            "nenhum_issue_critico": False
        }
        
        if response.status_code == 200:
            form_result = response.json()
            validacoes_etapa2["response_success_true"] = form_result.get("success", False)
            
            completion_pct = form_result.get("completion_percentage", 0)
            validacoes_etapa2["completion_percentage_90_plus"] = completion_pct >= 90
            
            validation_status = form_result.get("validation_status", "")
            validacoes_etapa2["validation_status_approved"] = validation_status in ["approved", "needs_review"]
            
            issues = form_result.get("validation_issues", [])
            critical_issues = [issue for issue in issues if issue.get("severity") == "critical"]
            validacoes_etapa2["nenhum_issue_critico"] = len(critical_issues) == 0
            
            print(f"✅ Completion percentage: {completion_pct}%")
            print(f"✅ Validation status: {validation_status}")
            print(f"✅ Issues encontrados: {len(issues)} (críticos: {len(critical_issues)})")
        
        print(f"\n🎯 VALIDAÇÕES OBRIGATÓRIAS ETAPA 2:")
        for validacao, passou in validacoes_etapa2.items():
            status = "✅" if passou else "❌"
            print(f"  {status} {validacao}: {passou}")
        
        etapa2_sucesso = all(validacoes_etapa2.values())
        results["etapa2_formulario_amigavel"] = {
            "success": etapa2_sucesso,
            "validacoes": validacoes_etapa2,
            "status_code": response.status_code,
            "response": form_result if response.status_code == 200 else None
        }
        
        if not etapa2_sucesso:
            print("❌ ETAPA 2 FALHOU - Continuando teste para diagnóstico")
            
    except Exception as e:
        print(f"❌ Exception na ETAPA 2: {str(e)}")
        results["etapa2_formulario_amigavel"] = {"success": False, "exception": str(e)}
    
    # ETAPA 3: VERIFICAÇÃO DE PERSISTÊNCIA DOS DADOS
    print("\n" + "="*80)
    print("📋 ETAPA 3: VERIFICAÇÃO DE PERSISTÊNCIA DOS DADOS")
    print("="*80)
    
    try:
        print(f"📝 Request: GET /api/auto-application/case/{case_id}")
        
        response = requests.get(
            f"{API_BASE}/auto-application/case/{case_id}",
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        # Validações Críticas de Dados (13 campos obrigatórios)
        validacoes_etapa3 = {
            "nome_completo_correto": False,
            "endereco_eua_correto": False,
            "cidade_eua_correto": False,
            "estado_eua_correto": False,
            "cep_eua_correto": False,
            "email_correto": False,
            "telefone_correto": False,
            "numero_passaporte_correto": False,
            "pais_nascimento_correto": False,
            "status_atual_correto": False,
            "status_solicitado_correto": False,
            "data_entrada_eua_correto": False,
            "numero_i94_correto": False
        }
        
        if response.status_code == 200:
            case_data = response.json()
            case_info = case_data.get("case", {})
            simplified_responses = case_info.get("simplified_form_responses", {})
            
            print(f"📄 Simplified Form Responses: {json.dumps(simplified_responses, indent=2, ensure_ascii=False)}")
            
            # Verificar cada campo individualmente
            expected_data = formulario_dados["friendly_form_data"]
            
            validacoes_etapa3["nome_completo_correto"] = simplified_responses.get("nome_completo") == expected_data["nome_completo"]
            validacoes_etapa3["endereco_eua_correto"] = simplified_responses.get("endereco_eua") == expected_data["endereco_eua"]
            validacoes_etapa3["cidade_eua_correto"] = simplified_responses.get("cidade_eua") == expected_data["cidade_eua"]
            validacoes_etapa3["estado_eua_correto"] = simplified_responses.get("estado_eua") == expected_data["estado_eua"]
            validacoes_etapa3["cep_eua_correto"] = simplified_responses.get("cep_eua") == expected_data["cep_eua"]
            validacoes_etapa3["email_correto"] = simplified_responses.get("email") == expected_data["email"]
            validacoes_etapa3["telefone_correto"] = simplified_responses.get("telefone") == expected_data["telefone"]
            validacoes_etapa3["numero_passaporte_correto"] = simplified_responses.get("numero_passaporte") == expected_data["numero_passaporte"]
            validacoes_etapa3["pais_nascimento_correto"] = simplified_responses.get("pais_nascimento") == expected_data["pais_nascimento"]
            validacoes_etapa3["status_atual_correto"] = simplified_responses.get("status_atual") == expected_data["status_atual"]
            validacoes_etapa3["status_solicitado_correto"] = simplified_responses.get("status_solicitado") == expected_data["status_solicitado"]
            validacoes_etapa3["data_entrada_eua_correto"] = simplified_responses.get("data_entrada_eua") == expected_data["data_entrada_eua"]
            validacoes_etapa3["numero_i94_correto"] = simplified_responses.get("numero_i94") == expected_data["numero_i94"]
        
        print(f"\n🎯 VALIDAÇÕES CRÍTICAS DE DADOS (13/13 campos):")
        campos_corretos = 0
        for validacao, passou in validacoes_etapa3.items():
            status = "✅" if passou else "❌"
            print(f"  {status} {validacao}: {passou}")
            if passou:
                campos_corretos += 1
        
        print(f"\n📊 VERIFICAÇÃO INDIVIDUAL: {campos_corretos}/13 campos corretos")
        
        etapa3_sucesso = campos_corretos >= 12  # Permitir 1 campo com problema
        results["etapa3_persistencia_dados"] = {
            "success": etapa3_sucesso,
            "validacoes": validacoes_etapa3,
            "campos_corretos": campos_corretos,
            "total_campos": 13,
            "status_code": response.status_code,
            "simplified_responses": simplified_responses if response.status_code == 200 else None
        }
        
    except Exception as e:
        print(f"❌ Exception na ETAPA 3: {str(e)}")
        results["etapa3_persistencia_dados"] = {"success": False, "exception": str(e)}
    
    # ETAPA 4: GERAÇÃO DO PDF OFICIAL I-539 (⭐ VALIDAÇÃO BUG P0)
    print("\n" + "="*80)
    print("📋 ETAPA 4: GERAÇÃO DO PDF OFICIAL I-539 (⭐ VALIDAÇÃO BUG P0)")
    print("="*80)
    
    try:
        print(f"📝 Request: POST /api/case/{case_id}/generate-form")
        
        response = requests.post(
            f"{API_BASE}/case/{case_id}/generate-form",
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        # Validações de Resposta
        validacoes_etapa4 = {
            "status_code_200": response.status_code == 200,
            "response_success_true": False,
            "filename_formato_correto": False,
            "file_size_adequado": False,
            "form_type_i539": False,
            "download_url_presente": False
        }
        
        if response.status_code == 200:
            pdf_result = response.json()
            validacoes_etapa4["response_success_true"] = pdf_result.get("success", False)
            
            filename = pdf_result.get("filename", "")
            validacoes_etapa4["filename_formato_correto"] = filename.startswith("I-539_OSP-") and filename.endswith(".pdf")
            
            file_size = pdf_result.get("file_size", 0)
            validacoes_etapa4["file_size_adequado"] = file_size > 300000  # >300KB
            
            validacoes_etapa4["form_type_i539"] = pdf_result.get("form_type") == "I-539"
            validacoes_etapa4["download_url_presente"] = pdf_result.get("download_url") is not None
            
            print(f"✅ Filename gerado: {filename}")
            print(f"✅ File size: {file_size} bytes")
            print(f"✅ Timestamp de geração: {datetime.utcnow().isoformat()}")
        
        print(f"\n🎯 VALIDAÇÕES DE RESPOSTA ETAPA 4:")
        for validacao, passou in validacoes_etapa4.items():
            status = "✅" if passou else "❌"
            print(f"  {status} {validacao}: {passou}")
        
        etapa4_sucesso = all(validacoes_etapa4.values())
        results["etapa4_geracao_pdf"] = {
            "success": etapa4_sucesso,
            "validacoes": validacoes_etapa4,
            "status_code": response.status_code,
            "pdf_result": pdf_result if response.status_code == 200 else None
        }
        
        if not etapa4_sucesso:
            print("❌ ETAPA 4 FALHOU - PDF generation failed")
            
    except Exception as e:
        print(f"❌ Exception na ETAPA 4: {str(e)}")
        results["etapa4_geracao_pdf"] = {"success": False, "exception": str(e)}
    
    # ETAPA 5: DOWNLOAD DO PDF
    print("\n" + "="*80)
    print("📋 ETAPA 5: DOWNLOAD DO PDF")
    print("="*80)
    
    pdf_path = None
    try:
        print(f"📝 Request: GET /api/case/{case_id}/download-form")
        
        response = requests.get(
            f"{API_BASE}/case/{case_id}/download-form",
            timeout=60
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"📏 Content-Length: {len(response.content)} bytes")
        
        # Validações
        validacoes_etapa5 = {
            "status_code_200": response.status_code == 200,
            "content_type_pdf": response.headers.get('Content-Type') == 'application/pdf',
            "content_length_adequado": len(response.content) > 300000,
            "arquivo_pdf_valido": False
        }
        
        if response.status_code == 200:
            # Salvar PDF
            pdf_path = f"/tmp/test_disciplina_i539_{case_id}.pdf"
            with open(pdf_path, 'wb') as f:
                f.write(response.content)
            
            # Verificar se é PDF válido
            try:
                with open(pdf_path, 'rb') as f:
                    pdf_reader = pypdf.PdfReader(f)
                    validacoes_etapa5["arquivo_pdf_valido"] = len(pdf_reader.pages) > 0
                    print(f"✅ PDF válido com {len(pdf_reader.pages)} páginas")
            except Exception:
                validacoes_etapa5["arquivo_pdf_valido"] = False
            
            # Calcular hash MD5 para integridade
            with open(pdf_path, 'rb') as f:
                pdf_hash = hashlib.md5(f.read()).hexdigest()
            
            print(f"💾 PDF salvo em: {pdf_path}")
            print(f"📊 Tamanho real: {len(response.content)} bytes")
            print(f"🔐 Hash MD5: {pdf_hash}")
        
        print(f"\n🎯 VALIDAÇÕES ETAPA 5:")
        for validacao, passou in validacoes_etapa5.items():
            status = "✅" if passou else "❌"
            print(f"  {status} {validacao}: {passou}")
        
        etapa5_sucesso = all(validacoes_etapa5.values())
        results["etapa5_download_pdf"] = {
            "success": etapa5_sucesso,
            "validacoes": validacoes_etapa5,
            "status_code": response.status_code,
            "file_size": len(response.content),
            "pdf_path": pdf_path,
            "pdf_hash": pdf_hash if response.status_code == 200 else None
        }
        
    except Exception as e:
        print(f"❌ Exception na ETAPA 5: {str(e)}")
        results["etapa5_download_pdf"] = {"success": False, "exception": str(e)}
    
    # ETAPA 6: ⭐ VALIDAÇÃO CRÍTICA DO BUG P0 - CAMPOS PREENCHIDOS NO PDF
    print("\n" + "="*80)
    print("📋 ETAPA 6: ⭐ VALIDAÇÃO CRÍTICA DO BUG P0 - CAMPOS PREENCHIDOS NO PDF")
    print("="*80)
    
    if not pdf_path or not os.path.exists(pdf_path):
        print("❌ PDF não disponível para análise")
        results["etapa6_validacao_bug_p0"] = {"success": False, "error": "PDF not available"}
    else:
        try:
            print(f"🔍 Analisando PDF: {pdf_path}")
            
            # Usar pypdf para extrair campos do formulário
            with open(pdf_path, 'rb') as pdf_file:
                pdf_reader = pypdf.PdfReader(pdf_file)
                
                print(f"📄 PDF tem {len(pdf_reader.pages)} páginas")
                
                # Extrair campos do formulário
                form_fields = {}
                
                # Método 1: get_form_text_fields()
                try:
                    text_fields = pdf_reader.get_form_text_fields()
                    if text_fields and isinstance(text_fields, dict):
                        form_fields.update(text_fields)
                        print(f"📊 Campos de texto detectados: {len(text_fields)}")
                except Exception as e:
                    print(f"⚠️  get_form_text_fields() falhou: {str(e)}")
                
                # Método 2: Extração manual de anotações
                try:
                    for page_num, page in enumerate(pdf_reader.pages):
                        if '/Annots' in page:
                            annotations = page['/Annots']
                            if annotations:
                                for annot_ref in annotations:
                                    try:
                                        annot = annot_ref.get_object()
                                        if annot and '/T' in annot and '/V' in annot:
                                            field_name = str(annot['/T'])
                                            field_value = str(annot['/V']) if annot['/V'] else ''
                                            if field_value and field_value != 'None':
                                                form_fields[field_name] = field_value
                                    except Exception:
                                        continue
                except Exception as e:
                    print(f"⚠️  Extração manual falhou: {str(e)}")
                
                print(f"📊 Total de campos encontrados: {len(form_fields)}")
                
                # Lista COMPLETA de todos os campos encontrados
                print(f"\n📄 TODOS OS CAMPOS ENCONTRADOS NO PDF:")
                for field_name, field_value in form_fields.items():
                    print(f"  {field_name}: '{field_value}'")
                
                # Validações Críticas (CAMPOS OBRIGATÓRIOS) - 10 campos principais
                campos_obrigatorios = {
                    "nome_familia": {
                        "esperado": "Silva",
                        "encontrado": "",
                        "preenchido": False,
                        "campos_possiveis": ["P1Line1a_FamilyName", "FamilyName", "LastName", "Surname"]
                    },
                    "nome_proprio": {
                        "esperado": "Roberto",
                        "encontrado": "",
                        "preenchido": False,
                        "campos_possiveis": ["P1_Line1b_GivenName", "GivenName", "FirstName", "Name"]
                    },
                    "endereco": {
                        "esperado": "2580 Ocean Drive",
                        "encontrado": "",
                        "preenchido": False,
                        "campos_possiveis": ["Part1_Item6_StreetName", "StreetAddress", "Address", "Street"]
                    },
                    "cidade": {
                        "esperado": "Orlando",
                        "encontrado": "",
                        "preenchido": False,
                        "campos_possiveis": ["Part2_Item11_City", "City", "CityName"]
                    },
                    "estado": {
                        "esperado": "FL",
                        "encontrado": "",
                        "preenchido": False,
                        "campos_possiveis": ["Part2_Item11_State", "State", "StateCode"]
                    },
                    "cep": {
                        "esperado": "32801",
                        "encontrado": "",
                        "preenchido": False,
                        "campos_possiveis": ["Part2_Item11_ZipCode", "ZipCode", "PostalCode", "Zip"]
                    },
                    "email": {
                        "esperado": "roberto.mendes@testqa.com",
                        "encontrado": "",
                        "preenchido": False,
                        "campos_possiveis": ["EmailAddress", "Email", "ContactEmail"]
                    },
                    "telefone": {
                        "esperado": "+1-407-555-1234",
                        "encontrado": "",
                        "preenchido": False,
                        "campos_possiveis": ["P5_Line3_DaytimePhoneNumber", "PhoneNumber", "Phone", "DaytimePhone"]
                    },
                    "passaporte": {
                        "esperado": "BR111222333",
                        "encontrado": "",
                        "preenchido": False,
                        "campos_possiveis": ["Part1_Item4_Number", "PassportNumber", "DocumentNumber"]
                    },
                    "pais_nascimento": {
                        "esperado": "Brazil",
                        "encontrado": "",
                        "preenchido": False,
                        "campos_possiveis": ["CountryOfBirth", "BirthCountry", "Country"]
                    }
                }
                
                # Verificar cada campo obrigatório
                for campo_nome, campo_info in campos_obrigatorios.items():
                    esperado = campo_info["esperado"]
                    
                    # Procurar em todos os campos possíveis
                    for field_name, field_value in form_fields.items():
                        if field_value and esperado.lower() in field_value.lower():
                            campo_info["encontrado"] = field_value
                            campo_info["preenchido"] = True
                            break
                        
                        # Verificar se o nome do campo corresponde
                        for campo_possivel in campo_info["campos_possiveis"]:
                            if campo_possivel.lower() in field_name.lower() and field_value:
                                if (esperado.lower() in field_value.lower() or 
                                    any(part.lower() in field_value.lower() for part in esperado.split())):
                                    campo_info["encontrado"] = field_value
                                    campo_info["preenchido"] = True
                                    break
                        
                        if campo_info["preenchido"]:
                            break
                
                # Contar campos preenchidos
                campos_preenchidos = sum(1 for campo in campos_obrigatorios.values() if campo["preenchido"])
                total_campos = len(campos_obrigatorios)
                
                print(f"\n🎯 VALIDAÇÃO CRÍTICA DO BUG P0:")
                print("=" * 60)
                
                for campo_nome, campo_info in campos_obrigatorios.items():
                    status = "✅" if campo_info["preenchido"] else "❌"
                    print(f"  {status} {campo_nome}:")
                    print(f"      Esperado: '{campo_info['esperado']}'")
                    print(f"      Encontrado: '{campo_info['encontrado']}'")
                    print(f"      Preenchido: {campo_info['preenchido']}")
                
                # Critério de Aprovação do Bug P0
                print(f"\n📊 CAMPOS PREENCHIDOS: {campos_preenchidos}/{total_campos}")
                
                if campos_preenchidos >= 7:
                    bug_p0_status = "CORRIGIDO"
                    bug_p0_aprovado = True
                    print(f"✅ BUG P0 CORRIGIDO: {campos_preenchidos}/10 campos preenchidos")
                elif campos_preenchidos >= 4:
                    bug_p0_status = "PARCIAL"
                    bug_p0_aprovado = False
                    print(f"⚠️  BUG P0 PARCIAL: {campos_preenchidos}/10 campos preenchidos")
                else:
                    bug_p0_status = "NÃO CORRIGIDO"
                    bug_p0_aprovado = False
                    print(f"❌ BUG P0 NÃO CORRIGIDO: {campos_preenchidos}/10 campos preenchidos")
                
                results["etapa6_validacao_bug_p0"] = {
                    "success": True,
                    "total_form_fields": len(form_fields),
                    "campos_obrigatorios": campos_obrigatorios,
                    "campos_preenchidos": campos_preenchidos,
                    "total_campos": total_campos,
                    "bug_p0_status": bug_p0_status,
                    "bug_p0_aprovado": bug_p0_aprovado,
                    "all_form_fields": form_fields
                }
                
        except Exception as e:
            print(f"❌ Exception na ETAPA 6: {str(e)}")
            results["etapa6_validacao_bug_p0"] = {"success": False, "exception": str(e)}
    
    # ETAPA 7: VERIFICAÇÃO DE INTEGRIDADE DO ARQUIVO
    print("\n" + "="*80)
    print("📋 ETAPA 7: VERIFICAÇÃO DE INTEGRIDADE DO ARQUIVO")
    print("="*80)
    
    if pdf_path and os.path.exists(pdf_path):
        try:
            with open(pdf_path, 'rb') as pdf_file:
                pdf_reader = pypdf.PdfReader(pdf_file)
                
                validacoes_etapa7 = {
                    "pdf_abre_sem_erros": True,
                    "numero_paginas_correto": len(pdf_reader.pages) >= 7,  # I-539 tem 7+ páginas
                    "pdf_nao_corrompido": True,
                    "metadados_presentes": bool(pdf_reader.metadata)
                }
                
                print(f"✅ PDF abre sem erros")
                print(f"📄 Número de páginas: {len(pdf_reader.pages)}")
                print(f"📊 Metadados presentes: {bool(pdf_reader.metadata)}")
                
                if pdf_reader.metadata:
                    print(f"📋 Metadados: {dict(pdf_reader.metadata)}")
                
                etapa7_sucesso = all(validacoes_etapa7.values())
                results["etapa7_integridade_arquivo"] = {
                    "success": etapa7_sucesso,
                    "validacoes": validacoes_etapa7,
                    "numero_paginas": len(pdf_reader.pages),
                    "metadados": dict(pdf_reader.metadata) if pdf_reader.metadata else None
                }
                
        except Exception as e:
            print(f"❌ Exception na ETAPA 7: {str(e)}")
            results["etapa7_integridade_arquivo"] = {"success": False, "exception": str(e)}
    else:
        results["etapa7_integridade_arquivo"] = {"success": False, "error": "PDF not available"}
    
    # ETAPA 8: TESTE DE EXTRAÇÃO DE TEXTO
    print("\n" + "="*80)
    print("📋 ETAPA 8: TESTE DE EXTRAÇÃO DE TEXTO")
    print("="*80)
    
    if pdf_path and os.path.exists(pdf_path):
        try:
            with open(pdf_path, 'rb') as pdf_file:
                pdf_reader = pypdf.PdfReader(pdf_file)
                
                # Extrair texto da primeira página
                first_page_text = pdf_reader.pages[0].extract_text()
                
                validacoes_etapa8 = {
                    "texto_nao_vazio": len(first_page_text.strip()) > 0,
                    "contem_dados_usuario": False
                }
                
                # Verificar se contém pelo menos 3 dos dados submetidos
                dados_encontrados = 0
                dados_procurados = ["Roberto", "Silva", "Orlando", "FL", "32801", "Brazil"]
                
                for dado in dados_procurados:
                    if dado in first_page_text:
                        dados_encontrados += 1
                
                validacoes_etapa8["contem_dados_usuario"] = dados_encontrados >= 3
                
                print(f"📄 Texto extraído (primeiros 500 chars): {first_page_text[:500]}")
                print(f"📊 Dados encontrados no texto: {dados_encontrados}/6")
                
                etapa8_sucesso = all(validacoes_etapa8.values())
                results["etapa8_extracao_texto"] = {
                    "success": etapa8_sucesso,
                    "validacoes": validacoes_etapa8,
                    "texto_length": len(first_page_text),
                    "dados_encontrados": dados_encontrados,
                    "primeiro_texto": first_page_text[:500]
                }
                
        except Exception as e:
            print(f"❌ Exception na ETAPA 8: {str(e)}")
            results["etapa8_extracao_texto"] = {"success": False, "exception": str(e)}
    else:
        results["etapa8_extracao_texto"] = {"success": False, "error": "PDF not available"}
    
    # ETAPA 9: COMPARAÇÃO: DADOS ENVIADOS vs DADOS NO PDF
    print("\n" + "="*80)
    print("📋 ETAPA 9: COMPARAÇÃO: DADOS ENVIADOS vs DADOS NO PDF")
    print("="*80)
    
    if results.get("etapa6_validacao_bug_p0", {}).get("success"):
        campos_obrigatorios = results["etapa6_validacao_bug_p0"]["campos_obrigatorios"]
        
        # Criar tabela comparativa
        print("| Campo | Valor Enviado | Valor no PDF | Status |")
        print("|-------|---------------|--------------|--------|")
        
        correspondencias = 0
        total_comparacoes = 0
        
        comparacao_dados = {}
        
        for campo_nome, campo_info in campos_obrigatorios.items():
            valor_enviado = campo_info["esperado"]
            valor_pdf = campo_info["encontrado"]
            status = "✅" if campo_info["preenchido"] else "❌"
            
            print(f"| {campo_nome} | {valor_enviado} | {valor_pdf} | {status} |")
            
            comparacao_dados[campo_nome] = {
                "valor_enviado": valor_enviado,
                "valor_pdf": valor_pdf,
                "corresponde": campo_info["preenchido"]
            }
            
            if campo_info["preenchido"]:
                correspondencias += 1
            total_comparacoes += 1
        
        taxa_correspondencia = (correspondencias / total_comparacoes) * 100 if total_comparacoes > 0 else 0
        
        print(f"\n📊 Taxa de correspondência: {correspondencias}/{total_comparacoes} campos corretos ({taxa_correspondencia:.1f}%)")
        
        etapa9_sucesso = taxa_correspondencia >= 70  # 70% de correspondência
        results["etapa9_comparacao_dados"] = {
            "success": etapa9_sucesso,
            "correspondencias": correspondencias,
            "total_comparacoes": total_comparacoes,
            "taxa_correspondencia": taxa_correspondencia,
            "comparacao_dados": comparacao_dados
        }
    else:
        results["etapa9_comparacao_dados"] = {"success": False, "error": "Etapa 6 failed"}
    
    # ETAPA 10: VERIFICAÇÃO FINAL DO FLUXO E2E
    print("\n" + "="*80)
    print("📋 ETAPA 10: VERIFICAÇÃO FINAL DO FLUXO E2E")
    print("="*80)
    
    # Checklist Final
    checklist_final = {
        "caso_criado_sucesso": results.get("etapa1_criacao_caso", {}).get("success", False),
        "formulario_aceito_validado": results.get("etapa2_formulario_amigavel", {}).get("success", False),
        "dados_persistidos_corretamente": results.get("etapa3_persistencia_dados", {}).get("success", False),
        "pdf_gerado_sem_erros": results.get("etapa4_geracao_pdf", {}).get("success", False),
        "pdf_pode_ser_baixado": results.get("etapa5_download_pdf", {}).get("success", False),
        "pdf_contem_dados_preenchidos": results.get("etapa6_validacao_bug_p0", {}).get("bug_p0_aprovado", False),
        "integridade_pdf_verificada": results.get("etapa7_integridade_arquivo", {}).get("success", False),
        "dados_correspondem": results.get("etapa9_comparacao_dados", {}).get("success", False),
        "sem_erros_500": True,  # Verificar se houve erros 500
        "tempo_execucao_adequado": (time.time() - start_time) < 30
    }
    
    # Verificar erros 500
    status_codes = [
        results.get("etapa1_criacao_caso", {}).get("status_code", 200),
        results.get("etapa2_formulario_amigavel", {}).get("status_code", 200),
        results.get("etapa4_geracao_pdf", {}).get("status_code", 200),
        results.get("etapa5_download_pdf", {}).get("status_code", 200)
    ]
    checklist_final["sem_erros_500"] = all(code != 500 for code in status_codes)
    
    tempo_total = time.time() - start_time
    
    print(f"🎯 CHECKLIST FINAL:")
    for item, passou in checklist_final.items():
        status = "✅" if passou else "❌"
        print(f"  {status} {item}: {passou}")
    
    print(f"\n⏰ Tempo total de execução: {tempo_total:.2f} segundos")
    
    itens_aprovados = sum(checklist_final.values())
    total_itens = len(checklist_final)
    taxa_sucesso_final = (itens_aprovados / total_itens) * 100
    
    print(f"📊 Taxa de sucesso geral: {itens_aprovados}/{total_itens} ({taxa_sucesso_final:.1f}%)")
    
    results["etapa10_verificacao_final"] = {
        "success": taxa_sucesso_final >= 80,
        "checklist_final": checklist_final,
        "itens_aprovados": itens_aprovados,
        "total_itens": total_itens,
        "taxa_sucesso_final": taxa_sucesso_final,
        "tempo_total_execucao": tempo_total
    }
    
    # RESUMO EXECUTIVO
    print("\n" + "="*100)
    print("📋 RESUMO EXECUTIVO")
    print("="*100)
    
    # Taxa de sucesso geral
    etapas_sucesso = [
        results.get("etapa1_criacao_caso", {}).get("success", False),
        results.get("etapa2_formulario_amigavel", {}).get("success", False),
        results.get("etapa3_persistencia_dados", {}).get("success", False),
        results.get("etapa4_geracao_pdf", {}).get("success", False),
        results.get("etapa5_download_pdf", {}).get("success", False),
        results.get("etapa6_validacao_bug_p0", {}).get("bug_p0_aprovado", False),
        results.get("etapa7_integridade_arquivo", {}).get("success", False),
        results.get("etapa8_extracao_texto", {}).get("success", False),
        results.get("etapa9_comparacao_dados", {}).get("success", False),
        results.get("etapa10_verificacao_final", {}).get("success", False)
    ]
    
    etapas_aprovadas = sum(etapas_sucesso)
    total_etapas = len(etapas_sucesso)
    taxa_sucesso_geral = (etapas_aprovadas / total_etapas) * 100
    
    # Conclusão sobre Bug P0
    bug_p0_status = results.get("etapa6_validacao_bug_p0", {}).get("bug_p0_status", "DESCONHECIDO")
    
    print(f"📊 Taxa de sucesso geral: {etapas_aprovadas}/{total_etapas} ({taxa_sucesso_geral:.1f}%)")
    print(f"⏰ Tempo total de execução: {tempo_total:.2f} segundos")
    print(f"🎯 Conclusão sobre Bug P0: {bug_p0_status}")
    
    # Sistema pronto para produção?
    sistema_pronto = taxa_sucesso_geral >= 80 and bug_p0_status == "CORRIGIDO"
    
    if sistema_pronto:
        print("\n✅ SISTEMA ESTÁ PRONTO PARA PRODUÇÃO")
        print("✅ Bug P0 foi resolvido")
        print("✅ Fluxo end-to-end operacional")
    else:
        print("\n❌ SISTEMA NÃO ESTÁ PRONTO PARA PRODUÇÃO")
        if bug_p0_status != "CORRIGIDO":
            print("❌ Bug P0 não foi totalmente resolvido")
        if taxa_sucesso_geral < 80:
            print(f"❌ Taxa de sucesso insuficiente ({taxa_sucesso_geral:.1f}% < 80%)")
    
    # Store final summary
    results["summary"] = {
        "etapas_aprovadas": etapas_aprovadas,
        "total_etapas": total_etapas,
        "taxa_sucesso_geral": taxa_sucesso_geral,
        "tempo_total_execucao": tempo_total,
        "bug_p0_status": bug_p0_status,
        "sistema_pronto_producao": sistema_pronto,
        "case_id": case_id,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    return results

if __name__ == "__main__":
    print("🎯 INICIANDO TESTE END-TO-END COMPLETO - USERsimulator-DISCIPLINA SESSION")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print(f"🔗 API Base: {API_BASE}")
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    print("🎯 Focus: Validação rigorosa em 10 etapas do sistema I-539")
    
    # Execute main test
    test_results = disciplina_i539_complete_e2e_test()
    
    # Save results to file
    results_file = "/app/disciplina_i539_e2e_test_results.json"
    with open(results_file, "w") as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultados completos salvos em: {results_file}")
    
    # Final assessment
    summary = test_results.get("summary", {})
    taxa_sucesso = summary.get("taxa_sucesso_geral", 0)
    bug_p0_status = summary.get("bug_p0_status", "DESCONHECIDO")
    sistema_pronto = summary.get("sistema_pronto_producao", False)
    
    print(f"\n🎯 AVALIAÇÃO FINAL:")
    print(f"📊 Taxa de Sucesso: {taxa_sucesso:.1f}%")
    print(f"🐛 Bug P0 Status: {bug_p0_status}")
    print(f"🚀 Sistema Pronto: {'SIM' if sistema_pronto else 'NÃO'}")
    
    if sistema_pronto:
        print("\n✅ RECOMENDAÇÃO: SISTEMA APROVADO PARA PRODUÇÃO")
    else:
        print("\n❌ RECOMENDAÇÃO: SISTEMA NECESSITA CORREÇÕES ANTES DA PRODUÇÃO")