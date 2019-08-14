import itertools

_ID_COL = 0
_LASTNAME_COL = 4
_FIRSTNAME_COL = 5
_MINOR_COL = 34
_DEPARTMENTS_COL = 35
_MINOR_DEPARTMENTS_COL = 37
_SHIFTS_COL = 38
_MINOR_SHIFTS_COL = 40
_STAGEHAND_SHIFTS_COL = 41
_CAMPING_SHIFTS_COL = 42
_TRASHHERO_SHIFTS_COL = 43
_CREW_SHIFTS_COL = 44

def convert_row(r, departments, shifts, logger):

    def split(s):
        return [c.strip() for c in s.split(', ') if c.strip()]

    isminor = False if r[_MINOR_COL] == 'Ja' else True
    if isminor:
        department_col = split(r[_MINOR_DEPARTMENTS_COL])
    else:
        department_col = split(r[_DEPARTMENTS_COL])
    desired_departments = []
    for name in department_col:
        if name in departments:
            desired_departments.append(departments[name])
        else:
            logger.warn("Unknown department: {}".format(repr(name)))

    desired_shifts = []

    if isminor:
        normal_shifts_col = split(r[_MINOR_SHIFTS_COL])
    else:
        normal_shifts_col = split(r[_SHIFTS_COL])

    special_shifts_col = {'Stagehand': split(r[_STAGEHAND_SHIFTS_COL]),
                          'Camping': split(r[_CAMPING_SHIFTS_COL]),
                          'Helferbereich': split(r[_CREW_SHIFTS_COL]),
                          'Trashhero': split(r[_TRASHHERO_SHIFTS_COL])}

    for dept in department_col:
        shifts_col = special_shifts_col.get(dept, normal_shifts_col)
        for shift in shifts_col:
            name = dept + " " + shift
            if name in shifts:
                desired_shifts.append(shifts[name])
            else:
                logger.warn("Unknown shift: {}".format(repr(name)))

    return {
        'id': int(r[_ID_COL]),
        'lastname': r[_LASTNAME_COL],
        'firstname': r[_FIRSTNAME_COL],
        'isminor': isminor,
        'assigned_shifts': [],
        'desired_departments': desired_departments,
        'desired_shifts': desired_shifts,
        'min_shifts': 2,
        'max_shifts': 2
    }
