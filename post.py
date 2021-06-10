class post:
    def __init__(self, id, person_id, title, category, description, location, reserved, date):
        self.id = id
        self.person_id = person_id
        self.title = title
        self.category = category
        self.description = description
        self.location = location
        self.reserved = reserved
        self.date = date


class post_request(post):
    def __init__(self, id, person_id, title, category, description, location, reserved, date):
        post.__init__(self, id, person_id, title, category, description, location, reserved, date)


class post_donation(post):
    def __init__(self, id, person_id, title, category, description, location, reserved, date, condition,
                 condition_description):
        post.__init__(self, id, person_id, title, category, description, location, reserved, date)
        self.condition = condition
        self.condition_description = condition_description
