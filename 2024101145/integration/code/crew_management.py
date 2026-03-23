class CrewManagementModule:
    VALID_ROLES = ["driver", "mechanic", "strategist"]

    def __init__(self, registration_module):
        self.registration = registration_module

    def assign_role(self, name, role):
        member = self.registration.get_member(name)
        if not member:
            return False, "Member not registered"
        if role not in self.VALID_ROLES:
            return False, "Invalid role"
        member.role = role
        return True, "Role assigned"

    def record_skill(self, name, skill_level):
        member = self.registration.get_member(name)
        if not member:
            return False, "Member not registered"
        member.skill_level = skill_level
        return True, "Skill level updated"

    def get_available_members(self, role):
        return [m for m in self.registration.members.values() if m.role == role]
