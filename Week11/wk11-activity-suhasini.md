# Week 11 Practice Assignment

## Diagnose the broken eval report

**Project:** CBSE Class IX Education & Curriculum Assistant\
**Name:** Suhasini Ramachandran

> **Scenario note:** This is an adapted, fictional version of Sam's
> diagnostic snapshot for the CBSE Class IX project. Its reported
> figures and row-level examples are illustrative exercise data, not the
> actual results from my Week 11 Notebook 2 offline-proxy evaluation.

## 1. Diagnose

  -------------------------------------------------------------------------
  Symptom /         Layer             Most likely cause   Evidence to
  evidence                                                confirm
  ----------------- ----------------- ------------------- -----------------
  Grounded response Generation        The assistant       Inspect g019's
  rate 0.61,                          answers a           retrieved chunks,
  hallucination                       school-specific     generated answer
  rate 0.39; g019                     question even       and citations.
  invents school                      though the CBSE     
  examination dates                   corpus does not     
  (faithfulness                       contain those       
  0.20).                              dates, instead of   
                                      abstaining.         

  Context recall    Retrieval         Retrieval misses    Check whether
  0.58; g015 covers                   part of the         retrieved chunks
  R1/R2/R3 but                        information needed  cover the
  misses the native                   for this multi-part language
  Indian language                     question.           definitions and
  requirement                                             native-language
  (recall 0.33).                                          requirement.

  Context precision Retrieval         The retrieved       Inspect the
  0.44; g004, g008                    results contain     top-three chunks
  and g011 have two                   irrelevant chunks   and assess their
  off-topic chunks                    alongside relevant  relevance to each
  in their top                        information.        question.
  three.                                                  

  Cache hit rate is Cache             Repeated questions  Compare cache
  12%.                                are not reusing     keys, hit/miss
                                      cached responses;   logs and
                                      cache keys may have invalidation
                                      changed or cache    events for
                                      invalidation may be repeated
                                      too frequent.       questions.

  Cache-hit         Cache             Some cached         Compare cached
  accuracy is 0.70,                   responses may be    answers with
  below cache-miss                    stale or incorrect. fresh answers and
  accuracy of 0.83.                                       the current CBSE
                                                          source documents.

  Evaluation rows   Process           Three documents     Inspect each
  contain both                        were re-ingested    row's KB-version
  `v2.w10` and                        during the run,     tag and document
  `v3.w11`.                           mixing              re-ingestion
                                      knowledge-base      timestamps.
                                      versions in one     
                                      evaluation.         

  Tool success rate Process /         Tool workflows are  Check project
  is reported as    reporting         not implemented     scope and whether
  0.00.                               yet, so the metric  any tools were
                                      is not measurable   executed.
                                      this week.          

  Escalation rate   Process /         Human-in-the-loop   Check whether an
  is reported as    reporting         escalation is not   escalation
  0.00.                               implemented yet, so workflow and
                                      the metric is not   event records
                                      measurable this     exist.
                                      week.               

  All four RAGAS    Evaluation /      The thresholds are  Review configured
  thresholds are    process           too permissive to   thresholds
  0.30 and marked                     detect poor quality against baseline
  as passed.                          or meaningful       scores and
                                      regressions.        required quality
                                                          standards.
  -------------------------------------------------------------------------

## 2. Prescribe

  -----------------------------------------------------------------------
  Problem                 Layer                   Specific one-line fix
  ----------------------- ----------------------- -----------------------
  g019 gives unsupported  Generation              Add an explicit
  school examination                              abstention rule: when
  dates.                                          retrieved CBSE
                                                  documents do not
                                                  contain school-specific
                                                  information, say it
                                                  cannot be determined
                                                  from the available
                                                  sources and direct the
                                                  user to the school's
                                                  official timetable.

  g015 misses part of the Retrieval               Improve retrieval
  language-scheme                                 coverage for multi-part
  requirements.                                   questions so chunks
                                                  covering R1/R2/R3 and
                                                  the native Indian
                                                  language requirement
                                                  are retrieved together.

  g004, g008 and g011     Retrieval               Tune retrieval and
  retrieve irrelevant                             reranking so the
  chunks.                                         top-three results
                                                  prioritise chunks
                                                  directly relevant to
                                                  the R3 provision,
                                                  English reading section
                                                  and Algebra topics.

  Cache hit rate is low.  Cache                   Inspect and standardise
                                                  cache-key generation so
                                                  equivalent repeated
                                                  questions can reuse
                                                  cached responses.

  Cache-hit accuracy is   Cache                   Invalidate cached
  low.                                            answers when the
                                                  underlying
                                                  knowledge-base version
                                                  changes and associate
                                                  cached responses with
                                                  the source version.

  KB versions are mixed   Process                 Freeze the KB version
  in one run.                                     for each evaluation and
                                                  rerun the evaluation so
                                                  every row uses the same
                                                  version.

  Tool success is         Process / reporting     Mark tool success as
  reported as zero.                               `N/A` until tool
                                                  workflows are
                                                  implemented in Week 13.

  Escalation is reported  Process / reporting     Mark escalation as
  as zero.                                        `N/A` until the
                                                  human-in-the-loop
                                                  workflow is implemented
                                                  in Week 17.

  Thresholds are set to   Evaluation / process    Replace tutorial floor
  0.30.                                           thresholds with
                                                  thresholds calibrated
                                                  from a reliable live
                                                  evaluation baseline.
  -----------------------------------------------------------------------

## 3. Set defensible thresholds

Sam's threshold of 0.30 for every metric is too low: a score of 0.30
would still pass even though it indicates weak performance.

The following are **provisional working thresholds for this exercise**,
not values established from Sam's measured baseline:

  RAGAS metric          Proposed provisional threshold
  ------------------- --------------------------------
  Faithfulness                                  ≥ 0.85
  Answer relevance                              ≥ 0.85
  Context precision                             ≥ 0.75
  Context recall                                ≥ 0.80

**Selection rule:** Set each threshold just below the corresponding
aggregate score from a reliable live evaluation baseline. This leaves
some room for normal evaluation variation while allowing a meaningful
regression to fail the test.

**To finalise the thresholds:** Run the full golden set using one frozen
KB version and live RAGAS metrics; repeat runs to understand normal
variation; inspect low-scoring individual questions as well as aggregate
scores; then set each threshold based on the measured baseline and the
quality required. Offline-proxy scores are not live RAGAS baseline
measurements and must not be substituted for them.

For the Week 11 dashboard, tool success should be `N/A` until Week 13
and escalation should be `N/A` until Week 17. They should not be
reported as ordinary numeric zeroes.

## 4. DR #2 statement

I would not recommend shipping this assistant for M2 in its current
state. The evaluation reveals significant retrieval and answer-quality
problems, with context precision at 0.44, context recall at 0.58 and
faithfulness at 0.61. My first priority would be to improve retrieval
precision and recall so that the assistant consistently retrieves all
relevant CBSE curriculum information. My second priority would be to
strengthen answer grounding and abstention so that it does not generate
unsupported information when the answer is unavailable in the corpus. I
would also address stale cache responses and ensure that future
evaluations use a single, consistent knowledge-base version. Finally, I
would replace the overly permissive thresholds with values based on a
reliable live evaluation baseline before making the M2 release decision.
