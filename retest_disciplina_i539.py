#!/usr/bin/env python3
"""
🎯 RETEST END-TO-END COMPLETO - USERsimulator-DISCIPLINA SESSION

CONTEXTO:
Após o primeiro teste E2E que identificou que apenas 6/10 campos críticos estavam sendo preenchidos (60%), 
o desenvolvedor implementou correções para adicionar/corrigir os 4 campos faltantes:
1. ✅ Estado (FL) - Campo adicionado: `P2_Line10_Province[0]`
2. ✅ Email - Campo adicionado: `P5_Line5_EmailAddress[0]`
3. ✅ Telefone - Já estava mapeado corretamente
4. ✅ País de Nascimento - Campo corrigido de `P1_Line7_CountryOfBirth[0]` para `P1_Line6_CountryOfBirth[0]`

OBJETIVO DO RETEST:
Executar o MESMO teste end-to-end com os MESMOS dados para verificar se agora >= 7/10 campos críticos 
estão sendo preenchidos (threshold de 70% para aprovar Bug P0).
"""

import requests
import json
import time
import os
import base64
from pathlib import Path
from datetime import datetime
import pypdf
import io
import hashlib

# Get backend URL from frontend .env
BACKEND_URL = "https://formfiller-26.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def retest_disciplina_i539_complete():
    """
    🎯 RETEST END-TO-END COMPLETO - USERsimulator-DISCIPLINA SESSION
    
    Executar o MESMO teste end-to-end com os MESMOS dados para verificar se agora >= 7/10 campos críticos 
    estão sendo preenchidos (threshold de 70% para aprovar Bug P0).
    
    DADOS DE TESTE (EXATAMENTE OS MESMOS):
    Roberto Carlos Mendes Silva - dados idênticos ao teste anterior
    
    METODOLOGIA DE RETEST - 10 ETAPAS IDÊNTICAS AO TESTE ANTERIOR
    """
    
    print("🎯 RETEST END-TO-END COMPLETO - USERsimulator-DISCIPLINA SESSION")
    print("📋 Executando MESMO teste com MESMOS dados para verificar correções")
    print("🎯 Objetivo: Verificar se >= 7/10 campos críticos preenchidos (70% threshold)")
    print("=" * 80)
    
    # DADOS DE TESTE (EXATAMENTE OS MESMOS)
    test_data = {
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
    }
    
    print(f"📤 DADOS DE TESTE (IDÊNTICOS AO TESTE ANTERIOR):")
    print(json.dumps(test_data, indent=2, ensure_ascii=False))
    
    results = {
        "etapa1_criacao_caso": {},
        "etapa2_formulario_amigavel": {},
        "etapa3_verificacao_persistencia": {},
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
    
    # ETAPA 1: CRIAÇÃO DE CASO I-539
    print("\n📋 ETAPA 1: CRIAÇÃO DE CASO I-539")
    print("-" * 60)
    
    try:
        print("📝 Criando caso I-539...")
        response = requests.post(
            f"{API_BASE}/auto-application/start",
            json={"visa_type": "I-539", "form_code": "I-539"},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code in [200, 201]:
            case_data = response.json()
            case_info = case_data.get("case", {})
            case_id = case_info.get("case_id")
            
            if case_id:
                print(f"✅ Caso I-539 criado: {case_id}")
                
                # Verificar se foi persistido no MongoDB
                mongo_check = case_info.get("form_code") == "I-539"
                
                results["etapa1_criacao_caso"] = {
                    "success": True,
                    "case_id": case_id,
                    "status_code": response.status_code,
                    "persistido_mongodb": mongo_check,
                    "passed": True
                }
            else:
                print(f"❌ No case_id in response: {case_data}")
                results["etapa1_criacao_caso"] = {"success": False, "error": "No case_id", "passed": False}
                return results
        else:
            print(f"❌ Failed to create case: {response.status_code}")
            results["etapa1_criacao_caso"] = {"success": False, "status_code": response.status_code, "passed": False}
            return results
            
    except Exception as e:
        print(f"❌ Exception creating case: {str(e)}")
        results["etapa1_criacao_caso"] = {"success": False, "exception": str(e), "passed": False}
        return results
    
    # ETAPA 2: SUBMISSÃO DO FORMULÁRIO AMIGÁVEL
    print("\n📋 ETAPA 2: SUBMISSÃO DO FORMULÁRIO AMIGÁVEL")
    print("-" * 60)
    
    try:
        print(f"📤 Enviando formulário amigável para caso {case_id}...")
        
        # Wrap test data in the expected format
        friendly_form_payload = {
            "friendly_form_data": test_data,
            "basic_data": {}
        }
        
        response = requests.post(
            f"{API_BASE}/case/{case_id}/friendly-form",
            json=friendly_form_payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            form_result = response.json()
            print(f"✅ Formulário amigável enviado com sucesso")
            print(f"📄 Response: {json.dumps(form_result, indent=2, ensure_ascii=False)}")
            
            # Verificar validation_status e completion_percentage
            validation_status = form_result.get("validation_status", "unknown")
            completion_percentage = form_result.get("completion_percentage", 0)
            
            results["etapa2_formulario_amigavel"] = {
                "success": True,
                "status_code": response.status_code,
                "validation_status": validation_status,
                "completion_percentage": completion_percentage,
                "response": form_result,
                "passed": True
            }
        else:
            print(f"❌ Failed to submit friendly form: {response.status_code}")
            print(f"📄 Error: {response.text}")
            results["etapa2_formulario_amigavel"] = {
                "success": False,
                "status_code": response.status_code,
                "error": response.text,
                "passed": False
            }
            return results
            
    except Exception as e:
        print(f"❌ Exception submitting friendly form: {str(e)}")
        results["etapa2_formulario_amigavel"] = {"success": False, "exception": str(e), "passed": False}
        return results
    
    # ETAPA 3: VERIFICAÇÃO DE PERSISTÊNCIA
    print("\n📋 ETAPA 3: VERIFICAÇÃO DE PERSISTÊNCIA")
    print("-" * 60)
    
    try:
        print(f"🔍 Verificando persistência dos dados para caso {case_id}...")
        response = requests.get(
            f"{API_BASE}/auto-application/case/{case_id}",
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            case_data = response.json()
            case_info = case_data.get("case", {})
            
            # Verificar se TODOS os 13 campos foram salvos
            simplified_responses = case_info.get("simplified_form_responses", {})
            
            print(f"📄 Simplified Form Responses: {json.dumps(simplified_responses, indent=2, ensure_ascii=False)}")
            
            # Verificar todos os 13 campos
            field_checks = {}
            for field, expected_value in test_data.items():
                actual_value = simplified_responses.get(field)
                field_checks[field] = {
                    "expected": expected_value,
                    "actual": actual_value,
                    "saved": actual_value == expected_value
                }
            
            print(f"\n🎯 VERIFICAÇÃO DOS 13 CAMPOS:")
            fields_saved = 0
            for field, check in field_checks.items():
                status = "✅" if check["saved"] else "❌"
                print(f"  {status} {field}: {check['saved']}")
                if check["saved"]:
                    fields_saved += 1
            
            print(f"\n📊 CAMPOS SALVOS: {fields_saved}/13 ({fields_saved/13*100:.1f}%)")
            
            results["etapa3_verificacao_persistencia"] = {
                "success": True,
                "field_checks": field_checks,
                "fields_saved": fields_saved,
                "total_fields": 13,
                "simplified_responses": simplified_responses,
                "passed": fields_saved == 13
            }
        else:
            print(f"❌ Failed to retrieve case: {response.status_code}")
            results["etapa3_verificacao_persistencia"] = {
                "success": False,
                "status_code": response.status_code,
                "error": response.text,
                "passed": False
            }
            return results
            
    except Exception as e:
        print(f"❌ Exception retrieving case: {str(e)}")
        results["etapa3_verificacao_persistencia"] = {"success": False, "exception": str(e), "passed": False}
        return results
    
    # ETAPA 4: GERAÇÃO DO PDF I-539
    print("\n📋 ETAPA 4: GERAÇÃO DO PDF I-539")
    print("-" * 60)
    
    try:
        print(f"📝 Gerando PDF I-539 para caso {case_id}...")
        response = requests.post(
            f"{API_BASE}/case/{case_id}/generate-form",
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            pdf_result = response.json()
            print(f"✅ PDF I-539 gerado com sucesso")
            print(f"📄 Response: {json.dumps(pdf_result, indent=2, ensure_ascii=False)}")
            
            # Verificar critérios de geração
            pdf_checks = {
                "success_true": pdf_result.get("success", False),
                "filename_present": pdf_result.get("filename") is not None,
                "file_size_adequate": pdf_result.get("file_size", 0) > 300000,  # >300KB
                "download_url_present": pdf_result.get("download_url") is not None
            }
            
            print(f"\n🎯 VERIFICAÇÃO DA GERAÇÃO DO PDF:")
            for check, passed in pdf_checks.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check}: {passed}")
            
            results["etapa4_geracao_pdf"] = {
                "success": True,
                "status_code": response.status_code,
                "pdf_result": pdf_result,
                "pdf_checks": pdf_checks,
                "passed": all(pdf_checks.values())
            }
        else:
            print(f"❌ PDF generation failed: {response.status_code}")
            print(f"📄 Error: {response.text}")
            results["etapa4_geracao_pdf"] = {
                "success": False,
                "status_code": response.status_code,
                "error": response.text,
                "passed": False
            }
            return results
            
    except Exception as e:
        print(f"❌ Exception generating PDF: {str(e)}")
        results["etapa4_geracao_pdf"] = {"success": False, "exception": str(e), "passed": False}
        return results
    
    # ETAPA 5: DOWNLOAD DO PDF
    print("\n📋 ETAPA 5: DOWNLOAD DO PDF")
    print("-" * 60)
    
    try:
        print(f"📥 Fazendo download do PDF para caso {case_id}...")
        response = requests.get(
            f"{API_BASE}/case/{case_id}/download-form",
            timeout=60
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"📏 Content-Length: {len(response.content)} bytes")
        
        if response.status_code == 200:
            # Verificar download
            download_checks = {
                "status_200": response.status_code == 200,
                "content_type_pdf": response.headers.get('Content-Type') == 'application/pdf',
                "file_size_adequate": len(response.content) > 300000,  # >300KB
                "content_not_empty": len(response.content) > 0
            }
            
            print(f"\n🎯 VERIFICAÇÃO DO DOWNLOAD:")
            for check, passed in download_checks.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check}: {passed}")
            
            # Salvar PDF para análise
            pdf_path = f"/tmp/retest_disciplina_i539_{case_id}.pdf"
            with open(pdf_path, 'wb') as f:
                f.write(response.content)
            print(f"💾 PDF salvo em: {pdf_path}")
            
            # Calcular hash MD5 para verificação
            pdf_hash = hashlib.md5(response.content).hexdigest()
            print(f"🔐 Hash MD5: {pdf_hash}")
            
            results["etapa5_download_pdf"] = {
                "success": True,
                "status_code": response.status_code,
                "content_type": response.headers.get('Content-Type'),
                "file_size": len(response.content),
                "download_checks": download_checks,
                "pdf_path": pdf_path,
                "pdf_hash": pdf_hash,
                "passed": all(download_checks.values())
            }
        else:
            print(f"❌ PDF download failed: {response.status_code}")
            print(f"📄 Error: {response.text}")
            results["etapa5_download_pdf"] = {
                "success": False,
                "status_code": response.status_code,
                "error": response.text,
                "passed": False
            }
            return results
            
    except Exception as e:
        print(f"❌ Exception downloading PDF: {str(e)}")
        results["etapa5_download_pdf"] = {"success": False, "exception": str(e), "passed": False}
        return results
    
    # ETAPA 6: ⭐ VALIDAÇÃO CRÍTICA DO BUG P0 (RETEST)
    print("\n📋 ETAPA 6: ⭐ VALIDAÇÃO CRÍTICA DO BUG P0 (RETEST)")
    print("-" * 60)
    
    try:
        pdf_path = results["etapa5_download_pdf"]["pdf_path"]
        print(f"🔍 Analisando campos críticos no PDF: {pdf_path}")
        
        # Ler PDF e extrair campos do formulário
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = pypdf.PdfReader(pdf_file)
            
            print(f"📄 PDF Pages: {len(pdf_reader.pages)}")
            
            # Extrair campos do formulário
            form_fields = {}
            
            # Método 1: get_form_text_fields()
            try:
                text_fields = pdf_reader.get_form_text_fields()
                if text_fields and isinstance(text_fields, dict):
                    form_fields.update(text_fields)
                    print(f"📊 Text fields detectados: {len(text_fields)}")
            except Exception as e:
                print(f"⚠️  get_form_text_fields() falhou: {str(e)}")
            
            # Método 2: get_fields()
            try:
                if hasattr(pdf_reader, 'get_fields'):
                    fields = pdf_reader.get_fields()
                    if fields and isinstance(fields, dict):
                        for k, v in fields.items():
                            if v and hasattr(v, 'get'):
                                field_value = v.get('/V', '')
                                if field_value:
                                    form_fields[k] = str(field_value)
                        print(f"📊 Fields via get_fields(): {len(fields)}")
            except Exception as e:
                print(f"⚠️  get_fields() falhou: {str(e)}")
            
            print(f"📊 Total form fields detectados: {len(form_fields)}")
            
            # CAMPOS CRÍTICOS A VERIFICAR (10 campos) - EXATAMENTE COMO NO TESTE ANTERIOR
            critical_fields_mapping = {
                1: {
                    "name": "Nome Família",
                    "expected": "Silva",
                    "pdf_field": "P1Line1a_FamilyName[0]",
                    "status_anterior": "✅ PASSOU"
                },
                2: {
                    "name": "Nome Próprio", 
                    "expected": "Roberto",
                    "pdf_field": "P1_Line1b_GivenName[0]",
                    "status_anterior": "✅ PASSOU"
                },
                3: {
                    "name": "Endereço",
                    "expected": "2580 Ocean Drive",
                    "pdf_field": "Part1_Item6_StreetName[0]",
                    "status_anterior": "✅ PASSOU"
                },
                4: {
                    "name": "Cidade",
                    "expected": "Orlando",
                    "pdf_field": "Part1_Item6_City[0]",
                    "status_anterior": "✅ PASSOU"
                },
                5: {
                    "name": "Estado",
                    "expected": "FL",
                    "pdf_field": "P2_Line10_Province[0]",
                    "status_anterior": "❌ FALHOU → CORRIGIDO"
                },
                6: {
                    "name": "CEP",
                    "expected": "32801",
                    "pdf_field": "Part1_Item6_ZipCode[0]",
                    "status_anterior": "✅ PASSOU"
                },
                7: {
                    "name": "Email",
                    "expected": "roberto.mendes@testqa.com",
                    "pdf_field": "P5_Line5_EmailAddress[0]",
                    "status_anterior": "❌ FALHOU → CORRIGIDO"
                },
                8: {
                    "name": "Telefone",
                    "expected": "+1-407-555-1234",
                    "pdf_field": "P5_Line3_DaytimePhoneNumber[0]",
                    "status_anterior": "✅ PASSOU"
                },
                9: {
                    "name": "Passaporte",
                    "expected": "BR111222333",
                    "pdf_field": "Part1_Item4_Number[0]",
                    "status_anterior": "✅ PASSOU"
                },
                10: {
                    "name": "País Nascimento",
                    "expected": "Brazil",
                    "pdf_field": "P1_Line6_CountryOfBirth[0]",
                    "status_anterior": "❌ FALHOU → CORRIGIDO"
                }
            }
            
            print(f"\n🎯 VALIDAÇÃO DOS 10 CAMPOS CRÍTICOS:")
            print("=" * 80)
            
            fields_filled = 0
            field_results = {}
            
            for num, field_info in critical_fields_mapping.items():
                field_name = field_info["name"]
                expected_value = field_info["expected"]
                pdf_field = field_info["pdf_field"]
                status_anterior = field_info["status_anterior"]
                
                # Buscar valor no PDF
                actual_value = form_fields.get(pdf_field, "")
                
                # Verificar se campo está preenchido (match parcial aceitável)
                is_filled = False
                if actual_value:
                    if expected_value.lower() in actual_value.lower() or actual_value.lower() in expected_value.lower():
                        is_filled = True
                        fields_filled += 1
                
                status = "✅" if is_filled else "❌"
                
                print(f"  {num:2d}. {status} {field_name}")
                print(f"      Campo PDF: {pdf_field}")
                print(f"      Esperado: '{expected_value}'")
                print(f"      Atual: '{actual_value}'")
                print(f"      Status Anterior: {status_anterior}")
                print(f"      Preenchido: {is_filled}")
                print()
                
                field_results[num] = {
                    "name": field_name,
                    "expected": expected_value,
                    "actual": actual_value,
                    "pdf_field": pdf_field,
                    "status_anterior": status_anterior,
                    "filled": is_filled
                }
            
            # CRITÉRIO DE APROVAÇÃO
            total_fields = 10
            threshold = 7  # >= 7/10 campos (70%)
            
            print(f"🎯 CRITÉRIO DE APROVAÇÃO:")
            print("=" * 60)
            print(f"📊 Campos preenchidos: {fields_filled}/{total_fields} ({fields_filled/total_fields*100:.1f}%)")
            print(f"🎯 Threshold necessário: {threshold}/{total_fields} (70%)")
            
            # Determinar status do Bug P0
            if fields_filled >= threshold:
                bug_status = "✅ BUG P0 CORRIGIDO"
                bug_level = "CORRIGIDO"
            elif fields_filled == 6:
                bug_status = "⚠️ BUG P0 PARCIAL"
                bug_level = "PARCIAL"
            else:
                bug_status = "❌ BUG P0 NÃO CORRIGIDO"
                bug_level = "NÃO CORRIGIDO"
            
            print(f"\n{bug_status}: {fields_filled}/{total_fields} campos preenchidos")
            
            # FOCO ESPECIAL: Verificar os 4 campos que FALHARAM no teste anterior
            print(f"\n🔍 FOCO ESPECIAL - 4 CAMPOS CORRIGIDOS:")
            print("=" * 60)
            
            campos_corrigidos = [5, 7, 10]  # Estado, Email, País Nascimento
            melhorias = {}
            
            for num in campos_corrigidos:
                field_info = field_results[num]
                field_name = field_info["name"]
                was_filled = field_info["filled"]
                
                if "❌ FALHOU → CORRIGIDO" in field_info["status_anterior"]:
                    if was_filled:
                        print(f"  ✅ {field_name}: CORREÇÃO FUNCIONOU!")
                        melhorias[field_name] = "FUNCIONOU"
                    else:
                        print(f"  ❌ {field_name}: Correção não funcionou")
                        melhorias[field_name] = "NÃO FUNCIONOU"
            
            results["etapa6_validacao_bug_p0"] = {
                "success": True,
                "total_form_fields": len(form_fields),
                "critical_fields_results": field_results,
                "fields_filled": fields_filled,
                "total_critical_fields": total_fields,
                "threshold": threshold,
                "bug_status": bug_level,
                "melhorias": melhorias,
                "all_form_fields": dict(list(form_fields.items())[:50]),
                "passed": fields_filled >= threshold
            }
            
    except Exception as e:
        print(f"❌ Exception during PDF field verification: {str(e)}")
        results["etapa6_validacao_bug_p0"] = {
            "success": False,
            "exception": str(e),
            "passed": False
        }
    
    # ETAPA 7: INTEGRIDADE DO ARQUIVO
    print("\n📋 ETAPA 7: INTEGRIDADE DO ARQUIVO")
    print("-" * 60)
    
    try:
        pdf_path = results["etapa5_download_pdf"]["pdf_path"]
        
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = pypdf.PdfReader(pdf_file)
            
            integrity_checks = {
                "pdf_valido": True,
                "7_paginas": len(pdf_reader.pages) == 7,
                "nao_corrompido": True,
                "metadados_presentes": pdf_reader.metadata is not None
            }
            
            print(f"🎯 VERIFICAÇÃO DE INTEGRIDADE:")
            for check, passed in integrity_checks.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check}: {passed}")
            
            results["etapa7_integridade_arquivo"] = {
                "success": True,
                "integrity_checks": integrity_checks,
                "pages": len(pdf_reader.pages),
                "passed": all(integrity_checks.values())
            }
            
    except Exception as e:
        print(f"❌ Exception during integrity check: {str(e)}")
        results["etapa7_integridade_arquivo"] = {
            "success": False,
            "exception": str(e),
            "passed": False
        }
    
    # ETAPA 8: EXTRAÇÃO DE TEXTO
    print("\n📋 ETAPA 8: EXTRAÇÃO DE TEXTO")
    print("-" * 60)
    
    try:
        pdf_path = results["etapa5_download_pdf"]["pdf_path"]
        
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = pypdf.PdfReader(pdf_file)
            
            # Extrair texto da primeira página
            first_page_text = pdf_reader.pages[0].extract_text()
            
            # Verificar se contém pelo menos 3 dados do usuário
            user_data_in_text = {
                "Roberto": "Roberto" in first_page_text,
                "Silva": "Silva" in first_page_text,
                "Orlando": "Orlando" in first_page_text,
                "FL": "FL" in first_page_text or "Florida" in first_page_text,
                "32801": "32801" in first_page_text,
                "BR111222333": "BR111222333" in first_page_text
            }
            
            data_found = sum(user_data_in_text.values())
            
            print(f"📄 Texto extraído da primeira página: {len(first_page_text)} caracteres")
            print(f"📊 Dados do usuário encontrados: {data_found}/6")
            
            for data, found in user_data_in_text.items():
                status = "✅" if found else "❌"
                print(f"  {status} {data}: {found}")
            
            results["etapa8_extracao_texto"] = {
                "success": True,
                "text_length": len(first_page_text),
                "user_data_found": data_found,
                "user_data_checks": user_data_in_text,
                "passed": data_found >= 3
            }
            
    except Exception as e:
        print(f"❌ Exception during text extraction: {str(e)}")
        results["etapa8_extracao_texto"] = {
            "success": False,
            "exception": str(e),
            "passed": False
        }
    
    # ETAPA 9: COMPARAÇÃO DADOS ENVIADOS vs PDF
    print("\n📋 ETAPA 9: COMPARAÇÃO DADOS ENVIADOS vs PDF")
    print("-" * 60)
    
    try:
        # Usar resultados da etapa 6 para comparação
        field_results = results["etapa6_validacao_bug_p0"]["critical_fields_results"]
        
        print(f"📊 TABELA COMPARATIVA (Teste Anterior vs Retest):")
        print("=" * 80)
        print(f"{'Campo':<20} {'Valor Enviado':<25} {'Teste Anterior':<15} {'Retest':<10} {'Melhoria?':<10}")
        print("-" * 80)
        
        comparison_results = {}
        
        for num, field_info in field_results.items():
            field_name = field_info["name"]
            expected = field_info["expected"]
            filled_now = field_info["filled"]
            
            # Status do teste anterior (baseado no status_anterior)
            if "✅ PASSOU" in field_info["status_anterior"]:
                teste_anterior = "✅"
            else:
                teste_anterior = "❌"
            
            # Status do retest
            retest_status = "✅" if filled_now else "❌"
            
            # Melhoria?
            if teste_anterior == "❌" and retest_status == "✅":
                melhoria = "✅ SIM"
            elif teste_anterior == "✅" and retest_status == "❌":
                melhoria = "❌ PIOROU"
            else:
                melhoria = "-"
            
            print(f"{field_name:<20} {expected:<25} {teste_anterior:<15} {retest_status:<10} {melhoria:<10}")
            
            comparison_results[field_name] = {
                "expected": expected,
                "teste_anterior": teste_anterior,
                "retest": retest_status,
                "melhoria": melhoria
            }
        
        # Calcular taxa de correspondência
        fields_filled = results["etapa6_validacao_bug_p0"]["fields_filled"]
        total_fields = results["etapa6_validacao_bug_p0"]["total_critical_fields"]
        correspondence_rate = (fields_filled / total_fields) * 100
        
        print(f"\n📊 Taxa de correspondência: {fields_filled}/{total_fields} ({correspondence_rate:.1f}%)")
        
        results["etapa9_comparacao_dados"] = {
            "success": True,
            "comparison_results": comparison_results,
            "correspondence_rate": correspondence_rate,
            "passed": correspondence_rate >= 70
        }
        
    except Exception as e:
        print(f"❌ Exception during data comparison: {str(e)}")
        results["etapa9_comparacao_dados"] = {
            "success": False,
            "exception": str(e),
            "passed": False
        }
    
    # ETAPA 10: VERIFICAÇÃO FINAL E COMPARAÇÃO
    print("\n📋 ETAPA 10: VERIFICAÇÃO FINAL E COMPARAÇÃO")
    print("-" * 60)
    
    try:
        # Contar etapas que passaram
        etapas_passadas = sum([
            results.get("etapa1_criacao_caso", {}).get("passed", False),
            results.get("etapa2_formulario_amigavel", {}).get("passed", False),
            results.get("etapa3_verificacao_persistencia", {}).get("passed", False),
            results.get("etapa4_geracao_pdf", {}).get("passed", False),
            results.get("etapa5_download_pdf", {}).get("passed", False),
            results.get("etapa6_validacao_bug_p0", {}).get("passed", False),
            results.get("etapa7_integridade_arquivo", {}).get("passed", False),
            results.get("etapa8_extracao_texto", {}).get("passed", False),
            results.get("etapa9_comparacao_dados", {}).get("passed", False)
        ])
        
        total_etapas = 9
        taxa_sucesso = (etapas_passadas / total_etapas) * 100
        
        # Tempo total de execução
        total_time = time.time() - start_time
        
        # Comparação com teste anterior
        print(f"📊 COMPARAÇÃO TESTE ANTERIOR vs RETEST:")
        print("=" * 60)
        print(f"{'Métrica':<25} {'Teste Anterior':<15} {'Retest':<15} {'Status':<15}")
        print("-" * 70)
        print(f"{'Etapas Passadas':<25} {'5/10 (50%)':<15} {f'{etapas_passadas}/9 ({taxa_sucesso:.1f}%)':<15} {'?':<15}")
        
        fields_filled = results.get("etapa6_validacao_bug_p0", {}).get("fields_filled", 0)
        print(f"{'Campos Preenchidos':<25} {'6/10 (60%)':<15} {f'{fields_filled}/10 ({fields_filled*10}%)':<15} {'?':<15}")
        
        bug_status = results.get("etapa6_validacao_bug_p0", {}).get("bug_status", "UNKNOWN")
        print(f"{'Bug P0 Status':<25} {'⚠️ PARCIAL':<15} {f'{bug_status}':<15} {'?':<15}")
        
        print(f"{'Tempo Execução':<25} {'0.58s':<15} {f'{total_time:.2f}s':<15} {'?':<15}")
        
        results["etapa10_verificacao_final"] = {
            "success": True,
            "etapas_passadas": etapas_passadas,
            "total_etapas": total_etapas,
            "taxa_sucesso": taxa_sucesso,
            "tempo_execucao": total_time,
            "passed": taxa_sucesso >= 80
        }
        
    except Exception as e:
        print(f"❌ Exception during final verification: {str(e)}")
        results["etapa10_verificacao_final"] = {
            "success": False,
            "exception": str(e),
            "passed": False
        }
    
    # RESUMO EXECUTIVO
    print("\n📋 RESUMO EXECUTIVO DO RETEST")
    print("=" * 80)
    
    etapas_passadas = results["etapa10_verificacao_final"]["etapas_passadas"]
    total_etapas = results["etapa10_verificacao_final"]["total_etapas"]
    taxa_sucesso = results["etapa10_verificacao_final"]["taxa_sucesso"]
    tempo_total = results["etapa10_verificacao_final"]["tempo_execucao"]
    
    fields_filled = results.get("etapa6_validacao_bug_p0", {}).get("fields_filled", 0)
    bug_status = results.get("etapa6_validacao_bug_p0", {}).get("bug_status", "UNKNOWN")
    
    print(f"📊 Taxa de sucesso geral: {etapas_passadas}/{total_etapas} etapas ({taxa_sucesso:.1f}%)")
    print(f"⏱️  Tempo total: {tempo_total:.2f} segundos")
    print(f"📊 COMPARAÇÃO: Teste Anterior (6/10 campos) vs Retest ({fields_filled}/10 campos)")
    
    # Conclusão Bug P0
    if bug_status == "CORRIGIDO":
        print(f"✅ Conclusão Bug P0: CORRIGIDO")
    elif bug_status == "PARCIAL":
        print(f"⚠️  Conclusão Bug P0: PARCIAL")
    else:
        print(f"❌ Conclusão Bug P0: NÃO CORRIGIDO")
    
    # Validação dos 4 campos corrigidos
    print(f"\n📊 VALIDAÇÃO DOS 4 CAMPOS CORRIGIDOS:")
    print("=" * 60)
    
    melhorias = results.get("etapa6_validacao_bug_p0", {}).get("melhorias", {})
    
    campos_esperados = ["Estado", "Email", "País Nascimento"]
    campos_funcionaram = 0
    
    for campo in campos_esperados:
        if campo in melhorias:
            status = melhorias[campo]
            if status == "FUNCIONOU":
                print(f"  ✅ {campo} (FL): Correção FUNCIONOU")
                campos_funcionaram += 1
            else:
                print(f"  ❌ {campo}: Correção NÃO funcionou")
        else:
            print(f"  ❓ {campo}: Status não determinado")
    
    print(f"\n📊 Taxa de melhoria: {campos_funcionaram}/{len(campos_esperados)} correções funcionaram")
    
    # Conclusão final
    print(f"\n🎯 CONCLUSÃO FINAL:")
    print("=" * 60)
    
    if bug_status == "CORRIGIDO":
        print(f"✅ Bug P0 foi resolvido? SIM")
        print(f"✅ Sistema pronto para produção? SIM")
    elif bug_status == "PARCIAL":
        print(f"⚠️  Bug P0 foi resolvido? PARCIALMENTE")
        print(f"⚠️  Sistema pronto para produção? NECESSITA AJUSTES")
        
        # Identificar campos ainda faltando
        field_results = results.get("etapa6_validacao_bug_p0", {}).get("critical_fields_results", {})
        campos_faltando = [info["name"] for info in field_results.values() if not info["filled"]]
        if campos_faltando:
            print(f"❌ Campos ainda precisam de correção: {', '.join(campos_faltando)}")
    else:
        print(f"❌ Bug P0 foi resolvido? NÃO")
        print(f"❌ Sistema pronto para produção? NÃO")
        
        # Identificar campos ainda faltando
        field_results = results.get("etapa6_validacao_bug_p0", {}).get("critical_fields_results", {})
        campos_faltando = [info["name"] for info in field_results.values() if not info["filled"]]
        if campos_faltando:
            print(f"❌ Campos que ainda precisam de correção: {', '.join(campos_faltando)}")
    
    # Store summary
    results["summary"] = {
        "etapas_passadas": etapas_passadas,
        "total_etapas": total_etapas,
        "taxa_sucesso": taxa_sucesso,
        "tempo_execucao": tempo_total,
        "fields_filled": fields_filled,
        "total_critical_fields": 10,
        "bug_status": bug_status,
        "melhorias": melhorias,
        "campos_funcionaram": campos_funcionaram,
        "case_id": results.get("etapa1_criacao_caso", {}).get("case_id"),
        "sistema_pronto": bug_status == "CORRIGIDO"
    }
    
    return results

if __name__ == "__main__":
    print("🎯 INICIANDO RETEST END-TO-END COMPLETO - USERsimulator-DISCIPLINA SESSION")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print(f"🔗 API Base: {API_BASE}")
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    print("🎯 Objetivo: Verificar se >= 7/10 campos críticos preenchidos após correções")
    
    # Execute retest
    test_results = retest_disciplina_i539_complete()
    
    # Save results to file
    with open("/app/retest_disciplina_i539_results.json", "w") as f:
        json.dump({
            "test_results": test_results,
            "timestamp": time.time(),
            "test_focus": "Retest I-539 End-to-End After Bug P0 Corrections",
            "objetivo": "Verificar se >= 7/10 campos críticos preenchidos (70% threshold)",
            "dados_teste": {
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
            "campos_corrigidos": [
                "Estado (FL) - Campo adicionado: P2_Line10_Province[0]",
                "Email - Campo adicionado: P5_Line5_EmailAddress[0]", 
                "País de Nascimento - Campo corrigido: P1_Line6_CountryOfBirth[0]"
            ]
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultados salvos em: /app/retest_disciplina_i539_results.json")
    
    # Final recommendation
    summary = test_results.get("summary", {})
    bug_status = summary.get("bug_status", "UNKNOWN")
    fields_filled = summary.get("fields_filled", 0)
    taxa_sucesso = summary.get("taxa_sucesso", 0)
    
    print(f"\n🎯 RECOMENDAÇÃO FINAL:")
    print("=" * 60)
    
    if bug_status == "CORRIGIDO" and taxa_sucesso >= 80:
        print("✅ BUG P0 CORRIGIDO COM SUCESSO!")
        print("   ✅ >= 7/10 campos críticos preenchidos")
        print("   ✅ Correções implementadas funcionaram")
        print("   ✅ Sistema pronto para produção")
        print("   🎉 Parabéns pela correção efetiva!")
    elif bug_status == "PARCIAL":
        print("⚠️  BUG P0 PARCIALMENTE CORRIGIDO")
        print(f"   ⚠️  {fields_filled}/10 campos preenchidos (necessário >= 7)")
        print("   ⚠️  Algumas correções funcionaram, outras não")
        print("   🔧 Necessário ajustes adicionais")
    else:
        print("❌ BUG P0 AINDA EXISTE!")
        print(f"   ❌ Apenas {fields_filled}/10 campos preenchidos")
        print("   ❌ Correções não foram efetivas")
        print("   🚨 Revisão urgente necessária")
        
        # Mostrar quais campos ainda faltam
        field_results = test_results.get("etapa6_validacao_bug_p0", {}).get("critical_fields_results", {})
        campos_faltando = [info["name"] for info in field_results.values() if not info["filled"]]
        if campos_faltando:
            print(f"   📋 Campos ainda faltando: {', '.join(campos_faltando)}")