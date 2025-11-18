"""
Integração Stripe para Pagamentos
Agente Coruja - Mudança de Status
"""

import os
import stripe
import logging
from typing import Dict, Optional
from datetime import datetime
from payment_packages import get_visa_package, calculate_final_price
from voucher_system import validate_voucher, increment_voucher_usage

logger = logging.getLogger(__name__)

# Configurar Stripe
stripe.api_key = os.environ.get('STRIPE_API_KEY')


async def create_checkout_session(
    visa_code: str,
    case_id: str,
    voucher_code: Optional[str] = None,
    success_url: str = None,
    cancel_url: str = None,
    db = None
) -> Dict:
    """
    Cria uma sessão de checkout do Stripe
    
    Args:
        visa_code: Código do visto (ex: "H-1B")
        case_id: ID do caso do usuário
        voucher_code: Código do voucher (opcional)
        success_url: URL de sucesso
        cancel_url: URL de cancelamento
        db: Conexão com banco de dados
    
    Returns:
        Dict com session_id e url de checkout
    """
    try:
        # Obter informações do pacote
        package = get_visa_package(visa_code)
        original_price = package["price"]
        
        # Nota: O desconto será aplicado diretamente no Stripe via promotion codes
        # Não aplicamos desconto aqui, o usuário digitará o cupom na página do Stripe
        
        # Criar linha de item para o Stripe (preço cheio)
        line_items = [{
            'price_data': {
                'currency': 'usd',
                'unit_amount': int(original_price * 100),  # Stripe usa centavos
                'product_data': {
                    'name': f'{package["name"]} - {visa_code}',
                    'description': package["description"],
                    'images': [],  # Pode adicionar logo da empresa
                },
            },
            'quantity': 1,
        }]
        
        # URLs de redirecionamento
        if not success_url:
            success_url = f"{os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:3000')}/payment/success?session_id={{CHECKOUT_SESSION_ID}}"
        if not cancel_url:
            cancel_url = f"{os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:3000')}/payment/cancel"
        
        # Criar sessão de checkout
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            allow_promotion_codes=True,  # Habilitar campo de cupom no Stripe
            metadata={
                'case_id': case_id,
                'visa_code': visa_code,
                'original_price': str(original_price)
            },
            customer_email=None,  # Pode adicionar email do usuário
        )
        
        # Salvar transação no banco
        if db:
            transaction = {
                'session_id': session.id,
                'case_id': case_id,
                'visa_code': visa_code,
                'original_price': original_price,
                'discount_percentage': discount_percentage,
                'final_price': final_price,
                'voucher_code': voucher_code,
                'voucher_info': voucher_info,
                'payment_status': 'pending',
                'stripe_session': session,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            await db.payment_transactions.insert_one(transaction)
            logger.info(f"Transação criada: {session.id} para case {case_id}")
        
        return {
            'success': True,
            'session_id': session.id,
            'checkout_url': session.url,
            'original_price': original_price,
            'message': 'Cupons de desconto podem ser aplicados na página de checkout do Stripe'
        }
        
    except stripe.error.StripeError as e:
        logger.error(f"Erro do Stripe: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }
    except Exception as e:
        logger.error(f"Erro ao criar checkout: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


async def verify_payment_status(session_id: str, db = None) -> Dict:
    """
    Verifica o status de um pagamento
    
    Args:
        session_id: ID da sessão do Stripe
        db: Conexão com banco de dados
    
    Returns:
        Dict com status do pagamento
    """
    try:
        # Buscar sessão no Stripe
        session = stripe.checkout.Session.retrieve(session_id)
        
        payment_status = session.payment_status  # 'paid', 'unpaid', 'no_payment_required'
        
        # Atualizar no banco de dados
        if db:
            await db.payment_transactions.update_one(
                {'session_id': session_id},
                {
                    '$set': {
                        'payment_status': payment_status,
                        'stripe_payment_intent': session.payment_intent,
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            # Se pagamento confirmado, incrementar uso do voucher
            if payment_status == 'paid':
                transaction = await db.payment_transactions.find_one({'session_id': session_id})
                if transaction and transaction.get('voucher_code'):
                    await increment_voucher_usage(transaction['voucher_code'], db)
                    logger.info(f"Voucher {transaction['voucher_code']} incrementado após pagamento")
                
                # Atualizar status do case para 'paid'
                if transaction and transaction.get('case_id'):
                    await db.auto_application_cases.update_one(
                        {'case_id': transaction['case_id']},
                        {
                            '$set': {
                                'payment_status': 'paid',
                                'payment_date': datetime.utcnow(),
                                'updated_at': datetime.utcnow()
                            }
                        }
                    )
                    logger.info(f"Case {transaction['case_id']} marcado como pago")
        
        return {
            'success': True,
            'session_id': session_id,
            'payment_status': payment_status,
            'amount_total': session.amount_total / 100,  # Converter centavos para dólares
            'currency': session.currency,
            'customer_email': session.customer_details.email if session.customer_details else None
        }
        
    except stripe.error.StripeError as e:
        logger.error(f"Erro ao verificar pagamento: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }
    except Exception as e:
        logger.error(f"Erro ao verificar status: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


async def handle_stripe_webhook(payload: bytes, sig_header: str, db = None) -> Dict:
    """
    Processa webhooks do Stripe
    
    Args:
        payload: Corpo da requisição
        sig_header: Assinatura do Stripe
        db: Conexão com banco de dados
    
    Returns:
        Dict com resultado do processamento
    """
    webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    if not webhook_secret:
        logger.warning("STRIPE_WEBHOOK_SECRET não configurado")
        return {'success': False, 'error': 'Webhook secret not configured'}
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
        
        # Processar evento
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            session_id = session['id']
            
            logger.info(f"Pagamento completado: {session_id}")
            
            # Atualizar status no banco
            if db:
                await db.payment_transactions.update_one(
                    {'session_id': session_id},
                    {
                        '$set': {
                            'payment_status': 'paid',
                            'stripe_payment_intent': session.get('payment_intent'),
                            'webhook_received': True,
                            'updated_at': datetime.utcnow()
                        }
                    }
                )
                
                # Marcar case como pago
                transaction = await db.payment_transactions.find_one({'session_id': session_id})
                if transaction and transaction.get('case_id'):
                    await db.auto_application_cases.update_one(
                        {'case_id': transaction['case_id']},
                        {
                            '$set': {
                                'payment_status': 'paid',
                                'payment_date': datetime.utcnow(),
                                'updated_at': datetime.utcnow()
                            }
                        }
                    )
        
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            logger.warning(f"Pagamento falhou: {payment_intent['id']}")
        
        return {'success': True, 'event_type': event['type']}
        
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Assinatura inválida do webhook: {str(e)}")
        return {'success': False, 'error': 'Invalid signature'}
    except Exception as e:
        logger.error(f"Erro ao processar webhook: {str(e)}")
        return {'success': False, 'error': str(e)}
