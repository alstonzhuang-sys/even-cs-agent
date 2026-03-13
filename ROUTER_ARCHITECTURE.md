# Router Architecture - Clarification

**Date:** 2026-03-13  
**Component:** Router (Intent Classification & Worker Assignment)

---

## Core Concept: Classification, NOT Fallback

### ❌ Wrong Understanding (Before)
```
Regex → (if fail) → LLM Fallback → (if fail) → Default to knowledge_worker
```
This implies LLM is a "backup plan" when Regex fails.

### ✅ Correct Understanding (Now)
```
Regex (80-90% coverage) → LLM Classification (10-20% coverage) → Worker Assignment
```
LLM is a **normal classification method** for queries that don't match Regex patterns.

---

## Router's Job: Classification & Routing

### Input (from Ingress)
```json
{
  "surface": "external" | "internal",
  "channel": "discord" | "feishu",
  "sender_id": "...",
  "message": "...",
  ...
}
```

### Processing
1. **Extract message** from Ingress payload
2. **Classify intent** using Regex + LLM
3. **Assign worker** based on intent

### Output
```json
{
  "intent": "specs_query",
  "worker": "knowledge_worker",
  "confidence": 1.0,
  "method": "regex"
}
```

---

## Classification Strategy

### Phase 1: Regex Matching (Fast Path)
- **Coverage:** 80-90% of queries
- **Speed:** <1ms
- **Accuracy:** 100% for covered patterns
- **Cost:** $0

**Patterns:**
- English: "battery life", "return product", "order #12345"
- Chinese: "退货", "电池续航", "订单"

### Phase 2: LLM Classification (Normal Path)
- **Coverage:** 10-20% of queries (Regex misses)
- **Speed:** ~500-1000ms
- **Accuracy:** ~85-90%
- **Cost:** ~$0.00001 per query

**Use Cases:**
- Ambiguous queries: "How long does it take?"
- Paraphrased queries: "I'd like to send it back"
- Multilingual queries: "Je veux retourner"
- Complex queries: "Can I return if I opened the box?"

### Phase 3: Error Handling (Actual Fallback)
- **Trigger:** LLM API error, no API key, import error
- **Action:** Route to `escalation_worker` (not knowledge_worker!)
- **Reason:** Cannot classify → Need human review

---

## Worker Assignment Rules

### Hard-coded Mapping (No LLM Needed)
```python
WORKER_ASSIGNMENT = {
    # Security
    "jailbreak": "escalation_worker",
    
    # High-risk operations (API calls)
    "order_status": "skill_worker",
    "return_request": "skill_worker",
    
    # Knowledge queries (RAG + LLM)
    "specs_query": "knowledge_worker",
    "policy_query": "knowledge_worker",
    "competitor_comparison": "knowledge_worker",
    "troubleshooting": "knowledge_worker",
    
    # Unknown/Error
    "unknown": "escalation_worker"
}
```

---

## Data Flow Example

### Example 1: Regex Match (Fast Path)
```
User: "What's the battery life of G2?"
  ↓
Ingress: {"message": "What's the battery life of G2?", "surface": "external"}
  ↓
Router (Regex): Matches "battery.*life" → intent="specs_query"
  ↓
Worker Assignment: specs_query → knowledge_worker
  ↓
Output: {"intent": "specs_query", "worker": "knowledge_worker", "method": "regex"}
```

### Example 2: LLM Classification (Normal Path)
```
User: "How long does it take to arrive?"
  ↓
Ingress: {"message": "How long does it take to arrive?", "surface": "external"}
  ↓
Router (Regex): No match
  ↓
Router (LLM): Gemini 2 Flash classifies → intent="policy_query"
  ↓
Worker Assignment: policy_query → knowledge_worker
  ↓
Output: {"intent": "policy_query", "worker": "knowledge_worker", "method": "llm"}
```

### Example 3: Error Handling (Actual Fallback)
```
User: "Tell me something"
  ↓
Ingress: {"message": "Tell me something", "surface": "external"}
  ↓
Router (Regex): No match
  ↓
Router (LLM): API error (no key / import error)
  ↓
Worker Assignment: unknown → escalation_worker
  ↓
Output: {"intent": "unknown", "worker": "escalation_worker", "method": "error"}
```

---

## Key Differences from Previous Understanding

| Aspect | ❌ Before | ✅ Now |
|--------|----------|--------|
| **LLM Role** | Fallback/backup | Normal classification method |
| **LLM Usage** | Only when Regex fails | Expected for 10-20% of queries |
| **Error Handling** | Default to knowledge_worker | Route to escalation_worker |
| **Worker Assignment** | LLM decides | Hard-coded mapping |
| **Confidence** | LLM = 0.3 (low) | LLM = 0.8 (normal) |

---

## Why This Matters

### 1. Cost Estimation
- **Before:** "LLM is expensive, avoid it"
- **Now:** "LLM handles 10-20% of queries, cost is ~$0.001 per 100 queries"

### 2. Performance Expectations
- **Before:** "LLM is slow, only use as last resort"
- **Now:** "90% of queries are <1ms (Regex), 10% are ~500ms (LLM), average ~50ms"

### 3. Error Handling
- **Before:** "LLM error → knowledge_worker (might give wrong answer)"
- **Now:** "LLM error → escalation_worker (human review)"

### 4. Monitoring
- **Before:** "Track LLM fallback rate (lower is better)"
- **Now:** "Track Regex coverage rate (higher is better), LLM classification accuracy"

---

## Next Steps

### Immediate
1. ✅ Regex patterns support Chinese
2. ✅ LLM classification logic corrected
3. ✅ Error handling routes to escalation_worker
4. 🔲 Test with real Gemini API key

### Future
1. Monitor Regex coverage rate (target: >85%)
2. Add more Regex patterns based on real queries
3. Fine-tune LLM prompt for better accuracy
4. A/B test different classification strategies

---

## Conclusion

**Router is a classifier, not a fallback chain.**

- **Regex:** Fast, deterministic, covers common patterns
- **LLM:** Normal classification for non-pattern queries
- **Error:** Route to escalation_worker for human review

This is a **two-stage classification system**, not a degradation chain.
