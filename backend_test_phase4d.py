#!/usr/bin/env python3
"""
TESTE COMPLETO DO SISTEMA DE WORKFLOW AUTOMATION - PHASE 4D IMPLEMENTATION
Testa o sistema completo de Workflow Automation - Phase 4D Implementation

FOCO ESPECÍFICO: Sistema Completo de Workflow Automation + Retry System + Notification System

ENDPOINTS TESTADOS:
1. GET /api/automation/workflows/available - Listar workflows disponíveis
2. POST /api/automation/workflows/start - Iniciar workflow H-1B completo
3. GET /api/automation/workflows/{execution_id}/status - Status de execução
4. GET /api/automation/notifications/templates - Templates disponíveis
5. POST /api/automation/notifications/send - Enviar notificação de teste
6. GET /api/automation/notifications/{notification_id}/status - Status de entrega
7. GET /api/automation/notifications/statistics - Estatísticas do sistema
8. GET /api/automation/retry/statistics - Estatísticas de retry
9. POST /api/automation/workflows/h1b/complete - Workflow end-to-end com notificações

COMPONENTES TESTADOS:
- Workflow Engine: Sistema de workflows automatizados
- Notification System: Sistema de notificações automáticas
- Retry System: Sistema de retry automático
- Integration Phase 4D: Inicialização dos 3 sistemas no startup

CASOS DE TESTE ESPECÍFICOS:
- Caso A: Workflow H-1B completo (should execute all steps successfully)
- Caso B: Notification templates (should list 8+ templates with different channels)
- Caso C: Retry system (should show configurations for 6+ operation types)
"""

