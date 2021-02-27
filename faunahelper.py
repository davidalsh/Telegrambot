from faunadb import query


class FaunaHelper:

    def __init__(self, clientf):
        self.clf = clientf

    def get_ideas_by_telegram_id(self, user_id):
        result = self.get_info_by_telegram_id(user_id)
        return result['ideas']

    def get_info_by_telegram_id(self, user_id):
        result = self.clf.query(query.get(query.match(query.index('people_by_telegram_id'), user_id)))
        return result['data']

    def delete_idea_list_by_telegram_id(self, user_id):
        result = self.get_info_by_telegram_id(user_id)
        result2 = {k: None for k in result['ideas']}
        self.clf.query(
            query.update(query.select('ref', query.get(query.match(query.index('people_by_telegram_id'), user_id))),
                         {'data': {'ideas': result2}}))

    def delete_idea_by_name_by_telegram_id(self, name_of_idea, user_id):
        self.clf.query(
            query.update(query.select('ref', query.get(query.match(query.index('people_by_telegram_id'), user_id))),
                         {'data': {'ideas': {name_of_idea: None}}}))

    def get_info_about_all_people(self):
        result = self.clf.query(
            query.map_(query.lambda_("x", query.get(query.var('x'))),
                       query.paginate(query.match((query.index('peopleinfo'))))))
        return result

    def get_info_about_all_id(self):
        result = self.get_info_about_all_people()
        return [user_data['data']['telegram_id'] for user_data in result['data']]

    def add_new_user_by_telegram_id(self, user_id):
        self.clf.query(query.create(query.collection("peopleinfo"), {'data': {'telegram_id': user_id, 'ideas': {}}}))

    def update_idea_by_telegram_id(self, name_of_idea, date, user_id):
        self.clf.query(
            query.update(query.select('ref', query.get(query.match(query.index('people_by_telegram_id'), user_id))),
                         {'data': {'ideas': {name_of_idea: date}}}))
