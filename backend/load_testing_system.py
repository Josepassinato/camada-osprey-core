"""
Load Testing System - Phase 4B
Sistema automatizado de teste de carga para APIs e serviços
"""

import asyncio
import aiohttp
import time
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import statistics
from concurrent.futures import ThreadPoolExecutor
import uuid
import random

logger = logging.getLogger(__name__)

@dataclass
class LoadTestConfig:
    """Configuração de teste de carga"""
    test_name: str
    target_endpoint: str
    method: str = "GET"
    headers: Dict[str, str] = field(default_factory=dict)
    payload: Optional[Dict[str, Any]] = None
    concurrent_users: int = 10
    duration_seconds: int = 60
    ramp_up_seconds: int = 10
    think_time_ms: int = 1000
    success_criteria: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LoadTestResult:
    """Resultado de um teste de carga individual"""
    request_id: str
    endpoint: str
    method: str
    status_code: int
    response_time_ms: float
    timestamp: datetime
    success: bool
    error_message: Optional[str] = None
    response_size: int = 0

@dataclass
class LoadTestSummary:
    """Resumo de um teste de carga"""
    test_name: str
    start_time: datetime
    end_time: datetime
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    percentile_95: float
    percentile_99: float
    requests_per_second: float
    success_rate: float
    error_distribution: Dict[str, int]
    performance_grade: str

