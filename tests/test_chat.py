import unittest
from unittest.mock import patch, MagicMock
import chat

class TestChat(unittest.TestCase):
    @patch('chat.requests.post')
    def test_send_payload_trims_context(self, mock_post):
        chat.config = {
            'api_key': 'token',
            'url': 'http://example.com',
            'model': 'gpt',
            'role': 'user',
            'temperature': '0',
            'context_length': 2,
        }
        chat.context = [
            {'role': 'user', 'content': 'u1'},
            {'role': 'assistant', 'content': 'a1'},
            {'role': 'user', 'content': 'u2'},
            {'role': 'assistant', 'content': 'a2'},
        ]

        mock_post.return_value.json.return_value = {}

        chat.send_payload('u3')

        self.assertEqual(len(chat.context), 3)
        self.assertEqual(chat.context[0]['content'], 'u2')
        self.assertEqual(chat.context[1]['content'], 'a2')
        self.assertEqual(chat.context[2]['content'], 'u3')

    def test_process_response_appends(self):
        chat.config = {}
        chat.context = []
        response = {'choices': [{'message': {'role': 'assistant', 'content': 'reply'}}]}
        with patch('builtins.print'):
            chat.process_response(response)
        self.assertEqual(chat.context[-1], {'role': 'assistant', 'content': 'reply'})

if __name__ == '__main__':
    unittest.main()
