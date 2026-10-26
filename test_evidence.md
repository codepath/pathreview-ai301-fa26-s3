# Test evidence: issue #35, review-completion webhooks

Branch `fix/35-review-webhooks` @ `fa8d761`; `main` @ `2f4e82f`. Run
2026-10-26 (UTC) on Linux, Python 3.12.3, Postgres 16 in Docker (port
5433), `LLM_PROVIDER=mock`.

## Seeded-bug check

`grep -rn "issue #35:" tests` returns nothing.

## The PR template's four checks (on the branch)

| Check | Result |
|---|---|
| `make test-unit` | pass: 385 passed, 53 xfailed, 6 warnings; all 10 tests this branch adds pass (9 in `test_webhook_service.py`, `test_process_review_notifies_on_early_return`) |
| `make test-integration` | no tests ran (exit 5): Path Review has no integration tests yet |
| `make lint` | pass: `All checks passed!` |
| `make typecheck` | **fails, also on `main`**: mypy stops on a syntax error inside numpy's own stubs before checking any project file. See below. |

**Why typecheck fails.** `pyproject.toml` sets `[tool.mypy] python_version = "3.11"`,
but the venv is Python 3.12 and its numpy stubs use the 3.12-only `type`
statement, so mypy errors on `numpy/__init__.pyi:737` and checks nothing
else. `main` fails the same way, so it's not caused by this branch. Run
with `--python-version 3.12`, mypy reports no issues on the branch (output
below). I didn't change the mypy config: it's outside issue #35.

### make test-unit

