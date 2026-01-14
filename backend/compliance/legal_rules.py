"""
REGRAS JURÍDICAS DE IMIGRAÇÃO
Fornecidas por advogado especialista em imigração

Este módulo contém todas as regras legais específicas que devem ser aplicadas
na validação de formulários e processos de imigração.
"""

from datetime import datetime
from typing import Dict, List, Tuple


class ImmigrationLegalRules:
    """Classe com todas as regras jurídicas de imigração"""
    
    @staticmethod
    def validate_f1_student_visa(form_data: Dict) -> Tuple[bool, List[str]]:
        """
        Valida regras específicas para visto F1 (Estudante)
        
        Regras:
        - Exige prova de proficiência em inglês
        - Exige I-20 emitido
        - Exige pagamento SEVIS confirmado
        - Valida regras de trabalho
        - Alerta sobre viagem durante processo
        """
        errors = []
        warnings = []
        
        # 1. Proficiência em inglês (OBRIGATÓRIO)
        english_proficiency = form_data.get('english_proficiency_proof')
        if not english_proficiency or english_proficiency == 'none':
            errors.append("❌ OBRIGATÓRIO: Prova de proficiência em inglês (TOEFL, IELTS, Duolingo, etc.)")
        
        # 2. I-20 emitido (OBRIGATÓRIO)
        has_i20 = form_data.get('has_i20_issued')
        if not has_i20 or has_i20 != 'yes':
            errors.append("❌ OBRIGATÓRIO: I-20 deve estar emitido pela instituição antes de prosseguir")
        
        # 3. SEVIS pago (OBRIGATÓRIO)
        sevis_paid = form_data.get('sevis_fee_paid')
        if not sevis_paid or sevis_paid != 'yes':
            errors.append("❌ OBRIGATÓRIO: Taxa SEVIS deve estar paga antes de prosseguir")
        
        # 4. Regras de trabalho
        wants_to_work = form_data.get('plans_to_work')
        if wants_to_work == 'yes':
            work_type = form_data.get('work_type')
            if work_type == 'off_campus':
                errors.append("❌ TRABALHO OFF-CAMPUS NÃO PERMITIDO: Apenas trabalho on-campus (até 20h/semana) ou OPT após conclusão")
            elif work_type == 'on_campus':
                hours_per_week = form_data.get('work_hours_per_week', 0)
                if int(hours_per_week) > 20:
                    errors.append("❌ LIMITE EXCEDIDO: Trabalho on-campus limitado a 20 horas por semana")
        
        # 5. Alerta sobre viagem
        plans_to_travel = form_data.get('plans_to_travel_during_process')
        if plans_to_travel == 'yes':
            warnings.append("⚠️ ATENÇÃO CRÍTICA: Viajar para fora dos EUA durante o processo de visto F1 ANULA seu pedido. Não viaje!")
        
        # 6. Mudança de B2 para F1
        current_status = form_data.get('current_visa_status')
        entry_date = form_data.get('entry_date_usa')
        if current_status == 'B2' and entry_date:
            try:
                entry = datetime.strptime(entry_date, '%Y-%m-%d')
                days_since_entry = (datetime.now() - entry).days
                if days_since_entry < 90:
                    errors.append(f"❌ MUDANÇA B2→F1 NÃO PERMITIDA: Você deve esperar pelo menos 90 dias desde a entrada nos EUA. Faltam {90 - days_since_entry} dias.")
            except:
                warnings.append("⚠️ Data de entrada inválida ou não fornecida")
        
        is_valid = len(errors) == 0
        all_messages = errors + warnings
        
        return is_valid, all_messages
    
    @staticmethod
    def validate_adjustment_of_status_marriage(form_data: Dict) -> Tuple[bool, List[str]]:
        """
        Valida regras para Ajuste de Status por Casamento
        
        Regras:
        - Apenas para quem está nos EUA com entrada legal
        - Formulários obrigatórios: I-130, I-130A, I-485, I-864
        - Formulários opcionais: I-765 (trabalho), I-131 (viagem)
        - Concurrent filing permitido
        """
        errors = []
        warnings = []
        
        # 1. Deve estar nos EUA
        currently_in_usa = form_data.get('currently_in_usa')
        if not currently_in_usa or currently_in_usa != 'yes':
            errors.append("❌ AJUSTE DE STATUS APENAS NOS EUA: Este processo é apenas para quem já está nos Estados Unidos. Se você está fora, deve fazer processo consular.")
        
        # 2. Entrada legal
        legal_entry = form_data.get('legal_entry')
        if not legal_entry or legal_entry != 'yes':
            errors.append("❌ ENTRADA LEGAL OBRIGATÓRIA: Você deve ter entrado legalmente nos EUA (ex: com visto B2, F1, etc.)")
        
        # 3. Formulários obrigatórios
        required_forms = ['I-130', 'I-130A', 'I-485', 'I-864']
        for form in required_forms:
            form_key = f'has_{form.lower().replace("-", "_")}'
            if not form_data.get(form_key):
                errors.append(f"❌ FORMULÁRIO OBRIGATÓRIO: {form} deve ser incluído")
        
        # 4. Formulários opcionais (informar)
        wants_work_permit = form_data.get('wants_work_permit')
        wants_travel_permit = form_data.get('wants_travel_permit')
        
        if wants_work_permit == 'yes' and not form_data.get('has_i_765'):
            warnings.append("💡 RECOMENDAÇÃO: Incluir formulário I-765 (Autorização de Trabalho)")
        
        if wants_travel_permit == 'yes' and not form_data.get('has_i_131'):
            warnings.append("💡 RECOMENDAÇÃO: Incluir formulário I-131 (Advance Parole para viagem)")
        
        # 5. Casamento válido
        marriage_date = form_data.get('marriage_date')
        if not marriage_date:
            errors.append("❌ DATA DE CASAMENTO OBRIGATÓRIA")
        
        is_valid = len(errors) == 0
        all_messages = errors + warnings
        
        return is_valid, all_messages
    
    @staticmethod
    def validate_green_card_renewal(form_data: Dict) -> Tuple[bool, List[str]]:
        """
        Valida regras para Renovação de Green Card
        
        Regras:
        - Pode aplicar até 6 meses antes do vencimento
        - Alerta se já estiver vencido
        """
        errors = []
        warnings = []
        
        expiration_date = form_data.get('green_card_expiration_date')
        if not expiration_date:
            errors.append("❌ DATA DE VENCIMENTO DO GREEN CARD OBRIGATÓRIA")
            return False, errors
        
        try:
            exp_date = datetime.strptime(expiration_date, '%Y-%m-%d')
            today = datetime.now()
            days_until_expiration = (exp_date - today).days
            
            # Já vencido
            if days_until_expiration < 0:
                warnings.append(f"⚠️ SEU GREEN CARD ESTÁ VENCIDO há {abs(days_until_expiration)} dias. Você pode continuar com a renovação, mas evite viajar internacionalmente.")
            
            # Mais de 6 meses para vencer
            elif days_until_expiration > 180:
                errors.append(f"❌ MUITO CEDO: Você só pode renovar seu Green Card nos 6 meses anteriores ao vencimento. Seu Green Card vence em {days_until_expiration} dias. Volte em {days_until_expiration - 180} dias.")
            
            # Dentro do período permitido
            else:
                warnings.append(f"✅ PERÍODO VÁLIDO: Seu Green Card vence em {days_until_expiration} dias. Você está dentro do período de renovação.")
        
        except:
            errors.append("❌ Formato de data inválido")
        
        is_valid = len(errors) == 0
        all_messages = errors + warnings
        
        return is_valid, all_messages
    
    @staticmethod
    def validate_status_extension_b2(form_data: Dict) -> Tuple[bool, List[str]]:
        """
        Valida regras para Extensão de Status (B2)
        
        Regras:
        - Só permitir após 90 dias da entrada
        - ESTA não pode ser estendido
        - Extensão padrão: +6 meses
        - Sair cancela o processo
        """
        errors = []
        warnings = []
        
        # 1. Verificar se é ESTA (não pode estender)
        entry_type = form_data.get('entry_type')
        if entry_type == 'ESTA':
            errors.append("❌ ESTA NÃO PODE SER ESTENDIDO: O programa ESTA não permite extensão. Você deve sair dos EUA e retornar com novo ESTA ou visto.")
        
        # 2. 90 dias mínimo desde entrada
        entry_date = form_data.get('entry_date_usa')
        if not entry_date:
            errors.append("❌ DATA DE ENTRADA NOS EUA OBRIGATÓRIA")
        else:
            try:
                entry = datetime.strptime(entry_date, '%Y-%m-%d')
                days_since_entry = (datetime.now() - entry).days
                if days_since_entry < 90:
                    errors.append(f"❌ MUITO CEDO PARA EXTENSÃO: Você deve esperar pelo menos 90 dias desde sua entrada nos EUA. Faltam {90 - days_since_entry} dias.")
            except:
                errors.append("❌ Formato de data de entrada inválido")
        
        # 3. Extensão padrão é de 6 meses
        extension_months = form_data.get('extension_duration_months', 6)
        if int(extension_months) > 6:
            warnings.append("⚠️ ATENÇÃO: A extensão padrão é de 6 meses. Períodos maiores podem ser negados pelo USCIS.")
        
        # 4. Alerta crítico sobre viagem
        plans_to_travel = form_data.get('plans_to_travel_during_process')
        if plans_to_travel == 'yes':
            warnings.append("🚨 ATENÇÃO CRÍTICA: Sair dos EUA durante o processo de extensão CANCELA automaticamente seu pedido. NÃO VIAJE!")
        
        is_valid = len(errors) == 0
        all_messages = errors + warnings
        
        return is_valid, all_messages
    
    @staticmethod
    def validate_f1_reinstatement(form_data: Dict) -> Tuple[bool, List[str]]:
        """
        Valida regras para Reinstatement F1
        
        Regras:
        - Apenas para quem teve status F1 encerrado pela escola
        - Exige novo I-20 com indicação "Reinstatement"
        - Exige I-539
        - Deve retornar às aulas imediatamente
        """
        errors = []
        warnings = []
        
        # 1. Status anterior F1
        previous_status = form_data.get('previous_visa_status')
        if previous_status != 'F1':
            errors.append("❌ REINSTATEMENT APENAS PARA F1: Este processo é apenas para quem teve status F1 anteriormente")
        
        # 2. Status encerrado pela escola
        termination_reason = form_data.get('f1_termination_reason')
        if not termination_reason:
            errors.append("❌ MOTIVO DO ENCERRAMENTO OBRIGATÓRIO: Informe por que seu status F1 foi encerrado")
        
        # 3. Novo I-20 com "Reinstatement"
        has_new_i20 = form_data.get('has_new_i20_for_reinstatement')
        if not has_new_i20 or has_new_i20 != 'yes':
            errors.append("❌ NOVO I-20 OBRIGATÓRIO: Você precisa de um novo I-20 da sua escola com indicação 'Reinstatement'")
        
        i20_says_reinstatement = form_data.get('i20_indicates_reinstatement')
        if not i20_says_reinstatement or i20_says_reinstatement != 'yes':
            errors.append("❌ I-20 DEVE INDICAR REINSTATEMENT: Seu novo I-20 deve especificamente indicar que é para 'Reinstatement'")
        
        # 4. Formulário I-539
        has_i539 = form_data.get('has_i_539')
        if not has_i539 or has_i539 != 'yes':
            errors.append("❌ FORMULÁRIO I-539 OBRIGATÓRIO: Você deve preencher o formulário I-539 para Reinstatement")
        
        # 5. Retorno às aulas
        warnings.append("⚠️ IMPORTANTE: Você deve retornar às aulas IMEDIATAMENTE após receber o novo I-20. Não espere a aprovação do Reinstatement.")
        
        is_valid = len(errors) == 0
        all_messages = errors + warnings
        
        return is_valid, all_messages
    
    @staticmethod
    def validate_mandatory_documents(form_data: Dict, visa_type: str) -> Tuple[bool, List[str]]:
        """
        Valida documentação obrigatória para qualquer extensão/mudança de status
        
        Documentos obrigatórios:
        - Passaporte válido (alerta se vencido)
        - Visto atual e I-94
        - Extrato bancário recente (traduzido)
        - Prova de vínculo com Brasil (traduzidos)
        - Se dependentes: passaportes, vistos, I-94s, certidões (traduzidas)
        - Fotos
        """
        errors = []
        warnings = []
        
        # 1. Passaporte
        passport_expiration = form_data.get('passport_expiration_date')
        if not passport_expiration:
            errors.append("❌ DATA DE VALIDADE DO PASSAPORTE OBRIGATÓRIA")
        else:
            try:
                exp_date = datetime.strptime(passport_expiration, '%Y-%m-%d')
                if exp_date < datetime.now():
                    warnings.append("⚠️ PASSAPORTE VENCIDO: Seu passaporte está vencido. Você pode continuar, mas isso pode afetar seu processo. Renove o quanto antes.")
                elif (exp_date - datetime.now()).days < 180:
                    warnings.append("⚠️ PASSAPORTE PRÓXIMO DO VENCIMENTO: Seu passaporte vence em menos de 6 meses. Considere renová-lo.")
            except:
                errors.append("❌ Formato de data do passaporte inválido")
        
        # 2. Visto atual
        has_current_visa = form_data.get('has_current_visa_copy')
        if not has_current_visa or has_current_visa != 'yes':
            errors.append("❌ CÓPIA DO VISTO ATUAL OBRIGATÓRIA")
        
        # 3. I-94
        has_i94 = form_data.get('has_i94')
        i94_expiration = form_data.get('i94_expiration_date')
        if not has_i94 or has_i94 != 'yes':
            errors.append("❌ I-94 OBRIGATÓRIO: Faça download em https://i94.cbp.dhs.gov/")
        if not i94_expiration:
            errors.append("❌ DATA DE VENCIMENTO DO I-94 OBRIGATÓRIA")
        
        # 4. Extrato bancário
        has_bank_statement = form_data.get('has_bank_statement')
        bank_statement_translated = form_data.get('bank_statement_translated')
        if not has_bank_statement or has_bank_statement != 'yes':
            errors.append("❌ EXTRATO BANCÁRIO RECENTE OBRIGATÓRIO (últimos 3 meses)")
        if bank_statement_translated != 'yes':
            warnings.append("⚠️ TRADUÇÃO OBRIGATÓRIA: Seu extrato bancário deve estar traduzido para inglês por tradutor juramentado")
        
        # 5. Prova de vínculo com Brasil
        has_brazil_ties = form_data.get('has_brazil_ties_proof')
        ties_translated = form_data.get('brazil_ties_translated')
        if not has_brazil_ties or has_brazil_ties != 'yes':
            errors.append("❌ PROVAS DE VÍNCULO COM BRASIL OBRIGATÓRIAS: Contas, CNPS, declaração IR, propriedades, etc.")
        if ties_translated != 'yes':
            warnings.append("⚠️ TRADUÇÃO OBRIGATÓRIA: Documentos brasileiros devem estar traduzidos para inglês")
        
        # 6. Dependentes
        has_dependents = form_data.get('has_dependents')
        if has_dependents == 'yes':
            num_dependents = form_data.get('number_of_dependents', 0)
            for i in range(int(num_dependents)):
                dep_has_passport = form_data.get(f'dependent_{i}_has_passport')
                dep_has_visa = form_data.get(f'dependent_{i}_has_visa')
                dep_has_i94 = form_data.get(f'dependent_{i}_has_i94')
                dep_has_birth_cert = form_data.get(f'dependent_{i}_has_birth_certificate')
                
                if not dep_has_passport or dep_has_passport != 'yes':
                    errors.append(f"❌ PASSAPORTE DO DEPENDENTE {i+1} OBRIGATÓRIO")
                if not dep_has_visa or dep_has_visa != 'yes':
                    errors.append(f"❌ VISTO DO DEPENDENTE {i+1} OBRIGATÓRIO")
                if not dep_has_i94 or dep_has_i94 != 'yes':
                    errors.append(f"❌ I-94 DO DEPENDENTE {i+1} OBRIGATÓRIO")
                if not dep_has_birth_cert or dep_has_birth_cert != 'yes':
                    errors.append(f"❌ CERTIDÃO DE NASCIMENTO DO DEPENDENTE {i+1} OBRIGATÓRIA (traduzida)")
        
        # 7. Fotos
        has_photos = form_data.get('has_passport_photos')
        num_photos = form_data.get('number_of_photos', 0)
        required_photos = 2
        if has_dependents == 'yes':
            required_photos += 2 * int(form_data.get('number_of_dependents', 0))
        
        if not has_photos or has_photos != 'yes' or int(num_photos) < required_photos:
            errors.append(f"❌ FOTOS OBRIGATÓRIAS: Você precisa de {required_photos} fotos padrão passaporte (2 por pessoa)")
        
        is_valid = len(errors) == 0
        all_messages = errors + warnings
        
        return is_valid, all_messages
    
    @staticmethod
    def validate_travel_during_process(form_data: Dict, process_type: str) -> Tuple[bool, List[str]]:
        """
        Valida regras sobre viagem durante processos ativos
        
        Regra geral: NUNCA sair do país durante processos ativos (exceto com Advance Parole)
        """
        warnings = []
        
        plans_to_travel = form_data.get('plans_to_travel_during_process')
        has_advance_parole = form_data.get('has_advance_parole')
        
        if plans_to_travel == 'yes':
            if has_advance_parole == 'yes':
                warnings.append("✅ ADVANCE PAROLE: Você possui Advance Parole e pode viajar. Leve o documento sempre com você!")
            else:
                warnings.append(f"🚨 PERIGO CRÍTICO: NÃO VIAJE durante o processo de {process_type}! Isso irá CANCELAR automaticamente seu pedido e você pode ter dificuldades para retornar aos EUA. Se precisar viajar, solicite Advance Parole (I-131) primeiro.")
        
        return True, warnings


