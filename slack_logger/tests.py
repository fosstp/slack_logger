import unittest

from pyramid import testing

class ViewTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.request = testing.DummyRequest()
            

    def tearDown(self):
        testing.tearDown()

    def test_home_view_with_request_should_return_list(self):
        from .views import home_view
        info = home_view(self.request)
        self.assertEqual(info['project'], 'slack_logger')

    def test_log_view_with_request_should_return_empty_and_do_nothing(self):
        from .views import log_view

        self.assertEqual(log_view(self.request), {})

    def test_log_view_with_request_should_return_empty_list_if_token_mismatch(self):
        from .views import log_view

        request = self.request
        #  如果 token 不同於設定檔中的 slack_token 則什麼事都不做且回傳空 list
        request.registry.settings['slack_token'] = 'secret_token'
        request.POST['token'] = 'mismatch token'
        self.assertEqual(log_view(request), {})

    def test_log_view_with_request_should_return_empty_list_if_is_slackbot_message(self):
        from .views import log_view

        request = self.request
        #  如果是 slackbot 的訊息則忽略不做任何事
        request.registry.settings['slack_token'] = request.POST['token'] = 'foo' # useless in this test
        request.POST['user_name'] = 'slackbot'
        self.assertEqual(log_view(request), {})

    def test_log_view_with_request_should_save_log_and_return_empty_list_if_condition_matched(self):
        import os, sqlite3
        from .views import log_view

        request = self.request
        #  如果 token 比對正確且不是 slackbot 則紀錄到資料庫
        request.registry.settings['database_path'] = '/tmp/test_log_view.db'
        request.registry.settings['slack_token'] = request.POST['token'] = 'foo'

        # init db file
        if os.path.exists(request.registry.settings['database_path']):
            os.remove(request.registry.settings['database_path'])
        sql_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database.sql'))
        db = sqlite3.connect(request.registry.settings['database_path'])
        cursor = db.cursor()
        with open(sql_file) as f:
            cursor.executescript(f.read())
        db.commit()

        # via slack webhook api
        request.POST['channel_name'] = 'foo channel'
        request.POST['user_name'] = 'foo user'
        request.POST['text'] = 'foo text'

        self.assertEqual(log_view(request), {})
        
        # check database record
        cursor.execute('SELECT * FROM log')
        result = cursor.fetchall()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], request.POST['channel_name'])
        self.assertEqual(result[0][2], request.POST['user_name'])
        self.assertEqual(result[0][3], request.POST['text'])
        db.close()


        # clean up
        os.remove(request.registry.settings['database_path'])