```
$ make test-unit
.venv/bin/pytest tests/unit -v -m unit
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.1.1, pluggy-1.6.0 -- /home/ein/Eu/codepath/ai301/pathreview-ai301-fa26-s3/.venv/bin/python3
cachedir: .pytest_cache
hypothesis profile 'default'
benchmark: 5.3.0 (defaults: timer=time.perf_counter disable_gc=False min_rounds=5 min_time=0.000005 max_time=1.0 calibration_precision=10 warmup=False warmup_iterations=100000)
rootdir: /home/ein/Eu/codepath/ai301/pathreview-ai301-fa26-s3
configfile: pyproject.toml
plugins: hypothesis-6.168.3, pytest_httpserver-1.1.5, platformdirs-4.12.2, asyncio-1.4.0, cov-7.1.0, benchmark-5.3.0, anyio-4.15.1
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 438 items

tests/unit/test_batch_processor.py::TestBatchEmbeddingProcessor::test_empty_chunks_list_returns_empty XFAIL [  0%]
tests/unit/test_batch_processor.py::TestBatchEmbeddingProcessor::test_normal_chunks_list_processes PASSED [  0%]
tests/unit/test_batch_processor.py::TestBatchEmbeddingProcessor::test_batches_chunks_correctly PASSED [  0%]
tests/unit/test_batch_processor.py::TestBatchEmbeddingProcessor::test_returns_chunk_and_embedding_id_tuples PASSED [  0%]
tests/unit/test_batch_processor.py::TestBatchEmbeddingProcessor::test_embedding_provider_called_with_texts PASSED [  1%]
tests/unit/test_batch_processor.py::TestBatchEmbeddingProcessor::test_chunk_metadata_preserved PASSED [  1%]
tests/unit/test_batch_processor.py::TestBatchEmbeddingProcessor::test_batch_size_limit PASSED [  1%]
tests/unit/test_batch_processor.py::TestBatchEmbeddingProcessor::test_many_chunks PASSED [  1%]
tests/unit/test_batch_processor.py::TestBatchEmbeddingProcessor::test_embedding_provider_exception_propagates PASSED [  2%]
tests/unit/test_batch_processor.py::TestBatchEmbeddingProcessor::test_store_embedding_called_for_each_chunk PASSED [  2%]
tests/unit/test_batch_processor.py::TestBatchEmbeddingProcessor::test_chunk_text_extraction PASSED [  2%]
tests/unit/test_bias_detector.py::TestBiasDetector::test_dismissive_bootcamp_language_detected XFAIL [  2%]
tests/unit/test_bias_detector.py::TestBiasDetector::test_bootcamp_lacks_rigor_detected XFAIL [  2%]
tests/unit/test_bias_detector.py::TestBiasDetector::test_bootcamp_inadequate_training_detected PASSED [  3%]
tests/unit/test_bias_detector.py::TestBiasDetector::test_self_taught_comparison_detected PASSED [  3%]
tests/unit/test_bias_detector.py::TestBiasDetector::test_positive_bootcamp_mention_not_flagged PASSED [  3%]
tests/unit/test_bias_detector.py::TestBiasDetector::test_neutral_bootcamp_mention_not_flagged PASSED [  3%]
tests/unit/test_bias_detector.py::TestBiasDetector::test_educational_background_positive_not_flagged PASSED [  4%]
tests/unit/test_bias_detector.py::TestBiasDetector::test_demographic_assumption_age_detected XFAIL [  4%]
tests/unit/test_bias_detector.py::TestBiasDetector::test_demographic_assumption_old_detected PASSED [  4%]
tests/unit/test_bias_detector.py::TestBiasDetector::test_demographic_assumption_background_detected PASSED [  4%]
tests/unit/test_bias_detector.py::TestBiasDetector::test_immigrant_developer_assumption_detected PASSED [  5%]
tests/unit/test_bias_detector.py::TestBiasDetector::test_international_developer_assumption_detected PASSED [  5%]
tests/unit/test_bias_detector.py::TestBiasDetector::test_clean_feedback_not_flagged PASSED [  5%]
tests/unit/test_bias_detector.py::TestBiasDetector::test_technical_feedback_not_flagged PASSED [  5%]
tests/unit/test_bias_detector.py::TestBiasDetector::test_development_suggestion_not_flagged PASSED [  5%]
tests/unit/test_bias_detector.py::TestBiasDetector::test_case_insensitive_detection PASSED [  6%]
tests/unit/test_bias_detector.py::TestBiasDetector::test_return_value_structure PASSED [  6%]
tests/unit/test_bias_detector.py::TestBiasDetector::test_unbiased_returns_empty_reason PASSED [  6%]
tests/unit/test_bias_detector.py::TestBiasDetector::test_biased_returns_reason PASSED [  6%]
tests/unit/test_bias_detector.py::TestBiasDetector::test_empty_text PASSED [  7%]
tests/unit/test_bias_detector.py::TestBiasDetector::test_whitespace_only PASSED [  7%]
tests/unit/test_bias_detector.py::TestBiasDetector::test_coding_bootcamp_variant XFAIL [  7%]
tests/unit/test_bias_detector.py::TestBiasDetector::test_online_course_bias_detected PASSED [  7%]
tests/unit/test_bias_detector.py::TestBiasDetector::test_developer_vs_programmer_distinction XFAIL [  7%]
tests/unit/test_bias_detector.py::TestBiasDetector::test_multiple_bias_indicators XFAIL [  8%]
tests/unit/test_bias_detector.py::TestBiasDetector::test_negative_educational_claim XFAIL [  8%]
tests/unit/test_bias_detector.py::TestBiasDetector::test_working_class_assumption PASSED [  8%]
tests/unit/test_bias_detector.py::TestBiasDetector::test_rich_poor_assumption XFAIL [  8%]
tests/unit/test_bias_detector.py::TestBiasDetector::test_foreign_developer_struggle_assumption PASSED [  9%]
tests/unit/test_bias_detector.py::TestBiasDetector::test_skill_assessment_not_biased PASSED [  9%]
tests/unit/test_bias_detector.py::TestBiasDetector::test_comparative_without_bias PASSED [  9%]
tests/unit/test_bias_detector.py::TestBiasDetector::test_assumption_vs_observation XFAIL [  9%]
tests/unit/test_faithfulness_checker.py::TestFaithfulnessChecker::test_feedback_fully_supported_by_context PASSED [ 10%]
tests/unit/test_faithfulness_checker.py::TestFaithfulnessChecker::test_feedback_with_no_support_in_context PASSED [ 10%]
tests/unit/test_faithfulness_checker.py::TestFaithfulnessChecker::test_partial_support_returns_middle_score XFAIL [ 10%]
tests/unit/test_faithfulness_checker.py::TestFaithfulnessChecker::test_empty_feedback_returns_zero PASSED [ 10%]
tests/unit/test_faithfulness_checker.py::TestFaithfulnessChecker::test_empty_context_chunks_returns_zero PASSED [ 10%]
tests/unit/test_faithfulness_checker.py::TestFaithfulnessChecker::test_both_empty_returns_zero PASSED [ 11%]
tests/unit/test_faithfulness_checker.py::TestFaithfulnessChecker::test_multiple_context_chunks XFAIL [ 11%]
tests/unit/test_faithfulness_checker.py::TestFaithfulnessChecker::test_extract_claims PASSED [ 11%]
tests/unit/test_faithfulness_checker.py::TestFaithfulnessChecker::test_extract_claims_with_punctuation PASSED [ 11%]
tests/unit/test_faithfulness_checker.py::TestFaithfulnessChecker::test_is_supported_with_keyword_overlap PASSED [ 12%]
tests/unit/test_faithfulness_checker.py::TestFaithfulnessChecker::test_is_supported_without_keywords PASSED [ 12%]
tests/unit/test_faithfulness_checker.py::TestFaithfulnessChecker::test_case_insensitive_support_check PASSED [ 12%]
tests/unit/test_faithfulness_checker.py::TestFaithfulnessChecker::test_score_never_returns_hardcoded_value PASSED [ 12%]
tests/unit/test_faithfulness_checker.py::TestFaithfulnessChecker::test_multiple_claims_varying_support XFAIL [ 13%]
tests/unit/test_faithfulness_checker.py::TestFaithfulnessChecker::test_very_long_feedback PASSED [ 13%]
tests/unit/test_faithfulness_checker.py::TestFaithfulnessChecker::test_very_long_context PASSED [ 13%]
tests/unit/test_faithfulness_checker.py::TestFaithfulnessChecker::test_common_words_filtered_in_overlap PASSED [ 13%]
tests/unit/test_faithfulness_checker.py::TestFaithfulnessChecker::test_minimum_overlap_required PASSED [ 13%]
tests/unit/test_faithfulness_checker.py::TestFaithfulnessChecker::test_none_context_chunk_text XFAIL [ 14%]
tests/unit/test_faithfulness_checker.py::TestFaithfulnessChecker::test_missing_text_key_in_chunk PASSED [ 14%]
tests/unit/test_faithfulness_checker.py::TestFaithfulnessChecker::test_score_consistency PASSED [ 14%]
tests/unit/test_faithfulness_checker.py::TestFaithfulnessChecker::test_specialized_technical_terms PASSED [ 14%]
tests/unit/test_keyword_search.py::TestKeywordSearcher::test_results_sorted_by_score_descending PASSED [ 15%]
tests/unit/test_keyword_search.py::TestKeywordSearcher::test_query_matching_no_documents PASSED [ 15%]
tests/unit/test_keyword_search.py::TestKeywordSearcher::test_query_matching_multiple_documents PASSED [ 15%]
tests/unit/test_keyword_search.py::TestKeywordSearcher::test_case_insensitive_matching PASSED [ 15%]
tests/unit/test_keyword_search.py::TestKeywordSearcher::test_top_k_limit PASSED [ 15%]
tests/unit/test_keyword_search.py::TestKeywordSearcher::test_top_k_larger_than_results PASSED [ 16%]
tests/unit/test_keyword_search.py::TestKeywordSearcher::test_results_have_bm25_score PASSED [ 16%]
tests/unit/test_keyword_search.py::TestKeywordSearcher::test_results_preserve_chunk_fields PASSED [ 16%]
tests/unit/test_keyword_search.py::TestKeywordSearcher::test_empty_index XFAIL [ 16%]
tests/unit/test_keyword_search.py::TestKeywordSearcher::test_index_not_called_returns_empty PASSED [ 17%]
tests/unit/test_keyword_search.py::TestKeywordSearcher::test_multi_word_query PASSED [ 17%]
tests/unit/test_keyword_search.py::TestKeywordSearcher::test_tokenization PASSED [ 17%]
tests/unit/test_keyword_search.py::TestKeywordSearcher::test_tokenization_case_handling PASSED [ 17%]
tests/unit/test_keyword_search.py::TestKeywordSearcher::test_large_corpus PASSED [ 18%]
tests/unit/test_keyword_search.py::TestKeywordSearcher::test_special_characters_in_query PASSED [ 18%]
tests/unit/test_keyword_search.py::TestKeywordSearcher::test_exact_phrase_matching PASSED [ 18%]
tests/unit/test_keyword_search.py::TestKeywordSearcher::test_single_word_chunks PASSED [ 18%]
tests/unit/test_llm_provider_contract.py::TestLLMProviderContract::test_mock_provider_returns_list_of_floats PASSED [ 18%]
tests/unit/test_llm_provider_contract.py::TestLLMProviderContract::test_openai_provider_would_return_floats PASSED [ 19%]
tests/unit/test_llm_provider_contract.py::TestLLMProviderContract::test_mock_provider_deterministic PASSED [ 19%]
tests/unit/test_llm_provider_contract.py::TestLLMProviderContract::test_mock_provider_embedding_dimension PASSED [ 19%]
tests/unit/test_llm_provider_contract.py::TestLLMProviderContract::test_providers_same_dimension PASSED [ 19%]
tests/unit/test_llm_provider_contract.py::TestLLMProviderContract::test_mock_provider_multiple_texts PASSED [ 20%]
tests/unit/test_llm_provider_contract.py::TestLLMProviderContract::test_mock_provider_empty_list PASSED [ 20%]
tests/unit/test_llm_provider_contract.py::TestLLMProviderContract::test_mock_provider_single_text PASSED [ 20%]
tests/unit/test_llm_provider_contract.py::TestLLMProviderContract::test_mock_provider_empty_string PASSED [ 20%]
tests/unit/test_llm_provider_contract.py::TestLLMProviderContract::test_mock_provider_different_inputs_different_outputs PASSED [ 21%]
tests/unit/test_llm_provider_contract.py::TestLLMProviderContract::test_mock_provider_embeddings_normalized PASSED [ 21%]
tests/unit/test_llm_provider_contract.py::TestLLMProviderContract::test_provider_interface_implements_embed PASSED [ 21%]
tests/unit/test_llm_provider_contract.py::TestLLMProviderContract::test_mock_provider_returns_floats_not_integers PASSED [ 21%]
tests/unit/test_llm_provider_contract.py::TestLLMProviderContract::test_multiple_providers_same_interface PASSED [ 21%]
tests/unit/test_llm_provider_contract.py::TestLLMProviderContract::test_mock_provider_consistency_across_calls PASSED [ 22%]
tests/unit/test_llm_provider_contract.py::TestLLMProviderContract::test_provider_embed_signature PASSED [ 22%]
tests/unit/test_llm_provider_contract.py::TestLLMProviderContract::test_mock_provider_with_very_long_text PASSED [ 22%]
tests/unit/test_llm_provider_contract.py::TestLLMProviderContract::test_mock_provider_with_special_characters PASSED [ 22%]
tests/unit/test_llm_provider_contract.py::TestLLMProviderContract::test_mock_provider_with_unicode PASSED [ 23%]
tests/unit/test_llm_provider_contract.py::TestLLMProviderContract::test_mock_provider_with_newlines PASSED [ 23%]
tests/unit/test_llm_provider_contract.py::TestLLMProviderContract::test_mock_provider_with_tabs PASSED [ 23%]
tests/unit/test_llm_provider_contract.py::TestLLMProviderContract::test_different_text_lengths_same_output_dimension PASSED [ 23%]
tests/unit/test_llm_provider_contract.py::TestLLMProviderContract::test_mock_provider_batch_processing PASSED [ 23%]
tests/unit/test_llm_provider_contract.py::TestLLMProviderContract::test_embedding_vector_values_in_valid_range PASSED [ 24%]
tests/unit/test_llm_provider_contract.py::TestLLMProviderContract::test_providers_inherit_from_abstract_base PASSED [ 24%]
tests/unit/test_llm_provider_contract.py::TestLLMProviderContract::test_abstract_base_class_has_embed_method PASSED [ 24%]
tests/unit/test_llm_provider_contract.py::TestLLMProviderContract::test_mock_provider_embedding_stability PASSED [ 24%]
tests/unit/test_output_parser.py::TestOutputParser::test_json_wrapped_in_code_fence PASSED [ 25%]
tests/unit/test_output_parser.py::TestOutputParser::test_raw_json_without_fence PASSED [ 25%]
tests/unit/test_output_parser.py::TestOutputParser::test_plain_text_fallback PASSED [ 25%]
tests/unit/test_output_parser.py::TestOutputParser::test_malformed_json_fallback PASSED [ 25%]
tests/unit/test_output_parser.py::TestOutputParser::test_feedback_section_has_required_fields PASSED [ 26%]
tests/unit/test_output_parser.py::TestOutputParser::test_json_with_multiple_sections PASSED [ 26%]
tests/unit/test_output_parser.py::TestOutputParser::test_confidence_scores_in_sections PASSED [ 26%]
tests/unit/test_output_parser.py::TestOutputParser::test_empty_json_object PASSED [ 26%]
tests/unit/test_output_parser.py::TestOutputParser::test_json_array_fallback XFAIL [ 26%]
tests/unit/test_output_parser.py::TestOutputParser::test_very_long_plain_text PASSED [ 27%]
tests/unit/test_output_parser.py::TestOutputParser::test_html_in_feedback PASSED [ 27%]
tests/unit/test_output_parser.py::TestOutputParser::test_code_in_feedback PASSED [ 27%]
tests/unit/test_output_parser.py::TestOutputParser::test_section_suggestions_extraction PASSED [ 27%]
tests/unit/test_output_parser.py::TestOutputParser::test_unicode_characters PASSED [ 28%]
tests/unit/test_output_parser.py::TestOutputParser::test_nested_json_structure PASSED [ 28%]
tests/unit/test_output_parser.py::TestOutputParser::test_mixed_content PASSED [ 28%]
tests/unit/test_output_parser.py::TestOutputParser::test_plaintext_output_helper PASSED [ 28%]
tests/unit/test_output_parser.py::TestOutputParser::test_multiple_code_fences PASSED [ 28%]
tests/unit/test_output_parser.py::TestOutputParser::test_no_suggestions_key PASSED [ 29%]
tests/unit/test_pii_scrubber.py::TestPIIScrubber::test_email_redaction PASSED [ 29%]
tests/unit/test_pii_scrubber.py::TestPIIScrubber::test_multiple_emails_redacted PASSED [ 29%]
tests/unit/test_pii_scrubber.py::TestPIIScrubber::test_us_phone_number_redaction XFAIL [ 29%]
tests/unit/test_pii_scrubber.py::TestPIIScrubber::test_us_phone_formats XFAIL [ 30%]
tests/unit/test_pii_scrubber.py::TestPIIScrubber::test_international_phone_redaction PASSED [ 30%]
tests/unit/test_pii_scrubber.py::TestPIIScrubber::test_ssn_redaction PASSED [ 30%]
tests/unit/test_pii_scrubber.py::TestPIIScrubber::test_ssn_variations PASSED [ 30%]
tests/unit/test_pii_scrubber.py::TestPIIScrubber::test_street_address_redaction PASSED [ 31%]
tests/unit/test_pii_scrubber.py::TestPIIScrubber::test_text_with_no_pii PASSED [ 31%]
tests/unit/test_pii_scrubber.py::TestPIIScrubber::test_detect_returns_list_of_pii PASSED [ 31%]
tests/unit/test_pii_scrubber.py::TestPIIScrubber::test_detect_email_pii PASSED [ 31%]
tests/unit/test_pii_scrubber.py::TestPIIScrubber::test_detect_phone_pii XFAIL [ 31%]
tests/unit/test_pii_scrubber.py::TestPIIScrubber::test_detect_ssn_pii PASSED [ 32%]
tests/unit/test_pii_scrubber.py::TestPIIScrubber::test_detect_positions_accurate PASSED [ 32%]
tests/unit/test_pii_scrubber.py::TestPIIScrubber::test_detect_multiple_pii_items PASSED [ 32%]
tests/unit/test_pii_scrubber.py::TestPIIScrubber::test_case_insensitive_email_matching PASSED [ 32%]
tests/unit/test_pii_scrubber.py::TestPIIScrubber::test_complex_email_addresses PASSED [ 33%]
tests/unit/test_pii_scrubber.py::TestPIIScrubber::test_phone_at_start_of_text XFAIL [ 33%]
tests/unit/test_pii_scrubber.py::TestPIIScrubber::test_phone_at_end_of_text PASSED [ 33%]
tests/unit/test_pii_scrubber.py::TestPIIScrubber::test_address_variations PASSED [ 33%]
tests/unit/test_pii_scrubber.py::TestPIIScrubber::test_empty_text PASSED [ 34%]
tests/unit/test_pii_scrubber.py::TestPIIScrubber::test_whitespace_only PASSED [ 34%]
tests/unit/test_pii_scrubber.py::TestPIIScrubber::test_mixed_pii_and_text XFAIL [ 34%]
tests/unit/test_pii_scrubber.py::TestPIIScrubber::test_scrub_idempotent PASSED [ 34%]
tests/unit/test_pii_scrubber.py::TestPIIScrubber::test_detect_no_false_positives PASSED [ 34%]
tests/unit/test_prompt_defense.py::TestPromptDefense::test_newline_injection_detected PASSED [ 35%]
tests/unit/test_prompt_defense.py::TestPromptDefense::test_system_role_switching_detected PASSED [ 35%]
tests/unit/test_prompt_defense.py::TestPromptDefense::test_human_role_switching_detected PASSED [ 35%]
tests/unit/test_prompt_defense.py::TestPromptDefense::test_assistant_role_switching_detected PASSED [ 35%]
tests/unit/test_prompt_defense.py::TestPromptDefense::test_template_injection_detected PASSED [ 36%]
tests/unit/test_prompt_defense.py::TestPromptDefense::test_jinja_injection_detected PASSED [ 36%]
tests/unit/test_prompt_defense.py::TestPromptDefense::test_ignore_instruction_detected PASSED [ 36%]
tests/unit/test_prompt_defense.py::TestPromptDefense::test_forget_instruction_detected PASSED [ 36%]
tests/unit/test_prompt_defense.py::TestPromptDefense::test_disregard_instruction_detected PASSED [ 36%]
tests/unit/test_prompt_defense.py::TestPromptDefense::test_override_instruction_detected PASSED [ 37%]
tests/unit/test_prompt_defense.py::TestPromptDefense::test_code_execution_attempt_detected PASSED [ 37%]
tests/unit/test_prompt_defense.py::TestPromptDefense::test_run_function_attempt_detected PASSED [ 37%]
tests/unit/test_prompt_defense.py::TestPromptDefense::test_eval_function_attempt_detected PASSED [ 37%]
tests/unit/test_prompt_defense.py::TestPromptDefense::test_clean_input_not_flagged PASSED [ 38%]
tests/unit/test_prompt_defense.py::TestPromptDefense::test_normal_text_not_flagged PASSED [ 38%]
tests/unit/test_prompt_defense.py::TestPromptDefense::test_sanitize_removes_template_delimiters PASSED [ 38%]
tests/unit/test_prompt_defense.py::TestPromptDefense::test_sanitize_removes_angle_brackets PASSED [ 38%]
tests/unit/test_prompt_defense.py::TestPromptDefense::test_sanitize_preserves_legitimate_content PASSED [ 39%]
tests/unit/test_prompt_defense.py::TestPromptDefense::test_sanitize_multiple_template_delimiters PASSED [ 39%]
tests/unit/test_prompt_defense.py::TestPromptDefense::test_separator_line_detected PASSED [ 39%]
tests/unit/test_prompt_defense.py::TestPromptDefense::test_long_separator_detected PASSED [ 39%]
tests/unit/test_prompt_defense.py::TestPromptDefense::test_case_insensitive_detection PASSED [ 39%]
tests/unit/test_prompt_defense.py::TestPromptDefense::test_whitespace_variations_detected XFAIL [ 40%]
tests/unit/test_prompt_defense.py::TestPromptDefense::test_multiple_injection_patterns PASSED [ 40%]
tests/unit/test_prompt_defense.py::TestPromptDefense::test_benign_mentions_not_flagged PASSED [ 40%]
tests/unit/test_prompt_defense.py::TestPromptDefense::test_empty_string PASSED [ 40%]
tests/unit/test_prompt_defense.py::TestPromptDefense::test_whitespace_only PASSED [ 41%]
tests/unit/test_prompt_defense.py::TestPromptDefense::test_sanitize_idempotent PASSED [ 41%]
tests/unit/test_prompt_defense.py::TestPromptDefense::test_complex_injection_attempt PASSED [ 41%]
tests/unit/test_prompt_defense.py::TestPromptDefense::test_legitimate_newlines_not_flagged PASSED [ 41%]
tests/unit/test_prompt_defense.py::TestPromptDefense::test_code_blocks_handled PASSED [ 42%]
tests/unit/test_prompt_defense.py::TestPromptDefense::test_sanitize_with_mixed_delimiters PASSED [ 42%]
tests/unit/test_prompt_templates.py::TestPromptTemplates::test_all_5_templates_exist PASSED [ 42%]
tests/unit/test_prompt_templates.py::TestPromptTemplates::test_skills_feedback_template_exists PASSED [ 42%]
tests/unit/test_prompt_templates.py::TestPromptTemplates::test_projects_feedback_template_exists PASSED [ 42%]
tests/unit/test_prompt_templates.py::TestPromptTemplates::test_presentation_feedback_template_exists PASSED [ 43%]
tests/unit/test_prompt_templates.py::TestPromptTemplates::test_gaps_feedback_template_exists PASSED [ 43%]
tests/unit/test_prompt_templates.py::TestPromptTemplates::test_first_impression_template_exists PASSED [ 43%]
tests/unit/test_prompt_templates.py::TestPromptTemplates::test_each_template_contains_context_placeholder PASSED [ 43%]
tests/unit/test_prompt_templates.py::TestPromptTemplates::test_each_template_contains_github_username_placeholder PASSED [ 44%]
tests/unit/test_prompt_templates.py::TestPromptTemplates::test_each_template_contains_project_count_placeholder PASSED [ 44%]
tests/unit/test_prompt_templates.py::TestPromptTemplates::test_get_template_returns_correct_template PASSED [ 44%]
tests/unit/test_prompt_templates.py::TestPromptTemplates::test_get_template_projects_feedback PASSED [ 44%]
tests/unit/test_prompt_templates.py::TestPromptTemplates::test_get_template_presentation_feedback PASSED [ 44%]
tests/unit/test_prompt_templates.py::TestPromptTemplates::test_get_template_gaps_feedback PASSED [ 45%]
tests/unit/test_prompt_templates.py::TestPromptTemplates::test_get_template_first_impression PASSED [ 45%]
tests/unit/test_prompt_templates.py::TestPromptTemplates::test_get_template_unknown_name_raises_error PASSED [ 45%]
tests/unit/test_prompt_templates.py::TestPromptTemplates::test_get_template_unknown_version_raises_error PASSED [ 45%]
tests/unit/test_prompt_templates.py::TestPromptTemplates::test_all_templates_have_v1 PASSED [ 46%]
tests/unit/test_prompt_templates.py::TestPromptTemplates::test_templates_are_strings PASSED [ 46%]
tests/unit/test_prompt_templates.py::TestPromptTemplates::test_templates_have_reasonable_length PASSED [ 46%]
tests/unit/test_prompt_templates.py::TestPromptTemplates::test_skills_feedback_mentions_technical_skills PASSED [ 46%]
tests/unit/test_prompt_templates.py::TestPromptTemplates::test_projects_feedback_mentions_code_quality PASSED [ 47%]
tests/unit/test_prompt_templates.py::TestPromptTemplates::test_gaps_feedback_mentions_missing_skills PASSED [ 47%]
tests/unit/test_prompt_templates.py::TestPromptTemplates::test_presentation_feedback_mentions_readme PASSED [ 47%]
tests/unit/test_prompt_templates.py::TestPromptTemplates::test_first_impression_is_concise PASSED [ 47%]
tests/unit/test_prompt_templates.py::TestPromptTemplates::test_get_template_default_version PASSED [ 47%]
tests/unit/test_prompt_templates.py::TestPromptTemplates::test_template_snapshot_content_hash PASSED [ 48%]
tests/unit/test_prompt_templates.py::TestPromptTemplates::test_skills_feedback_requests_json_format PASSED [ 48%]
tests/unit/test_prompt_templates.py::TestPromptTemplates::test_projects_feedback_requests_json_format PASSED [ 48%]
tests/unit/test_prompt_templates.py::TestPromptTemplates::test_presentation_feedback_requests_json_format PASSED [ 48%]
tests/unit/test_prompt_templates.py::TestPromptTemplates::test_gaps_feedback_requests_json_format PASSED [ 49%]
tests/unit/test_prompt_templates.py::TestPromptTemplates::test_first_impression_plain_text PASSED [ 49%]
tests/unit/test_prompt_templates.py::TestPromptTemplates::test_templates_have_portfolio_context PASSED [ 49%]
tests/unit/test_prompt_templates.py::TestPromptTemplates::test_template_get_logs_retrieval PASSED [ 49%]
tests/unit/test_prompt_templates.py::TestPromptTemplates::test_each_template_name_is_valid_identifier PASSED [ 50%]
tests/unit/test_prompt_templates.py::TestPromptTemplates::test_template_versions_are_strings PASSED [ 50%]
tests/unit/test_prompt_templates.py::TestPromptTemplates::test_no_hardcoded_usernames_in_templates PASSED [ 50%]
tests/unit/test_prompt_templates.py::TestPromptTemplates::test_templates_use_consistent_placeholders PASSED [ 50%]
tests/unit/test_rate_limiter.py::TestRateLimiter::test_first_request_allowed PASSED [ 50%]
tests/unit/test_rate_limiter.py::TestRateLimiter::test_requests_up_to_limit_allowed PASSED [ 51%]
tests/unit/test_rate_limiter.py::TestRateLimiter::test_request_at_limit_plus_one_denied PASSED [ 51%]
tests/unit/test_rate_limiter.py::TestRateLimiter::test_remaining_count_correct PASSED [ 51%]
tests/unit/test_rate_limiter.py::TestRateLimiter::test_rolling_window_removes_old_entries PASSED [ 51%]
tests/unit/test_rate_limiter.py::TestRateLimiter::test_different_identifiers_independent PASSED [ 52%]
tests/unit/test_rate_limiter.py::TestRateLimiter::test_key_format_correct PASSED [ 52%]
tests/unit/test_rate_limiter.py::TestRateLimiter::test_entry_added_to_redis PASSED [ 52%]
tests/unit/test_rate_limiter.py::TestRateLimiter::test_expiry_set_correctly PASSED [ 52%]
tests/unit/test_rate_limiter.py::TestRateLimiter::test_custom_window_size PASSED [ 52%]
tests/unit/test_rate_limiter.py::TestRateLimiter::test_redis_error_handling PASSED [ 53%]
tests/unit/test_rate_limiter.py::TestRateLimiter::test_zero_limit PASSED [ 53%]
tests/unit/test_rate_limiter.py::TestRateLimiter::test_negative_limit PASSED [ 53%]
tests/unit/test_rate_limiter.py::TestRateLimiter::test_large_limit PASSED [ 53%]
tests/unit/test_rate_limiter.py::TestRateLimiter::test_return_tuple_structure PASSED [ 54%]
tests/unit/test_rate_limiter.py::TestRateLimiter::test_multiple_requests_same_user PASSED [ 54%]
tests/unit/test_rate_limiter.py::TestRateLimiter::test_time_based_window_calculation PASSED [ 54%]
tests/unit/test_rate_limiter.py::TestRateLimiter::test_ip_address_as_identifier PASSED [ 54%]
tests/unit/test_rate_limiter.py::TestRateLimiter::test_api_key_as_identifier PASSED [ 55%]
tests/unit/test_readme_parser.py::TestReadmeParser::test_parse_standard_readme XFAIL [ 55%]
tests/unit/test_readme_parser.py::TestReadmeParser::test_parse_readme_longer_than_10000_chars PASSED [ 55%]
tests/unit/test_readme_parser.py::TestReadmeParser::test_parse_readme_with_code_blocks PASSED [ 55%]
tests/unit/test_readme_parser.py::TestReadmeParser::test_parse_readme_without_code_blocks PASSED [ 55%]
tests/unit/test_readme_parser.py::TestReadmeParser::test_parse_empty_readme PASSED [ 56%]
tests/unit/test_readme_parser.py::TestReadmeParser::test_parse_readme_with_only_whitespace PASSED [ 56%]
tests/unit/test_readme_parser.py::TestReadmeParser::test_parse_readme_bytes_input PASSED [ 56%]
tests/unit/test_readme_parser.py::TestReadmeParser::test_parse_readme_bytes_with_utf8 PASSED [ 56%]
tests/unit/test_readme_parser.py::TestReadmeParser::test_parse_invalid_content_type PASSED [ 57%]
tests/unit/test_readme_parser.py::TestReadmeParser::test_extract_heading_hierarchy XFAIL [ 57%]
tests/unit/test_readme_parser.py::TestReadmeParser::test_extract_heading_hierarchy_no_headings PASSED [ 57%]
tests/unit/test_readme_parser.py::TestReadmeParser::test_parse_readme_with_badges PASSED [ 57%]
tests/unit/test_readme_parser.py::TestReadmeParser::test_parse_readme_without_badges PASSED [ 57%]
tests/unit/test_readme_parser.py::TestReadmeParser::test_metadata_structure PASSED [ 58%]
tests/unit/test_readme_parser.py::TestReadmeParser::test_word_count_accuracy PASSED [ 58%]
tests/unit/test_readme_scorer.py::TestReadmeScorer::test_readme_with_all_quality_signals XFAIL [ 58%]
tests/unit/test_readme_scorer.py::TestReadmeScorer::test_readme_with_no_content PASSED [ 58%]
tests/unit/test_readme_scorer.py::TestReadmeScorer::test_readme_with_only_title PASSED [ 59%]
tests/unit/test_readme_scorer.py::TestReadmeScorer::test_word_count_category_minimal PASSED [ 59%]
tests/unit/test_readme_scorer.py::TestReadmeScorer::test_word_count_category_adequate PASSED [ 59%]
tests/unit/test_readme_scorer.py::TestReadmeScorer::test_word_count_category_comprehensive PASSED [ 59%]
tests/unit/test_readme_scorer.py::TestReadmeScorer::test_installation_section_detection PASSED [ 60%]
tests/unit/test_readme_scorer.py::TestReadmeScorer::test_usage_section_detection PASSED [ 60%]
tests/unit/test_readme_scorer.py::TestReadmeScorer::test_setup_keyword_counts_as_installation PASSED [ 60%]
tests/unit/test_readme_scorer.py::TestReadmeScorer::test_quickstart_counts_as_usage PASSED [ 60%]
tests/unit/test_readme_scorer.py::TestReadmeScorer::test_badge_detection PASSED [ 60%]
tests/unit/test_readme_scorer.py::TestReadmeScorer::test_demo_link_detection PASSED [ 61%]
tests/unit/test_readme_scorer.py::TestReadmeScorer::test_tech_stack_section_detection PASSED [ 61%]
tests/unit/test_readme_scorer.py::TestReadmeScorer::test_technologies_keyword_counts PASSED [ 61%]
tests/unit/test_readme_scorer.py::TestReadmeScorer::test_overall_score_calculation PASSED [ 61%]
tests/unit/test_readme_scorer.py::TestReadmeScorer::test_missing_readme_content_key PASSED [ 62%]
tests/unit/test_readme_scorer.py::TestReadmeScorer::test_result_has_all_required_fields PASSED [ 62%]
tests/unit/test_readme_scorer.py::TestReadmeScorer::test_case_insensitive_section_detection PASSED [ 62%]
tests/unit/test_readme_scorer.py::TestReadmeScorer::test_whitespace_only_readme PASSED [ 62%]
tests/unit/test_readme_scorer.py::TestReadmeScorer::test_example_keyword_counts_as_usage PASSED [ 63%]
tests/unit/test_readme_scorer.py::TestReadmeScorer::test_score_scales_with_word_count PASSED [ 63%]
tests/unit/test_readme_scorer.py::TestReadmeScorer::test_try_it_as_demo_indicator PASSED [ 63%]
tests/unit/test_readme_scorer.py::TestReadmeScorer::test_built_with_counts_as_tech_stack PASSED [ 63%]
tests/unit/test_relevance_scorer.py::TestRelevanceScorer::test_query_with_perfect_keyword_match PASSED [ 63%]
tests/unit/test_relevance_scorer.py::TestRelevanceScorer::test_query_with_zero_keyword_overlap PASSED [ 64%]
tests/unit/test_relevance_scorer.py::TestRelevanceScorer::test_query_with_partial_overlap XFAIL [ 64%]
tests/unit/test_relevance_scorer.py::TestRelevanceScorer::test_empty_chunks_list_returns_zero PASSED [ 64%]
tests/unit/test_relevance_scorer.py::TestRelevanceScorer::test_empty_query_returns_zero PASSED [ 64%]
tests/unit/test_relevance_scorer.py::TestRelevanceScorer::test_multiple_chunks_aggregated PASSED [ 65%]
tests/unit/test_relevance_scorer.py::TestRelevanceScorer::test_case_insensitive_matching PASSED [ 65%]
tests/unit/test_relevance_scorer.py::TestRelevanceScorer::test_tokenization PASSED [ 65%]
tests/unit/test_relevance_scorer.py::TestRelevanceScorer::test_empty_text_in_chunk PASSED [ 65%]
tests/unit/test_relevance_scorer.py::TestRelevanceScorer::test_very_long_query PASSED [ 65%]
tests/unit/test_relevance_scorer.py::TestRelevanceScorer::test_very_long_chunk PASSED [ 66%]
tests/unit/test_relevance_scorer.py::TestRelevanceScorer::test_special_characters_ignored PASSED [ 66%]
tests/unit/test_relevance_scorer.py::TestRelevanceScorer::test_multiple_keyword_matches PASSED [ 66%]
tests/unit/test_relevance_scorer.py::TestRelevanceScorer::test_single_word_chunks PASSED [ 66%]
tests/unit/test_relevance_scorer.py::TestRelevanceScorer::test_score_ranges_from_zero_to_one PASSED [ 67%]
tests/unit/test_relevance_scorer.py::TestRelevanceScorer::test_common_words_not_preventing_scoring PASSED [ 67%]
tests/unit/test_relevance_scorer.py::TestRelevanceScorer::test_chunk_without_text_key PASSED [ 67%]
tests/unit/test_relevance_scorer.py::TestRelevanceScorer::test_whitespace_only_in_chunks PASSED [ 67%]
tests/unit/test_relevance_scorer.py::TestRelevanceScorer::test_average_relevance_calculation PASSED [ 68%]
tests/unit/test_resume_parser.py::TestResumeParser::test_parse_single_column_resume_text XFAIL [ 68%]
tests/unit/test_resume_parser.py::TestResumeParser::test_parse_resume_no_work_experience XFAIL [ 68%]
tests/unit/test_resume_parser.py::TestResumeParser::test_parse_multipage_pdf PASSED [ 68%]
tests/unit/test_resume_parser.py::TestResumeParser::test_parse_markdown_resume XFAIL [ 68%]
tests/unit/test_resume_parser.py::TestResumeParser::test_parse_invalid_content_type PASSED [ 69%]
tests/unit/test_resume_parser.py::TestResumeParser::test_parse_invalid_list_content PASSED [ 69%]
tests/unit/test_resume_parser.py::TestResumeParser::test_detect_sections XFAIL [ 69%]
tests/unit/test_resume_parser.py::TestResumeParser::test_strip_markdown_syntax XFAIL [ 69%]
tests/unit/test_resume_parser.py::TestResumeParser::test_pdf_parsing_error_handling PASSED [ 70%]
tests/unit/test_resume_parser.py::TestResumeParser::test_parse_preserves_text_content PASSED [ 70%]
tests/unit/test_review_service.py::TestReviewService::test_create_review_returns_review_with_pending_status PASSED [ 70%]
tests/unit/test_review_service.py::TestReviewService::test_get_review_returns_review_for_correct_owner XFAIL [ 70%]
tests/unit/test_review_service.py::TestReviewService::test_get_review_returns_none_for_wrong_user XFAIL [ 71%]
tests/unit/test_review_service.py::TestReviewService::test_list_reviews_returns_paginated_results XFAIL [ 71%]
tests/unit/test_review_service.py::TestReviewService::test_list_reviews_page_2_returns_correct_offset XFAIL [ 71%]
tests/unit/test_review_service.py::TestReviewService::test_list_reviews_returns_tuple XFAIL [ 71%]
tests/unit/test_review_service.py::TestReviewService::test_create_review_calls_db_add PASSED [ 71%]
tests/unit/test_review_service.py::TestReviewService::test_create_review_calls_db_commit PASSED [ 72%]
tests/unit/test_review_service.py::TestReviewService::test_create_review_calls_db_refresh PASSED [ 72%]
tests/unit/test_review_service.py::TestReviewService::test_get_review_uses_select_and_join XFAIL [ 72%]
tests/unit/test_review_service.py::TestReviewService::test_list_reviews_default_pagination XFAIL [ 72%]
tests/unit/test_review_service.py::TestReviewService::test_list_reviews_custom_page_size XFAIL [ 73%]
tests/unit/test_review_service.py::TestReviewService::test_create_review_with_uuid_ids PASSED [ 73%]
tests/unit/test_review_service.py::TestReviewService::test_get_review_verifies_ownership XFAIL [ 73%]
tests/unit/test_review_service.py::TestReviewService::test_list_reviews_counts_total XFAIL [ 73%]
tests/unit/test_review_service.py::TestReviewService::test_list_reviews_returns_reviews_list XFAIL [ 73%]
tests/unit/test_review_service.py::TestReviewService::test_review_sections_and_score_initially_none PASSED [ 74%]
tests/unit/test_review_service.py::TestReviewService::test_get_review_with_valid_uuid XFAIL [ 74%]
tests/unit/test_review_service.py::TestReviewService::test_list_reviews_ordered_by_created_at XFAIL [ 74%]
tests/unit/test_review_service.py::TestReviewService::test_process_review_notifies_on_early_return PASSED [ 74%]
tests/unit/test_security.py::TestSecurity::test_hash_password_returns_bcrypt_hash PASSED [ 75%]
tests/unit/test_security.py::TestSecurity::test_verify_password_correct PASSED [ 75%]
tests/unit/test_security.py::TestSecurity::test_verify_password_incorrect PASSED [ 75%]
tests/unit/test_security.py::TestSecurity::test_verify_password_case_sensitive PASSED [ 75%]
tests/unit/test_security.py::TestSecurity::test_hash_same_password_different_hash PASSED [ 76%]
tests/unit/test_security.py::TestSecurity::test_create_access_token_returns_string PASSED [ 76%]
tests/unit/test_security.py::TestSecurity::test_create_access_token_is_jwt PASSED [ 76%]
tests/unit/test_security.py::TestSecurity::test_decode_access_token_valid PASSED [ 76%]
tests/unit/test_security.py::TestSecurity::test_decode_access_token_invalid_token PASSED [ 76%]
tests/unit/test_security.py::TestSecurity::test_decode_access_token_malformed PASSED [ 77%]
tests/unit/test_security.py::TestSecurity::test_decode_access_token_empty_string PASSED [ 77%]
tests/unit/test_security.py::TestSecurity::test_roundtrip_token_with_data PASSED [ 77%]
tests/unit/test_security.py::TestSecurity::test_create_access_token_with_custom_expiry PASSED [ 77%]
tests/unit/test_security.py::TestSecurity::test_access_token_includes_expiration PASSED [ 78%]
tests/unit/test_security.py::TestSecurity::test_password_hash_different_for_different_passwords PASSED [ 78%]
tests/unit/test_security.py::TestSecurity::test_verify_password_with_empty_strings PASSED [ 78%]
tests/unit/test_security.py::TestSecurity::test_verify_password_with_special_characters PASSED [ 78%]
tests/unit/test_security.py::TestSecurity::test_token_with_empty_data PASSED [ 78%]
tests/unit/test_security.py::TestSecurity::test_token_with_special_characters_in_data PASSED [ 79%]
tests/unit/test_security.py::TestSecurity::test_token_with_unicode_data PASSED [ 79%]
tests/unit/test_security.py::TestSecurity::test_hash_password_long_input PASSED [ 79%]
tests/unit/test_security.py::TestSecurity::test_verify_with_wrong_hash_format XFAIL [ 79%]
tests/unit/test_security.py::TestSecurity::test_token_tampering_detection PASSED [ 80%]
tests/unit/test_security.py::TestSecurity::test_create_token_consistency PASSED [ 80%]
tests/unit/test_security.py::TestSecurity::test_password_with_whitespace PASSED [ 80%]
tests/unit/test_semantic_chunker.py::TestSemanticChunker::test_empty_input_returns_empty_list PASSED [ 80%]
tests/unit/test_semantic_chunker.py::TestSemanticChunker::test_whitespace_only_input PASSED [ 81%]
tests/unit/test_semantic_chunker.py::TestSemanticChunker::test_short_text_returns_single_chunk PASSED [ 81%]
tests/unit/test_semantic_chunker.py::TestSemanticChunker::test_long_text_returns_multiple_chunks PASSED [ 81%]
tests/unit/test_semantic_chunker.py::TestSemanticChunker::test_chunk_metadata_includes_chunk_index PASSED [ 81%]
tests/unit/test_semantic_chunker.py::TestSemanticChunker::test_chunks_preserve_source_metadata PASSED [ 81%]
tests/unit/test_semantic_chunker.py::TestSemanticChunker::test_chunk_has_character_positions PASSED [ 82%]
tests/unit/test_semantic_chunker.py::TestSemanticChunker::test_bullet_points_not_split_mid_bullet PASSED [ 82%]
tests/unit/test_semantic_chunker.py::TestSemanticChunker::test_sentence_splitting PASSED [ 82%]
tests/unit/test_semantic_chunker.py::TestSemanticChunker::test_sentence_splitting_with_exclamation_marks PASSED [ 82%]
tests/unit/test_semantic_chunker.py::TestSemanticChunker::test_sentence_splitting_preserves_punctuation PASSED [ 83%]
tests/unit/test_semantic_chunker.py::TestSemanticChunker::test_overlap_between_chunks PASSED [ 83%]
tests/unit/test_semantic_chunker.py::TestSemanticChunker::test_chunks_have_non_zero_text PASSED [ 83%]
tests/unit/test_semantic_chunker.py::TestSemanticChunker::test_paragraph_boundaries_respected PASSED [ 83%]
tests/unit/test_semantic_chunker.py::TestSemanticChunker::test_metadata_copied_not_mutated PASSED [ 84%]
tests/unit/test_semantic_chunker.py::TestSemanticChunker::test_chunk_indexing_is_sequential PASSED [ 84%]
tests/unit/test_skill_extractor.py::TestSkillExtractor::test_text_with_python_imports PASSED [ 84%]
tests/unit/test_skill_extractor.py::TestSkillExtractor::test_text_with_python_type_annotations PASSED [ 84%]
tests/unit/test_skill_extractor.py::TestSkillExtractor::test_text_with_typescript_files XFAIL [ 84%]
tests/unit/test_skill_extractor.py::TestSkillExtractor::test_jupyter_ipynb_detection PASSED [ 85%]
tests/unit/test_skill_extractor.py::TestSkillExtractor::test_mixed_language_text PASSED [ 85%]
tests/unit/test_skill_extractor.py::TestSkillExtractor::test_frameworks_detected_with_high_confidence PASSED [ 85%]
tests/unit/test_skill_extractor.py::TestSkillExtractor::test_react_detection PASSED [ 85%]
tests/unit/test_skill_extractor.py::TestSkillExtractor::test_database_technology_detection XFAIL [ 86%]
tests/unit/test_skill_extractor.py::TestSkillExtractor::test_devops_tool_detection XFAIL [ 86%]
tests/unit/test_skill_extractor.py::TestSkillExtractor::test_skill_has_evidence_list PASSED [ 86%]
tests/unit/test_skill_extractor.py::TestSkillExtractor::test_filename_based_detection PASSED [ 86%]
tests/unit/test_skill_extractor.py::TestSkillExtractor::test_javascript_detection XFAIL [ 86%]
tests/unit/test_skill_extractor.py::TestSkillExtractor::test_docker_compose_detection XFAIL [ 87%]
tests/unit/test_skill_extractor.py::TestSkillExtractor::test_aws_gcp_azure_detection PASSED [ 87%]
tests/unit/test_skill_extractor.py::TestSkillExtractor::test_empty_text PASSED [ 87%]
tests/unit/test_skill_extractor.py::TestSkillExtractor::test_unrecognized_language PASSED [ 87%]
tests/unit/test_skill_extractor.py::TestSkillExtractor::test_confidence_scores_are_floats PASSED [ 88%]
tests/unit/test_skill_extractor.py::TestSkillExtractor::test_skill_detection_dataclass PASSED [ 88%]
tests/unit/test_structural_chunker.py::TestStructuralChunker::test_empty_input_returns_empty_list PASSED [ 88%]
tests/unit/test_structural_chunker.py::TestStructuralChunker::test_whitespace_only_input PASSED [ 88%]
tests/unit/test_structural_chunker.py::TestStructuralChunker::test_document_with_no_headings XFAIL [ 89%]
tests/unit/test_structural_chunker.py::TestStructuralChunker::test_document_with_nested_headings PASSED [ 89%]
tests/unit/test_structural_chunker.py::TestStructuralChunker::test_heading_path_format PASSED [ 89%]
tests/unit/test_structural_chunker.py::TestStructuralChunker::test_large_section_sub_chunked PASSED [ 89%]
tests/unit/test_structural_chunker.py::TestStructuralChunker::test_chunk_metadata_includes_heading_level PASSED [ 89%]
tests/unit/test_structural_chunker.py::TestStructuralChunker::test_chunk_metadata_structure PASSED [ 90%]
tests/unit/test_structural_chunker.py::TestStructuralChunker::test_preserve_source_metadata PASSED [ 90%]
tests/unit/test_structural_chunker.py::TestStructuralChunker::test_multiple_h1_headings PASSED [ 90%]
tests/unit/test_structural_chunker.py::TestStructuralChunker::test_heading_path_breadcrumb PASSED [ 90%]
tests/unit/test_structural_chunker.py::TestStructuralChunker::test_chunks_have_text_content PASSED [ 91%]
tests/unit/test_structural_chunker.py::TestStructuralChunker::test_section_extraction_with_multiple_levels PASSED [ 91%]
tests/unit/test_structural_chunker.py::TestStructuralChunker::test_heading_not_in_middle_of_content PASSED [ 91%]
tests/unit/test_structural_chunker.py::TestStructuralChunker::test_empty_sections_handled PASSED [ 91%]
tests/unit/test_tech_detector.py::TestTechDetector::test_single_language_repo PASSED [ 92%]
tests/unit/test_tech_detector.py::TestTechDetector::test_mixed_language_repo_python_primary PASSED [ 92%]
tests/unit/test_tech_detector.py::TestTechDetector::test_ipynb_counted_as_python_not_json PASSED [ 92%]
tests/unit/test_tech_detector.py::TestTechDetector::test_node_modules_excluded XFAIL [ 92%]
tests/unit/test_tech_detector.py::TestTechDetector::test_vendor_files_excluded PASSED [ 92%]
tests/unit/test_tech_detector.py::TestTechDetector::test_build_directory_excluded XFAIL [ 93%]
tests/unit/test_tech_detector.py::TestTechDetector::test_config_file_detection PASSED [ 93%]
tests/unit/test_tech_detector.py::TestTechDetector::test_dockerfile_detection PASSED [ 93%]
tests/unit/test_tech_detector.py::TestTechDetector::test_github_actions_detection PASSED [ 93%]
tests/unit/test_tech_detector.py::TestTechDetector::test_makefile_detection PASSED [ 94%]
tests/unit/test_tech_detector.py::TestTechDetector::test_typescript_detection PASSED [ 94%]
tests/unit/test_tech_detector.py::TestTechDetector::test_go_detection PASSED [ 94%]
tests/unit/test_tech_detector.py::TestTechDetector::test_rust_detection PASSED [ 94%]
tests/unit/test_tech_detector.py::TestTechDetector::test_java_detection PASSED [ 94%]
tests/unit/test_tech_detector.py::TestTechDetector::test_multiple_python_files PASSED [ 95%]
tests/unit/test_tech_detector.py::TestTechDetector::test_empty_file_list PASSED [ 95%]
tests/unit/test_tech_detector.py::TestTechDetector::test_no_files_key PASSED [ 95%]
tests/unit/test_tech_detector.py::TestTechDetector::test_result_structure PASSED [ 95%]
tests/unit/test_tech_detector.py::TestTechDetector::test_framework_detection PASSED [ 96%]
tests/unit/test_tech_detector.py::TestTechDetector::test_unknown_extensions PASSED [ 96%]
tests/unit/test_tech_detector.py::TestTechDetector::test_case_insensitive_extension_matching PASSED [ 96%]
tests/unit/test_tech_detector.py::TestTechDetector::test_multiple_extensions_same_file PASSED [ 96%]
tests/unit/test_tech_detector.py::TestTechDetector::test_all_languages_sorted PASSED [ 97%]
tests/unit/test_tech_detector.py::TestTechDetector::test_frameworks_sorted PASSED [ 97%]
tests/unit/test_tech_detector.py::TestTechDetector::test_ruby_detection PASSED [ 97%]
tests/unit/test_tech_detector.py::TestTechDetector::test_csharp_detection PASSED [ 97%]
tests/unit/test_tech_detector.py::TestTechDetector::test_cpp_detection PASSED [ 97%]
tests/unit/test_webhook_service.py::TestNotifyReviewFinished::test_finished_review_is_posted_once[complete] PASSED [ 98%]
tests/unit/test_webhook_service.py::TestNotifyReviewFinished::test_finished_review_is_posted_once[failed] PASSED [ 98%]
tests/unit/test_webhook_service.py::TestNotifyReviewFinished::test_review_is_reloaded_from_db PASSED [ 98%]
tests/unit/test_webhook_service.py::TestNotifyReviewFinished::test_unfinished_review_is_not_posted[pending] PASSED [ 98%]
tests/unit/test_webhook_service.py::TestNotifyReviewFinished::test_unfinished_review_is_not_posted[processing] PASSED [ 99%]
tests/unit/test_webhook_service.py::TestNotifyReviewFinished::test_missing_review_is_not_posted PASSED [ 99%]
tests/unit/test_webhook_service.py::TestNotifyReviewFinished::test_owner_without_webhooks_is_not_posted PASSED [ 99%]
tests/unit/test_webhook_service.py::TestNotifyReviewFinished::test_unreachable_url_is_logged_not_raised PASSED [ 99%]
tests/unit/test_webhook_service.py::TestNotifyReviewFinished::test_broken_session_is_logged_not_raised PASSED [100%]/home/ein/Eu/codepath/ai301/pathreview-ai301-fa26-s3/.venv/lib/python3.12/site-packages/_pytest/unraisableexception.py:33: RuntimeWarning: coroutine 'AsyncMockMixin._execute_mock_call' was never awaited
  gc.collect()
RuntimeWarning: Enable tracemalloc to get the object allocation traceback


=============================== warnings summary ===============================
core/config.py:7
  /home/ein/Eu/codepath/ai301/pathreview-ai301-fa26-s3/core/config.py:7: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.13/migration/
    class Settings(BaseSettings):

.venv/lib/python3.12/site-packages/passlib/utils/__init__.py:854
  /home/ein/Eu/codepath/ai301/pathreview-ai301-fa26-s3/.venv/lib/python3.12/site-packages/passlib/utils/__init__.py:854: DeprecationWarning: 'crypt' is deprecated and slated for removal in Python 3.13
    from crypt import crypt as _crypt

tests/unit/test_review_service.py::TestReviewService::test_get_review_returns_none_for_wrong_user
tests/unit/test_review_service.py::TestReviewService::test_get_review_with_valid_uuid
  /usr/lib/python3.12/unittest/mock.py:2188: RuntimeWarning: coroutine 'AsyncMockMixin._execute_mock_call' was never awaited
    def __init__(self, name, parent):
  Enable tracemalloc to get traceback where the object was allocated.
  See https://docs.pytest.org/en/stable/how-to/capture-warnings.html#resource-warnings for more info.

tests/unit/test_review_service.py::TestReviewService::test_create_review_calls_db_add
  /usr/lib/python3.12/unittest/mock.py:434: RuntimeWarning: coroutine 'AsyncMockMixin._execute_mock_call' was never awaited
    new = type(cls.__name__, bases, {'__doc__': cls.__doc__})
  Enable tracemalloc to get traceback where the object was allocated.
  See https://docs.pytest.org/en/stable/how-to/capture-warnings.html#resource-warnings for more info.

tests/unit/test_semantic_chunker.py::TestSemanticChunker::test_empty_input_returns_empty_list
  /home/ein/Eu/codepath/ai301/pathreview-ai301-fa26-s3/.venv/lib/python3.12/site-packages/urllib3/__init__.py:18: RuntimeWarning: coroutine 'AsyncMockMixin._execute_mock_call' was never awaited
    from .connectionpool import HTTPConnectionPool, HTTPSConnectionPool, connection_from_url
  Enable tracemalloc to get traceback where the object was allocated.
  See https://docs.pytest.org/en/stable/how-to/capture-warnings.html#resource-warnings for more info.

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
================= 385 passed, 53 xfailed, 6 warnings in 11.04s =================
```

