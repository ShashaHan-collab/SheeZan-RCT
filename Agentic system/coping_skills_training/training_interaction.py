"""Developer-editable settings for a training session.

This file contains two things a developer may want to change:

- `TRAINING_MODULES`: the available trainings. Each entry maps an internal
  machine key to the name shown to the chat participant. To add a new
  training, add an entry here and add its prompts in
  `prompts/coping_skills_training.py`.
- The rating contract: the 1-10 question that closes the first two phases of
  every training. The interface uses this wording to draw its number picker,
  and the training agent looks for it to decide when to move to the next
  phase."""

from prompts.coping_skills_training import RATING_ASK, RATING_SCALE

TRAINING_MODULES = {
    "Cognitive_Restructuring": "Cognitive Restructuring",
    "Episodic_Future_Thinking": "Episodic Future Thinking",
}


RATING_MARKERS = (RATING_SCALE, RATING_ASK, "from 1 to 10", "1-10")

PHASE_CAP = 20
