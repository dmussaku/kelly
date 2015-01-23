def get_subscr_id(user_env, service_slug):
    for subscr_id in user_env['subscriptions']:
        subscr_data = user_env['subscription_{}'.format(subscr_id)]
        if subscr_data['slug'] == service_slug:
            return subscr_id
    return None
