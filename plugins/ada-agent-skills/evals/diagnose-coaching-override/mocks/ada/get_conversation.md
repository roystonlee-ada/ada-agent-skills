{
 "id": "66a1b2c3d4e5f60718293a4b",
 "url": "https://acme.ada.support/conversations/66a1b2c3d4e5f60718293a4b",
 "transcript": [
  {
   "role": "customer",
   "text": "Hi, my order #48213 arrived 9 days late. Can I get a refund?"
  },
  {
   "role": "reasoning",
   "text": "Coaching 'Refund requests go to a person' (cch_77) applies: any message mentioning a refund goes to billing. Playbook Refunds matched but coaching takes precedence."
  },
  {
   "role": "event",
   "type": "playbook_started",
   "playbook_id": "pb_refunds"
  },
  {
   "role": "event",
   "type": "playbook_exited",
   "playbook_id": "pb_refunds",
   "at_step": "step_1_ask_order",
   "reason": "handoff requested by coaching"
  },
  {
   "role": "event",
   "type": "handoff",
   "reason_code": "handoff_configured",
   "reasoning": "Refund requests are handed to billing per coaching."
  },
  {
   "role": "agent",
   "text": "I'll connect you with our billing team."
  }
 ],
 "knowledge_searches": [],
 "actions": [],
 "coaching_used": [
  {
   "id": "cch_77",
   "title": "Refund requests go to a person"
  }
 ]
}
