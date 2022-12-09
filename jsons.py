class CandidatesResults:
    def __init__(self, candidate_id=0, result=0):
        self.candidate_id = candidate_id
        self.result = result


class JsonComission:
    def __init__(self, vrn=0, district_id=0, commission_id=0, total_voters=0, received_ballots=0,
                 issued_ballots_inside=0,
                 issued_ballots_outside=0,
                 not_used_ballots=0, ballots_from_outside_boxes=0, ballots_from_inside_boxes=0, invalid_ballots=0,
                 lost_ballots=0,
                 not_counted_received_ballots=0, candidates_results=None):
        self.vrn = vrn
        self.district_id = district_id
        self.commission_id = commission_id
        self.total_voters = total_voters
        self.received_ballots = received_ballots
        self.issued_ballots_inside = issued_ballots_inside
        self.issued_ballots_outside = issued_ballots_outside
        self.not_used_ballots = not_used_ballots
        self.ballots_from_outside_boxes = ballots_from_outside_boxes
        self.ballots_from_inside_boxes = ballots_from_inside_boxes
        self.invalid_ballots = invalid_ballots
        self.lost_ballots = lost_ballots
        self.not_counted_received_ballots = not_counted_received_ballots
        self.candidates_results = candidates_results


class JsonCandidate:
    def __init__(self, vrn=1, district_id=1, candidate_id=1, name="", dob="", place_of_birth="", place_of_living="",
                 education="",
                 employer="", position="",
                 deputy_info="", criminal_record=None, inoagent="", status="", subject_of_nominmation="", nomination="",
                 registration="",
                 elected=""):
        self.vrn = vrn
        self.district_id = district_id
        self.candidate_id = candidate_id
        self.name = name
        self.dob = dob
        self.place_of_birth = place_of_birth
        self.place_of_living = place_of_living
        self.education = education
        self.employer = employer
        self.position = position
        self.deputy_info = deputy_info
        self.criminal_record = criminal_record
        self.inoagent = inoagent
        self.status = status
        self.subject_of_nominmation = subject_of_nominmation
        self.nomination = nomination
        self.registration = registration
        self.elected = elected


class JsonVrn:
    def __init__(self, vrn=1, title="", level="", date=""):
        self.vrn = vrn
        self.title = title
        self.level = level
        self.date = date


class JsonVrnDistrict:
    def __init__(self, vrn, district_id, district_name):
        self.vrn = vrn
        self.district_id = district_id
        self.district_name = district_name