# Função helper para aplicar todas as regras relevantes
def apply_legal_rules(form_data: Dict, visa_type: str) -> Tuple[bool, List[str]]:
    """
    Aplica todas as regras jurídicas relevantes para o tipo de visto
    
    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_messages)
    """
    rules = ImmigrationLegalRules()
    all_messages = []
    is_valid = True
    
    # 🆕 BUG P3 FIX: Aplicar regras específicas por tipo de visto (com proteção contra None)
    visa_type_upper = visa_type.upper() if visa_type else ''
    
    if visa_type_upper == 'F-1' or visa_type_upper == 'F1':
        valid, messages = rules.validate_f1_student_visa(form_data)
        is_valid = is_valid and valid
        all_messages.extend(messages)
    
    elif 'ADJUSTMENT' in visa_type_upper or 'MARRIAGE' in visa_type_upper:
        valid, messages = rules.validate_adjustment_of_status_marriage(form_data)
        is_valid = is_valid and valid
        all_messages.extend(messages)
    
    elif 'GREEN CARD' in visa_type_upper and 'RENEWAL' in visa_type_upper:
        valid, messages = rules.validate_green_card_renewal(form_data)
        is_valid = is_valid and valid
        all_messages.extend(messages)
    
    elif 'B-2' in visa_type_upper or 'B2' in visa_type_upper or 'EXTENSION' in visa_type_upper:
        valid, messages = rules.validate_status_extension_b2(form_data)
        is_valid = is_valid and valid
        all_messages.extend(messages)
    
    elif 'REINSTATEMENT' in visa_type_upper:
        valid, messages = rules.validate_f1_reinstatement(form_data)
        is_valid = is_valid and valid
        all_messages.extend(messages)
    
    # Aplicar validação de documentos obrigatórios (para todos)
    valid, messages = rules.validate_mandatory_documents(form_data, visa_type)
    is_valid = is_valid and valid
    all_messages.extend(messages)
    
    # Aplicar regras de viagem (para todos)
    valid, messages = rules.validate_travel_during_process(form_data, visa_type)
    all_messages.extend(messages)
    
    return is_valid, all_messages
