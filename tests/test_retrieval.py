from harness.retrieval.knowledge_base import LocalKnowledgeBase

def test_retrieves_sample_support_policy(tmp_path):
    (tmp_path / "policy.md").write_text("# Policy\nSupport responds within 24 hours on business days.", encoding="utf-8")
    kb = LocalKnowledgeBase(tmp_path)
    results = kb.search("support response time 24 hours", top_k=2)
    assert results
    assert "24 hours" in results[0].text
    assert results[0].source_id.startswith("KB")
