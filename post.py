class post:
    def __init__(self, id, person_id, title, category, description, location, reserved, date, is_charity, lat, lng):
        self.id = id
        self.person_id = person_id
        self.title = title
        self.category = category
        self.description = description
        self.location = location
        self.reserved = reserved
        self.date = date
        self.is_charity = is_charity
        self.lat = lat
        self.lng = lng


class post_request(post):
    def __init__(self, id, person_id, title, category, description, location, reserved, date, is_charity, lat, lng):
        post.__init__(self, id, person_id, title, category, description, location, reserved, date, is_charity, lat, lng)


class post_donation(post):
    def __init__(self, id, person_id, title, category, description, location, reserved, date, is_charity,
                 condition, condition_description, lat, lng):
        post.__init__(self, id, person_id, title, category, description, location, reserved, date, is_charity, lat, lng)
        self.condition = condition
        self.condition_description = condition_description
