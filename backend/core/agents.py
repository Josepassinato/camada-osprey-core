oracle = None
consult_oracle = None
document_analyzer = None
form_filler = None
translator = None
analyze_uploaded_document = None
fill_form_automatically = None
translate_text = None


def set_agents(
    *,
    oracle_instance=None,
    consult_oracle_fn=None,
    document_analyzer_instance=None,
    form_filler_instance=None,
    translator_instance=None,
    analyze_uploaded_document_fn=None,
    fill_form_automatically_fn=None,
    translate_text_fn=None,
):
    global oracle, consult_oracle, document_analyzer, form_filler, translator
    global analyze_uploaded_document, fill_form_automatically, translate_text

    oracle = oracle_instance
    consult_oracle = consult_oracle_fn
    document_analyzer = document_analyzer_instance
    form_filler = form_filler_instance
    translator = translator_instance
    analyze_uploaded_document = analyze_uploaded_document_fn
    fill_form_automatically = fill_form_automatically_fn
    translate_text = translate_text_fn
