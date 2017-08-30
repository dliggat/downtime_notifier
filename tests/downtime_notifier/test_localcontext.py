import mock
import unittest

from downtime_notifier.localcontext import LocalContext


class TestLocalContext(unittest.TestCase):

    @mock.patch('downtime_notifier.localcontext.Utility')
    def testInvokedFunctionArn(self, mock_utility):
        """Tests the output of LocalContext.invoked_function_arn."""
        mock_utility.aws_account_id.return_value = 123456654321
        obj = LocalContext()
        self.assertEqual(obj.invoked_function_arn,
            'arn:aws:lambda:us-west-2:123456654321:function:func-name')


def main():
    unittest.main()


if __name__ == '__main__':
    main()