### make test-integration

```
$ make test-integration
.venv/bin/pytest tests/integration -v -m integration
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.1.1, pluggy-1.6.0 -- /home/ein/Eu/codepath/ai301/pathreview-ai301-fa26-s3/.venv/bin/python3
cachedir: .pytest_cache
hypothesis profile 'default'
benchmark: 5.3.0 (defaults: timer=time.perf_counter disable_gc=False min_rounds=5 min_time=0.000005 max_time=1.0 calibration_precision=10 warmup=False warmup_iterations=100000)
rootdir: /home/ein/Eu/codepath/ai301/pathreview-ai301-fa26-s3
configfile: pyproject.toml
plugins: hypothesis-6.168.3, pytest_httpserver-1.1.5, platformdirs-4.12.2, asyncio-1.4.0, cov-7.1.0, benchmark-5.3.0, anyio-4.15.1
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 0 items

============================ no tests ran in 0.14s =============================
make: *** [Makefile:43: test-integration] Error 5
```

### make lint

```
$ make lint
.venv/bin/ruff check .
All checks passed!
```

### make typecheck

```
$ make typecheck
.venv/bin/mypy api/ core/ ingestion/ rag/ agent/ safety/
.venv/lib/python3.12/site-packages/numpy/__init__.pyi:737: error: Type statement is only supported in Python 3.12 and greater  [syntax]
Found 1 error in 1 file (errors prevented further checking)
make: *** [Makefile:57: typecheck] Error 2
```

