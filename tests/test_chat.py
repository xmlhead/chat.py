import unittest
from unittest.mock import patch
import chat


class TestChat(unittest.TestCase):
    def setUp(self):
        globals_patch = patch.multiple(chat, create=True, config={
            'api_key': 'token',
            'url': 'http://example.com',
            'model': 'gpt',
            'role': 'user',
            'temperature': '0',
            'context_length': 2,
        }, context=[])
        self.addCleanup(globals_patch.stop)
        globals_patch.start()

    @patch('chat.requests.post', autospec=True)
    def test_send_payload_trims_context_and_returns_json(self, mock_post):
        chat.context.extend([
            {'role': 'user', 'content': 'u1'},
            {'role': 'assistant', 'content': 'a1'},
            {'role': 'user', 'content': 'u2'},
            {'role': 'assistant', 'content': 'a2'},
        ])
        response = {'choices': [{'message': {'role': 'assistant', 'content': 'reply'}}]}
        mock_post.return_value.json.return_value = response

        result = chat.send_payload('u3')

        expected_context = [
            {'role': 'user', 'content': 'u2'},
            {'role': 'assistant', 'content': 'a2'},
            {'role': 'user', 'content': 'u3', 'temperature': '0'},
        ]
        mock_post.assert_called_once_with(
            'http://example.com',
            headers={'Content-Type': 'application/json', 'Authorization': 'token'},
            json={'model': 'gpt', 'messages': expected_context},
        )
        mock_post.return_value.json.assert_called_once_with()
        self.assertIs(result, response)
        self.assertEqual(chat.context, expected_context)

        # send_payload only decodes JSON; the caller processes the reply.
        with patch('builtins.print') as mock_print:
            self.assertEqual(chat.process_response(result), 'reply')
        mock_print.assert_called_once_with('reply')
        self.assertEqual(chat.context, expected_context + [
            {'role': 'assistant', 'content': 'reply'},
        ])

    @patch('chat.requests.post', autospec=True)
    def test_send_payload_returns_unexpected_json_unchanged(self, mock_post):
        response = {'error': {'message': 'invalid request'}}
        mock_post.return_value.json.return_value = response

        self.assertIs(chat.send_payload('hello'), response)

        mock_post.return_value.json.assert_called_once_with()
        self.assertEqual(chat.context, [
            {'role': 'user', 'content': 'hello', 'temperature': '0'},
        ])

    def test_process_response_appends(self):
        for content in ('reply\\nsecond line', ''):
            with self.subTest(content=content):
                previous_context = list(chat.context)
                message = {'role': 'assistant', 'content': content}
                response = {'choices': [{'message': message}]}
                with patch('builtins.print') as mock_print:
                    self.assertEqual(chat.process_response(response), content)
                mock_print.assert_called_once_with(content.replace('\\n', '\n'))
                self.assertEqual(chat.context, previous_context + [message])

    def test_process_response_missing_keys(self):
        chat.context.append({'role': 'user', 'content': 'previous question'})
        previous_context = list(chat.context)
        cases = [
            ('choices', {}),
            ('message', {'choices': [{}]}),
            ('content', {'choices': [{'message': {}}]}),
            ('content', {'choices': [{'message': {'role': 'assistant'}}]}),
            ('role', {'choices': [{'message': {'content': 'reply'}}]}),
        ]
        for key, response in cases:
            with self.subTest(response=response):
                with patch('builtins.print') as mock_print:
                    self.assertIsNone(chat.process_response(response))
                mock_print.assert_called_once_with(
                    f"Unexpected response structure: '{key}'")
                self.assertEqual(chat.context, previous_context)

    def test_process_response_malformed_structures(self):
        chat.context.append({'role': 'user', 'content': 'previous question'})
        previous_context = list(chat.context)
        responses = [
            None, [], 'not an object',
            {'choices': []},
            {'choices': None},
            {'choices': {}},
            {'choices': 1},
            {'choices': 'not a list'},
            {'choices': [None]},
            {'choices': [[]]},
            {'choices': ['not an object']},
            {'choices': [{'message': None}]},
            {'choices': [{'message': []}]},
            {'choices': [{'message': 'not an object'}]},
        ]
        responses.extend(
            {'choices': [{'message': {'role': 'assistant', 'content': content}}]}
            for content in (None, 1, [], {})
        )
        for response in responses:
            with self.subTest(response=response):
                with patch('builtins.print') as mock_print:
                    self.assertIsNone(chat.process_response(response))
                mock_print.assert_called_once()
                self.assertTrue(mock_print.call_args.args[0].startswith(
                    'Unexpected response structure: '))
                self.assertEqual(chat.context, previous_context)


if __name__ == '__main__':
    unittest.main()
