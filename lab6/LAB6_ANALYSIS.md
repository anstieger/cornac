# Lab #6 - Investigation Record

**Team / student(s):** Antonia Stieger / [anstieger](https://github.com/anstieger)  
**Mode:** individual 
**Approved upstream project:** https://github.com/PreferredAI/cornac (Cornac, tag `v3.0.1`)  
**Fork / working branch:** https://github.com/anstieger/cornac/tree/semester-investigation  
**Original Lab #5 version:** `cee4b9063adedfea9a502dd84d6bd19d942a254d` (upstream `v3.0.1`, see `LAB5_SELECTION.md`)
**Lab #6 pre-refactoring baseline:** TODO - full SHA + link of the commit the baseline scans run on (current branch head before Lab 6: `b42c394a67d58216b972a10e2c1f91d259f5a108`)

## Task 1 - Stakeholder, GQM, and Code Smell Selection

**Selected stakeholder and exact fictional concern from handout:** Scenario A - Alex, Software Maintainer:
> "Our software keeps evolving. Future contributors need to understand and modify its components, but certain design choices might make that work unnecessarily difficult. Please investigate possible code smells, identify maintainability concerns worth addressing, and demonstrate a focused improvement without changing the software's intended behavior."

**GQM goal:** Analyze **the evaluation framework `cornac/eval_methods`** for the purpose of **detecting code smells that make future modification harder**, with respect to **understandability and modifiability**, from the viewpoint of **Alex, the software maintainer**, in the context of **the Cornac 3.0.1 fork (`anstieger/cornac`, branch `semester-investigation`), handwritten Python source, analyzed with GitHub Actions**.

| Initial question | Question wording                                                                                                | Relevant metric(s) / observation(s)                                                                                                                                    | Why useful?                                                                                                           |
| ---------------- | --------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| **Q1**           | Where is the same logic repeated in `cornac/eval_methods`, so that one change has to be made in several places? | Duplicated fragments and duplicated lines (jscpd); number of copies of the same logic found by source inspection                                                       | Modifiability: every copy is one more place a contributor has to find and change consistently.                        |
| **Q2**           | Which classes in `cornac/eval_methods` take on too many responsibilities?                                       | Class size (LOC), number of methods, WMC = sum of method complexities (slide 42, from the Pylint mccabe extension); inspection of what the methods are responsible for | Understandability: a class with many unrelated responsibilities is harder to read and to change without side effects. |

**Code-smell types chosen from the lecture:** 

| Smell type                              | Lecture slide(s) | Why relevant to our GQM?                                                                                                                                                                                     | How we plan to investigate it (tool/rule/metric/inspection)                                                                                                                                                                                                                                                                                                        |
| --------------------------------------- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1. Duplicated Code (Dispensables)       | 32, 72-77        | Q1 / modifiability: if the same logic exists in several places, one change has to be repeated in every copy, and copies that are changed inconsistently can introduce defects (slide 73).                    | **Automatic:** Pylint `R0801 duplicate-code` (compares all files of `cornac/eval_methods` with each other)                                                                                                                                                                                                                                                         |
| 2. Large Class / God Class (Bloaters)   | 32, 38-42        | Q2 / understandability: a class that centralizes too much of the system's intelligence is hard to read and to change without side effects (slide 38).                                                        | **Metric-based:** class size (LOC), Pylint `R0904 too-many-public-methods`, `R0902 too-many-instance-attributes`, and WMC = sum of the method complexities from the Pylint mccabe extension (`R1260 too-complex`, slide 42). ATFD/TCC (slide 41) are not computed by Pylint, so foreign-data access and cohesion are checked by **inspection**.                    |
| 3. Divergent Change (Change Preventers) | 32, 62-65        | Q2 / modifiability: if one class changes for many different reasons, each kind of change touches a different subset of its methods, so the class mixes responsibilities that should be separated (slide 63). | **No automatic rule**, so it is a *reasoned candidate*, not a tool finding. **Inspection:** group the methods of the large classes found in smell 2 by responsibility (e.g. data splitting, modality handling, evaluation). **GitHub-visible evidence:** the file's commit history on GitHub, to check whether the class is changed for several unrelated reasons. |


**Primary GitHub-integrated tool:** Pylint, run in GitHub Actions on the fork - https://pylint.readthedocs.io/ (rules: [R0801](https://pylint.readthedocs.io/en/stable/user_guide/messages/refactor/duplicate-code.html), [R0902](https://pylint.readthedocs.io/en/stable/user_guide/messages/refactor/too-many-instance-attributes.html), [R0904](https://pylint.readthedocs.io/en/stable/user_guide/messages/refactor/too-many-public-methods.html), [mccabe extension](https://pylint.readthedocs.io/en/stable/user_guide/checkers/extensions.html#design-checker))  
**Complementary tool (only if needed):** N/A
**Why these tools match our questions and selected smells:** Pylint is the only one of the supported Python tools that covers both questions: it detects duplicated blocks across files (Q1, Duplicated Code) and reports class size and method complexity (Q2, Large Class). Divergent Change has no detection rule in any of the supported tools, so it is investigated by source inspection and the GitHub commit history, using the Pylint class metrics only to decide which classes to inspect.

## Task 2 - Detect and Investigate Code Smells

**Analysis configuration:**

- Fork branch and **baseline SHA**: `semester-investigation` @ [TODO: full SHA of the commit that adds the workflow]
- Source directory/directories analyzed: `cornac/eval_methods/*.py` (9 files, handwritten Python)
- Exclusions (generated/test/vendor/weight data, etc.): everything outside `cornac/eval_methods` (models, data, metrics, tests, docs, notebooks). No Cython `.pyx` files exist in this folder, so nothing in scope is skipped by the parser.
- Tool(s), versions and relevant enabled rules/settings: Pylint 3.3.7 on GitHub Actions (`ubuntu-24.04`, Python 3.12), workflow [`.github/workflows/lab6-pylint.yml`](https://github.com/anstieger/cornac/blob/semester-investigation/.github/workflows/lab6-pylint.yml). `--disable=all`, enabled only: `R0801 duplicate-code` (default `min-similarity-lines=4`, comments/docstrings/imports ignored), `R0902 too-many-instance-attributes` (default max 7), `R0904 too-many-public-methods` (default max 20), `R1260 too-complex` via `pylint.extensions.mccabe` with `--max-complexity=0` (reports every method, used to sum WMC per class). Class LOC and number of methods are computed in the workflow from the source with Python `ast`.
- **Baseline GitHub scan / Actions run link(s):** [TODO: link to the *Lab6 - Pylint* run for the baseline SHA]

| Selected smell type | Found / not found / not assessable | Tool result or source link | Interpretation / limitations |
|---|---|---|---|
| | | | |
| | | | |
| | | | |
| | | | |
| | | | |
| | | | |

**Candidate issues inspected in source (at least two):**

| Candidate ID | File/entity permalink | What was actually observed? | Why it might matter / why uncertain |
|---|---|---|---|
| C1 | | | |
| C2 | | | |
| C3 (optional) | | | |

**One warning we challenged, or one potentially missed issue:** [brief explanation of tool limitations, possible false alarm or incomplete coverage]

## Task 3 - Prioritize Technical Debt and Plan Refactoring

| Candidate | Expected future impact / relevance | Estimated effort and behavior risk | Prioritize now or defer? Why? |
|---|---|---|---|
| C1 | | | |
| C2 | | | |
| Additional (if needed) | | | |

**Selected documented issue(s) and individual ownership:** [1-2 per student; pair total 2-4]

| Contributor / GitHub handle | Candidate ID | Planned refactoring | Expected benefit | GitHub regression check planned |
|---|---|---|---|---|
| | | | | |
| [second member if pair] | | | | |

## Task 4 - Refactor, Verify, and Commit

**Baseline test/check run(s) on GitHub:** [URL(s) and outcomes]  
**After-refactoring SHA(s):** [full SHA(s)]  
**After-refactoring scan / workflow run(s):** [URL(s)]  
**After-refactoring test/check run(s):** [URL(s) and outcomes]

| Issue / contributor | Before (same scope and measurement) | After | Test / verification result | What does this actually establish? |
|---|---|---|---|---|
| | | | | |
| | | | | |

**Answers to the original GQM questions:**

- **Q1:** [answer based on evidence, not only a warning count]
- **Q2:** [answer based on evidence, not only a warning count]

**Conclusion and limits:** [What was improved? Did any measurements worsen or remain unchanged? What cannot be claimed about maintainability or preserved behavior?]

### Individual implementation commits - permanent GitHub links

> Each student creates and pushes **their own** changes from **their own machine/account**. Include direct `/commit/FULL_SHA` links, **not just repository or PR URLs**. Do not squash individual source commits into a single partner-authored commit.

| Contributor / GitHub account | Documented issue (C1, C2, ...) | What was refactored? | **Permanent commit link** | PR or GitHub Actions push-run link |
|---|---|---|---|---|
| Student 1 | | | `https://github.com/OWNER/REPO/commit/FULL_SHA` | |
| Student 1 (second issue, if applicable) | | | | |
| Student 2 (pair only) | | | | |
| Student 2 (second issue, if applicable) | | | | |

**Completed template location on `semester-investigation`:** [GitHub file URL]  
**Template/report commit link:** [GitHub `/commit/FULL_SHA` URL]

**Evidence preservation note:** [If any GitHub Actions artifact is relevant, provide a run link and preserve its essential figures here because workflow artifacts can expire.]