Same command on `main` (temporary worktree, same venv):

```
$ make typecheck
.venv/bin/mypy api/ core/ ingestion/ rag/ agent/ safety/
.venv/lib/python3.12/site-packages/numpy/__init__.pyi:737: error: Type statement is only supported in Python 3.12 and greater  [syntax]
Found 1 error in 1 file (errors prevented further checking)
make: *** [Makefile:57: typecheck] Error 2
```

On the branch, with the target version matching the venv:

```
$ .venv/bin/mypy --python-version 3.12 api/ core/ ingestion/ rag/ agent/ safety/
Success: no issues found in 80 source files
```

## Unit 2 repro, before and after

Same script (`evidence/run_repro.sh`, my Unit 2 steps plus the plan's
test-plan checks), same DB and seed data. Before: uvicorn served from a
temporary worktree of `main`. After: uvicorn served from the branch.

| Step | Before (`main`) | After (branch) | Plan expected |
|---|---|---|---|
| `/openapi.json` lists `/webhooks` | no | yes | yes |
| 4a `POST /webhooks` | 404 | 200, `id` + `url` | 200, `id` + `url` |
| 4b same request again | 404 | 200, same `id`; 1 row | same `id`, no duplicate |
| 5–6 create review, poll 5 s, wait 5 s | `complete`; listener **0** requests | `complete`; listener **exactly 1** POST, `id` and `"status":"complete"` match | exactly 1 POST |
| Webhook body vs `GET /reviews/{id}` | no body | identical | same JSON |
| Server log after `review_processing_completed` | nothing | `webhook_delivered status_code=200` | `webhook_delivered` 200 |
| `POST /webhooks {"url": "not-a-url"}` | 404 | 422 | 422 |
| user2 (no webhook) creates a review | 0 requests | 0 requests, no `webhook_*` line | 0 requests |
| listener stopped, user1 creates a review | `complete` | `complete`, `webhook_delivery_failed error='All connection attempts failed'`, no traceback | `webhook_delivery_failed`, no traceback |

