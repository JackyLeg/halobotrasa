# Analysis of Rasa Warnings

The user received warnings like:
`/opt/venv/lib/python3.10/site-packages/rasa/shared/utils/io.py:100: UserWarning: The utterance 'utter_answer_hasil_kartuHasilStudi' is not used in any story or rule.`

This happens because Rasa Open Source's `data validate` command statically checks if every `utter_*` response declared in your `domain.yml` files is explicitly written inside a `steps:` block in your `stories.yml` or `rules.yml` files.

However, in our architecture, these specific utterances (`utter_answer_hasil_...`, `utter_answer_prosedur_...`, etc.) are *not* called directly from the stories. Instead, the stories call the custom action:
```yaml
- action: action_answer_kartuHasilStudi
```
And then, during runtime, the Python custom action evaluates the slot and dynamically dispatches the string:
```python
dispatcher.utter_message(response="utter_answer_hasil_kartuHasilStudi")
```

Because `data validate` doesn't execute or parse custom Python code at validation time, it simply doesn't know these responses are actually being used by `actions.py`.

**Conclusion:**
This warning is entirely benign and expected when using dynamic Python dispatcher responses. There is no error here, and it says at the bottom:
`No story structure conflicts found.`
