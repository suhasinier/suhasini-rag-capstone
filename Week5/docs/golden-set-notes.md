# Golden Set Notes
## 1. Coverage Mix

The golden set contains 20 entries covering three evaluation buckets:

- **Happy-path: 14 entries (g001–g014)** — straightforward questions covering curriculum, learning outcomes, assessment, competency-based education, experiential learning, pedagogy, inclusive education, foundational learning, education frameworks, teacher and student roles, curriculum planning, and education policy.
- **Harder: 4 entries (g015–g018)** — questions requiring reasoning across multiple concepts, combining conditions, or interpreting information across more than one area of the education domain.
- **Edge: 2 entries (g019–g020)** — questions that are either outside the selected CBSE/NCERT document corpus or outside the intended scope of the assistant. These entries test whether the system can acknowledge insufficient evidence instead of inventing an answer.

The 14/4/2 distribution provides a mixture of routine questions, reasoning-intensive questions, and out-of-scope cases for evaluation.

## 2. Sourcing

The golden-set questions were constructed specifically for the AI-powered Education & Curriculum Assistant capstone. They were based on the project's defined use case and the CBSE/NCERT education topics identified during the coverage-planning stage.

The questions were written to resemble realistic questions that a CBSE school teacher or other education stakeholder might ask while working with curriculum, learning outcomes, assessment, pedagogy, inclusion, and education frameworks.

The entries were not collected from an actual production support-ticket or user-query dataset. Therefore, the questions should be treated as a manually constructed baseline rather than as a statistically representative sample of real user traffic.

The ideal answers were written to capture the expected information and reasoning for each question rather than requiring one exact wording. The harder and edge entries were deliberately included to test multi-hop reasoning and graceful handling of questions that cannot be reliably answered from the selected document scope.

## 3. Hardest to Write

The **edge cases** were the hardest to design because the expected behaviour is not simply to provide an answer. The system must recognize when the requested information is not supported by the selected CBSE/NCERT corpus or falls outside the assistant's intended scope.

The harder questions were also important because they test a limitation of simple retrieval: a system may find relevant information for each individual concept but still produce an incorrect answer when the question requires combining multiple concepts or interpreting a condition. These cases therefore provide useful tests beyond straightforward document lookup.