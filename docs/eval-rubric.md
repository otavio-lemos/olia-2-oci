# OCI Specialist LLM - Evaluation Rubric

## Criteria (1-5 Scale)

### 1. Technical Correctness

| Score | Description |
|-------|-------------|
| 1 | Completely incorrect or fabricated information |
| 2 | Mostly incorrect with some correct elements |
| 3 | Partially correct but with significant errors |
| 4 | Mostly correct with minor inaccuracies |
| 5 | Completely accurate OCI information |

### 2. Depth of Knowledge

| Score | Description |
|-------|-------------|
| 1 | Surface-level, generic answer |
| 2 | Basic understanding shown |
| 3 | Adequate detail for intermediate user |
| 4 | Comprehensive for most scenarios |
| 5 | Expert-level, production-ready guidance |

### 3. Structural Clarity

| Score | Description |
|-------|-------------|
| 1 | Disorganized, hard to follow |
| 2 | Some structure but unclear |
| 3 | Acceptable structure |
| 4 | Well-organized with clear sections |
| 5 | Excellent structure with clear steps |

### 4. Hallucination

| Score | Description |
|-------|-------------|
| 1 | Significant fabricated services/commands |
| 2 | Some incorrect technical details |
| 3 | Minor inaccuracies |
| 4 | No hallucinations, minor interpretation |
| 5 | Perfect accuracy |

### 5. Clarity and Communication

| Score | Description |
|-------|-------------|
| 1 | Incomprehensible |
| 2 | Confusing or ambiguous |
| 3 | Understandable but unclear |
| 4 | Clear and concise |
| 5 | Excellent communication |

### 6. Multi-Cloud Comparison Quality

| Score | Description |
|-------|-------------|
| 1 | No comparison or completely wrong |
| 2 | Superficial comparison |
| 3 | Basic mapping provided |
| 4 | Accurate with context |
| 5 | Excellent migration guidance |

## Benchmark Structure

### Test Categories
- oci-core/networking/vcn: 20 questions
- oci-security/iam: 15 questions
- oci-migration/aws-to-oci: 15 questions
- oci-terraform: 10 questions

### Minimum Passing Scores
- Technical Correctness: ≥4 average
- Depth: ≥3.5 average
- Hallucination: ≥4 average
- Overall: ≥3.5 average

## Evaluation Output

Save to `outputs/benchmarks/eval-YYYY-MM-DD.md`:
- Per-question scores
- Category averages
- Pass/fail determination
- Failure examples with explanations
