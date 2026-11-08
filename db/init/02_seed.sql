BEGIN;

INSERT INTO users (id, name, password) VALUES
  ('5eed0000-0000-4000-9000-000000000001', 'alice', 'alice-password'),
  ('5eed0000-0000-4000-9000-000000000002', 'bob',   'bob-password'),
  ('5eed0000-0000-4000-9000-000000000003', 'carol', 'carol-password');

INSERT INTO conversations (id, user_id, title, created_at, updated_at) VALUES
  ('5eed0000-0000-4000-8000-000000000001',
   '5eed0000-0000-4000-9000-000000000001', 'Plan a weekend in Kyoto',
   now() - interval '3 days', now() - interval '3 days' + interval '3 minutes'),
  ('5eed0000-0000-4000-8000-000000000002',
   '5eed0000-0000-4000-9000-000000000002', 'Explain Python list comprehensions',
   now() - interval '1 day', now() - interval '1 day' + interval '3 minutes'),
  ('5eed0000-0000-4000-8000-000000000003',
   '5eed0000-0000-4000-9000-000000000001', 'Draft a follow-up email',
   now() - interval '2 hours', now() - interval '2 hours' + interval '3 minutes');

INSERT INTO conversation_messages (conversation_id, role, content, created_at) VALUES
  ('5eed0000-0000-4000-8000-000000000001', 'HUMAN',
   'I have a weekend in Kyoto. What should I prioritize?',
   now() - interval '3 days'),
  ('5eed0000-0000-4000-8000-000000000001', 'AI',
   'Start early at Fushimi Inari to beat the crowds, then spend the afternoon in Higashiyama and Gion. On day two, visit Arashiyama''s bamboo grove and Tenryu-ji.',
   now() - interval '3 days' + interval '1 minute'),
  ('5eed0000-0000-4000-8000-000000000001', 'HUMAN',
   'Any food I shouldn''t miss?',
   now() - interval '3 days' + interval '2 minutes'),
  ('5eed0000-0000-4000-8000-000000000001', 'AI',
   'Try yudofu (simmered tofu) near Nanzen-ji, matcha sweets in Uji, and the stalls at Nishiki Market.',
   now() - interval '3 days' + interval '3 minutes'),

  ('5eed0000-0000-4000-8000-000000000002', 'HUMAN',
   'What is a list comprehension in Python?',
   now() - interval '1 day'),
  ('5eed0000-0000-4000-8000-000000000002', 'AI',
   'It''s a compact way to build a list from an iterable: [x * 2 for x in numbers] doubles every item.',
   now() - interval '1 day' + interval '1 minute'),
  ('5eed0000-0000-4000-8000-000000000002', 'HUMAN',
   'Can I filter items too?',
   now() - interval '1 day' + interval '2 minutes'),
  ('5eed0000-0000-4000-8000-000000000002', 'AI',
   'Yes, add an if clause: [x for x in numbers if x % 2 == 0] keeps only even numbers.',
   now() - interval '1 day' + interval '3 minutes'),

  ('5eed0000-0000-4000-8000-000000000003', 'HUMAN',
   'Help me write a short follow-up email after a job interview.',
   now() - interval '2 hours'),
  ('5eed0000-0000-4000-8000-000000000003', 'AI',
   'Subject: Thank you for your time. Hi Jordan, thank you for meeting with me today. I enjoyed learning about the team and I''m excited about the role. Best, Alex',
   now() - interval '2 hours' + interval '1 minute'),
  ('5eed0000-0000-4000-8000-000000000003', 'HUMAN',
   'Make it a bit warmer.',
   now() - interval '2 hours' + interval '2 minutes'),
  ('5eed0000-0000-4000-8000-000000000003', 'AI',
   'Hi Jordan, thank you so much for the conversation today. Hearing how the team collaborates made me even more excited about the role. I''d love to contribute. Warm regards, Alex',
   now() - interval '2 hours' + interval '3 minutes');

COMMIT;
