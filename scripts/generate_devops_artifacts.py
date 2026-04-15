import json
import random
import os

# Ensure the directory exists
os.makedirs("data/curated", exist_ok=True)

categories = [
    "Registry",
    "Scanning",
    "Promotion",
    "Versioning",
    "Storage",
    "Signing",
    "Distribution",
]
difficulties = ["Beginner", "Intermediate", "Advanced"]
personas = [
    "DevOps Engineer",
    "Cloud Architect",
    "Security Engineer",
    "Release Manager",
    "Site Reliability Engineer",
]
intents = ["Learn", "Troubleshoot", "Optimize", "Comply", "Audit"]
lifecycles = ["Build", "Test", "Staging", "Production", "Deployment"]
actions = [
    "consult the documentation",
    "use the CLI tool",
    "configure the pipeline",
    "review the security policy",
    "optimize the storage",
    "implement RBAC controls",
    "set up webhook notifications",
    "enable automated scanning",
    "use immutable tags",
    "configure retention policies",
]

examples = []

for i in range(180):
    category = random.choice(categories)
    difficulty = random.choice(difficulties)
    persona = random.choice(personas)
    intent = random.choice(intents)
    lifecycle = random.choice(lifecycles)
    action = random.choice(actions)

    # Question templates
    q_templates = [
        f"Example {i + 1}: How to {intent.lower()} {category.lower()} for a {persona}?",
        f"Example {i + 1}: What is the recommended way to {intent.lower()} {category.lower()} in {lifecycle}?",
        f"Example {i + 1}: Explain {category.lower()} {intent.lower()} for {persona}?",
        f"Example {i + 1}: In the {lifecycle} stage, how should one {intent.lower()} {category.lower()}?",
        f"Example {i + 1}: As a {persona}, how do you {intent.lower()} {category.lower()}?",
    ]

    # Answer templates with [MUTABLE] and [CHECK DOCS]
    a_templates = [
        f"To {intent.lower()} {category.lower()}, you should {action}. Pricing is [MUTABLE]. For detailed limits, [CHECK DOCS].",
        f"For {intent.lower()} {category.lower()}, {action} is recommended. Refer to [MUTABLE] for pricing and [CHECK DOCS] for limits.",
        f"The best way to {intent.lower()} {category.lower()} is to {action}. See [MUTABLE] for cost details and [CHECK DOCS] for restrictions.",
        f"To achieve {intent.lower()} in {category.lower()}, perform {action}. Pricing: [MUTABLE]. Limits: [CHECK DOCS].",
        f"{action} helps with {intent.lower()} {category.lower()}. Check [MUTABLE] for prices and [CHECK DOCS] for boundaries.",
    ]

    question = random.choice(q_templates)
    answer = random.choice(a_templates)

    example = {
        "question": question,
        "answer": answer,
        "metadata": {
            "category": category,
            "difficulty": difficulty,
            "persona": persona,
            "intent": intent,
            "lifecycle": lifecycle,
        },
    }
    examples.append(example)

# Write to JSONL file
with open("data/curated/devops-artifacts.jsonl", "w") as f:
    for example in examples:
        f.write(json.dumps(example) + "\n")

print(f"Generated {len(examples)} examples in data/curated/devops-artifacts.jsonl")