class LoadTestingSystem:
    """
    Sistema automatizado de teste de carga
    """
    
    def __init__(self):
        self.active_tests: Dict[str, bool] = {}
        self.test_results: Dict[str, List[LoadTestResult]] = {}
        self.test_summaries: Dict[str, LoadTestSummary] = {}
        
        # Configurações de teste padrão para diferentes cenários
        self.default_configs = {
            # Teste de APIs críticas
            "api_critical": LoadTestConfig(
                test_name="API Critical Endpoints",
                target_endpoint="/api/documents/analyze-with-ai",
                method="POST",
                concurrent_users=20,
                duration_seconds=300,  # 5 minutos
                success_criteria={
                    "max_avg_response_time": 3000,  # 3 segundos
                    "min_success_rate": 0.95,
                    "max_error_rate": 0.05
                }
            ),
            
            # Teste de workflow automation
            "workflow_stress": LoadTestConfig(
                test_name="Workflow Automation Stress",
                target_endpoint="/api/automation/workflows/start",
                method="POST",
                concurrent_users=50,
                duration_seconds=180,  # 3 minutos
                success_criteria={
                    "max_avg_response_time": 2000,
                    "min_success_rate": 0.90
                }
            ),
            
            # Teste de dashboard analytics
            "dashboard_load": LoadTestConfig(
                test_name="Dashboard Analytics Load",
                target_endpoint="/api/analytics/dashboard",
                method="GET",
                concurrent_users=100,
                duration_seconds=120,  # 2 minutos
                think_time_ms=500,
                success_criteria={
                    "max_avg_response_time": 1500,
                    "min_success_rate": 0.98
                }
            ),
            
            # Teste de notificações
            "notification_burst": LoadTestConfig(
                test_name="Notification System Burst",
                target_endpoint="/api/automation/notifications/send",
                method="POST",
                concurrent_users=30,
                duration_seconds=60,
                success_criteria={
                    "max_avg_response_time": 1000,
                    "min_success_rate": 0.92
                }
            )
        }
    
    async def run_load_test(self, config: LoadTestConfig, base_url: str = "http://localhost:8001") -> str:
        """
        Executa teste de carga baseado na configuração
        """
        test_id = str(uuid.uuid4())
        self.active_tests[test_id] = True
        self.test_results[test_id] = []
        
        logger.info(f"🚀 Starting load test: {config.test_name} (ID: {test_id})")
        
        start_time = datetime.now(timezone.utc)
        
        try:
            # Executar teste com usuários concorrentes
            await self._execute_concurrent_load(config, base_url, test_id)
            
            end_time = datetime.now(timezone.utc)
            
            # Gerar resumo
            summary = self._generate_test_summary(config, test_id, start_time, end_time)
            self.test_summaries[test_id] = summary
            
            logger.info(f"✅ Load test completed: {config.test_name}")
            logger.info(f"📊 Results: {summary.success_rate:.1%} success, {summary.avg_response_time:.0f}ms avg")
            
            return test_id
            
        except Exception as e:
            logger.error(f"❌ Load test failed: {e}")
            self.active_tests[test_id] = False
            raise
        finally:
            self.active_tests[test_id] = False
    
    async def _execute_concurrent_load(self, config: LoadTestConfig, base_url: str, test_id: str):
        """
        Executa carga concorrente com ramp-up gradual
        """
        # Calcular timing
        total_duration = config.duration_seconds
        ramp_up_duration = config.ramp_up_seconds
        users_per_second = config.concurrent_users / ramp_up_duration if ramp_up_duration > 0 else config.concurrent_users
        
        # Semáforo para controlar concorrência
        semaphore = asyncio.Semaphore(config.concurrent_users)
        
        # Lista de tasks
        tasks = []
        
        # Ramp-up gradual
        for second in range(total_duration):
            if not self.active_tests.get(test_id, False):
                break
            
            # Calcular quantos usuários devem estar ativos neste segundo
            if second < ramp_up_duration:
                active_users = int(users_per_second * (second + 1))
            else:
                active_users = config.concurrent_users
            
            # Criar tasks para usuários ativos
            current_tasks = len([t for t in tasks if not t.done()])
            new_users_needed = active_users - current_tasks
            
            for _ in range(max(0, new_users_needed)):
                task = asyncio.create_task(
                    self._simulate_user_session(config, base_url, test_id, semaphore)
                )
                tasks.append(task)
            
            await asyncio.sleep(1)
        
        # Aguardar conclusão de todos os tasks
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _simulate_user_session(self, config: LoadTestConfig, base_url: str, test_id: str, semaphore: asyncio.Semaphore):
        """
        Simula sessão de usuário individual
        """
        async with semaphore:
            session_start = time.time()
            session_duration = random.uniform(10, config.duration_seconds)  # Sessão varia de 10s até duração total
            
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                connector=aiohttp.TCPConnector(limit=100)
            ) as session:
                
                while time.time() - session_start < session_duration and self.active_tests.get(test_id, False):
                    try:
                        # Executar request
                        result = await self._execute_request(config, base_url, session)
                        self.test_results[test_id].append(result)
                        
                        # Think time (tempo entre requests)
                        if config.think_time_ms > 0:
                            await asyncio.sleep(config.think_time_ms / 1000.0)
                            
                    except Exception as e:
                        # Registrar erro
                        error_result = LoadTestResult(
                            request_id=str(uuid.uuid4()),
                            endpoint=config.target_endpoint,
                            method=config.method,
                            status_code=0,
                            response_time_ms=0,
                            timestamp=datetime.now(timezone.utc),
                            success=False,
                            error_message=str(e)
                        )
                        self.test_results[test_id].append(error_result)
                        
                        # Pequena pausa em caso de erro
                        await asyncio.sleep(1)
    
    async def _execute_request(self, config: LoadTestConfig, base_url: str, session: aiohttp.ClientSession) -> LoadTestResult:
        """
        Executa request individual e mede performance
        """
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Preparar URL e payload
        url = f"{base_url}{config.target_endpoint}"
        headers = config.headers.copy()
        headers.setdefault('Content-Type', 'application/json')
        
        # Gerar payload dinâmico se necessário
        payload = config.payload
        if config.method == "POST" and not payload:
            payload = self._generate_test_payload(config.target_endpoint)
        
        try:
            # Executar request
            if config.method.upper() == "GET":
                async with session.get(url, headers=headers) as response:
                    response_text = await response.text()
                    response_size = len(response_text.encode('utf-8'))
            else:
                async with session.post(url, json=payload, headers=headers) as response:
                    response_text = await response.text()
                    response_size = len(response_text.encode('utf-8'))
            
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            
            # Determinar sucesso
            success = 200 <= response.status < 400
            
            return LoadTestResult(
                request_id=request_id,
                endpoint=config.target_endpoint,
                method=config.method,
                status_code=response.status,
                response_time_ms=response_time_ms,
                timestamp=datetime.now(timezone.utc),
                success=success,
                response_size=response_size,
                error_message=None if success else f"HTTP {response.status}"
            )
            
        except Exception as e:
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            
            return LoadTestResult(
                request_id=request_id,
                endpoint=config.target_endpoint,
                method=config.method,
                status_code=0,
                response_time_ms=response_time_ms,
                timestamp=datetime.now(timezone.utc),
                success=False,
                error_message=str(e)
            )
    
    def _generate_test_payload(self, endpoint: str) -> Dict[str, Any]:
        """
        Gera payload de teste baseado no endpoint
        """
        if "documents/analyze" in endpoint:
            return {
                "document_type": "passport",
                "visa_type": "H-1B",
                "applicant_name": f"Test User {random.randint(1000, 9999)}",
                "file_data": "test_file_data_base64",
                "filename": f"test_document_{uuid.uuid4().hex[:8]}.pdf"
            }
        
        elif "workflows/start" in endpoint:
            return {
                "workflow_name": random.choice(["h1b_complete_process", "f1_student_process"]),
                "case_id": f"LOAD_TEST_{uuid.uuid4().hex[:8]}",
                "context": {"load_test": True}
            }
        
        elif "notifications/send" in endpoint:
            return {
                "template_id": "workflow_started",
                "recipient": {
                    "user_id": f"load_test_user_{random.randint(1, 1000)}",
                    "name": f"Load Test User {random.randint(1, 1000)}",
                    "email": f"loadtest{random.randint(1, 1000)}@example.com"
                },
                "variables": {"case_id": f"LOAD_TEST_{uuid.uuid4().hex[:8]}"}
            }
        
        else:
            return {"test": True, "timestamp": datetime.now().isoformat()}
    
    def _generate_test_summary(self, config: LoadTestConfig, test_id: str, start_time: datetime, end_time: datetime) -> LoadTestSummary:
        """
        Gera resumo estatístico do teste
        """
        results = self.test_results[test_id]
        
        if not results:
            return LoadTestSummary(
                test_name=config.test_name,
                start_time=start_time,
                end_time=end_time,
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                avg_response_time=0,
                min_response_time=0,
                max_response_time=0,
                percentile_95=0,
                percentile_99=0,
                requests_per_second=0,
                success_rate=0,
                error_distribution={},
                performance_grade="F"
            )
        
        # Calcular estatísticas
        total_requests = len(results)
        successful_requests = len([r for r in results if r.success])
        failed_requests = total_requests - successful_requests
        
        response_times = [r.response_time_ms for r in results if r.success]
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            percentile_95 = statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max_response_time
            percentile_99 = statistics.quantiles(response_times, n=100)[98] if len(response_times) >= 100 else max_response_time
        else:
            avg_response_time = min_response_time = max_response_time = percentile_95 = percentile_99 = 0
        
        # Calcular RPS
        duration = (end_time - start_time).total_seconds()
        requests_per_second = total_requests / duration if duration > 0 else 0
        
        # Taxa de sucesso
        success_rate = successful_requests / total_requests if total_requests > 0 else 0
        
        # Distribuição de erros
        error_distribution = {}
        for result in results:
            if not result.success:
                error = result.error_message or f"HTTP {result.status_code}"
                error_distribution[error] = error_distribution.get(error, 0) + 1
        
        # Calcular grade de performance
        performance_grade = self._calculate_performance_grade(config, success_rate, avg_response_time)
        
        return LoadTestSummary(
            test_name=config.test_name,
            start_time=start_time,
            end_time=end_time,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            percentile_95=percentile_95,
            percentile_99=percentile_99,
            requests_per_second=requests_per_second,
            success_rate=success_rate,
            error_distribution=error_distribution,
            performance_grade=performance_grade
        )
    
    def _calculate_performance_grade(self, config: LoadTestConfig, success_rate: float, avg_response_time: float) -> str:
        """
        Calcula grade de performance baseada nos critérios
        """
        criteria = config.success_criteria
        
        # Verificar critérios de sucesso
        success_rate_ok = success_rate >= criteria.get("min_success_rate", 0.9)
        response_time_ok = avg_response_time <= criteria.get("max_avg_response_time", 2000)
        
        if success_rate_ok and response_time_ok:
            if success_rate >= 0.99 and avg_response_time <= 500:
                return "A+"
            elif success_rate >= 0.98 and avg_response_time <= 1000:
                return "A"
            elif success_rate >= 0.95 and avg_response_time <= 1500:
                return "B"
            else:
                return "C"
        else:
            if success_rate >= 0.85:
                return "D"
            else:
                return "F"
    
    # ===========================================
    # PUBLIC METHODS
    # ===========================================
    
    async def run_predefined_test(self, test_type: str, base_url: str = "http://localhost:8001") -> str:
        """
        Executa teste predefinido
        """
        if test_type not in self.default_configs:
            raise ValueError(f"Test type '{test_type}' not found. Available: {list(self.default_configs.keys())}")
        
        config = self.default_configs[test_type]
        return await self.run_load_test(config, base_url)
    
    def get_test_result(self, test_id: str) -> Optional[LoadTestSummary]:
        """
        Obtém resultado de teste
        """
        return self.test_summaries.get(test_id)
    
    def list_active_tests(self) -> List[str]:
        """
        Lista testes ativos
        """
        return [test_id for test_id, active in self.active_tests.items() if active]
    
    def stop_test(self, test_id: str) -> bool:
        """
        Para teste em execução
        """
        if test_id in self.active_tests:
            self.active_tests[test_id] = False
            return True
        return False
    
    def get_test_progress(self, test_id: str) -> Dict[str, Any]:
        """
        Obtém progresso de teste em execução
        """
        if test_id not in self.test_results:
            return {"error": "Test not found"}
        
        results = self.test_results[test_id]
        active = self.active_tests.get(test_id, False)
        
        if results:
            recent_results = results[-100:]  # Últimos 100 requests
            success_count = len([r for r in recent_results if r.success])
            avg_response_time = statistics.mean([r.response_time_ms for r in recent_results if r.success]) if recent_results else 0
        else:
            success_count = 0
            avg_response_time = 0
        
        return {
            "test_id": test_id,
            "active": active,
            "total_requests": len(results),
            "recent_success_rate": success_count / len(results[-100:]) if results else 0,
            "recent_avg_response_time": avg_response_time,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

# Instância global
load_testing_system = LoadTestingSystem()