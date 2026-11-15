# Show the complete experience

Keep 3 to 6 scenario tabs. Give each scenario a stable `id`, a title,
`kind`, a one-line `expect` and its main sequence in `turns`.
Add `paths` for materially different outcomes that share an entry.
Each alternate has a stable `id` unique within its scenario, a title,
`entry` that names where and why it diverges, its own `expect`, and
`turns` from that point to its ending. The reviewer should be able to
follow the shared turns and the alternate as one complete conversation.

Keep the original `text` and `options` for each turn. Put the review
copy in `translation` and `options_translation`, in the same order as the
original choices. `translation_language` defaults to English. Use
`who: "system"` for visible platform events and to mark the boundary
where the experience ends. Keep operational annotations out of agent copy.

In `notes`, map each applicable policy rule and material edge case to a
scenario or alternate ID. Include the policy source and the applicable
market and version when they matter. Mark an unverified fact OPEN and an
illustrative behavior ASSUMED. Carry any unresolved cases into the next
review round. When the runtime needs a transcript supplement, include
these notes there too.

The example below assumes a fictional Spanish web chat. It shows the
survey as a platform event, the action of answering it as a system event,
and the playbook exit as a separate boundary.

```
<<<ADA-DESIGN>>>
{
  "work": "delivery-coverage",
  "title": "Delivery coverage",
  "goal": "Explain delivery coverage for the destination country.",
  "round": 1,
  "channels": ["Web chat"],
  "notes": [
    "Example delivery policy: Spain and Portugal are supported. See spain and repeat for supported destinations and other for the unsupported case.",
    "ASSUMED: the Spanish greeting appears on fresh chat. Survey completion and skip both return to the open chat. See spain and spain/skip."
  ],
  "scenarios": [
    {
      "id": "spain", "title": "Confirm a supported country", "kind": "main",
      "expect": "The customer confirms Spain, gets the coverage answer, rates it and returns to chat.",
      "turns": [
        {"who": "bot", "text": "Hola, ¿en qué puedo ayudarte?", "translation": "Hi, how can I help?"},
        {"who": "customer", "text": "¿Hacéis envíos a mi país?", "translation": "Do you ship to my country?"},
        {"who": "bot", "text": "Tu región parece ser España. ¿A qué país va el envío?", "translation": "Your region looks like Spain. Which country is the order shipping to?", "options": ["España", "Portugal", "Otro"], "options_translation": ["Spain", "Portugal", "Other"]},
        {"who": "customer", "text": "España", "translation": "Spain"},
        {"who": "bot", "text": "Sí, hacemos envíos a España.", "translation": "Yes, we ship to Spain."},
        {"who": "system", "text": "¿Cómo valorarías esta atención?", "translation": "How would you rate this support?", "options": ["Buena", "Mala", "Omitir"], "options_translation": ["Good", "Bad", "Skip"]},
        {"who": "system", "text": "Customer submits a rating. The playbook exits and the chat stays open."}
      ],
      "paths": [
        {
          "id": "skip", "title": "Skip the survey", "entry": "At the survey, the customer chooses Skip.",
          "expect": "The playbook exits without a rating and the chat stays open.",
          "turns": [{"who": "system", "text": "Customer skips the survey. The playbook exits and the chat stays open."}]
        }
      ]
    },
    {
      "id": "other", "title": "Unsupported country", "kind": "edge",
      "expect": "The customer gives an unsupported destination and gets a clear answer.",
      "turns": [
        {"who": "customer", "text": "¿Enviáis a Canadá?", "translation": "Do you ship to Canada?"},
        {"who": "bot", "text": "Por ahora enviamos a España y Portugal.", "translation": "We currently ship to Spain and Portugal."},
        {"who": "system", "text": "ASSUMED: the playbook exits without a survey on this path. The chat stays open."}
      ]
    },
    {
      "id": "repeat", "title": "Ask again in the same chat", "kind": "edge",
      "expect": "The agent uses the new destination and answers with fresh wording.",
      "turns": [
        {"who": "customer", "text": "¿Y si el envío es a Portugal?", "translation": "What if it's shipping to Portugal?"},
        {"who": "bot", "text": "También puedes recibir tu pedido en Portugal.", "translation": "You can receive your order in Portugal too."},
        {"who": "system", "text": "ASSUMED: no second survey in this chat. The playbook exits and the chat stays open."}
      ]
    }
  ]
}
<<<END-ADA-DESIGN>>>
```
