"""
Simulação de dados A/B Testing para demonstração
"""

import asyncio
import random
from ab_testing import ab_testing_manager

async def simulate_ab_testing_data():
    """
    Simula dados de A/B testing para demonstração
    """
    
    print("🧪 Simulando dados de A/B Testing...")
    print("=" * 50)
    
    # Simulate multiple document analyses
    for i in range(20):
        user_id = f"user_{i % 10}"  # 10 different users
        
        # Simulate passport processing
        ab_decision = ab_testing_manager.should_use_pipeline(
            user_id=user_id,
            document_type="passport",
            filename="passport.jpg"
        )
        
        # Simulate results based on system used
        if ab_decision['use_pipeline']:
            # Pipeline results (better performance)
            processing_time = random.uniform(2.5, 4.0)  # Faster
            confidence = random.uniform(85, 98)  # Higher confidence
            success = random.choice([True, True, True, False])  # 75% success rate
        else:
            # Legacy results (current performance)
            processing_time = random.uniform(3.0, 5.5)  # Slower
            confidence = random.uniform(70, 90)  # Lower confidence
            success = random.choice([True, True, False])  # 67% success rate
        
        # Record the result
        ab_testing_manager.record_analysis_result(
            test_group=ab_decision['test_group'],
            processing_time=processing_time,
            confidence=confidence / 100.0,
            success=success,
            analysis_result={}
        )
        
        print(f"📄 Doc {i+1}: {ab_decision['test_group']}, "
              f"Success: {success}, Time: {processing_time:.2f}s, "
              f"Confidence: {confidence:.1f}%")
    
    # Get comparison results
    print("\n" + "=" * 50)
    print("📊 RESULTADOS DO TESTE A/B")
    print("=" * 50)
    
    comparison = ab_testing_manager.get_test_comparison()
    
    pipeline_stats = comparison['pipeline']
    legacy_stats = comparison['legacy']
    improvements = comparison['improvements']
    
    print(f"\n🔵 PIPELINE MODULAR:")
    print(f"   📄 Documentos: {pipeline_stats['total_documents']}")
    print(f"   ✅ Taxa de sucesso: {pipeline_stats['success_rate']:.1%}")
    print(f"   ⚡ Tempo médio: {pipeline_stats['avg_processing_time_ms']:.0f}ms")
    print(f"   🎯 Confiança: {pipeline_stats['avg_confidence_pct']:.1f}%")
    
    print(f"\n⚪ SISTEMA LEGADO:")
    print(f"   📄 Documentos: {legacy_stats['total_documents']}")
    print(f"   ✅ Taxa de sucesso: {legacy_stats['success_rate']:.1%}")
    print(f"   ⚡ Tempo médio: {legacy_stats['avg_processing_time_ms']:.0f}ms")
    print(f"   🎯 Confiança: {legacy_stats['avg_confidence_pct']:.1f}%")
    
    print(f"\n🚀 MELHORIAS:")
    if improvements['success_rate_improvement_points'] > 0:
        print(f"   ✅ Taxa de sucesso: +{improvements['success_rate_improvement_points']:.1f} pontos")
    if improvements['processing_time_improvement_pct'] > 0:
        print(f"   ⚡ Velocidade: {improvements['processing_time_improvement_pct']:.1f}% mais rápido")
    if improvements['confidence_improvement_points'] > 0:
        print(f"   🎯 Confiança: +{improvements['confidence_improvement_points']:.1f} pontos")
    
    print(f"\n🏆 RESULTADO: Pipeline {'SUPERIOR' if improvements['success_rate_improvement_points'] > 0 else 'EM TESTE'}")
    
    return comparison

if __name__ == "__main__":
    asyncio.run(simulate_ab_testing_data())