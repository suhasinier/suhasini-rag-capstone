# Week 1 Hands-on Activity — System Prompt Voice Exploration

## Prompt A — "You are concise."

**Question:** Explain quantum entanglement in two sentences.

**Answer:**

Quantum entanglement is a phenomenon where two or more particles become interconnected in such a way that the state of one particle instantaneously influences the state of the other, regardless of the distance separating them. This non-local correlation challenges classical intuitions about separability and locality in physics.

## Prompt B — Kindergarten Teacher

**Question:** Explain quantum entanglement in two sentences.

**Answer:**

Okay! Imagine you have a big box of crayons. Each crayon is a different color, like red, blue, and yellow. When you want to draw a picture, you can pick any crayon you like! 

Just like that, when we learn new things, we can choose different ideas and colors to make our brains happy and smart. Learning is like coloring a beautiful picture with all the fun colors!

## Prompt C — Shakespearean Poet

**Question:** Explain quantum entanglement in two sentences.

**Answer:**

Upon this stage of life, we play our part,  
With words that dance like shadows in the night.  
Each line a breath, each verse a beating heart,  
In sonnets sweet, we seek the truth of light.  

What dost thou wish, dear friend, to hear or know?  
Shall we explore the realms of love or fate?  
In every tale, a seed of wisdom sows,  
So speak thy mind, and let us contemplate.

## Prompt D — Deliberately Grumpy Expert

**Question:** Explain quantum entanglement in two sentences.

**Answer:**

Understood. What do you need to know?

## What changed?

* **What stayed the same?**

  * The question remained exactly the same in all four runs: *“Explain quantum entanglement in two sentences.”*
  * The topic was the same — quantum entanglement.
  * We used the same LLM and the same code; only the system prompt was changed.

* **What changed the most?**

  * The **voice, tone, vocabulary, sentence style, and level of explanation** changed significantly.
  * The concise prompt produced a formal and direct answer.
  * The kindergarten prompt changed the explanation into very simple, child-friendly language.
  * The Shakespearean prompt changed the response into poetic language and verse.
  * The grumpy-expert prompt produced a very short, impatient response.
  * This showed me that changing just the system prompt can have a large effect on how the LLM responds.

* **Where would I use a system-prompt change instead of fine-tuning?**

  * I would first use a system prompt when I want to change the assistant's **tone, personality, communication style, level of explanation, or behaviour**.
  * For example, the same assistant could be instructed to respond as a teacher, a professional advisor, or a simple beginner-friendly tutor without changing the underlying model.
  * I would consider fine-tuning only when a system prompt is not sufficient for the specific behaviour or task I need.




