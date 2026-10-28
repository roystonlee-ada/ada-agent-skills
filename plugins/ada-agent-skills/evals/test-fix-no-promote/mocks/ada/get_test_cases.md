{
 "test_cases": [
  {
   "id": "tc_101",
   "name": "Refunds: late order",
   "user_message": "My order came 9 days late, refund please",
   "expected": "Asks for the order number, looks it up, confirms the refund"
  },
  {
   "id": "tc_102",
   "name": "Refunds: on-time order",
   "user_message": "I want a refund for order 48213",
   "expected": "Explains the order was on time and offers store credit"
  },
  {
   "id": "tc_103",
   "name": "Refunds: no order number",
   "user_message": "refund. I don't have the order number",
   "expected": "Hands off to the billing team"
  }
 ]
}
