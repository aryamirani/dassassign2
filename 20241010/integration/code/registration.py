class CrewMember:
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.skill_level = 1

class RegistrationModule:
    def __init__(self):
        self.members = {}

    def register_member(self, name, role):
        if name in self.members:
            return False, "Already registered"
        self.members[name] = CrewMember(name, role)
        return True, "Registered successfully"

    def get_member(self, name):
        return self.members.get(name)
