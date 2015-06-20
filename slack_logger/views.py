from pyramid.view import view_config

@view_config(route_name='home', renderer='templates/home.jinja2')
def home_view(request):
    return {'project': 'slack_logger'}

@view_config(route_name='log', renderer='json')
def log_view(request):
    import sqlite3, datetime, time

    post = request.POST
    settings = request.registry.settings

    if (post['token'] == settings['slack_token']) and (post['user_name'] != 'slackbot'):
        db = sqlite3.connect(settings['database_path'])
        cursor = db.cursor()
        insert_data = (request.POST['channel_name'], int(time.time()),
                       request.POST['user_name'], request.POST['text'])
        cursor.execute('INSERT INTO log (channel, datetime, user, message) VALUES (?, ?, ?, ?)', insert_data)
        db.commit()
        db.close()

    return {}