Ordering: the listener logged the POST at `01:14:46.006Z`; the review's
`updated_at` is `01:14:45.921` UTC as stored, so delivery came ~85 ms
after. (`GET` shows that instant as `05:14:45.921Z`: the existing
naive-datetime offset, also on `main`, outside #35.)

Notes on the transcripts:
- The `webhooks` row user1 registers was created on 2026-10-08 by my
  first after-run and the DB wasn't reset, so 4a returns that row's
  `created_at`, and the before run's row count also reads 1 (`main` has
  no code that touches the table).
- The only traceback in either server log is passlib's trapped
  `AttributeError: module 'bcrypt' has no attribute '__about__'` at the
  first login. It's in both runs and unrelated.

### Before (`main`)

```
### server under test: main @ 2f4e82f
### script run from: fix/35-review-webhooks @ fa8d761 (the server under test is named on the line above)
### 2026-10-26T01:14:23Z

## Step 3: log in as user1 (form-encoded)

$ TOKEN1=$(curl -s -X POST $API/auth/login -d "username=user1@example.com&password=password1" | json "[\"access_token\"]"); echo "token: ${TOKEN1:0:16}..."
token: eyJhbGciOiJIUzI1...

## Step 4: read user1's profile_id from the database

$ PROFILE1=$(psql_q "SELECT p.id FROM profiles p JOIN users u ON u.id=p.user_id WHERE u.email='user1@example.com'"); echo $PROFILE1
e1bd943f-67ec-4f5c-bcaf-c2089d8a536e

## Route list

$ curl -s $API/openapi.json | $PY -c "import json,sys; print(\"\n\".join(sorted(json.load(sys.stdin)[\"paths\"])))"
/
/auth/login
/auth/register
/health
/profiles
/profiles/{profile_id}
/reviews
/reviews/{review_id}
/reviews/{review_id}/status

## New 4a: register a webhook

$ curl -s -w "\n  HTTP %{http_code}\n" -X POST $API/webhooks -H "Authorization: Bearer $TOKEN1" -H "Content-Type: application/json" -d "{\"url\": \"http://127.0.0.1:9999/hook\"}"
{"detail":"Not Found"}
  HTTP 404

## New 4b: register the same URL again

$ curl -s -w "\n  HTTP %{http_code}\n" -X POST $API/webhooks -H "Authorization: Bearer $TOKEN1" -H "Content-Type: application/json" -d "{\"url\": \"http://127.0.0.1:9999/hook\"}"
{"detail":"Not Found"}
  HTTP 404

$ psql_q "SELECT count(*) FROM webhooks w JOIN users u ON u.id=w.user_id WHERE u.email='user1@example.com'"
1

## Step 5: create a review (with callback_url, as in Unit 2)

$ R=$(curl -s -X POST $API/reviews -H "Authorization: Bearer $TOKEN1" -H "Content-Type: application/json" -d "{\"profile_id\": \"$PROFILE1\", \"callback_url\": \"http://127.0.0.1:9999/hook\"}"); echo "$R"
{"id":"3458dd8d-3b4b-462b-bc74-baa79b80e6f3","profile_id":"e1bd943f-67ec-4f5c-bcaf-c2089d8a536e","status":"pending","sections":null,"overall_score":null,"error_message":null,"created_at":"2026-10-26T05:14:25.325470Z","updated_at":"2026-10-26T05:14:25.325473Z"}

## Step 6: poll status once a second for 5 s, then wait 5 s

$ for i in 1 2 3 4 5; do echo "[$(date -u +%T.%3N)] $(curl -s $API/reviews/$RID/status -H "Authorization: Bearer $TOKEN1")"; sleep 1; done; sleep 5
[01:14:25.379] {"review_id":"3458dd8d-3b4b-462b-bc74-baa79b80e6f3","status":"complete","progress_pct":0}
[01:14:26.401] {"review_id":"3458dd8d-3b4b-462b-bc74-baa79b80e6f3","status":"complete","progress_pct":0}
[01:14:27.427] {"review_id":"3458dd8d-3b4b-462b-bc74-baa79b80e6f3","status":"complete","progress_pct":0}
[01:14:28.457] {"review_id":"3458dd8d-3b4b-462b-bc74-baa79b80e6f3","status":"complete","progress_pct":0}
[01:14:29.504] {"review_id":"3458dd8d-3b4b-462b-bc74-baa79b80e6f3","status":"complete","progress_pct":0}

$ curl -s $API/reviews/$RID -H "Authorization: Bearer $TOKEN1" | $PY -c "import json,sys; d=json.load(sys.stdin); print(\"status\", d[\"status\"], \"| updated_at\", d[\"updated_at\"])"
status complete | updated_at 2026-10-26T05:14:25.351806Z

## Listener after step 6 (0 request(s))

$ cat $LISTENER_LOG
listening on 127.0.0.1:9999

## Webhook body vs GET /reviews/{id} (plan: same JSON)

$ curl -s $API/reviews/$RID -H "Authorization: Bearer $TOKEN1" > $OUT/get_review.json; grep -o "POST /hook .*" $LISTENER_LOG | tail -1 | cut -d" " -f3- > $OUT/webhook_body.json; $PY -c "import json; a=json.load(open(\"$OUT/get_review.json\")); b=json.load(open(\"$OUT/webhook_body.json\")) if open(\"$OUT/webhook_body.json\").read().strip() else {}; d=[k for k in a if a.get(k)!=b.get(k)]; print(\"identical\" if not d else \"differs: \"+\", \".join(f\"{k}: GET={a.get(k)!r} webhook={b.get(k)!r}\" for k in d))"
differs: id: GET='3458dd8d-3b4b-462b-bc74-baa79b80e6f3' webhook=None, profile_id: GET='e1bd943f-67ec-4f5c-bcaf-c2089d8a536e' webhook=None, status: GET='complete' webhook=None, sections: GET=[{'section_name': 'Technical Skills', 'content': 'Detailed feedback on technical skills based on portfolio analysis', 'confidence': 0.85, 'suggestions': ['Add more detail on AI/ML experience', 'Include specific technologies and frameworks']}, {'section_name': 'Project Experience', 'content': 'Detailed feedback on project experience and impact', 'confidence': 0.8, 'suggestions': ['Include measurable impact metrics', 'Add links to project repositories']}, {'section_name': 'Career Growth', 'content': 'Feedback on career progression and development', 'confidence': 0.78, 'suggestions': ['Document learning from each role', 'Highlight growth in responsibilities']}] webhook=None, overall_score: GET=0.81 webhook=None, created_at: GET='2026-10-26T05:14:25.325470Z' webhook=None, updated_at: GET='2026-10-26T05:14:25.351806Z' webhook=None

## Server log lines for this review

$ grep -E "$RID" $SERVER_LOG | grep -vE "\"GET |HTTP/1.1\"" 
2026-10-25 21:14:25,325 INFO sqlalchemy.engine.Engine [generated in 0.00028s] ('3458dd8d-3b4b-462b-bc74-baa79b80e6f3', UUID('e1bd943f-67ec-4f5c-bcaf-c2089d8a536e'), 'pending', 'null', None, None, datetime.datetime(2026, 10, 26, 1, 14, 25, 325470), datetime.datetime(2026, 10, 26, 1, 14, 25, 325473))
2026-10-25 21:14:25,336 INFO sqlalchemy.engine.Engine [generated in 0.00014s] ('3458dd8d-3b4b-462b-bc74-baa79b80e6f3',)
2026-10-25 21:14:25 [info     ] review_created                 profile_id=e1bd943f-67ec-4f5c-bcaf-c2089d8a536e request_id=5417e47a-019e-44b0-97a3-23fbaecd2fd2 review_id=3458dd8d-3b4b-462b-bc74-baa79b80e6f3 user_id=8689561e-23c5-49ea-a531-4d94f6d4e08f
2026-10-25 21:14:25,340 INFO sqlalchemy.engine.Engine [generated in 0.00020s] ('3458dd8d-3b4b-462b-bc74-baa79b80e6f3',)
2026-10-25 21:14:25,345 INFO sqlalchemy.engine.Engine [generated in 0.00020s] ('processing', datetime.datetime(2026, 10, 26, 1, 14, 25, 345295), '3458dd8d-3b4b-462b-bc74-baa79b80e6f3')
2026-10-25 21:14:25 [info     ] review_processing_started      profile_id=e1bd943f-67ec-4f5c-bcaf-c2089d8a536e request_id=5417e47a-019e-44b0-97a3-23fbaecd2fd2 review_id=3458dd8d-3b4b-462b-bc74-baa79b80e6f3
2026-10-25 21:14:25 [info     ] ingestion_pipeline_completed   request_id=5417e47a-019e-44b0-97a3-23fbaecd2fd2 review_id=3458dd8d-3b4b-462b-bc74-baa79b80e6f3 sources_count=2
2026-10-25 21:14:25 [info     ] agent_orchestration_completed  request_id=5417e47a-019e-44b0-97a3-23fbaecd2fd2 review_id=3458dd8d-3b4b-462b-bc74-baa79b80e6f3 sections_count=2
2026-10-25 21:14:25 [info     ] rag_retrieval_completed        request_id=5417e47a-019e-44b0-97a3-23fbaecd2fd2 review_id=3458dd8d-3b4b-462b-bc74-baa79b80e6f3
2026-10-25 21:14:25,353 INFO sqlalchemy.engine.Engine [generated in 0.00019s] ('complete', '[{"section_name": "Technical Skills", "content": "Detailed feedback on technical skills based on portfolio analysis", "confidence": 0.85, "suggestion ... (368 characters truncated) ... areer progression and development", "confidence": 0.78, "suggestions": ["Document learning from each role", "Highlight growth in responsibilities"]}]', 0.81, datetime.datetime(2026, 10, 26, 1, 14, 25, 351806), '3458dd8d-3b4b-462b-bc74-baa79b80e6f3')
2026-10-25 21:14:25 [info     ] review_processing_completed    overall_score=0.81 request_id=5417e47a-019e-44b0-97a3-23fbaecd2fd2 review_id=3458dd8d-3b4b-462b-bc74-baa79b80e6f3
2026-10-25 21:14:25,390 INFO sqlalchemy.engine.Engine [generated in 0.00015s] (UUID('3458dd8d-3b4b-462b-bc74-baa79b80e6f3'), '8689561e-23c5-49ea-a531-4d94f6d4e08f')
2026-10-25 21:14:26,417 INFO sqlalchemy.engine.Engine [cached since 1.027s ago] (UUID('3458dd8d-3b4b-462b-bc74-baa79b80e6f3'), '8689561e-23c5-49ea-a531-4d94f6d4e08f')
2026-10-25 21:14:27,447 INFO sqlalchemy.engine.Engine [cached since 2.057s ago] (UUID('3458dd8d-3b4b-462b-bc74-baa79b80e6f3'), '8689561e-23c5-49ea-a531-4d94f6d4e08f')
2026-10-25 21:14:28,491 INFO sqlalchemy.engine.Engine [cached since 3.101s ago] (UUID('3458dd8d-3b4b-462b-bc74-baa79b80e6f3'), '8689561e-23c5-49ea-a531-4d94f6d4e08f')
2026-10-25 21:14:29,517 INFO sqlalchemy.engine.Engine [cached since 4.127s ago] (UUID('3458dd8d-3b4b-462b-bc74-baa79b80e6f3'), '8689561e-23c5-49ea-a531-4d94f6d4e08f')
2026-10-25 21:14:35,545 INFO sqlalchemy.engine.Engine [cached since 10.16s ago] (UUID('3458dd8d-3b4b-462b-bc74-baa79b80e6f3'), '8689561e-23c5-49ea-a531-4d94f6d4e08f')
2026-10-25 21:14:35,589 INFO sqlalchemy.engine.Engine [cached since 10.2s ago] (UUID('3458dd8d-3b4b-462b-bc74-baa79b80e6f3'), '8689561e-23c5-49ea-a531-4d94f6d4e08f')

## Negative: bad URL

$ curl -s -o /dev/null -w "  HTTP %{http_code}\n" -X POST $API/webhooks -H "Authorization: Bearer $TOKEN1" -H "Content-Type: application/json" -d "{\"url\": \"not-a-url\"}"
  HTTP 404

## Negative: user2 (no webhook) creates a review

$ R2=$(curl -s -X POST $API/reviews -H "Authorization: Bearer $TOKEN2" -H "Content-Type: application/json" -d "{\"profile_id\": \"$PROFILE2\"}"); RID2=$(echo "$R2" | json "[\"id\"]"); sleep 3; curl -s $API/reviews/$RID2/status -H "Authorization: Bearer $TOKEN2"; echo
{"review_id":"91f98dab-25d9-4150-8a70-f4e9726a2307","status":"complete","progress_pct":0}
listener requests before: 0, after: 0

$ grep -E "$RID2" $SERVER_LOG | grep -cE "webhook_" || true
0

## Negative: listener stopped, user1 creates a review

$ R3=$(curl -s -X POST $API/reviews -H "Authorization: Bearer $TOKEN1" -H "Content-Type: application/json" -d "{\"profile_id\": \"$PROFILE1\"}"); RID3=$(echo "$R3" | json "[\"id\"]"); sleep 3; curl -s $API/reviews/$RID3/status -H "Authorization: Bearer $TOKEN1"; echo
{"review_id":"58cf25c4-3734-4402-93d4-9583eb2f8fc2","status":"complete","progress_pct":0}

$ grep -E "$RID3" $SERVER_LOG | grep -E "webhook_|review_processing_completed|Traceback"
2026-10-25 21:14:39 [info     ] review_processing_completed    overall_score=0.81 request_id=94e457a3-275a-48c2-85ad-91be477e304c review_id=58cf25c4-3734-4402-93d4-9583eb2f8fc2

$ grep -A4 Traceback $SERVER_LOG | grep -E "^[A-Za-z.]*(Error|Exception)" || echo "(no tracebacks)"
AttributeError: module 'bcrypt' has no attribute '__about__'
```