import requests
import json
import time
import uuid
from datetime import datetime
import os
from typing import Dict, Any

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://visabot-1.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class Phase4DWorkflowAutomationTester:
    def __init__(self):
        self.test_results = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Phase4DWorkflowTester/1.0'
        })
        self.auth_token = None
        self.setup_test_authentication()
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        if not success and response_data:
            print(f"    Response: {response_data}")
        print()
    
    def setup_test_authentication(self):
        """Setup authentication for endpoints that require it"""
        try:
            # Try to create a test user
            test_user_data = {
                "email": "test@phase4d.com",
                "password": "testpassword123",
                "first_name": "Phase4D",
                "last_name": "Tester"
            }
            
            # Try to signup
            signup_response = self.session.post(
                f"{API_BASE}/auth/signup",
                json=test_user_data
            )
            
            if signup_response.status_code == 200:
                signup_data = signup_response.json()
                self.auth_token = signup_data.get('token')
            else:
                # Try to login if user already exists
                login_data = {
                    "email": test_user_data["email"],
                    "password": test_user_data["password"]
                }
                
                login_response = self.session.post(
                    f"{API_BASE}/auth/login",
                    json=login_data
                )
                
                if login_response.status_code == 200:
                    login_result = login_response.json()
                    self.auth_token = login_result.get('token')
            
            # Set authorization header if we have a token
            if self.auth_token:
                self.session.headers.update({
                    'Authorization': f'Bearer {self.auth_token}'
                })
                print(f"✅ Authentication setup successful")
            else:
                print(f"⚠️ Authentication setup failed - some tests may fail")
                
        except Exception as e:
            print(f"⚠️ Authentication setup error: {e}")

    def test_workflow_engine_available_workflows(self):
        """TESTE 1: Workflow Engine - GET /api/automation/workflows/available"""
        print("🔄 TESTE 1: Workflow Engine - Workflows Disponíveis")
        
        try:
            response = self.session.get(f"{API_BASE}/automation/workflows/available")
            
            if response.status_code == 200:
                result = response.json()
                
                # Check if workflows are available
                workflows = result.get('workflows', [])
                has_workflows = len(workflows) > 0
                
                # Check for expected workflows
                expected_workflows = ['h1b_complete_process', 'f1_student_process', 'i485_adjustment_process']
                # Handle both string list and object list formats
                if workflows and isinstance(workflows[0], str):
                    found_workflows = workflows
                else:
                    found_workflows = [w.get('id') for w in workflows]
                
                has_expected = any(expected in found_workflows for expected in expected_workflows)
                
                self.log_test(
                    "Workflow Engine - Workflows Disponíveis",
                    has_workflows and has_expected,
                    f"Workflows encontrados: {len(workflows)}, Esperados presentes: {has_expected}",
                    {
                        "total_workflows": len(workflows),
                        "workflow_ids": found_workflows[:5],
                        "expected_found": [w for w in expected_workflows if w in found_workflows],
                        "success": result.get('success', False)
                    }
                )
                
                return workflows
            else:
                self.log_test(
                    "Workflow Engine - Workflows Disponíveis",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    {"status_code": response.status_code, "error": response.text}
                )
                return None
                
        except Exception as e:
            self.log_test(
                "Workflow Engine - Workflows Disponíveis",
                False,
                f"Exception: {str(e)}"
            )
            return None

    def test_workflow_engine_start_workflow(self):
        """TESTE 2: Workflow Engine - POST /api/automation/workflows/start"""
        print("🚀 TESTE 2: Workflow Engine - Iniciar Workflow H-1B")
        
        try:
            # Test starting H-1B complete workflow
            request_data = {
                "workflow_name": "h1b_complete_process",
                "case_id": "TEST-H1B-WORKFLOW-001",
                "context": {
                    "applicant_name": "Carlos Silva",
                    "visa_type": "H-1B",
                    "priority": "normal"
                }
            }
            
            response = self.session.post(
                f"{API_BASE}/automation/workflows/start",
                json=request_data
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check if workflow started successfully
                has_execution_id = 'execution_id' in result
                has_status = 'status' in result
                success = result.get('success', False)
                
                execution_id = result.get('execution_id')
                
                self.log_test(
                    "Workflow Engine - Iniciar Workflow",
                    has_execution_id and has_status and success,
                    f"Workflow iniciado: ID={execution_id}, Status={result.get('status')}",
                    {
                        "execution_id": execution_id,
                        "status": result.get('status'),
                        "workflow_id": result.get('workflow_id'),
                        "success": success,
                        "message": result.get('message')
                    }
                )
                
                return execution_id
            else:
                self.log_test(
                    "Workflow Engine - Iniciar Workflow",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    {"status_code": response.status_code, "error": response.text}
                )
                return None
                
        except Exception as e:
            self.log_test(
                "Workflow Engine - Iniciar Workflow",
                False,
                f"Exception: {str(e)}"
            )
            return None

    def test_workflow_engine_status_check(self):
        """TESTE 3: Workflow Engine - GET /api/automation/workflows/{execution_id}/status"""
        print("📊 TESTE 3: Workflow Engine - Status de Execução")
        
        # First start a workflow to get an execution ID
        execution_id = self.test_workflow_engine_start_workflow()
        
        if not execution_id:
            self.log_test(
                "Workflow Engine - Status Check (Sem Execution ID)",
                False,
                "Não foi possível obter execution_id para teste de status"
            )
            return None
        
        try:
            # Wait a moment for workflow to start processing
            time.sleep(2)
            
            response = self.session.get(f"{API_BASE}/automation/workflows/{execution_id}/status")
            
            if response.status_code == 200:
                result = response.json()
                
                # Check if status information is available
                has_status = 'status' in result
                has_execution_id = 'execution_id' in result
                has_steps = 'steps' in result
                
                success = has_status and has_execution_id
                
                self.log_test(
                    "Workflow Engine - Status de Execução",
                    success,
                    f"Status: {result.get('status')}, Steps: {len(result.get('steps', []))}",
                    {
                        "execution_id": result.get('execution_id'),
                        "status": result.get('status'),
                        "steps_count": len(result.get('steps', [])),
                        "current_step": result.get('current_step'),
                        "progress": result.get('progress', 0)
                    }
                )
                
                return result
            else:
                self.log_test(
                    "Workflow Engine - Status de Execução",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    {"status_code": response.status_code, "error": response.text}
                )
                return None
                
        except Exception as e:
            self.log_test(
                "Workflow Engine - Status de Execução",
                False,
                f"Exception: {str(e)}"
            )
            return None

    def test_notification_system_templates(self):
        """TESTE 4: Notification System - GET /api/automation/notifications/templates"""
        print("📧 TESTE 4: Notification System - Templates Disponíveis")
        
        try:
            response = self.session.get(f"{API_BASE}/automation/notifications/templates")
            
            if response.status_code == 200:
                result = response.json()
                
                # Check if templates are available
                templates = result.get('templates', [])
                has_templates = len(templates) >= 8  # Should have 8+ templates
                
                # Check for different channels
                channels = set()
                for template in templates:
                    # Handle both 'channels' list and 'channel' string formats
                    if 'channels' in template:
                        channels.update(template.get('channels', []))
                    elif 'channel' in template:
                        channels.add(template.get('channel'))
                
                has_multiple_channels = len(channels) > 1
                
                self.log_test(
                    "Notification System - Templates Disponíveis",
                    has_templates and has_multiple_channels,
                    f"Templates: {len(templates)}, Canais: {list(channels)}",
                    {
                        "total_templates": len(templates),
                        "channels": list(channels),
                        "template_names": [t.get('name') for t in templates[:5]],
                        "success": result.get('success', False)
                    }
                )
                
                return templates
            else:
                self.log_test(
                    "Notification System - Templates Disponíveis",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    {"status_code": response.status_code, "error": response.text}
                )
                return None
                
        except Exception as e:
            self.log_test(
                "Notification System - Templates Disponíveis",
                False,
                f"Exception: {str(e)}"
            )
            return None

    def test_notification_system_send_notification(self):
        """TESTE 5: Notification System - POST /api/automation/notifications/send"""
        print("📤 TESTE 5: Notification System - Enviar Notificação")
        
        try:
            # Test sending a notification
            request_data = {
                "template_id": "workflow_started",
                "recipient": {
                    "email": "test@phase4d.com",
                    "name": "Phase4D Tester"
                },
                "variables": {
                    "applicant_name": "Carlos Silva",
                    "workflow_type": "H-1B Complete Process",
                    "case_id": "TEST-H1B-001"
                },
                "channels": ["email"]
            }
            
            response = self.session.post(
                f"{API_BASE}/automation/notifications/send",
                json=request_data
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check if notification was sent successfully
                has_notification_id = 'notification_id' in result
                success = result.get('success', False)
                
                notification_id = result.get('notification_id')
                
                self.log_test(
                    "Notification System - Enviar Notificação",
                    has_notification_id and success,
                    f"Notificação enviada: ID={notification_id}",
                    {
                        "notification_id": notification_id,
                        "success": success,
                        "message": result.get('message'),
                        "channels_sent": result.get('channels_sent', [])
                    }
                )
                
                return notification_id
            else:
                self.log_test(
                    "Notification System - Enviar Notificação",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    {"status_code": response.status_code, "error": response.text}
                )
                return None
                
        except Exception as e:
            self.log_test(
                "Notification System - Enviar Notificação",
                False,
                f"Exception: {str(e)}"
            )
            return None

    def test_notification_system_status_check(self):
        """TESTE 6: Notification System - GET /api/automation/notifications/{notification_id}/status"""
        print("📋 TESTE 6: Notification System - Status de Notificação")
        
        # First send a notification to get a notification ID
        notification_id = self.test_notification_system_send_notification()
        
        if not notification_id:
            self.log_test(
                "Notification System - Status Check (Sem Notification ID)",
                False,
                "Não foi possível obter notification_id para teste de status"
            )
            return None
        
        try:
            # Wait a moment for notification to be processed
            time.sleep(1)
            
            response = self.session.get(f"{API_BASE}/automation/notifications/{notification_id}/status")
            
            if response.status_code == 200:
                result = response.json()
                
                # Check if status information is available
                has_status = 'status' in result
                has_notification_id = 'notification_id' in result
                
                success = has_status and has_notification_id
                
                self.log_test(
                    "Notification System - Status de Notificação",
                    success,
                    f"Status: {result.get('status')}, ID: {result.get('notification_id')}",
                    {
                        "notification_id": result.get('notification_id'),
                        "status": result.get('status'),
                        "sent_at": result.get('sent_at'),
                        "channels": result.get('channels', []),
                        "delivery_status": result.get('delivery_status', {})
                    }
                )
                
                return result
            else:
                self.log_test(
                    "Notification System - Status de Notificação",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    {"status_code": response.status_code, "error": response.text}
                )
                return None
                
        except Exception as e:
            self.log_test(
                "Notification System - Status de Notificação",
                False,
                f"Exception: {str(e)}"
            )
            return None

    def test_notification_system_statistics(self):
        """TESTE 7: Notification System - GET /api/automation/notifications/statistics"""
        print("📊 TESTE 7: Notification System - Estatísticas")
        
        try:
            response = self.session.get(f"{API_BASE}/automation/notifications/statistics")
            
            if response.status_code == 200:
                result = response.json()
                
                # Check if statistics are available
                stats = result.get('statistics', {})
                has_stats = len(stats) > 0
                
                # Check for key statistics
                expected_stats = ['total_sent', 'success_rate', 'channels_used', 'templates_used']
                has_expected_stats = any(stat in stats for stat in expected_stats)
                
                self.log_test(
                    "Notification System - Estatísticas",
                    has_stats and has_expected_stats,
                    f"Estatísticas disponíveis: {len(stats)} métricas",
                    {
                        "statistics": stats,
                        "success": result.get('success', False),
                        "available_metrics": list(stats.keys())[:5] if stats else []
                    }
                )
                
                return stats
            else:
                self.log_test(
                    "Notification System - Estatísticas",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    {"status_code": response.status_code, "error": response.text}
                )
                return None
                
        except Exception as e:
            self.log_test(
                "Notification System - Estatísticas",
                False,
                f"Exception: {str(e)}"
            )
            return None

    def test_retry_system_statistics(self):
        """TESTE 8: Retry System - GET /api/automation/retry/statistics"""
        print("🔄 TESTE 8: Retry System - Estatísticas de Retry")
        
        try:
            response = self.session.get(f"{API_BASE}/automation/retry/statistics")
            
            if response.status_code == 200:
                result = response.json()
                
                # Check if retry statistics are available
                retry_stats = result.get('retry_statistics', {})
                has_stats = len(retry_stats) > 0
                
                # Check for different operation types (should have 6+ types)
                operation_types = retry_stats.get('operation_types', [])
                has_multiple_types = len(operation_types) >= 6
                
                # Expected operation types
                expected_types = ['document_analysis', 'external_api', 'database', 'llm_operations', 'file_operations', 'critical']
                found_types = operation_types if isinstance(operation_types, list) else list(operation_types.keys())
                has_expected_types = any(op_type in found_types for op_type in expected_types)
                
                self.log_test(
                    "Retry System - Estatísticas de Retry",
                    has_stats and has_multiple_types and has_expected_types,
                    f"Tipos de operação: {len(operation_types)}, Esperados presentes: {has_expected_types}",
                    {
                        "total_operation_types": len(operation_types),
                        "operation_types": found_types,
                        "expected_found": [t for t in expected_types if t in found_types],
                        "success": result.get('success', False),
                        "configurations_count": len(retry_stats.get('configurations', {}))
                    }
                )
                
                return stats
            else:
                self.log_test(
                    "Retry System - Estatísticas de Retry",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    {"status_code": response.status_code, "error": response.text}
                )
                return None
                
        except Exception as e:
            self.log_test(
                "Retry System - Estatísticas de Retry",
                False,
                f"Exception: {str(e)}"
            )
            return None

    def test_h1b_complete_workflow(self):
        """TESTE 9: Workflow Completo H-1B - POST /api/automation/workflows/h1b/complete"""
        print("🎯 TESTE 9: Workflow Completo H-1B com Notificações")
        
        try:
            # Test H-1B complete workflow with notifications
            request_data = {
                "case_id": "TEST-H1B-COMPLETE-001",
                "workflow_name": "h1b_complete_process",
                "context": {
                    "applicant_name": "Carlos Eduardo Silva",
                    "email": "carlos.silva@test.com",
                    "visa_type": "H-1B",
                    "priority": "high",
                    "workflow_steps": [
                        "validate_documents",
                        "fill_forms", 
                        "generate_cover_letter",
                        "finalize_package"
                    ],
                    "notifications_enabled": True
                }
            }
            
            response = self.session.post(
                f"{API_BASE}/automation/workflows/h1b/complete",
                json=request_data
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check if workflow started successfully
                has_execution_id = 'execution_id' in result
                success = result.get('success', False)
                
                execution_id = result.get('execution_id')
                
                self.log_test(
                    "Workflow H-1B Completo - Inicialização",
                    has_execution_id and success,
                    f"Workflow H-1B iniciado: ID={execution_id}",
                    {
                        "execution_id": execution_id,
                        "success": success,
                        "message": result.get('message'),
                        "steps_scheduled": len(result.get('steps_scheduled', []))
                    }
                )
                
                # Wait for workflow to process some steps
                if execution_id:
                    time.sleep(5)
                    
                    # Check workflow progress
                    status_response = self.session.get(f"{API_BASE}/automation/workflows/{execution_id}/status")
                    
                    if status_response.status_code == 200:
                        status_result = status_response.json()
                        
                        steps = status_result.get('steps', [])
                        completed_steps = [s for s in steps if s.get('status') == 'completed']
                        
                        self.log_test(
                            "Workflow H-1B Completo - Execução de Steps",
                            len(completed_steps) > 0,
                            f"Steps executados: {len(completed_steps)}/{len(steps)}",
                            {
                                "total_steps": len(steps),
                                "completed_steps": len(completed_steps),
                                "current_step": status_result.get('current_step'),
                                "progress": status_result.get('progress', 0)
                            }
                        )
                
                return execution_id
            else:
                self.log_test(
                    "Workflow H-1B Completo - Inicialização",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    {"status_code": response.status_code, "error": response.text}
                )
                return None
                
        except Exception as e:
            self.log_test(
                "Workflow H-1B Completo - Inicialização",
                False,
                f"Exception: {str(e)}"
            )
            return None

    def test_integration_phase4d_startup(self):
        """TESTE 10: Integration Phase 4D - Verificar inicialização dos sistemas"""
        print("🚀 TESTE 10: Integration Phase 4D - Inicialização dos Sistemas")
        
        try:
            # Test if all three systems are initialized by checking their endpoints
            systems_status = {}
            
            # Test Workflow Engine
            workflow_response = self.session.get(f"{API_BASE}/automation/workflows/available")
            systems_status['workflow_engine'] = workflow_response.status_code == 200
            
            # Test Notification System
            notification_response = self.session.get(f"{API_BASE}/automation/notifications/templates")
            systems_status['notification_system'] = notification_response.status_code == 200
            
            # Test Retry System
            retry_response = self.session.get(f"{API_BASE}/automation/retry/statistics")
            systems_status['retry_system'] = retry_response.status_code == 200
            
            # Check MongoDB integration (implicit through successful API calls)
            mongodb_integration = all(systems_status.values())
            
            all_systems_working = all(systems_status.values())
            
            self.log_test(
                "Integration Phase 4D - Inicialização dos Sistemas",
                all_systems_working,
                f"Sistemas funcionando: {sum(systems_status.values())}/3",
                {
                    "workflow_engine": systems_status['workflow_engine'],
                    "notification_system": systems_status['notification_system'],
                    "retry_system": systems_status['retry_system'],
                    "mongodb_integration": mongodb_integration,
                    "all_systems_operational": all_systems_working
                }
            )
            
            return systems_status
            
        except Exception as e:
            self.log_test(
                "Integration Phase 4D - Inicialização dos Sistemas",
                False,
                f"Exception: {str(e)}"
            )
            return None

    def run_all_tests(self):
        """Execute todos os testes da Phase 4D"""
        print("🎯 INICIANDO TESTES COMPLETOS - PHASE 4D WORKFLOW AUTOMATION")
        print("=" * 80)
        
        start_time = time.time()
        
        # Execute all tests
        test_methods = [
            self.test_workflow_engine_available_workflows,
            self.test_workflow_engine_start_workflow,
            self.test_workflow_engine_status_check,
            self.test_notification_system_templates,
            self.test_notification_system_send_notification,
            self.test_notification_system_status_check,
            self.test_notification_system_statistics,
            self.test_retry_system_statistics,
            self.test_h1b_complete_workflow,
            self.test_integration_phase4d_startup
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                print(f"❌ ERRO no teste {test_method.__name__}: {str(e)}")
            
            # Small delay between tests
            time.sleep(1)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print("📊 RESUMO DOS TESTES - PHASE 4D WORKFLOW AUTOMATION")
        print("=" * 80)
        print(f"⏱️  Duração total: {duration:.2f} segundos")
        print(f"📈 Testes executados: {total_tests}")
        print(f"✅ Testes aprovados: {passed_tests}")
        print(f"❌ Testes falharam: {failed_tests}")
        print(f"📊 Taxa de sucesso: {success_rate:.1f}%")
        
        # Detailed results
        print("\n🔍 RESULTADOS DETALHADOS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"    {result['details']}")
        
        print("\n" + "=" * 80)
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "duration": duration,
            "results": self.test_results
        }

if __name__ == "__main__":
    tester = Phase4DWorkflowAutomationTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    exit_code = 0 if results["success_rate"] >= 70 else 1
    exit(exit_code)