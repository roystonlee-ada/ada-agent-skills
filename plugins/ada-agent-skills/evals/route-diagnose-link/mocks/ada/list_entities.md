{
 "entity_type": "playbooks",
 "items": [
  {
   "id": "pb_refunds",
   "name": "Refunds",
   "description": "Customer wants a refund for an order",
   "steps": [
    {
     "id": "step_1_ask_order",
     "type": "ASK",
     "text": "Ask for the order number"
    },
    {
     "id": "step_2_lookup",
     "type": "ACTION",
     "action": "order_lookup"
    },
    {
     "id": "step_3_eligibility",
     "type": "IF",
     "text": "Late by more than 7 days -> eligible"
    },
    {
     "id": "step_4_refund",
     "type": "ACTION",
     "action": "issue_refund"
    }
   ],
   "exits": [
    "Customer asks for a person"
   ]
  },
  {
   "id": "pb_baggage",
   "name": "Baggage",
   "description": "Lost or delayed baggage"
  }
 ],
 "tools": [
  {
   "id": "ct_order_lookup",
   "type": "code",
   "name": "order_lookup"
  },
  {
   "id": "act_issue_refund",
   "type": "api",
   "name": "issue_refund"
  }
 ]
}
