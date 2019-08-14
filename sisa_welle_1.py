import itertools

_ID_COL = 0
_LASTNAME_COL = 4
_FIRSTNAME_COL = 5
_DURING_FESTIVAL_COL = 33
_MINOR_COL = 44
_DEPARTMENTS_COL = 45
_MINOR_DEPARTMENTS_COL = 46
_SHIFTS_COL = 48
_MINOR_SHIFTS_COL = 49
_STAGEHAND_SHIFTS_COL = 50
_CAMPING_SHIFTS_COL = 51

_DEPARTMENT_CONVERSION = {
    'Creworga': 'Helferbereich'
}

_SHIFT_CONVERSION = {
    'Donnerstag Früh': 'Donnerstag 13:30 - 20:00 Uhr',
    'Freitag Früh': 'Freitag 13:30 - 19:30 Uhr',
    'Freitag Spät': 'Freitag 19:00 - 02:00 Uhr',
    'Samstag Früh': 'Samstag 13:30 - 19:30 Uhr',
    'Samstag Spät': 'Samstag 19:00 - 02:00 Uhr'
}

_SPECIAL_SHIFT_CONVERSION = {
    'Stagehand': {
        'Donnerstag 14:00 - 19:00 Uhr': 'Donnerstag 12:00 - 20:00 Uhr',
        'Freitag 14:00 - 02:00 Uhr': 'Freitag 12:00 - 00:00 Uhr',
        'Samstag 14:00 - 02:00 Uhr': 'Samstag 12:00 - 00:00 Uhr'
    }
}

def convert_row(r, departments, shifts, logger):

    def split(s):
        return [c.strip() for c in s.split(', ') if c.strip()]

    if r[_DURING_FESTIVAL_COL] != 'Ja':
        return None

    isminor = False if r[_MINOR_COL] == 'Ja' else True
    if isminor:
        department_col = split(r[_MINOR_DEPARTMENTS_COL])
    else:
        department_col = split(r[_DEPARTMENTS_COL])
    desired_departments = []
    for name in department_col:
        name = _DEPARTMENT_CONVERSION.get(name, name)
        if name in departments:
            desired_departments.append(departments[name])
        else:
            logger.warn("Unknown department: {}".format(repr(name)))

    if not desired_departments:
        return None

    desired_shifts = []

    if isminor:
        normal_shifts_col = split(r[_MINOR_SHIFTS_COL])
    else:
        normal_shifts_col = split(r[_SHIFTS_COL])

    special_shifts_col = {'Stagehand': split(r[_STAGEHAND_SHIFTS_COL]),
                          'Camping': split(r[_CAMPING_SHIFTS_COL])}

    for dept in department_col:
        dept = _DEPARTMENT_CONVERSION.get(dept, dept)
        shifts_col = special_shifts_col.get(dept, normal_shifts_col)
        for shift in shifts_col:
            shift = _SPECIAL_SHIFT_CONVERSION.get(dept, _SHIFT_CONVERSION).get(shift, shift)
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
        'min_shifts': 0,
        'max_shifts': 2
    }
