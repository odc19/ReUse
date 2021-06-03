class post:
    def __init__(self, id, person_id, title, category, description, location, reserved):
        self.id = id
        self.person_id = person_id
        self.title = title
        self.category = category
        self.description = description
        self.location = location
        self.reserved = reserved


class post_request(post):
    def __init__(self, id, person_id, title, category, description, location, reserved):
        post.__init__(self, id, person_id, title, category, description, location, reserved)


class post_donation(post):
    def __init__(self, id, person_id, title, category, description, location, reserved, condition, condition_description):
        post.__init__(self, id, person_id, title, category, description, location, reserved)
        self.condition = condition
        self.condition_description = condition_description
