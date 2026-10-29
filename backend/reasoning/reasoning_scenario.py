from .model_client import ask_model


SYSTEM_PROMPT = """
You are the reasoning brain of AURA, a private personal AI assistant.

AURA receives observations from sensors such as camera, microphone, and screen.
Your job is to infer the user's current context from these observations.

Do not assume certainty when the evidence is ambiguous.
Separate observations from inferences.
If confidence is low, say what additional information would help.
Do not describe your internal analysis process or repeat the instructions.
"""


response = ask_model(
    """
You are the reasoning brain of AURA, a private personal AI assistant.

AURA receives structured observations from sensors, personal memory, retrieved documents, and available tools.

Your job is to maintain an accurate understanding of the user's current state and decide whether AURA should retrieve information, speak, remain silent, or take an action.

Do not assume certainty when evidence is ambiguous.
Separate observations from inferences.
Do not invent facts, memories, tool results, or user intentions.

SCENARIO:

10:00 AM
- Screen: Java IDE open.
- Java source code visible.
- Continuous keyboard activity.
- User has been working on Java for 20 minutes.
- AURA has no indication that the user wants help.

10:25 AM
- Keyboard activity stops.
- Java IDE remains open.
- No explicit statement that the Java task is finished.

10:27 AM
- Camera context: user has moved from desk to kitchen.
- Cutting board, knife, vegetables, and saucepan are visible.
- Stove is OFF.

10:30 AM
- Laptop is now in the kitchen.
- YouTube is open to "How to Make Vegetable Pasta."
- Java IDE is also open in another window.
- No speech directed toward AURA.

10:35 AM
- User is actively cutting vegetables.
- Saucepan is still visible.
- Stove remains OFF.

10:42 AM
- Saucepan is now on the stove.
- Stove is ON.
- User is handling food near the stove.

10:44 AM
- User asks AURA:
  "How long should I cook this?"

AVAILABLE DOCUMENT:
D1 — "Vegetable Pasta Recipe.pdf"

Relevant retrieved section:
"Heat the pan over medium heat. Add the chopped vegetables and sauté for approximately 5–7 minutes, stirring occasionally. Continue until the vegetables are tender."

PERSONAL WORLD MODEL:

M1:
The user prefers concise, practical explanations while doing a task.

M2:
The user dislikes unnecessary interruptions while focused.

M3:
The user is currently working on a Java assignment.

M4:
The user previously asked AURA to help with cooking instructions while cooking.

M5:
The user sometimes studies Java in the morning.

M6:
The user likes mango shakes.

M7:
The user has previously cooked vegetable pasta.

AVAILABLE TOOLS:

T1 — Document retrieval
T2 — Reminder creation
T3 — Timer creation
T4 — Messaging
T5 — Web search

CURRENT REQUEST:
"How long should I cook this?"

TASK:

Analyze the complete sequence and determine how AURA should behave.

Address all of the following:

1. At each major time point, identify the user's most likely current context.
2. Clearly distinguish:
   - direct observations
   - inferences
   - uncertainty
3. Identify when the context actually changes from Java work to food preparation and then to active cooking.
4. Explain whether Java context should be deleted, retained, paused, or restored when the user returns to it.
5. Identify which memories should be retrieved at 10:44 and which should not.
6. Determine whether D1 should be retrieved or used.
7. Determine whether web search is necessary.
8. Determine whether AURA should speak proactively at any point before 10:44.
9. At 10:44, determine the best response to the user's question.
10. Determine whether AURA should use a tool such as a timer.
11. If a timer is appropriate, determine whether it should be created automatically or whether AURA should ask first.
12. Determine what should enter working memory.
13. Determine what, if anything, should become long-term memory.
14. Identify any facts or actions the reasoning model would be wrong to invent.
15. Describe the final state transition represented by this scenario.

Important rules:

- A location change does not automatically mean an activity change.
- One observation does not establish a long-term behavioral pattern.
- Raw camera observations should not automatically become permanent memories.
- Current context is not the same thing as memory retrieval.
- A stored memory does not have to be retrieved simply because it exists.
- Relevant information does not automatically mean AURA should speak.
- Do not treat the open Java IDE as proof that the user is actively studying Java.
- Do not treat YouTube being open as proof that the user is actively watching it.
- The stove being OFF does not by itself prove that food preparation is occurring; use the observed cutting activity as evidence.
- At 10:42, active cooking is highly likely, but do not invent specific cooking actions that were not observed.
- D1 is the authoritative source for the recipe timing supplied in this scenario.
- Do not use web search when the retrieved document already provides the required answer.
- M4 may help personalize the interaction, but it does not mean the user wants every cooking action to automatically trigger a tool.
- Do not assume the user wants a timer merely because a cooking duration is mentioned.
- Do not invent previous timer behavior or user preferences that are not provided.
- Do not claim that a timer was created unless the timer tool actually succeeds.
- Do not describe your internal analysis process or repeat these instructions.
- Provide a detailed but focused reasoning result.
""",
    system_prompt=SYSTEM_PROMPT
)

print(response)