### After (`fix/35-review-webhooks`)

```
### server under test: fix/35-review-webhooks @ fa8d761
### script run from: fix/35-review-webhooks @ fa8d761 (the server under test is named on the line above)
### 2026-10-26T01:14:44Z

## Step 3: log in as user1 (form-encoded)

$ TOKEN1=$(curl -s -X POST $API/auth/login -d "username=user1@example.com&password=password1" | json "[\"access_token\"]"); echo "token: ${TOKEN1:0:16}..."
token: eyJhbGciOiJIUzI1...

## Step 4: read user1's profile_id from the database

$ PROFILE1=$(psql_q "SELECT p.id FROM profiles p JOIN users u ON u.id=p.user_id WHERE u.email='user1@example.com'"); echo $PROFILE1
e1bd943f-67ec-4f5c-bcaf-c2089d8a536e

## Route list

$ curl -s $API/openapi.json | $PY -c "import json,sys; print(\"\n\".join(sorted(json.load(sys.stdin)[\"paths\"])))"
/
/auth/login
/auth/register
/health
/profiles
/profiles/{profile_id}
/reviews
/reviews/{review_id}
/reviews/{review_id}/status
/webhooks

## New 4a: register a webhook

$ curl -s -w "\n  HTTP %{http_code}\n" -X POST $API/webhooks -H "Authorization: Bearer $TOKEN1" -H "Content-Type: application/json" -d "{\"url\": \"http://127.0.0.1:9999/hook\"}"
{"id":"56dc199c-6ee7-4f6b-9f65-057cf19c4c10","url":"http://127.0.0.1:9999/hook","created_at":"2026-10-08T06:54:21.779402Z"}
  HTTP 200

## New 4b: register the same URL again

$ curl -s -w "\n  HTTP %{http_code}\n" -X POST $API/webhooks -H "Authorization: Bearer $TOKEN1" -H "Content-Type: application/json" -d "{\"url\": \"http://127.0.0.1:9999/hook\"}"
{"id":"56dc199c-6ee7-4f6b-9f65-057cf19c4c10","url":"http://127.0.0.1:9999/hook","created_at":"2026-10-08T06:54:21.779402Z"}
  HTTP 200

$ psql_q "SELECT count(*) FROM webhooks w JOIN users u ON u.id=w.user_id WHERE u.email='user1@example.com'"
1

## Step 5: create a review (with callback_url, as in Unit 2)

$ R=$(curl -s -X POST $API/reviews -H "Authorization: Bearer $TOKEN1" -H "Content-Type: application/json" -d "{\"profile_id\": \"$PROFILE1\", \"callback_url\": \"http://127.0.0.1:9999/hook\"}"); echo "$R"
{"id":"05aaa210-f041-4c5a-b5a2-0df4b19995b2","profile_id":"e1bd943f-67ec-4f5c-bcaf-c2089d8a536e","status":"pending","sections":null,"overall_score":null,"error_message":null,"created_at":"2026-10-26T05:14:45.891781Z","updated_at":"2026-10-26T05:14:45.891785Z"}

## Step 6: poll status once a second for 5 s, then wait 5 s

$ for i in 1 2 3 4 5; do echo "[$(date -u +%T.%3N)] $(curl -s $API/reviews/$RID/status -H "Authorization: Bearer $TOKEN1")"; sleep 1; done; sleep 5
[01:14:45.956] {"review_id":"05aaa210-f041-4c5a-b5a2-0df4b19995b2","status":"complete","progress_pct":0}
[01:14:47.052] {"review_id":"05aaa210-f041-4c5a-b5a2-0df4b19995b2","status":"complete","progress_pct":0}
[01:14:48.084] {"review_id":"05aaa210-f041-4c5a-b5a2-0df4b19995b2","status":"complete","progress_pct":0}
[01:14:49.133] {"review_id":"05aaa210-f041-4c5a-b5a2-0df4b19995b2","status":"complete","progress_pct":0}
[01:14:50.161] {"review_id":"05aaa210-f041-4c5a-b5a2-0df4b19995b2","status":"complete","progress_pct":0}

$ curl -s $API/reviews/$RID -H "Authorization: Bearer $TOKEN1" | $PY -c "import json,sys; d=json.load(sys.stdin); print(\"status\", d[\"status\"], \"| updated_at\", d[\"updated_at\"])"
status complete | updated_at 2026-10-26T05:14:45.920698Z

## Listener after step 6 (1 request(s))

$ cat $LISTENER_LOG
listening on 127.0.0.1:9999
[2026-10-26T01:14:46.005995+00:00] POST /hook {"id":"05aaa210-f041-4c5a-b5a2-0df4b19995b2","profile_id":"e1bd943f-67ec-4f5c-bcaf-c2089d8a536e","status":"complete","sections":[{"section_name":"Technical Skills","content":"Detailed feedback on technical skills based on portfolio analysis","confidence":0.85,"suggestions":["Add more detail on AI/ML experience","Include specific technologies and frameworks"]},{"section_name":"Project Experience","content":"Detailed feedback on project experience and impact","confidence":0.8,"suggestions":["Include measurable impact metrics","Add links to project repositories"]},{"section_name":"Career Growth","content":"Feedback on career progression and development","confidence":0.78,"suggestions":["Document learning from each role","Highlight growth in responsibilities"]}],"overall_score":0.81,"error_message":null,"created_at":"2026-10-26T05:14:45.891781Z","updated_at":"2026-10-26T05:14:45.920698Z"}

## Webhook body vs GET /reviews/{id} (plan: same JSON)

$ curl -s $API/reviews/$RID -H "Authorization: Bearer $TOKEN1" > $OUT/get_review.json; grep -o "POST /hook .*" $LISTENER_LOG | tail -1 | cut -d" " -f3- > $OUT/webhook_body.json; $PY -c "import json; a=json.load(open(\"$OUT/get_review.json\")); b=json.load(open(\"$OUT/webhook_body.json\")) if open(\"$OUT/webhook_body.json\").read().strip() else {}; d=[k for k in a if a.get(k)!=b.get(k)]; print(\"identical\" if not d else \"differs: \"+\", \".join(f\"{k}: GET={a.get(k)!r} webhook={b.get(k)!r}\" for k in d))"
identical

## Server log lines for this review

$ grep -E "$RID" $SERVER_LOG | grep -vE "\"GET |HTTP/1.1\"" 
2026-10-25 21:14:45,891 INFO sqlalchemy.engine.Engine [generated in 0.00026s] ('05aaa210-f041-4c5a-b5a2-0df4b19995b2', UUID('e1bd943f-67ec-4f5c-bcaf-c2089d8a536e'), 'pending', 'null', None, None, datetime.datetime(2026, 10, 26, 1, 14, 45, 891781), datetime.datetime(2026, 10, 26, 1, 14, 45, 891785))
2026-10-25 21:14:45,906 INFO sqlalchemy.engine.Engine [generated in 0.00013s] ('05aaa210-f041-4c5a-b5a2-0df4b19995b2',)
2026-10-25 21:14:45 [info     ] review_created                 profile_id=e1bd943f-67ec-4f5c-bcaf-c2089d8a536e request_id=45651d8c-954b-428a-8720-d60194f88be6 review_id=05aaa210-f041-4c5a-b5a2-0df4b19995b2 user_id=8689561e-23c5-49ea-a531-4d94f6d4e08f
2026-10-25 21:14:45,909 INFO sqlalchemy.engine.Engine [generated in 0.00015s] ('05aaa210-f041-4c5a-b5a2-0df4b19995b2',)
2026-10-25 21:14:45,914 INFO sqlalchemy.engine.Engine [generated in 0.00020s] ('processing', datetime.datetime(2026, 10, 26, 1, 14, 45, 914360), '05aaa210-f041-4c5a-b5a2-0df4b19995b2')
2026-10-25 21:14:45 [info     ] review_processing_started      profile_id=e1bd943f-67ec-4f5c-bcaf-c2089d8a536e request_id=45651d8c-954b-428a-8720-d60194f88be6 review_id=05aaa210-f041-4c5a-b5a2-0df4b19995b2
2026-10-25 21:14:45 [info     ] ingestion_pipeline_completed   request_id=45651d8c-954b-428a-8720-d60194f88be6 review_id=05aaa210-f041-4c5a-b5a2-0df4b19995b2 sources_count=2
2026-10-25 21:14:45 [info     ] agent_orchestration_completed  request_id=45651d8c-954b-428a-8720-d60194f88be6 review_id=05aaa210-f041-4c5a-b5a2-0df4b19995b2 sections_count=2
2026-10-25 21:14:45 [info     ] rag_retrieval_completed        request_id=45651d8c-954b-428a-8720-d60194f88be6 review_id=05aaa210-f041-4c5a-b5a2-0df4b19995b2
2026-10-25 21:14:45,922 INFO sqlalchemy.engine.Engine [generated in 0.00022s] ('complete', '[{"section_name": "Technical Skills", "content": "Detailed feedback on technical skills based on portfolio analysis", "confidence": 0.85, "suggestion ... (368 characters truncated) ... areer progression and development", "confidence": 0.78, "suggestions": ["Document learning from each role", "Highlight growth in responsibilities"]}]', 0.81, datetime.datetime(2026, 10, 26, 1, 14, 45, 920698), '05aaa210-f041-4c5a-b5a2-0df4b19995b2')
2026-10-25 21:14:45 [info     ] review_processing_completed    overall_score=0.81 request_id=45651d8c-954b-428a-8720-d60194f88be6 review_id=05aaa210-f041-4c5a-b5a2-0df4b19995b2
2026-10-25 21:14:45,929 INFO sqlalchemy.engine.Engine [cached since 0.01999s ago] ('05aaa210-f041-4c5a-b5a2-0df4b19995b2',)
2026-10-25 21:14:46 [info     ] webhook_delivered              request_id=45651d8c-954b-428a-8720-d60194f88be6 review_id=05aaa210-f041-4c5a-b5a2-0df4b19995b2 status_code=200 url=http://127.0.0.1:9999/hook
2026-10-25 21:14:46,043 INFO sqlalchemy.engine.Engine [generated in 0.00016s] (UUID('05aaa210-f041-4c5a-b5a2-0df4b19995b2'), '8689561e-23c5-49ea-a531-4d94f6d4e08f')
2026-10-25 21:14:47,071 INFO sqlalchemy.engine.Engine [cached since 1.028s ago] (UUID('05aaa210-f041-4c5a-b5a2-0df4b19995b2'), '8689561e-23c5-49ea-a531-4d94f6d4e08f')
2026-10-25 21:14:48,119 INFO sqlalchemy.engine.Engine [cached since 2.076s ago] (UUID('05aaa210-f041-4c5a-b5a2-0df4b19995b2'), '8689561e-23c5-49ea-a531-4d94f6d4e08f')
2026-10-25 21:14:49,150 INFO sqlalchemy.engine.Engine [cached since 3.107s ago] (UUID('05aaa210-f041-4c5a-b5a2-0df4b19995b2'), '8689561e-23c5-49ea-a531-4d94f6d4e08f')
2026-10-25 21:14:50,196 INFO sqlalchemy.engine.Engine [cached since 4.153s ago] (UUID('05aaa210-f041-4c5a-b5a2-0df4b19995b2'), '8689561e-23c5-49ea-a531-4d94f6d4e08f')
2026-10-25 21:14:56,249 INFO sqlalchemy.engine.Engine [cached since 10.21s ago] (UUID('05aaa210-f041-4c5a-b5a2-0df4b19995b2'), '8689561e-23c5-49ea-a531-4d94f6d4e08f')
2026-10-25 21:14:56,295 INFO sqlalchemy.engine.Engine [cached since 10.25s ago] (UUID('05aaa210-f041-4c5a-b5a2-0df4b19995b2'), '8689561e-23c5-49ea-a531-4d94f6d4e08f')

## Negative: bad URL

$ curl -s -o /dev/null -w "  HTTP %{http_code}\n" -X POST $API/webhooks -H "Authorization: Bearer $TOKEN1" -H "Content-Type: application/json" -d "{\"url\": \"not-a-url\"}"
  HTTP 422

## Negative: user2 (no webhook) creates a review

$ R2=$(curl -s -X POST $API/reviews -H "Authorization: Bearer $TOKEN2" -H "Content-Type: application/json" -d "{\"profile_id\": \"$PROFILE2\"}"); RID2=$(echo "$R2" | json "[\"id\"]"); sleep 3; curl -s $API/reviews/$RID2/status -H "Authorization: Bearer $TOKEN2"; echo
{"review_id":"c4ed75e7-b98f-4d48-a4af-0e4a82a1c052","status":"complete","progress_pct":0}
listener requests before: 1, after: 1

$ grep -E "$RID2" $SERVER_LOG | grep -cE "webhook_" || true
0

## Negative: listener stopped, user1 creates a review

$ R3=$(curl -s -X POST $API/reviews -H "Authorization: Bearer $TOKEN1" -H "Content-Type: application/json" -d "{\"profile_id\": \"$PROFILE1\"}"); RID3=$(echo "$R3" | json "[\"id\"]"); sleep 3; curl -s $API/reviews/$RID3/status -H "Authorization: Bearer $TOKEN1"; echo
{"review_id":"6f60aafd-7f40-4c64-b4fc-25987e7c98f5","status":"complete","progress_pct":0}

$ grep -E "$RID3" $SERVER_LOG | grep -E "webhook_|review_processing_completed|Traceback"
2026-10-25 21:15:00 [info     ] review_processing_completed    overall_score=0.81 request_id=1f0c9f2d-35de-40ee-8451-3156d33ab5cb review_id=6f60aafd-7f40-4c64-b4fc-25987e7c98f5
2026-10-25 21:15:00 [warning  ] webhook_delivery_failed        error='All connection attempts failed' request_id=1f0c9f2d-35de-40ee-8451-3156d33ab5cb review_id=6f60aafd-7f40-4c64-b4fc-25987e7c98f5 url=http://127.0.0.1:9999/hook

$ grep -A4 Traceback $SERVER_LOG | grep -E "^[A-Za-z.]*(Error|Exception)" || echo "(no tracebacks)"
AttributeError: module 'bcrypt' has no attribute '__about__'
```
